#!/usr/bin/env python3
"""
GTK4 Installer - Main Application
A modern installer interface with multiple configuration pages
"""

# Debug helpers
import os
print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print(f"Assets directory exists: {os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'))}")
print(f"Assets directory contents: {os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'))}")

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
import sys
import os

from pages.language_page import LanguagePage
from pages.timezone_page import TimezonePage
from pages.keyboard_page import KeyboardPage
from pages.disk_page import DiskPage
from pages.wifi_page import WifiPage
from pages.user_page import UserPage
from pages.welcome_page import WelcomePage # Import WelcomePage

class InstallerWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Window properties
        self.set_title("System Installer")
        self.set_default_size(1024, 720) # Increased window size
        self.set_resizable(False)
        
        # Remove titlebar for clean rounded look
        self.set_decorated(False)
        
        # Load custom CSS
        self.load_css()
        
        # Create main stack for pages
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        
        # Initialize pages
        self.init_pages()
        
        # Create main layout
        self.setup_layout()
        
        # Show first page
        self.stack.set_visible_child_name("welcome") # Start with welcome page
    
    def load_css(self):
        """Load custom CSS styling"""
        css_provider = Gtk.CssProvider()
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        
        try:
            css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                self.get_display(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Warning: Could not load CSS: {e}")
    
    def init_pages(self):
        """Initialize all installer pages"""
        self.pages = {
            "welcome": WelcomePage(self.navigate_to), # Add welcome page
            "language": LanguagePage(self.navigate_to),
            "timezone": TimezonePage(self.navigate_to),
            "keyboard": KeyboardPage(self.navigate_to),
            "disk": DiskPage(self.navigate_to),
            "wifi": WifiPage(self.navigate_to),
            "user": UserPage(self.navigate_to)        }
        
        # Add pages to stack
        for name, page in self.pages.items():
            self.stack.add_named(page, name)
    
    def setup_layout(self):
        """Setup main layout"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.add_css_class("main-window")
        main_box.append(self.stack)
        self.set_content(main_box)
    
    def navigate_to(self, page_name):
        """Navigate to specified page"""
        if page_name in self.pages:
            self.stack.set_visible_child_name(page_name)
        elif page_name == "finish":
            self.finish_installation()
    
    def finish_installation(self):
        """Handle installation completion"""
        dialog = Adw.MessageDialog.new(
            self,
            "Installation Complete",
            "The system has been configured successfully!"
        )
        dialog.add_response("ok", "OK")
        dialog.connect("response", lambda d, r: self.close())
        dialog.present()

class InstallerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.zen.installer")
        self.connect('activate', self.on_activate)
    
    def on_activate(self, app):
        self.win = InstallerWindow(application=app)
        self.win.present()

def main():
    app = InstallerApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    main()
