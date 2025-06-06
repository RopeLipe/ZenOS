# Linux GTK4 Installer

A modern, user-friendly Linux system installer built with GTK4 and Python.

## Features

- **Modern GTK4 Interface**: Clean, accessible user interface
- **Multi-step Installation Process**: Guided setup through all necessary steps
- **Input Validation**: Comprehensive validation with real-time feedback
- **Safety Features**: Confirmation dialogs and warnings for destructive operations
- **Progress Tracking**: Real-time installation progress with detailed logging
- **Flexible Configuration**: Support for various locales, keyboards, timezones
- **Network Configuration**: WiFi setup with connection testing
- **User Management**: User account creation with security options

## Installation Steps

1. **Language Selection**: Choose system locale and language
2. **Keyboard Layout**: Select and test keyboard layout
3. **Timezone**: Set system timezone with auto-detection
4. **Disk Selection**: Choose installation disk with safety warnings
5. **Network Setup**: Configure WiFi (optional)
6. **User Account**: Create user account with security options
7. **Confirmation**: Review settings before installation
8. **Installation**: Automated system installation with progress

## Requirements

### System Requirements
- Root/sudo access
- Linux environment with required tools
- At least 2GB of available disk space
- Python 3.8+ with GTK4 bindings

### Required System Tools
- `sgdisk` (GPT partitioning)
- `parted` (partition management)
- `mkfs.ext4` (filesystem creation)
- `mount`/`umount` (filesystem mounting)
- `debootstrap` (Debian base system)
- `chroot` (change root environment)
- `grub-install` (bootloader)
- `update-grub` (bootloader configuration)
- `blkid` (UUID detection for fstab generation)
- `nmcli` (network management)

### Python Dependencies
```bash
pip install -r requirements.txt
```

On Ubuntu/Debian:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 dbus-x11
```

## Usage

### Running the Installer

**Recommended method** (with environment checks):
```bash
sudo python3 launcher.py
```

**Direct method**:
```bash
sudo python3 main.py
```

The `launcher.py` script provides:
- Prerequisites checking (Python version, GTK4, D-Bus)
- Environment setup (display, D-Bus session)
- Better error reporting and guidance
- Automatic privilege escalation if needed

**Important**: The installer must be run with root privileges to perform system-level operations.

### Development Mode
For testing the UI without system modifications:
```bash
python3 main.py --dry-run  # (if implemented)
```

## Project Structure

```
├── main.py                 # Main application entry point
├── launcher.py             # Launcher with prerequisites checking
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── system_utils.py    # System information gathering
│   └── validation.py      # Input validation functions
│
├── pages/                 # UI pages
│   ├── __init__.py
│   ├── base_page.py       # Base page class and common pages
│   ├── locale_page.py     # Language selection
│   ├── keyboard_page.py   # Keyboard layout
│   ├── timezone_page.py   # Timezone selection
│   ├── disk_page.py       # Disk selection
│   ├── wifi_page.py       # WiFi configuration
│   └── user_page.py       # User account creation
│
├── installer/             # Installation logic
│   ├── __init__.py
│   └── installation_manager.py  # Core installation logic
│
└── styles/                # Styling
    └── installer.css      # GTK CSS styles
```

## Bug Fixes and Improvements

### Original Issues Fixed

1. **Navigation Issues**
   - Added Back button for navigation
   - Proper page validation before navigation
   - Progress indicator

2. **Input Validation**
   - Real-time validation with visual feedback
   - Comprehensive error checking
   - Safety confirmations for destructive operations

3. **Error Handling**
   - Robust subprocess error handling
   - Timeout protection for long operations
   - Graceful fallbacks for missing tools/data

4. **User Experience**
   - Modern, accessible interface
   - Clear progress indication during installation
   - Helpful tooltips and descriptions
   - Auto-detection features where possible

5. **Safety Features**
   - Multiple confirmation dialogs
   - Clear warnings for data loss
   - Dependency checking before installation
   - Installation logging

6. **Code Organization**
   - Separated concerns into logical modules
   - Reusable base classes
   - Clean separation of UI and logic
   - Comprehensive documentation

### New Features Added

- **Auto-detection**: Timezone and locale detection
- **Connection Testing**: WiFi connection verification
- **Progress Tracking**: Real-time installation progress
- **Input Validation**: Live validation with visual feedback
- **Safety Checks**: Dependency verification and warnings
- **Improved UI**: Modern GTK4 interface with better styling
- **Error Recovery**: Better error handling and recovery options

## Security Considerations

- Root password is randomly generated for security
- Input validation prevents injection attacks
- Safe subprocess execution with timeouts
- Proper error handling prevents information disclosure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (especially on virtual machines)
5. Submit a pull request

## Testing

**Warning**: This installer performs destructive operations. Always test on virtual machines or dedicated test hardware.

### Test Environment Setup
1. Create a virtual machine with sufficient disk space
2. Boot from a Linux live environment
3. Install the installer dependencies
4. Run the installer

## License

This project is provided as-is for educational and development purposes. Use at your own risk.

## Disclaimer

**⚠️ WARNING**: This installer will permanently erase all data on the selected disk. Always backup important data before running the installer. Test thoroughly in virtual machines before using on physical hardware.

## Troubleshooting

### Common Issues

**D-Bus Session Warning**: 
```
Unable to acquire session bus: Failed to execute child process "dbus-launch"
```
- Solution: Install D-Bus X11 support: `sudo apt install dbus-x11`
- The launcher.py script will attempt to start a D-Bus session automatically

**GTK4 Not Found**:
```
Error: GTK4 not available
```
- Solution: Install GTK4 bindings: `sudo apt install python3-gi gir1.2-gtk-4.0`

**Missing System Tools**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'tool_name'
```
- Install required system tools:
  - Ubuntu/Debian: `sudo apt install util-linux parted e2fsprogs debootstrap grub-pc-bin grub-efi-amd64-bin network-manager`
  - Fedora: `sudo dnf install util-linux parted e2fsprogs debootstrap grub2-tools NetworkManager`
  - Note: Some tools like `debootstrap` are Debian-specific and may need alternatives on other distributions
```
AttributeError: 'MessageDialog' object has no attribute 'format_secondary_text'
```
- This is handled automatically with fallbacks to simpler dialogs
- Install libadwaita for better dialog support: `sudo apt install gir1.2-adw-1`

**Root Permission Issues**:
- The installer requires root access for system operations
- Use `sudo python3 launcher.py` to run with proper privileges
- The launcher will attempt to re-run with sudo if needed

**Display Issues**:
- Ensure you're running in a graphical environment
- For SSH: use `ssh -X user@host` for X11 forwarding
- For WSL: install an X server like VcXsrv
