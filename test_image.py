#!/usr/bin/env python3
"""
Test script to verify image loading
"""

import gi
import os
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

class TestWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Image Test")
        self.set_default_size(400, 300)
        
        # Create box layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        
        # Debug information
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "language-icon.png")
        
        label = Gtk.Label(label=f"Image path: {icon_path}")
        label.set_wrap(True)
        label.set_xalign(0)
        box.append(label)
        
        exists_label = Gtk.Label(label=f"File exists: {os.path.exists(icon_path)}")
        exists_label.set_xalign(0)
        box.append(exists_label)
        
        # Try Method 1: Direct file loading
        try:
            image1 = Gtk.Image()
            image1.set_from_file(icon_path)
            label1 = Gtk.Label(label="Method 1: Image.set_from_file()")
            label1.set_xalign(0)
            box.append(label1)
            box.append(image1)
        except Exception as e:
            error_label = Gtk.Label(label=f"Method 1 error: {e}")
            error_label.set_xalign(0)
            box.append(error_label)
            
        # Try Method 2: Using Gio.File
        try:
            file = Gio.File.new_for_path(icon_path)
            image2 = Gtk.Image.new_from_gicon(Gio.FileIcon.new(file))
            label2 = Gtk.Label(label="Method 2: Image.new_from_gicon()")
            label2.set_xalign(0)
            box.append(label2)
            box.append(image2)
        except Exception as e:
            error_label = Gtk.Label(label=f"Method 2 error: {e}")
            error_label.set_xalign(0)
            box.append(error_label)
        
        self.set_child(box)

class TestApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.test.imageloading")
        
    def do_activate(self):
        win = TestWindow(application=self)
        win.present()

if __name__ == "__main__":
    app = TestApp()
    app.run(None)
