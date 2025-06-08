# GTK4 System Installer

A modern, dark-themed system installer built with GTK4 and Python. Features a sleek interface with multiple configuration pages for system setup.

## Features

- **Language Selection**: Choose your preferred language
- **Timezone Configuration**: Select your timezone and region
- **Keyboard Layout**: Configure keyboard layout and language
- **Disk Selection**: Choose installation disk with encryption options
- **WiFi Setup**: Connect to wireless networks
- **User Account Creation**: Create user accounts with avatar support

## Design

The installer features a modern dark theme with:
- Dark background (#0D0D0D) with subtle borders
- Blue accent color (#4490EC) for primary actions
- Inter font family throughout
- Consistent spacing and typography
- Smooth page transitions

## Requirements

- Python 3.8+
- GTK4
- PyGObject
- Libadwaita

## Installation

### On Ubuntu/Debian:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
pip install -r requirements.txt
```

### On Fedora:
```bash
sudo dnf install python3-gobject gtk4-devel libadwaita-devel
pip install -r requirements.txt
```

### On Arch Linux:
```bash
sudo pacman -S python-gobject gtk4 libadwaita
pip install -r requirements.txt
```

## Usage

Run the installer:
```bash
python3 main.py
```

## Project Structure

```
├── main.py              # Main application entry point
├── style.css            # Custom CSS styling
├── requirements.txt     # Python dependencies
├── pages/              # Individual installer pages
│   ├── __init__.py
│   ├── base_page.py    # Base page class
│   ├── language_page.py # Language selection
│   ├── timezone_page.py # Timezone configuration
│   ├── keyboard_page.py # Keyboard layout
│   ├── disk_page.py    # Disk selection
│   ├── wifi_page.py    # WiFi setup
│   └── user_page.py    # User account creation
└── README.md
```

## Screenshots

The installer includes the following pages:
1. Language selection with searchable list
2. Timezone selection with region/city dropdowns
3. Keyboard layout with live preview
4. Disk selection with encryption options
5. WiFi setup with network scanning
6. User account creation with avatar support

## Customization

The installer uses CSS for styling. Modify `style.css` to customize:
- Colors and themes
- Fonts and typography
- Spacing and layouts
- Button styles
- Form elements

## Development

This is a frontend-only implementation focusing on the UI/UX. For a production installer, you would need to implement:
- Actual system detection and configuration
- Real disk partitioning and formatting
- Network management integration
- Package installation and system setup
- Hardware detection and driver installation

## License

MIT License - feel free to use and modify as needed.
