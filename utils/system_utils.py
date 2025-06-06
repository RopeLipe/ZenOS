"""
System utility functions for the GTK installer.
Handles system information gathering and validation.
"""

import subprocess
import os
import json
from typing import List, Optional


def get_all_locales() -> List[str]:
    """Get all available system locales."""
    locales = set()
    locale_files = ["/usr/share/i18n/SUPPORTED", "/etc/locale.gen"]
    
    for locale_file in locale_files:
        try:
            with open(locale_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        locale = line.split()[0]
                        locales.add(locale)
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error reading locale file {locale_file}: {e}")
    
    # Fallback locales if files not found
    if not locales:
        locales = {"en_US.UTF-8", "C.UTF-8", "POSIX"}
    
    return sorted(locales)


def get_all_keymaps() -> List[str]:
    """Get all available keyboard layouts."""
    try:
        result = subprocess.run(
            ["localectl", "list-keymaps"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            keymaps = result.stdout.strip().split('\n')
            return sorted(set(filter(None, keymaps)))
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error getting keymaps: {e}")
    
    # Fallback common keymaps
    return ["us", "uk", "de", "fr", "es", "it"]


def get_all_timezones() -> List[str]:
    """Get all available timezones."""
    zones = []
    timezone_dir = "/usr/share/zoneinfo"
    
    if not os.path.exists(timezone_dir):
        # Fallback common timezones
        return [
            "UTC", "America/New_York", "America/Los_Angeles",
            "Europe/London", "Europe/Berlin", "Asia/Tokyo"
        ]
    
    try:
        for root, dirs, files in os.walk(timezone_dir):
            # Skip certain directories
            if any(skip in root for skip in ["posix", "right", "Etc"]):
                continue
                
            for name in files:
                if name[0].isupper():  # Timezone files start with uppercase
                    path = os.path.join(root, name)
                    zone = os.path.relpath(path, timezone_dir)
                    zones.append(zone)
    except Exception as e:
        print(f"Error reading timezone directory: {e}")
        return ["UTC"]
    
    return sorted(zones)


def get_disks() -> List[dict]:
    """Get all available disks with detailed information."""
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,SIZE,TYPE,MODEL", "-d", "-J"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            disks = []
            for device in data.get('blockdevices', []):
                if device.get('type') == 'disk':
                    disks.append({
                        'name': f"/dev/{device['name']}",
                        'size': device.get('size', 'Unknown'),
                        'model': device.get('model', 'Unknown'),
                        'display': f"/dev/{device['name']} ({device.get('size', 'Unknown')}) - {device.get('model', 'Unknown')}"
                    })
            return disks
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error getting disk information: {e}")
    
    return []


def get_wifi_networks() -> List[str]:
    """Get available WiFi networks."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID", "dev", "wifi", "list"], 
            capture_output=True, 
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            ssids = list(set(filter(None, result.stdout.strip().split('\n'))))
            return sorted(ssids)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error getting WiFi networks: {e}")
    
    return []


def check_dependencies() -> dict:
    """Check if all required tools are available."""
    required_tools = [
        'sgdisk', 'parted', 'mkfs.ext4', 'mount', 'umount',
        'debootstrap', 'chroot', 'grub-install', 'update-grub',
        'blkid', 'nmcli'  # Use blkid instead of genfstab for UUID detection
    ]
    
    results = {}
    for tool in required_tools:
        try:
            result = subprocess.run(['which', tool], capture_output=True, timeout=5)
            results[tool] = result.returncode == 0
        except subprocess.TimeoutExpired:
            results[tool] = False
    
    return results


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username according to Linux standards."""
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 2:
        return False, "Username must be at least 2 characters"
    
    if len(username) > 32:
        return False, "Username must be less than 32 characters"
    
    if not username[0].isalpha():
        return False, "Username must start with a letter"
    
    if not username.replace('_', '').replace('-', '').isalnum():
        return False, "Username can only contain letters, numbers, hyphens, and underscores"
    
    if username.lower() in ['root', 'daemon', 'bin', 'sys', 'sync', 'games', 'man', 'lp', 'mail', 'news', 'uucp', 'proxy', 'www-data', 'backup', 'list', 'irc', 'gnats', 'nobody']:
        return False, "Username conflicts with system user"
    
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    return True, ""


def get_device_uuid(device_path: str) -> str:
    """Get UUID of a block device."""
    try:
        result = subprocess.run(
            ["blkid", "-s", "UUID", "-o", "value", device_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    return ""


def get_device_fstype(device_path: str) -> str:
    """Get filesystem type of a block device."""
    try:
        result = subprocess.run(
            ["blkid", "-s", "TYPE", "-o", "value", device_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    return ""


def is_running_as_root() -> bool:
    """Check if the installer is running with root privileges."""
    return os.geteuid() == 0
