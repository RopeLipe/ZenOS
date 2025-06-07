"""
User Account Creation Page
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GdkPixbuf
from .base_page import BasePage

class UserPage(BasePage):
    def __init__(self, navigate_callback):
        super().__init__(navigate_callback)
        self.setup_page()
        
    def setup_page(self):
        # Create header
        self.create_header(
            "Account",
            "Create an Account", 
            "Enter your Account details."
        )
        
        # User creation form
        self.setup_user_form()
        
        # Setup navigation
        self.back_btn.connect("clicked", lambda x: self.navigate("wifi"))
        self.continue_btn.connect("clicked", self.on_continue)
        self.continue_btn.set_sensitive(False)  # Initially disabled
        
        # Update continue button text
        self.continue_btn.set_label("Continue")
        self.continue_btn.add_css_class("btn-disabled")
        self.continue_btn.remove_css_class("btn-primary")
        
    def setup_user_form(self):
        """Setup user account creation form"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.set_spacing(40)
        
        # Left side - Avatar
        avatar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        avatar_box.set_spacing(16)
        avatar_box.set_valign(Gtk.Align.START)
        
        # Avatar placeholder (circular)
        self.avatar_button = Gtk.Button()
        self.avatar_button.set_size_request(136, 136)
        self.avatar_button.add_css_class("avatar-placeholder")
        self.avatar_button.connect("clicked", self.on_avatar_clicked)
        
        # Avatar icon/image placeholder
        avatar_icon = Gtk.Label(label="👤")
        avatar_icon.set_markup('<span font="48">👤</span>')
        self.avatar_button.set_child(avatar_icon)
        
        avatar_box.append(self.avatar_button)
        
        # Right side - Form fields
        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        form_box.set_spacing(16)
        form_box.set_hexpand(True)
        
        # Username field
        username_row = self.create_form_row("Username:", self.create_username_entry())
        form_box.append(username_row)
        
        # Password field
        password_row = self.create_form_row("Password:", self.create_password_entry())
        form_box.append(password_row)
        
        # Full name field (optional)
        fullname_row = self.create_form_row("Full Name (Optional):", self.create_fullname_entry())
        form_box.append(fullname_row)
        
        # Computer name field
        computer_row = self.create_form_row("Computer Name:", self.create_computer_entry())
        form_box.append(computer_row)
        
        # Account options
        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        options_box.set_spacing(8)
        options_box.add_css_class("form-section")
        
        # Auto-login checkbox
        self.auto_login_check = Gtk.CheckButton(label="Log in automatically")
        options_box.append(self.auto_login_check)
        
        # Admin privileges checkbox
        self.admin_check = Gtk.CheckButton(label="Make this user an administrator")
        self.admin_check.set_active(True)  # Default to admin
        options_box.append(self.admin_check)
        
        form_box.append(options_box)
        
        # Password strength indicator
        self.password_strength = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.password_strength.set_spacing(4)
        self.password_strength.set_visible(False)
        
        strength_label = Gtk.Label(label="Password strength:")
        strength_label.add_css_class("info-text")
        self.password_strength.append(strength_label)
        
        self.strength_indicator = Gtk.Label(label="Weak")
        self.strength_indicator.add_css_class("warning-text")
        self.password_strength.append(self.strength_indicator)
        
        form_box.append(self.password_strength)
        
        main_box.append(avatar_box)
        main_box.append(form_box)
        
        self.content_box.append(main_box)
        
    def create_username_entry(self):
        """Create username entry"""
        self.username_entry = Gtk.Entry()
        self.username_entry.set_placeholder_text("Enter Username")
        self.username_entry.connect("changed", self.on_field_changed)
        self.username_entry.connect("changed", self.on_username_changed)
        return self.username_entry
        
    def create_password_entry(self):
        """Create password entry"""
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_placeholder_text("Enter Password")
        self.password_entry.connect("changed", self.on_field_changed)
        self.password_entry.connect("changed", self.on_password_changed)
        return self.password_entry
        
    def create_fullname_entry(self):
        """Create full name entry"""
        self.fullname_entry = Gtk.Entry()
        self.fullname_entry.set_placeholder_text("Enter your full name")
        return self.fullname_entry
        
    def create_computer_entry(self):
        """Create computer name entry"""
        self.computer_entry = Gtk.Entry()
        self.computer_entry.set_placeholder_text("Enter computer name")
        self.computer_entry.set_text("zen-desktop")  # Default name
        return self.computer_entry
        
    def on_username_changed(self, entry):
        """Handle username change - update computer name"""
        username = entry.get_text().strip()
        if username and not self.computer_entry.get_text().startswith(username):
            self.computer_entry.set_text(f"{username}-desktop")
            
    def on_password_changed(self, entry):
        """Handle password change - show strength indicator"""
        password = entry.get_text()
        
        if not password:
            self.password_strength.set_visible(False)
            return
            
        self.password_strength.set_visible(True)
        
        # Simple password strength calculation
        strength_score = 0
        
        if len(password) >= 8:
            strength_score += 1
        if any(c.isupper() for c in password):
            strength_score += 1
        if any(c.islower() for c in password):
            strength_score += 1
        if any(c.isdigit() for c in password):
            strength_score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            strength_score += 1
            
        # Update strength indicator
        if strength_score <= 2:
            self.strength_indicator.set_text("Weak")
            self.strength_indicator.remove_css_class("info-text")
            self.strength_indicator.add_css_class("warning-text")
        elif strength_score <= 3:
            self.strength_indicator.set_text("Medium")
            self.strength_indicator.remove_css_class("warning-text")
            self.strength_indicator.remove_css_class("info-text")
            self.strength_indicator.set_markup('<span color="#FFA500">Medium</span>')
        else:
            self.strength_indicator.set_text("Strong")
            self.strength_indicator.remove_css_class("warning-text")
            self.strength_indicator.add_css_class("info-text")
            self.strength_indicator.set_markup('<span color="#4490EC">Strong</span>')
            
    def on_field_changed(self, entry):
        """Handle form field changes - validate form"""
        username = self.username_entry.get_text().strip()
        password = self.password_entry.get_text().strip()
        
        # Enable continue button if both username and password are provided
        if username and password:
            self.continue_btn.set_sensitive(True)
            self.continue_btn.remove_css_class("btn-disabled")
            self.continue_btn.add_css_class("btn-primary")
            # Update button text color
            continue_label = self.continue_btn.get_child()
            if isinstance(continue_label, Gtk.Label):
                continue_label.set_markup('<span color="#FFFFFF">Continue</span>')
        else:
            self.continue_btn.set_sensitive(False)
            self.continue_btn.add_css_class("btn-disabled")
            self.continue_btn.remove_css_class("btn-primary")
            # Reset button text color
            continue_label = self.continue_btn.get_child()
            if isinstance(continue_label, Gtk.Label):
                continue_label.set_markup('<span color="rgba(255, 255, 255, 0.5)">Continue</span>')
                
    def on_avatar_clicked(self, button):
        """Handle avatar button click"""
        # In a real app, this would open a file chooser for avatar selection
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Avatar Selection",
            secondary_text="Avatar selection feature would be implemented here."
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
        
    def validate_form(self):
        """Validate the form data"""
        username = self.username_entry.get_text().strip()
        password = self.password_entry.get_text().strip()
        computer_name = self.computer_entry.get_text().strip()
        
        errors = []
        
        # Username validation
        if not username:
            errors.append("Username is required.")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        elif not username.isalnum():
            errors.append("Username can only contain letters and numbers.")
            
        # Password validation
        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
            
        # Computer name validation
        if not computer_name:
            errors.append("Computer name is required.")
        elif len(computer_name) < 2:
            errors.append("Computer name must be at least 2 characters long.")
            
        return errors
        
    def show_errors(self, errors):
        """Show validation errors"""
        error_text = "\\n".join(errors)
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Validation Error",
            secondary_text=error_text
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
        
    def on_continue(self, button):
        """Handle continue button click"""
        # Validate form
        errors = self.validate_form()
        if errors:
            self.show_errors(errors)
            return
            
        # Get form data
        user_data = {
            "username": self.username_entry.get_text().strip(),
            "password": self.password_entry.get_text().strip(),
            "fullname": self.fullname_entry.get_text().strip(),
            "computer_name": self.computer_entry.get_text().strip(),
            "auto_login": self.auto_login_check.get_active(),
            "is_admin": self.admin_check.get_active()
        }
        
        print("User account data:")
        for key, value in user_data.items():
            if key != "password":  # Don't print password
                print(f"  {key}: {value}")
                
        # Navigate to finish (or next step)
        self.navigate("finish")
