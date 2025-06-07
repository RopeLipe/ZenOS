"""
Main installer window and application.
"""

import gi
import logging
import sys
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

# Try to use Adw for better dialogs if available
try:
    gi.require_version("Adw", "1")
    from gi.repository import Adw
    HAS_ADW = True
except (ImportError, ValueError):
    HAS_ADW = False

# Import pages
from pages.locale_page import LocalePage
from pages.keyboard_page import KeyboardPage
from pages.timezone_page import TimezonePage
from pages.disk_page import DiskPage
from pages.wifi_page import WiFiPage
from pages.user_page import UserPage
from pages.base_page import LoadingPage, ConfirmationPage

# Import utilities
from utils.system_utils import check_dependencies, is_running_as_root
from utils.validation import validate_all_inputs
from installer.installation_manager import InstallationManager, InstallationError


class InstallerWindow(Gtk.ApplicationWindow):
    """Main installer window."""
    
    def __init__(self, app):        super().__init__(application=app)
        self.set_title("Linux System Installer")
        
        # Set up window properties
        self.set_default_size(900, 700)  # Reasonable size that fits on most screens
        self.set_resizable(False)  # Not resizable
        
        # Set up logging
        self._setup_logging()
        
        # Check prerequisites
        if not self._check_prerequisites():
            return
        
        # Initialize UI
        self._setup_ui()
        self._setup_pages()
        self._setup_navigation()
        
        # Show first page
        self.current_page_index = 0
        self._update_navigation()
        self._show_current_page()
    
    def _setup_logging(self):
        """Set up logging for the installer."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('/tmp/installer.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Installer started")
    def _check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        try:
            # Check if running as root
            if not is_running_as_root():
                self._show_error_dialog(
                    "Root Access Required",
                    "This installer must be run with root privileges.\n"
                    "Please run with 'sudo' or as root user."
                )
                return False
            
            # Check dependencies
            deps = check_dependencies()
            missing = [tool for tool, available in deps.items() if not available]
            
            if missing:
                self._show_error_dialog(
                    "Missing Dependencies",
                    f"The following required tools are missing:\n\n" +
                    "\n".join(f"• {tool}" for tool in missing) +
                    "\n\nPlease install these tools before running the installer."
                )
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Prerequisites check failed: {e}")
            # Don't show error dialog here to avoid recursion
            print(f"Error checking prerequisites: {e}")
            return False    def _setup_ui(self):
        """Set up the main UI layout."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)
        
        # Custom titlebar with only close button
        titlebar = Gtk.HeaderBar()
        titlebar.set_show_title_buttons(False)  # Hide all default buttons
        
        # Title label
        title_label = Gtk.Label(label="Linux System Installer")
        title_label.add_css_class("installer-title")
        titlebar.set_title_widget(title_label)
        
        # Close button
        close_button = Gtk.Button()
        close_button.set_icon_name("window-close-symbolic")
        close_button.add_css_class("circular")
        close_button.add_css_class("destructive-action")
        close_button.set_tooltip_text("Close Installer")
        close_button.connect("clicked", self._on_close_clicked)
        titlebar.pack_end(close_button)
        
        self.set_titlebar(titlebar)
        
        # Add CSS classes for styling
        self.add_css_class("installer-window")
        
        # Step indicator at the top
        self._setup_step_indicator(main_box)
        
        # Content area with stack
        content_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        content_container.set_hexpand(True)
        content_container.set_vexpand(True)
        content_container.set_margin_start(20)
        content_container.set_margin_end(20)
        content_container.set_margin_top(10)
        content_container.set_margin_bottom(10)
        
        # Stack for pages
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        content_container.append(self.stack)        
        
        main_box.append(content_container)
        
        # Circular navigation buttons - bottom right
        nav_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        nav_container.set_halign(Gtk.Align.END)
        nav_container.set_margin_end(30)
        nav_container.set_margin_bottom(30)
        nav_container.set_spacing(15)
        
        # Back button - circular
        self.back_button = Gtk.Button()
        self.back_button.set_icon_name("go-previous-symbolic")
        self.back_button.connect("clicked", self._on_back_clicked)
        self.back_button.add_css_class("circular-nav-button")
        self.back_button.set_size_request(50, 50)
        nav_container.append(self.back_button)
        
        # Next button - circular
        self.next_button = Gtk.Button()
        self.next_button.set_icon_name("go-next-symbolic")
        self.next_button.connect("clicked", self._on_next_clicked)
        self.next_button.add_css_class("circular-nav-button")
        self.next_button.add_css_class("suggested-action")
        self.next_button.set_size_request(50, 50)
        nav_container.append(self.next_button)
        
        main_box.append(nav_container)
    
    def _setup_step_indicator(self, parent_box):
        """Set up the animated step indicator at the top."""
        step_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        step_container.set_halign(Gtk.Align.CENTER)
        step_container.set_margin_top(20)
        step_container.set_margin_bottom(20)
        step_container.set_spacing(40)
        step_container.add_css_class("step-indicator")
        
        self.step_circles = []
        self.step_labels = []
        step_names = ["Language", "Keyboard", "Timezone", "Storage", "Network", "User"]
        
        for i, step_name in enumerate(step_names):
            step_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            step_box.set_halign(Gtk.Align.CENTER)
            
            # Step circle
            circle = Gtk.Label(label=str(i + 1))
            circle.set_size_request(40, 40)
            circle.add_css_class("step-circle")
            circle.add_css_class("step-inactive")
            self.step_circles.append(circle)
            step_box.append(circle)
            
            # Step label
            label = Gtk.Label(label=step_name)
            label.add_css_class("step-label")
            label.add_css_class("step-inactive")
            self.step_labels.append(label)
            step_box.append(label)
            
            step_container.append(step_box)
            
            # Add connecting line (except for last step)
            if i < len(step_names) - 1:
                line = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                line.set_size_request(30, 2)
                line.set_valign(Gtk.Align.CENTER)
                line.add_css_class("step-connector")
                step_container.append(line)
        
        parent_box.append(step_container)
    
    def _setup_pages(self):
        """Initialize all installer pages."""
        self.pages = [
            LocalePage(),
            KeyboardPage(),
            TimezonePage(),
            DiskPage(),
            WiFiPage(),
            UserPage()
        ]
        
        # Add pages to stack
        for i, page in enumerate(self.pages):
            self.stack.add_named(page, f"page_{i}")
        
        # Special pages
        self.confirmation_page = ConfirmationPage()
        self.stack.add_named(self.confirmation_page, "confirmation")
        
        self.loading_page = LoadingPage()
        self.stack.add_named(self.loading_page, "loading")
    
    def _setup_navigation(self):
        """Set up navigation state."""
        self.current_page_index = 0
        self.total_pages = len(self.pages)
        self.installation_data = {}
      def _update_navigation(self):
        """Update navigation button states and step indicators."""
        # Update back button
        self.back_button.set_sensitive(self.current_page_index > 0)
        
        # Update next button icon
        if self.current_page_index < self.total_pages - 1:
            self.next_button.set_icon_name("go-next-symbolic")
        else:
            self.next_button.set_icon_name("system-run-symbolic")
          # Update step indicators
        self._update_step_indicators()
    
    def _update_step_indicators(self):
        """Update the step indicator circles and labels."""
        for i, (circle, label) in enumerate(zip(self.step_circles, self.step_labels)):
            # Remove existing state classes
            circle.remove_css_class("step-active")
            circle.remove_css_class("step-completed")
            circle.remove_css_class("step-inactive")
            label.remove_css_class("step-active")
            label.remove_css_class("step-completed")
            label.remove_css_class("step-inactive")
            
            # Add appropriate state class
            if i < self.current_page_index:
                circle.add_css_class("step-completed")
                label.add_css_class("step-completed")
                circle.set_text("✓")
            elif i == self.current_page_index:
                circle.add_css_class("step-active")
                label.add_css_class("step-active")
                circle.set_text(str(i + 1))
            else:
                circle.add_css_class("step-inactive")
                label.add_css_class("step-inactive")
                circle.set_text(str(i + 1))
      def _show_current_page(self):
        """Show the current page and call its enter handler."""
        if 0 <= self.current_page_index < len(self.pages):
            page = self.pages[self.current_page_index]
            page.on_page_enter()
            self.stack.set_visible_child_name(f"page_{self.current_page_index}")
        
        self._update_navigation()
    
    def _on_back_clicked(self, button):
        """Handle back button click."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self._show_current_page()
    
    def _on_next_clicked(self, button):
        """Handle next button click."""
        current_page = self.pages[self.current_page_index]
        
        # Validate current page
        if not current_page.on_page_leave():
            return  # Validation failed, stay on current page
        
        # Store page data
        page_data = current_page.get_data()
        self.installation_data.update(page_data)
        
        # Move to next page or show confirmation
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self._show_current_page()
        else:
            self._show_confirmation()
      def _show_confirmation(self):
        """Show the installation confirmation page."""
        # Update confirmation page with collected data
        self.confirmation_page.update_summary(self.installation_data)
        self.stack.set_visible_child_name("confirmation")
        
        # Update navigation for confirmation
        self.back_button.set_sensitive(True)
        self.next_button.set_icon_name("system-run-symbolic")
          # Hide step indicators during confirmation
        for circle, label in zip(self.step_circles, self.step_labels):
            circle.get_parent().set_visible(False)
        
        # Connect to final install
        try:
            self.next_button.disconnect_by_func(self._on_next_clicked)
        except:
            pass
        self.next_button.connect("clicked", self._on_install_clicked)
    
    def _on_install_clicked(self, button):
        """Start the installation process."""
        # Final validation
        is_valid, errors = validate_all_inputs(self.installation_data)
        if not is_valid:
            error_msg = "Please fix the following issues:\n\n" + "\n".join(f"• {error}" for error in errors)
            self._show_error_dialog("Validation Error", error_msg)
            return        # Show loading page
        self.stack.set_visible_child_name("loading")
        self.back_button.set_sensitive(False)
        self.next_button.set_sensitive(False)
        
        # Start installation
        self._start_installation()
    
    def _start_installation(self):
        """Start the installation process."""
        def progress_callback(message: str, percent: int):
            """Handle progress updates from installation."""
            GLib.idle_add(self.loading_page.update_progress, message, percent)
        
        def installation_complete(success: bool):
            """Handle installation completion."""
            if success:
                GLib.idle_add(self._show_success_dialog)
            else:
                GLib.idle_add(self._show_installation_error)
        
        # Create installation manager
        installer = InstallationManager(progress_callback)
        
        # Run installation in a separate thread (simplified for this example)
        import threading
        
        def install_thread():
            try:
                success = installer.install_system(self.installation_data)
                installation_complete(success)
            except Exception as e:
                self.logger.error(f"Installation failed: {e}")
                installation_complete(False)        
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
    
    def _show_success_dialog(self):
            """Show installation success dialog."""
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Installation Complete!"
            )
            dialog.set_property("secondary-text", 
                "The system has been installed successfully. "
                "The computer will restart automatically."            )
            dialog.connect("response", self._on_success_response)
            dialog.present()
    
    def _show_installation_error(self):
            """Show installation error dialog."""
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Installation Failed"
            )
            dialog.set_property("secondary-text",
                "The installation could not be completed. "
                "Please check the log file for details and try again."            )
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()
        
        # Re-enable navigation
        self.back_button.set_sensitive(True)
        self.next_button.set_sensitive(True)
    
    def _on_success_response(self, dialog, response):
        """Handle success dialog response."""        dialog.destroy()
        
        # Trigger reboot (in a real installer)
        import subprocess
        try:
            subprocess.run(["reboot"], check=False)
        except:
            pass
        
        # Close application
        self.close()
    
    def _show_error_dialog(self, title: str, message: str):
        """Show a generic error dialog."""
        # Try Adw.MessageDialog first (preferred for GTK4)
        if HAS_ADW:
            try:
                dialog = Adw.MessageDialog.new(self, title, message)
                dialog.add_response("ok", "OK")
                dialog.set_default_response("ok")
                dialog.connect("response", lambda d, r: d.destroy())
                dialog.present()
                return
            except Exception as e:
                print(f"Adw.MessageDialog failed: {e}")
        
        # Fallback to Gtk.MessageDialog
        try:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=title
            )
            # Use format_secondary_text for GTK4 compatibility
            dialog.format_secondary_text(message)
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.present()
        except Exception as e:
            # Fallback for when GTK dialog fails
            print(f"ERROR: {title}")
            print(f"Message: {message}")
            print(f"Dialog error: {e}")
            
            # Create a simple dialog as fallback
            try:
                dialog = Gtk.Dialog(title=title, transient_for=self, modal=True)
                dialog.add_button("OK", Gtk.ResponseType.OK)
                
                content_area = dialog.get_content_area()
                label = Gtk.Label(label=f"{title}\n\n{message}")
                label.set_wrap(True)
                label.set_margin_top(20)
                label.set_margin_bottom(20)
                label.set_margin_start(20)
                label.set_margin_end(20)
                content_area.append(label)
                
                dialog.connect("response", lambda d, r: d.destroy())
                dialog.present()
            except Exception as e2:
                print(f"Fallback dialog also failed: {e2}")
                # Final fallback - just print and continue
                print("Using console output as final fallback")


class InstallerApp(Gtk.Application):
    """Main installer application."""
    
    def __init__(self):
        super().__init__(application_id="org.example.linux.installer")
        self.connect("activate", self.on_activate)
        
        # Initialize Adw if available
        if HAS_ADW:
            Adw.init()
    
    def on_activate(self, app):
        """Handle application activation."""
        win = InstallerWindow(self)
        win.present()


def main():
    """Main entry point."""
    app = InstallerApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
