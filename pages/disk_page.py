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
        erase_radio = Gtk.CheckButton(label=\"Erase disk and install (Recommended)\")\n        erase_radio.set_active(True)\n        erase_radio.install_type = \"erase\"\n        self.install_type_group.append(erase_radio)\n        options_box.append(erase_radio)\n        \n        # Manual partitioning\n        manual_radio = Gtk.CheckButton(label=\"Manual partitioning (Advanced)\")\n        manual_radio.set_group(erase_radio)\n        manual_radio.install_type = \"manual\"\n        self.install_type_group.append(manual_radio)\n        options_box.append(manual_radio)\n        \n        main_box.append(options_box)\n        \n        # Encryption option\n        encrypt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)\n        encrypt_box.set_spacing(8)\n        \n        self.encrypt_check = Gtk.CheckButton(label=\"Encrypt the installation for security\")\n        encrypt_box.append(self.encrypt_check)\n        \n        # Encryption password (initially hidden)\n        self.encrypt_password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)\n        self.encrypt_password_box.set_spacing(8)\n        self.encrypt_password_box.set_visible(False)\n        \n        password_row = self.create_form_row(\"Encryption Password:\", self.create_password_entry())\n        confirm_row = self.create_form_row(\"Confirm Password:\", self.create_confirm_entry())\n        \n        self.encrypt_password_box.append(password_row)\n        self.encrypt_password_box.append(confirm_row)\n        \n        encrypt_box.append(self.encrypt_password_box)\n        \n        # Connect encryption checkbox\n        self.encrypt_check.connect(\"toggled\", self.on_encrypt_toggled)\n        \n        main_box.append(encrypt_box)\n        \n        # Warning message\n        warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)\n        warning_box.set_spacing(8)\n        warning_box.add_css_class(\"warning-text\")\n        \n        warning_icon = Gtk.Label(label=\"⚠️\")\n        warning_text = Gtk.Label(label=\"WARNING: This will permanently erase all data on the selected disk.\")\n        warning_text.set_wrap(True)\n        \n        warning_box.append(warning_icon)\n        warning_box.append(warning_text)\n        \n        main_box.append(warning_box)\n        \n        self.content_box.append(main_box)\n        \n    def create_disk_list(self):\n        \"\"\"Create disk selection list\"\"\"\n        scrolled = Gtk.ScrolledWindow()\n        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)\n        scrolled.set_min_content_height(150)\n        \n        self.disk_listbox = Gtk.ListBox()\n        self.disk_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)\n        \n        # Mock disk data (in real app, this would come from system)\n        disks = [\n            {\n                \"name\": \"/dev/sda\",\n                \"size\": \"500 GB\",\n                \"type\": \"SSD\",\n                \"model\": \"Samsung SSD 850 EVO\"\n            },\n            {\n                \"name\": \"/dev/sdb\",\n                \"size\": \"1 TB\",\n                \"type\": \"HDD\",\n                \"model\": \"Western Digital Blue\"\n            },\n            {\n                \"name\": \"/dev/nvme0n1\",\n                \"size\": \"256 GB\",\n                \"type\": \"NVMe SSD\",\n                \"model\": \"Intel SSD 660p\"\n            }\n        ]\n        \n        for disk in disks:\n            row = Gtk.ListBoxRow()\n            row.set_margin_start(12)\n            row.set_margin_end(12)\n            row.set_margin_top(8)\n            row.set_margin_bottom(8)\n            \n            disk_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)\n            disk_box.set_spacing(4)\n            \n            # Disk name and size\n            name_label = Gtk.Label(label=f\"{disk['name']} - {disk['size']}\")\n            name_label.set_halign(Gtk.Align.START)\n            name_label.add_css_class(\"page-subtitle\")\n            disk_box.append(name_label)\n            \n            # Disk details\n            details_label = Gtk.Label(label=f\"{disk['type']} - {disk['model']}\")\n            details_label.set_halign(Gtk.Align.START)\n            details_label.add_css_class(\"info-text\")\n            disk_box.append(details_label)\n            \n            row.set_child(disk_box)\n            row.disk_info = disk\n            self.disk_listbox.append(row)\n        \n        # Select first disk by default\n        self.disk_listbox.select_row(self.disk_listbox.get_row_at_index(0))\n        \n        scrolled.set_child(self.disk_listbox)\n        return scrolled\n        \n    def create_password_entry(self):\n        \"\"\"Create encryption password entry\"\"\"\n        self.encrypt_password = Gtk.Entry()\n        self.encrypt_password.set_visibility(False)\n        self.encrypt_password.set_placeholder_text(\"Enter encryption password\")\n        return self.encrypt_password\n        \n    def create_confirm_entry(self):\n        \"\"\"Create password confirmation entry\"\"\"\n        self.confirm_password = Gtk.Entry()\n        self.confirm_password.set_visibility(False)\n        self.confirm_password.set_placeholder_text(\"Confirm encryption password\")\n        return self.confirm_password\n        \n    def on_encrypt_toggled(self, checkbox):\n        \"\"\"Handle encryption checkbox toggle\"\"\"\n        self.encrypt_password_box.set_visible(checkbox.get_active())\n        \n    def on_continue(self, button):\n        \"\"\"Handle continue button click\"\"\"\n        selected_disk = self.disk_listbox.get_selected_row()\n        if not selected_disk:\n            return\n            \n        disk_info = selected_disk.disk_info\n        \n        # Get selected installation type\n        install_type = \"erase\"\n        for radio in self.install_type_group:\n            if radio.get_active():\n                install_type = radio.install_type\n                break\n        \n        # Check encryption\n        encrypt = self.encrypt_check.get_active()\n        \n        if encrypt:\n            password = self.encrypt_password.get_text()\n            confirm = self.confirm_password.get_text()\n            \n            if not password:\n                self.show_error(\"Please enter an encryption password.\")\n                return\n            \n            if password != confirm:\n                self.show_error(\"Passwords do not match.\")\n                return\n        \n        print(f\"Selected disk: {disk_info['name']} ({disk_info['size']})\")\n        print(f\"Installation type: {install_type}\")\n        print(f\"Encryption: {encrypt}\")\n        \n        self.navigate(\"wifi\")\n        \n    def show_error(self, message):\n        \"\"\"Show error dialog\"\"\"\n        dialog = Gtk.MessageDialog(\n            transient_for=self.get_root(),\n            modal=True,\n            message_type=Gtk.MessageType.ERROR,\n            buttons=Gtk.ButtonsType.OK,\n            text=message\n        )\n        dialog.connect(\"response\", lambda d, r: d.destroy())\n        dialog.present()
