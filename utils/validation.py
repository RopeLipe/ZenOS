"""
Validation utilities for the GTK installer.
Provides input validation and error checking functions.
"""

import re
import os
from typing import Tuple


def validate_empty_field(value: str, field_name: str) -> Tuple[bool, str]:
    """Validate that a field is not empty."""
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty"
    return True, ""


def validate_disk_selection(disk_info: dict) -> Tuple[bool, str]:
    """Validate disk selection and check if it's safe to use."""
    if not disk_info:
        return False, "No disk selected"
    
    disk_path = disk_info.get('name', '')
    if not disk_path.startswith('/dev/'):
        return False, "Invalid disk path"
    
    if not os.path.exists(disk_path):
        return False, f"Disk {disk_path} not found"
    
    return True, ""


def validate_wifi_password(password: str, ssid: str = "") -> Tuple[bool, str]:
    """Validate WiFi password based on common requirements."""
    if not ssid:  # If no SSID selected, password validation is skipped
        return True, ""
    
    if not password:
        return False, "WiFi password is required for selected network"
    
    if len(password) < 8:
        return False, "WiFi password must be at least 8 characters"
    
    if len(password) > 63:
        return False, "WiFi password cannot exceed 63 characters"
    
    return True, ""


def validate_hostname(hostname: str) -> Tuple[bool, str]:
    """Validate hostname according to RFC standards."""
    if not hostname:
        return False, "Hostname cannot be empty"
    
    if len(hostname) > 63:
        return False, "Hostname cannot exceed 63 characters"
    
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', hostname):
        return False, "Hostname can only contain letters, numbers, and hyphens (not at start/end)"
    
    if hostname.lower() in ['localhost', 'local']:
        return False, "Hostname cannot be 'localhost' or 'local'"
    
    return True, ""


def validate_all_inputs(data: dict) -> Tuple[bool, list]:
    """Validate all installer inputs at once."""
    errors = []
    
    # Validate locale
    if not data.get('locale'):
        errors.append("Language/locale must be selected")
    
    # Validate keyboard
    if not data.get('keyboard'):
        errors.append("Keyboard layout must be selected")
    
    # Validate timezone
    if not data.get('timezone'):
        errors.append("Timezone must be selected")
    
    # Validate disk
    is_valid, error = validate_disk_selection(data.get('disk', {}))
    if not is_valid:
        errors.append(error)
    
    # Validate username
    username = data.get('username', '')
    is_valid, error = validate_empty_field(username, "Username")
    if not is_valid:
        errors.append(error)
    else:
        from .system_utils import validate_username
        is_valid, error = validate_username(username)
        if not is_valid:
            errors.append(error)
    
    # Validate password
    password = data.get('password', '')
    is_valid, error = validate_empty_field(password, "Password")
    if not is_valid:
        errors.append(error)
    else:
        from .system_utils import validate_password
        is_valid, error = validate_password(password)
        if not is_valid:
            errors.append(error)
    
    # Validate WiFi if selected
    wifi_ssid = data.get('wifi_ssid', '')
    wifi_password = data.get('wifi_password', '')
    if wifi_ssid:
        is_valid, error = validate_wifi_password(wifi_password, wifi_ssid)
        if not is_valid:
            errors.append(error)
    
    return len(errors) == 0, errors
