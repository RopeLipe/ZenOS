"""
User account creation page.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .base_page import BasePage
from utils.system_utils import validate_username, validate_password
from utils.validation import validate_hostname


class UserPage(BasePage):
    """Page for creating user account."""
    
    def __init__(self):
        super().__init__(
            "User Account", 
            "Create your user account for the new system."
        )
        
        # Create form grid
        grid = Gtk.Grid()
        grid.set_row_spacing(12)
        grid.set_column_spacing(12)
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_margin_top(20)
        
        # Username
        username_label = Gtk.Label(label="Username:")
        username_label.set_halign(Gtk.Align.END)
        grid.attach(username_label, 0, 0, 1, 1)
        
        self.username_entry = Gtk.Entry()
        self.username_entry.set_placeholder_text("Enter username")
        self.username_entry.set_hexpand(True)
        self.username_entry.set_size_request(250, -1)
        self.username_entry.connect("changed", self._on_username_changed)
        grid.attach(self.username_entry, 1, 0, 1, 1)
        
        self.username_status = Gtk.Label()
        self.username_status.set_halign(Gtk.Align.START)
        self.username_status.set_visible(False)
        grid.attach(self.username_status, 2, 0, 1, 1)
        
        # Full name (optional)
        fullname_label = Gtk.Label(label="Full Name:")
        fullname_label.set_halign(Gtk.Align.END)
        grid.attach(fullname_label, 0, 1, 1, 1)
        
        self.fullname_entry = Gtk.Entry()
        self.fullname_entry.set_placeholder_text("Enter full name (optional)")
        self.fullname_entry.set_hexpand(True)
        grid.attach(self.fullname_entry, 1, 1, 1, 1)
          # Password
        password_label = Gtk.Label(label="Password:")
        password_label.set_halign(Gtk.Align.END)
        grid.attach(password_label, 0, 2, 1, 1)
        
        # Password field with eye toggle
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        password_box.set_hexpand(True)
        password_box.add_css_class("linked")
        
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Enter password")
        self.password_entry.set_visibility(False)
        self.password_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self.password_entry.set_hexpand(True)
        self.password_entry.connect("changed", self._on_password_changed)
        password_box.append(self.password_entry)
        
        self.password_toggle = Gtk.Button()
        self.password_toggle.set_icon_name("view-conceal-symbolic")
        self.password_toggle.set_tooltip_text("Show/hide password")
        self.password_toggle.add_css_class("flat")
        self.password_toggle.connect("clicked", self._on_password_toggle)
        password_box.append(self.password_toggle)
        
        grid.attach(password_box, 1, 2, 1, 1)
        
        self.password_status = Gtk.Label()
        self.password_status.set_halign(Gtk.Align.START)
        self.password_status.set_visible(False)
        grid.attach(self.password_status, 2, 2, 1, 1)
          # Confirm password
        confirm_label = Gtk.Label(label="Confirm Password:")
        confirm_label.set_halign(Gtk.Align.END)
        grid.attach(confirm_label, 0, 3, 1, 1)
        
        # Confirm password field with eye toggle
        confirm_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        confirm_box.set_hexpand(True)
        confirm_box.add_css_class("linked")
        
        self.confirm_entry = Gtk.Entry()
        self.confirm_entry.set_placeholder_text("Confirm password")
        self.confirm_entry.set_visibility(False)
        self.confirm_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self.confirm_entry.set_hexpand(True)
        self.confirm_entry.connect("changed", self._on_confirm_changed)
        confirm_box.append(self.confirm_entry)
        
        self.confirm_toggle = Gtk.Button()
        self.confirm_toggle.set_icon_name("view-conceal-symbolic")
        self.confirm_toggle.set_tooltip_text("Show/hide password")
        self.confirm_toggle.add_css_class("flat")
        self.confirm_toggle.connect("clicked", self._on_confirm_toggle)
        confirm_box.append(self.confirm_toggle)
        
        grid.attach(confirm_box, 1, 3, 1, 1)
        
        self.confirm_status = Gtk.Label()
        self.confirm_status.set_halign(Gtk.Align.START)
        self.confirm_status.set_visible(False)
        grid.attach(self.confirm_status, 2, 3, 1, 1)
        
        # Hostname
        hostname_label = Gtk.Label(label="Computer Name:")
        hostname_label.set_halign(Gtk.Align.END)
        grid.attach(hostname_label, 0, 4, 1, 1)
        
        self.hostname_entry = Gtk.Entry()
        self.hostname_entry.set_placeholder_text("Enter computer name")
        self.hostname_entry.set_hexpand(True)
        self.hostname_entry.connect("changed", self._on_hostname_changed)
        grid.attach(self.hostname_entry, 1, 4, 1, 1)
        
        self.hostname_status = Gtk.Label()
        self.hostname_status.set_halign(Gtk.Align.START)
        self.hostname_status.set_visible(False)
        grid.attach(self.hostname_status, 2, 4, 1, 1)
          self.content_box.append(grid)
        
        # Additional options
        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        options_box.set_margin_top(20)
        
        self.auto_login = Gtk.CheckButton(label="Log in automatically")
        self.auto_login.set_tooltip_text("Automatically log in this user when the system starts")
        options_box.append(self.auto_login)
        
        self.admin_user = Gtk.CheckButton(label="Make this user an administrator")
        self.admin_user.set_active(True)  # Default to admin
        self.admin_user.set_tooltip_text("Give this user administrative privileges (sudo access)")
        options_box.append(self.admin_user)
        
        self.content_box.append(options_box)
        
        # Info
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small>Your username will be used to log into the system. "
            "Choose a password that is secure but memorable. "
            "The computer name identifies your system on the network.</small>"
        )
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.START)
        info_label.add_css_class("dim-label")
        info_label.set_margin_top(16)
        self.content_box.append(info_label)
      def _on_username_changed(self, entry):
        """Validate username as user types."""
        username = entry.get_text()
        if username:
            is_valid, error = validate_username(username)
            if is_valid:
                self.username_status.set_text("✓")
                self.username_status.add_css_class("success")
                self.username_status.remove_css_class("error")
                
                # Auto-update hostname in real-time if it's still default or empty
                current_hostname = self.hostname_entry.get_text()
                if not current_hostname or current_hostname.endswith("-computer"):
                    suggested_hostname = f"{username}-computer"
                    self.hostname_entry.set_text(suggested_hostname)
            else:
                self.username_status.set_text("✗")
                self.username_status.add_css_class("error")
                self.username_status.remove_css_class("success")
                self.username_status.set_tooltip_text(error)
            self.username_status.set_visible(True)
        else:
            self.username_status.set_visible(False)
    
    def _on_password_changed(self, entry):
        """Validate password as user types."""
        password = entry.get_text()
        if password:
            is_valid, error = validate_password(password)
            if is_valid:
                self.password_status.set_text("✓")
                self.password_status.add_css_class("success")
                self.password_status.remove_css_class("error")
            else:
                self.password_status.set_text("✗")
                self.password_status.add_css_class("error")
                self.password_status.remove_css_class("success")
                self.password_status.set_tooltip_text(error)
            self.password_status.set_visible(True)
        else:
            self.password_status.set_visible(False)
        
        # Re-validate confirm password
        self._on_confirm_changed(self.confirm_entry)
    
    def _on_confirm_changed(self, entry):
        """Validate password confirmation."""
        password = self.password_entry.get_text()
        confirm = entry.get_text()
        
        if confirm:
            if password == confirm:
                self.confirm_status.set_text("✓")
                self.confirm_status.add_css_class("success")
                self.confirm_status.remove_css_class("error")
            else:
                self.confirm_status.set_text("✗")
                self.confirm_status.add_css_class("error")
                self.confirm_status.remove_css_class("success")
                self.confirm_status.set_tooltip_text("Passwords do not match")
            self.confirm_status.set_visible(True)
        else:
            self.confirm_status.set_visible(False)
    
    def _on_hostname_changed(self, entry):
        """Validate hostname as user types."""
        hostname = entry.get_text()
        if hostname:
            is_valid, error = validate_hostname(hostname)
            if is_valid:
                self.hostname_status.set_text("✓")
                self.hostname_status.add_css_class("success")
                self.hostname_status.remove_css_class("error")
            else:
                self.hostname_status.set_text("✗")
                self.hostname_status.add_css_class("error")
                self.hostname_status.remove_css_class("success")
                self.hostname_status.set_tooltip_text(error)
            self.hostname_status.set_visible(True)
        else:
            self.hostname_status.set_visible(False)
      def _on_show_password_toggled(self, checkbox):
        """Toggle password visibility."""
        visible = checkbox.get_active()
        self.password_entry.set_visibility(visible)
        self.confirm_entry.set_visibility(visible)
    
    def _on_password_toggle(self, button):
        """Toggle password visibility for main password field."""
        visible = not self.password_entry.get_visibility()
        self.password_entry.set_visibility(visible)
        
        # Update icon
        if visible:
            button.set_icon_name("view-reveal-symbolic")
            button.set_tooltip_text("Hide password")
        else:
            button.set_icon_name("view-conceal-symbolic")
            button.set_tooltip_text("Show password")
    
    def _on_confirm_toggle(self, button):
        """Toggle password visibility for confirm password field."""
        visible = not self.confirm_entry.get_visibility()
        self.confirm_entry.set_visibility(visible)
        
        # Update icon
        if visible:
            button.set_icon_name("view-reveal-symbolic")
            button.set_tooltip_text("Hide password")
        else:
            button.set_icon_name("view-conceal-symbolic")
            button.set_tooltip_text("Show password")
    
    def get_data(self) -> dict:
        """Get user account data."""
        return {
            "username": self.username_entry.get_text(),
            "password": self.password_entry.get_text(),  
            "fullname": self.fullname_entry.get_text(),
            "hostname": self.hostname_entry.get_text(),
            "auto_login": self.auto_login.get_active(),
            "admin_user": self.admin_user.get_active()
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate all user data."""
        data = self.get_data()
        
        # Validate username
        username = data.get("username", "")
        if not username:
            return False, "Username is required"
        
        is_valid, error = validate_username(username)
        if not is_valid:
            return False, f"Username: {error}"
        
        # Validate password
        password = data.get("password", "")
        if not password:
            return False, "Password is required"
        
        is_valid, error = validate_password(password)
        if not is_valid:
            return False, f"Password: {error}"
        
        # Validate password confirmation
        confirm = self.confirm_entry.get_text()
        if password != confirm:
            return False, "Passwords do not match"
        
        # Validate hostname
        hostname = data.get("hostname", "")
        if not hostname:
            return False, "Computer name is required"
        
        is_valid, error = validate_hostname(hostname)
        if not is_valid:
            return False, f"Computer name: {error}"
        
        return True, ""
    
    def on_page_enter(self):
        """Focus username entry when page becomes visible."""
        self.username_entry.grab_focus()
