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

def check_display_environment():
    """Check if we have a proper display environment."""
    display = os.environ.get('DISPLAY')
    wayland_display = os.environ.get('WAYLAND_DISPLAY')
    
    if not display and not wayland_display:
        print("Warning: No display environment detected.")
        print("Make sure you're running this in a graphical environment.")
        print("If using SSH, try: ssh -X user@host")
        return False
    
    return True

def check_dbus():
    """Check if dbus is available and set up environment."""
    try:
        # Check if dbus-launch is available
        result = subprocess.run(['which', 'dbus-launch'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("Warning: dbus-launch not found. GTK may have issues.")
            print("Install with: sudo apt install dbus-x11")
            return False
        
        # Check if DBUS_SESSION_BUS_ADDRESS is set
        if not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
            print("Info: Starting dbus session...")
            try:
                # Start dbus session if not running
                result = subprocess.run(['dbus-launch', '--sh-syntax'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Parse and set dbus environment variables
                    for line in result.stdout.strip().split('\n'):
                        if '=' in line and line.startswith('DBUS_'):
                            key, value = line.split('=', 1)
                            # Remove quotes from value
                            value = value.strip('\'"')
                            os.environ[key] = value
                    print("Info: D-Bus session started successfully")
                else:
                    print("Warning: Failed to start dbus session")
            except subprocess.TimeoutExpired:
                print("Warning: dbus-launch timed out")
            except Exception as e:
                print(f"Warning: Error starting dbus: {e}")
                
    except Exception:
        print("Warning: Could not check dbus availability")
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
    
    # Check display environment
    if not check_display_environment():
        print("Continuing anyway...")
    
    # Check dbus
    if not check_dbus():
        print("Continuing anyway...")
    
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
