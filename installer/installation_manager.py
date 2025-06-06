"""
Installation logic for the GTK installer.
Handles the actual system installation process.
"""

import subprocess
import os
import random
import string
import logging
from typing import Dict, Callable, Optional
from pathlib import Path

# Import utility functions
from utils.system_utils import is_running_as_root, get_device_uuid, get_device_fstype


class InstallationError(Exception):
    """Custom exception for installation errors."""
    pass


class InstallationManager:
    """Manages the Linux installation process."""
    
    def __init__(self, progress_callback: Optional[Callable[[str, int], None]] = None):
        """
        Initialize the installation manager.
        
        Args:
            progress_callback: Function to call with (message, progress_percent)
        """
        self.progress_callback = progress_callback
        self.mount_point = "/mnt"
        self.logger = logging.getLogger(__name__)
        
    def _update_progress(self, message: str, percent: int):
        """Update progress if callback is provided."""
        if self.progress_callback:
            self.progress_callback(message, percent)
        self.logger.info(f"Progress {percent}%: {message}")
    
    def _run_command(self, cmd: list, check: bool = True, timeout: int = 300) -> subprocess.CompletedProcess:
        """Run a system command with error handling."""
        try:
            self.logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=check,
                timeout=timeout
            )
            if result.stderr:
                self.logger.warning(f"Command stderr: {result.stderr}")
            return result
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(cmd)}\nError: {e.stderr}"
            self.logger.error(error_msg)
            raise InstallationError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out: {' '.join(cmd)}"
            self.logger.error(error_msg)
            raise InstallationError(error_msg)
    
    def prepare_disk(self, disk_path: str):
        """Prepare the disk for installation."""
        self._update_progress("Preparing disk...", 10)
        
        # Unmount any existing partitions
        try:
            self._run_command(["umount", "-f", f"{disk_path}*"], check=False)
        except:
            pass  # Ignore errors if nothing was mounted
        
        # Clear partition table
        self._run_command(["sgdisk", "--zap-all", disk_path])
        
        # Create new GPT partition table
        self._run_command(["parted", disk_path, "mklabel", "gpt", "--script"])
        
        # Create EFI partition (512MB)
        self._run_command([
            "parted", disk_path, "mkpart", "primary", "fat32", "1MiB", "513MiB", "--script"
        ])
        self._run_command(["parted", disk_path, "set", "1", "esp", "on", "--script"])
        
        # Create root partition (rest of disk)
        self._run_command([
            "parted", disk_path, "mkpart", "primary", "ext4", "513MiB", "100%", "--script"
        ])
        
        # Wait for kernel to recognize partitions
        self._run_command(["partprobe", disk_path])
        
        self._update_progress("Formatting partitions...", 20)
        
        # Format partitions
        efi_part = f"{disk_path}1"
        root_part = f"{disk_path}2"
        
        self._run_command(["mkfs.fat", "-F32", efi_part])
        self._run_command(["mkfs.ext4", "-F", root_part])
        
        return efi_part, root_part
    
    def mount_partitions(self, efi_part: str, root_part: str):
        """Mount the partitions for installation."""
        self._update_progress("Mounting partitions...", 25)
        
        # Create mount point if it doesn't exist
        os.makedirs(self.mount_point, exist_ok=True)
        
        # Mount root partition
        self._run_command(["mount", root_part, self.mount_point])
        
        # Create and mount EFI partition
        efi_mount = f"{self.mount_point}/boot/efi"
        os.makedirs(efi_mount, exist_ok=True)
        self._run_command(["mount", efi_part, efi_mount])
    
    def install_base_system(self):
        """Install the base system using debootstrap."""
        self._update_progress("Installing base system...", 30)
        
        # Install base system
        self._run_command([
            "debootstrap", 
            "--arch=amd64", 
            "stable", 
            self.mount_point, 
            "http://deb.debian.org/debian"
        ], timeout=1800)  # 30 minutes timeout
        
        self._update_progress("Base system installed", 60)
    
    def configure_system(self, config: Dict[str, str]):
        """Configure the installed system."""
        self._update_progress("Configuring system...", 65)
        
        # Configure locale
        locale_gen_path = f"{self.mount_point}/etc/locale.gen"
        with open(locale_gen_path, "w") as f:
            f.write(f"{config['locale']} UTF-8\n")
        
        self._run_command(["chroot", self.mount_point, "locale-gen"])
        
        # Configure timezone
        timezone_path = f"{self.mount_point}/etc/timezone"
        with open(timezone_path, "w") as f:
            f.write(f"{config['timezone']}\n")
        
        self._run_command([
            "chroot", self.mount_point, "ln", "-sf", 
            f"/usr/share/zoneinfo/{config['timezone']}", "/etc/localtime"
        ])
        
        # Configure keyboard
        vconsole_path = f"{self.mount_point}/etc/vconsole.conf"
        with open(vconsole_path, "w") as f:
            f.write(f"KEYMAP={config['keyboard']}\n")
        
        # Set hostname
        hostname = config.get('hostname', 'debian-system')
        hostname_path = f"{self.mount_point}/etc/hostname"
        with open(hostname_path, "w") as f:
            f.write(f"{hostname}\n")
        
        # Configure hosts file
        hosts_path = f"{self.mount_point}/etc/hosts"
        with open(hosts_path, "w") as f:
            f.write("127.0.0.1\tlocalhost\n")
            f.write(f"127.0.1.1\t{hostname}\n")
            f.write("::1\t\tlocalhost ip6-localhost ip6-loopback\n")
    
    def create_user(self, username: str, password: str):
        """Create a user account."""
        self._update_progress("Creating user account...", 75)
        
        # Create user
        self._run_command([
            "chroot", self.mount_point, "useradd", "-m", "-s", "/bin/bash", username
        ])
        
        # Set user password
        self._run_command([
            "chroot", self.mount_point, "bash", "-c", 
            f"echo '{username}:{password}' | chpasswd"
        ])
        
        # Add user to sudo group
        self._run_command([
            "chroot", self.mount_point, "usermod", "-aG", "sudo", username
        ])
        
        # Set random root password for security
        root_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        self._run_command([
            "chroot", self.mount_point, "bash", "-c", 
            f"echo 'root:{root_password}' | chpasswd"
        ])
        
        self.logger.info(f"Root password set to: {root_password}")
    
    def configure_network(self, wifi_ssid: str = "", wifi_password: str = ""):
        """Configure network settings."""
        if wifi_ssid and wifi_password:
            self._update_progress("Configuring WiFi...", 80)
            # Copy NetworkManager connections
            src = "/etc/NetworkManager/system-connections"
            dst = f"{self.mount_point}/etc/NetworkManager/system-connections"
            if os.path.exists(src):
                self._run_command(["cp", "-r", src, dst], check=False)
    
    def install_bootloader(self, disk_path: str):
        """Install and configure the bootloader."""
        self._update_progress("Installing bootloader...", 85)
        
        # Install GRUB packages
        self._run_command([
            "chroot", self.mount_point, "apt-get", "update"
        ])
        self._run_command([
            "chroot", self.mount_point, "apt-get", "install", "-y", 
            "grub-efi-amd64", "grub-efi-amd64-signed"
        ])
        
        # Install GRUB
        self._run_command([
            "chroot", self.mount_point, "grub-install", 
            "--target=x86_64-efi", "--efi-directory=/boot/efi", 
            "--bootloader-id=GRUB", disk_path
        ])
          # Generate GRUB configuration
        self._run_command([
            "chroot", self.mount_point, "update-grub"
        ])
    
    def generate_fstab(self):
        """Generate filesystem table manually."""
        self._update_progress("Generating filesystem table...", 90)
        
        fstab_path = f"{self.mount_point}/etc/fstab"
        
        # Get UUID and filesystem type of the root partition
        root_partition = f"{self.disk}2"  # Typically the root partition
        root_uuid = get_device_uuid(root_partition)
        root_fstype = get_device_fstype(root_partition) or "ext4"
        
        # Generate fstab content
        fstab_content = f"""# /etc/fstab: static file system information.
#
# Use 'blkid' to print the universally unique identifier for a
# device; this may be used with UUID= as a more robust way to name devices
# that works even if disks are added and removed. See fstab(5).
#
# <file system>             <mount point>   <type>  <options>       <dump>  <pass>
"""
        
        # Add root partition
        if root_uuid:
            fstab_content += f"UUID={root_uuid}     /               {root_fstype}    defaults        0       1\n"
        else:
            # Fallback to device name if UUID detection fails
            fstab_content += f"{root_partition}        /               {root_fstype}    defaults        0       1\n"
            
        # Add EFI partition if it exists
        efi_partition = f"{self.disk}1"  # Typically the EFI partition
        efi_uuid = get_device_uuid(efi_partition)
        efi_fstype = get_device_fstype(efi_partition)
        
        if efi_uuid and efi_fstype in ["vfat", "fat32"]:
            fstab_content += f"UUID={efi_uuid}     /boot/efi       vfat    defaults        0       2\n"
        elif efi_fstype in ["vfat", "fat32"]:
            fstab_content += f"{efi_partition}        /boot/efi       vfat    defaults        0       2\n"
            
        # Add common tmpfs entries for better performance
        fstab_content += """
# tmpfs for temporary files
tmpfs                     /tmp            tmpfs   defaults,noatime,mode=1777  0  0
"""
        
        # Add swap if configured (placeholder for future implementation)
        # swap_partition = f"{self.disk}3"  # If swap partition exists
        # swap_uuid = get_device_uuid(swap_partition)
        # if swap_uuid:
        #     fstab_content += f"UUID={swap_uuid}     none            swap    sw              0       0\n"
        
        try:
            with open(fstab_path, "w") as f:
                f.write(fstab_content)
            self.logger.info(f"Generated fstab: {fstab_path}")
        except Exception as e:
            raise InstallationError(f"Failed to generate fstab: {e}")
    
    def cleanup(self):
        """Unmount partitions and cleanup."""
        self._update_progress("Cleaning up...", 95)
        
        try:
            self._run_command(["umount", "-R", self.mount_point], check=False)
        except:
            pass  # Ignore errors during cleanup
    
    def install_system(self, config: Dict[str, str]) -> bool:
        """
        Perform complete system installation.
        
        Args:
            config: Dictionary containing installation configuration
            
        Returns:
            True if installation successful, False otherwise
        """
        try:
            # Prepare disk
            efi_part, root_part = self.prepare_disk(config['disk'])
            
            # Mount partitions
            self.mount_partitions(efi_part, root_part)
            
            # Install base system
            self.install_base_system()
            
            # Configure system
            self.configure_system(config)
            
            # Create user
            self.create_user(config['username'], config['password'])
            
            # Configure network
            self.configure_network(
                config.get('wifi_ssid', ''), 
                config.get('wifi_password', '')
            )
            
            # Install bootloader
            self.install_bootloader(config['disk'])
            
            # Generate fstab
            self.generate_fstab()
            
            # Cleanup
            self.cleanup()
            
            self._update_progress("Installation completed successfully!", 100)
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            self._update_progress(f"Installation failed: {str(e)}", -1)
            
            # Attempt cleanup
            try:
                self.cleanup()
            except:
                pass
            
            return False
