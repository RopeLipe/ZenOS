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
print("DEBUG: Attempting to import GTK and Adwaita...")

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
print("DEBUG: GTK and Adwaita versions required.")

from gi.repository import Gtk, Adw, Gio, GLib, Gdk # Added Gdk
print("DEBUG: GTK and Adwaita modules imported.")
import sys

print("DEBUG: Importing page modules...")
from pages.language_page import LanguagePage
from pages.timezone_page import TimezonePage
from pages.keyboard_page import KeyboardPage
from pages.disk_page import DiskPage
from pages.wifi_page import WifiPage
from pages.user_page import UserPage
from pages.welcome_page import WelcomePage # Import WelcomePage
print("DEBUG: Page modules imported successfully.")

class InstallerWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        print("DEBUG: InstallerWindow __init__ - ENTERED CONSTRUCTOR.") # Print at very start
        super().__init__(**kwargs)
        print("DEBUG: InstallerWindow __init__ - Adw.ApplicationWindow super().__init__() COMPLETED.")

        # Window properties
        self.set_title("System Installer")
        print("DEBUG: InstallerWindow __init__ - Title SET.")
        
        # Remove titlebar for clean rounded look
        self.set_decorated(False)
        print("DEBUG: InstallerWindow __init__ - Decoration SET to False.")
        
        # Load custom CSS
        self.load_css()
        print("DEBUG: InstallerWindow __init__ - CSS LOADED.")
        
        # Create main stack for pages
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        print("DEBUG: InstallerWindow __init__ - Stack CREATED.")
        
        # Initialize pages
        self.init_pages()
        print("DEBUG: InstallerWindow __init__ - Pages INITIALIZED.")
        
        # Create main layout
        self.setup_layout()
        print("DEBUG: InstallerWindow __init__ - Layout SETUP.")
        
        # Show first page
        self.stack.set_visible_child_name("welcome") # Start with welcome page
        print("DEBUG: InstallerWindow __init__ - Visible child SET to 'welcome'.")
        print("DEBUG: InstallerWindow __init__ - END (CONSTRUCTOR FINISHED)")
    
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
        print("DEBUG: InstallerApp __init__ - START")
        # Try with application_id=None again, but with the original on_activate
        super().__init__(application_id=None, # Changed back to None
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        print("DEBUG: InstallerApp __init__ - Adw.Application super().__init__() COMPLETED (id=None, flags=NONE).")
        
        self.win = None
        
        self.connect('activate', self.on_activate) # Connect to original on_activate
        print("DEBUG: InstallerApp __init__ - 'activate' signal CONNECTED to self.on_activate.")
        print("DEBUG: InstallerApp __init__ - END")

    def on_activate(self, app_instance): 
        print("DEBUG: InstallerApp on_activate (ORIGINAL) - CALLED.")
        
        if not self.win:
            print("DEBUG: InstallerApp on_activate - Creating InstallerWindow.")
            self.win = InstallerWindow(application=app_instance)
            print("DEBUG: InstallerApp on_activate - InstallerWindow INSTANTIATED.")
        else:
            print("DEBUG: InstallerApp on_activate - InstallerWindow ALREADY EXISTS.")
        
        if self.win:
            self.win.present()
            print("DEBUG: InstallerApp on_activate - InstallerWindow PRESENTED.")
        else:
            print("ERROR: InstallerApp on_activate - self.win is None, cannot present.")
        print("DEBUG: InstallerApp on_activate (ORIGINAL) - END.")

def main():
    print("DEBUG: main() function called.")
    app = InstallerApp()
    print("DEBUG: InstallerApp instantiated in main().")
    exit_code = 1 # Default to error
    try:
        print("DEBUG: Attempting to run app.run(sys.argv)...")
        exit_code = app.run(sys.argv) # Use standard app.run()
        print(f"DEBUG: app.run() finished with exit_code: {exit_code}")
    except GLib.Error as e:
        print(f"GLib Error during app.run(): {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    except Exception as e:
        print(f"Unhandled Python Exception during app.run() or earlier: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    finally:
        print(f"DEBUG: main() function returning {exit_code}.")
        return exit_code

if __name__ == "__main__":
    print("DEBUG: Script entry point (__name__ == '__main__').")
    final_exit_code = main()
    print(f"DEBUG: Script exiting with code: {final_exit_code}.")
    sys.exit(final_exit_code)
