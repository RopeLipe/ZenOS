import gi
import os
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

def load_image_from_path(path):
    """
    Helper function to load an image from a path
    """
    if not os.path.exists(path):
        print(f"Error: Image file not found at {path}")
        return None
        
    try:
        # Try Gio.File method
        file = Gio.File.new_for_path(path)
        file_icon = Gio.FileIcon.new(file)
        image = Gtk.Image.new_from_gicon(file_icon)
        return image
    except Exception as e:
        print(f"Error loading image with Gio: {e}")
        
    try:
        # Try direct file method
        image = Gtk.Image.new_from_file(path)
        return image
    except Exception as e:
        print(f"Error loading image directly: {e}")
        
    # All methods failed
    return None
