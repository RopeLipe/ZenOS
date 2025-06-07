"""
Disk Selection Page
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .base_page import BasePage

class DiskPage(BasePage):
    def __init__(self, navigate_callback):
        super().__init__(navigate_callback)
        self.setup_page()
        
    def setup_page(self):
        # Create header
        self.create_header(
            "Storage",
            "Select Installation Disk",
            "Choose where to install the system. WARNING: This will erase all data on the selected disk."
        )
        
        # Disk selection
        self.setup_disk_selection()
        
        # Setup navigation
        self.back_btn.connect("clicked", lambda x: self.navigate("keyboard"))
        self.continue_btn.connect("clicked", self.on_continue)
        
    def setup_disk_selection(self):
        """Setup disk selection interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_spacing(20)
        
        # Disk list
        disk_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        disk_box.set_spacing(8)
        
        disk_label = Gtk.Label(label="Available Disks:")
        disk_label.add_css_class("form-label")
        disk_label.set_halign(Gtk.Align.START)
        disk_box.append(disk_label)
        
        self.disk_list = self.create_disk_list()
        disk_box.append(self.disk_list)
        
        main_box.append(disk_box)
        
        # Installation options
        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        options_box.set_spacing(12)
        
        options_label = Gtk.Label(label="Installation Options:")
        options_label.add_css_class("form-label")
        options_label.set_halign(Gtk.Align.START)
        options_box.append(options_label)
          # Installation type radio buttons
        self.install_type_group = []
        
        # Erase and install
        erase_radio = Gtk.CheckButton(label="Erase disk and install (Recommended)")
        erase_radio.set_active(True)
        erase_radio.install_type = "erase"
        self.install_type_group.append(erase_radio)
        options_box.append(erase_radio)
        
        # Manual partitioning
        manual_radio = Gtk.CheckButton(label="Manual partitioning (Advanced)")
        manual_radio.set_group(erase_radio)
        manual_radio.install_type = "manual"
        self.install_type_group.append(manual_radio)
        options_box.append(manual_radio)
        
        main_box.append(options_box)
        
        # Encryption option
        encrypt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        encrypt_box.set_spacing(8)
        
        self.encrypt_check = Gtk.CheckButton(label="Encrypt the installation for security")
        encrypt_box.append(self.encrypt_check)
        
        # Encryption password (initially hidden)
        self.encrypt_password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.encrypt_password_box.set_spacing(8)
        self.encrypt_password_box.set_visible(False)
        
        password_row = self.create_form_row("Encryption Password:", self.create_password_entry())
        confirm_row = self.create_form_row("Confirm Password:", self.create_confirm_entry())
        
        self.encrypt_password_box.append(password_row)
        self.encrypt_password_box.append(confirm_row)
        
        encrypt_box.append(self.encrypt_password_box)
        
        # Connect encryption checkbox
        self.encrypt_check.connect("toggled", self.on_encrypt_toggled)
        
        main_box.append(encrypt_box)
        
        # Warning message
        warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        warning_box.set_spacing(8)
        warning_box.add_css_class("warning-text")
        
        warning_icon = Gtk.Label(label="⚠️")
        warning_text = Gtk.Label(label="WARNING: This will permanently erase all data on the selected disk.")
        warning_text.set_wrap(True)
        
        warning_box.append(warning_icon)
        warning_box.append(warning_text)
        
        main_box.append(warning_box)
        
        self.content_box.append(main_box)
        
    def create_disk_list(self):
        """Create disk selection list"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(150)
        
        self.disk_listbox = Gtk.ListBox()
        self.disk_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        
        # Mock disk data (in real app, this would come from system)
        disks = [
            {
                "name": "/dev/sda",
                "size": "500 GB",
                "type": "SSD",
                "model": "Samsung SSD 850 EVO"
            },
            {
                "name": "/dev/sdb",
                "size": "1 TB",
                "type": "HDD",
                "model": "Western Digital Blue"
            },
            {
                "name": "/dev/nvme0n1",
                "size": "256 GB",
                "type": "NVMe SSD",
                "model": "Intel SSD 660p"
            }
        ]
        
        for disk in disks:
            row = Gtk.ListBoxRow()
            row.set_margin_start(12)
            row.set_margin_end(12)
            row.set_margin_top(8)
            row.set_margin_bottom(8)
            
            disk_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            disk_box.set_spacing(4)
            
            # Disk name and size
            name_label = Gtk.Label(label=f"{disk['name']} - {disk['size']}")
            name_label.set_halign(Gtk.Align.START)
            name_label.add_css_class("page-subtitle")
            disk_box.append(name_label)
            
            # Disk details
            details_label = Gtk.Label(label=f"{disk['type']} - {disk['model']}")
            details_label.set_halign(Gtk.Align.START)
            details_label.add_css_class("info-text")
            disk_box.append(details_label)
            
            row.set_child(disk_box)
            row.disk_info = disk
            self.disk_listbox.append(row)
        
        # Select first disk by default
        self.disk_listbox.select_row(self.disk_listbox.get_row_at_index(0))
        
        scrolled.set_child(self.disk_listbox)
        return scrolled
        
    def create_password_entry(self):
        """Create encryption password entry"""
        self.encrypt_password = Gtk.Entry()
        self.encrypt_password.set_visibility(False)
        self.encrypt_password.set_placeholder_text("Enter encryption password")
        return self.encrypt_password
        
    def create_confirm_entry(self):
        """Create password confirmation entry"""
        self.confirm_password = Gtk.Entry()
        self.confirm_password.set_visibility(False)
        self.confirm_password.set_placeholder_text("Confirm encryption password")
        return self.confirm_password
        
    def on_encrypt_toggled(self, checkbox):
        """Handle encryption checkbox toggle"""
        self.encrypt_password_box.set_visible(checkbox.get_active())
        
    def on_continue(self, button):
        """Handle continue button click"""
        selected_disk = self.disk_listbox.get_selected_row()
        if not selected_disk:
            return
            
        disk_info = selected_disk.disk_info
        
        # Get selected installation type
        install_type = "erase"
        for radio in self.install_type_group:
            if radio.get_active():
                install_type = radio.install_type
                break
        
        # Check encryption
        encrypt = self.encrypt_check.get_active()
        
        if encrypt:
            password = self.encrypt_password.get_text()
            confirm = self.confirm_password.get_text()
            
            if not password:
                self.show_error("Please enter an encryption password.")
                return
            
            if password != confirm:
                self.show_error("Passwords do not match.")
                return
        
        print(f"Selected disk: {disk_info['name']} ({disk_info['size']})")
        print(f"Installation type: {install_type}")
        print(f"Encryption: {encrypt}")
        
        self.navigate("wifi")
        
    def show_error(self, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
