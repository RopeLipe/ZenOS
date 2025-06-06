"""
System utility functions for the GTK installer.
Handles system information gathering and validation.
"""

import subprocess
import os
import json
from typing import List, Optional


def get_all_locales() -> List[str]:
    """Get all available system locales with user-friendly names."""
    locale_mapping = {
        # Common locales with friendly names
        "en_US.UTF-8": "English (United States)",
        "en_GB.UTF-8": "English (United Kingdom)",
        "en_CA.UTF-8": "English (Canada)",
        "en_AU.UTF-8": "English (Australia)",
        "es_ES.UTF-8": "Spanish (Spain)",
        "es_MX.UTF-8": "Spanish (Mexico)",
        "fr_FR.UTF-8": "French (France)",
        "fr_CA.UTF-8": "French (Canada)",
        "de_DE.UTF-8": "German (Germany)",
        "it_IT.UTF-8": "Italian (Italy)",
        "pt_BR.UTF-8": "Portuguese (Brazil)",
        "pt_PT.UTF-8": "Portuguese (Portugal)",
        "ru_RU.UTF-8": "Russian (Russia)",
        "zh_CN.UTF-8": "Chinese (Simplified)",
        "zh_TW.UTF-8": "Chinese (Traditional)",
        "ja_JP.UTF-8": "Japanese (Japan)",
        "ko_KR.UTF-8": "Korean (South Korea)",
        "ar_SA.UTF-8": "Arabic (Saudi Arabia)",
        "hi_IN.UTF-8": "Hindi (India)",
        "nl_NL.UTF-8": "Dutch (Netherlands)",
        "sv_SE.UTF-8": "Swedish (Sweden)",
        "da_DK.UTF-8": "Danish (Denmark)",
        "no_NO.UTF-8": "Norwegian (Norway)",
        "fi_FI.UTF-8": "Finnish (Finland)",
        "pl_PL.UTF-8": "Polish (Poland)",
        "tr_TR.UTF-8": "Turkish (Turkey)",
        "C.UTF-8": "C/POSIX (Default)",
        "POSIX": "POSIX (Minimal)"
    }
    
    available_locales = set()
    locale_files = ["/usr/share/i18n/SUPPORTED", "/etc/locale.gen"]
    
    for locale_file in locale_files:
        try:
            with open(locale_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        locale = line.split()[0]
                        if locale in locale_mapping:
                            available_locales.add(locale)
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error reading locale file {locale_file}: {e}")
    
    # Fallback locales if files not found
    if not available_locales:
        available_locales = {"en_US.UTF-8", "C.UTF-8", "POSIX"}
    
    # Return sorted list of available locales that have friendly names
    return sorted([loc for loc in available_locales if loc in locale_mapping])


def get_locale_display_name(locale_code: str) -> str:
    """Get display name for a locale code."""
    locale_mapping = {
        "en_US.UTF-8": "English (United States)",
        "en_GB.UTF-8": "English (United Kingdom)",
        "en_CA.UTF-8": "English (Canada)",
        "en_AU.UTF-8": "English (Australia)",
        "es_ES.UTF-8": "Spanish (Spain)",
        "es_MX.UTF-8": "Spanish (Mexico)",
        "fr_FR.UTF-8": "French (France)",
        "fr_CA.UTF-8": "French (Canada)",
        "de_DE.UTF-8": "German (Germany)",
        "it_IT.UTF-8": "Italian (Italy)",
        "pt_BR.UTF-8": "Portuguese (Brazil)",
        "pt_PT.UTF-8": "Portuguese (Portugal)",
        "ru_RU.UTF-8": "Russian (Russia)",
        "zh_CN.UTF-8": "Chinese (Simplified)",
        "zh_TW.UTF-8": "Chinese (Traditional)",
        "ja_JP.UTF-8": "Japanese (Japan)",
        "ko_KR.UTF-8": "Korean (South Korea)",
        "ar_SA.UTF-8": "Arabic (Saudi Arabia)",
        "hi_IN.UTF-8": "Hindi (India)",
        "nl_NL.UTF-8": "Dutch (Netherlands)",
        "sv_SE.UTF-8": "Swedish (Sweden)",
        "da_DK.UTF-8": "Danish (Denmark)",
        "no_NO.UTF-8": "Norwegian (Norway)",
        "fi_FI.UTF-8": "Finnish (Finland)",
        "pl_PL.UTF-8": "Polish (Poland)",
        "tr_TR.UTF-8": "Turkish (Turkey)",
        "C.UTF-8": "C/POSIX (Default)",
        "POSIX": "POSIX (Minimal)"
    }
    return locale_mapping.get(locale_code, locale_code)


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
