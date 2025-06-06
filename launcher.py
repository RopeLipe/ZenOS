#!/usr/bin/env python3
"""
Launch script for the GTK installer.
This script checks prerequisites and starts the main installer.
"""

import sys
import os
import subprocess

def check_root():
    """Check if running as root."""
    return os.geteuid() == 0 if hasattr(os, 'geteuid') else True

def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        return False
    return True

def check_gtk():
    """Check if GTK4 is available."""
    try:
        import gi
        gi.require_version("Gtk", "4.0")
        from gi.repository import Gtk
        return True
    except (ImportError, ValueError) as e:
        print(f"Error: GTK4 not available: {e}")
        print("Please install GTK4 Python bindings:")
        print("  Ubuntu/Debian: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0")
        print("  Fedora: sudo dnf install python3-gobject gtk4-devel")
        print("  Arch: sudo pacman -S python-gobject gtk4")
        return False

def main():
    """Main launcher function."""
    print("GTK Linux Installer Launcher")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check GTK availability
    if not check_gtk():
        sys.exit(1)
    
    # Check root access
    if not check_root():
        print("Warning: This installer requires root privileges.")
        print("Please run with: sudo python3 launcher.py")
        
        # Try to re-run with sudo
        try:
            subprocess.run(["sudo", sys.executable] + sys.argv)
            sys.exit(0)
        except KeyboardInterrupt:
            print("\nInstaller cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"Failed to run with sudo: {e}")
            sys.exit(1)
    
    # All checks passed, start the installer
    try:
        from main import main as installer_main
        sys.exit(installer_main())
    except ImportError as e:
        print(f"Error: Could not import installer: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInstaller cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Installer error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
