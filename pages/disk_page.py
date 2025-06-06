"""
Disk selection page for installation.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .base_page import BasePage
from utils.system_utils import get_disks
from utils.validation import validate_disk_selection


class DiskPage(BasePage):
    """Page for selecting installation disk."""
    
    def __init__(self):
        super().__init__(
            "Installation Disk", 
            "Choose the disk where the system will be installed. All data on this disk will be erased!"
        )
        
        # Warning box
        warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        warning_box.add_css_class("warning")
        warning_box.set_margin_bottom(20)
          warning_icon = Gtk.Image.new_from_icon_name("dialog-warning")
        warning_icon.set_icon_size(Gtk.IconSize.NORMAL)
        warning_box.append(warning_icon)
        
        warning_label = Gtk.Label()
        warning_label.set_markup("<b>WARNING:</b> All data on the selected disk will be permanently erased!")
        warning_label.set_wrap(True)
        warning_box.append(warning_label)
        
        self.content_box.append(warning_box)
        
        # Disk selection
        disk_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        disk_label = Gtk.Label(label="Available Disks:")
        disk_label.set_halign(Gtk.Align.START)
        disk_box.append(disk_label)
        
        # Container for disk list
        self.disk_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Refresh button
        refresh_button = Gtk.Button(label="Refresh Disk List")
        refresh_button.connect("clicked", self._on_refresh_disks)
        refresh_button.set_halign(Gtk.Align.START)
        disk_box.append(refresh_button)
        
        # Scrolled window for disk list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        scrolled.set_child(self.disk_list_box)
        disk_box.append(scrolled)
        
        self.content_box.append(disk_box)
        
        # Selected disk info
        self.selected_info = Gtk.Label()
        self.selected_info.set_halign(Gtk.Align.START)
        self.selected_info.set_visible(False)
        self.selected_info.add_css_class("success")
        self.content_box.append(self.selected_info)
        
        # Additional info
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small><b>Important:</b> Make sure you have backed up any important data. "
            "The installation will create a new partition table and format the entire disk. "
            "This action cannot be undone.</small>"
        )
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.START)
        info_label.add_css_class("dim-label")
        info_label.set_margin_top(16)
        self.content_box.append(info_label)
        
        # Store selected disk info
        self.selected_disk = None
        
        # Load initial disk list
        self._load_disks()
    
    def _load_disks(self):
        """Load available disks and create selection buttons."""
        # Clear existing disk list
        child = self.disk_list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.disk_list_box.remove(child)
            child = next_child
        
        disks = get_disks()
        
        if not disks:
            no_disks_label = Gtk.Label(label="No suitable disks found. Please connect a disk and refresh.")
            no_disks_label.add_css_class("error")
            no_disks_label.set_halign(Gtk.Align.START)
            self.disk_list_box.append(no_disks_label)
            return
        
        # Create radio buttons for disk selection
        group_button = None
        for disk in disks:
            disk_button = Gtk.CheckButton()
            if group_button is None:
                group_button = disk_button
            else:
                disk_button.set_group(group_button)
            
            # Create disk info display
            disk_info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            
            disk_button.connect("toggled", self._on_disk_selected, disk)
            disk_info_box.append(disk_button)
            
            # Disk icon
            disk_icon = Gtk.Image.new_from_icon_name("drive-harddisk")
            disk_icon.set_icon_size(Gtk.IconSize.LARGE)
            disk_info_box.append(disk_icon)
            
            # Disk details
            details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            
            name_label = Gtk.Label()
            name_label.set_markup(f"<b>{disk['name']}</b>")
            name_label.set_halign(Gtk.Align.START)
            details_box.append(name_label)
            
            info_text = f"Size: {disk['size']}"
            if disk['model'] != 'Unknown':
                info_text += f" | Model: {disk['model']}"
            
            info_label = Gtk.Label(label=info_text)
            info_label.set_halign(Gtk.Align.START)
            info_label.add_css_class("dim-label")
            details_box.append(info_label)
            
            disk_info_box.append(details_box)
            
            # Make the whole box clickable
            clickable = Gtk.Button()
            clickable.set_child(disk_info_box)
            clickable.add_css_class("flat")
            clickable.connect("clicked", lambda btn, db=disk_button: db.set_active(True))
            
            self.disk_list_box.append(clickable)
    
    def _on_refresh_disks(self, button):
        """Refresh the disk list."""
        self._load_disks()
        self.selected_disk = None
        self.selected_info.set_visible(False)
    
    def _on_disk_selected(self, button, disk_info):
        """Handle disk selection."""
        if button.get_active():
            self.selected_disk = disk_info
            self.selected_info.set_text(f"Selected: {disk_info['display']}")
            self.selected_info.set_visible(True)
            self.hide_error()
    
    def get_data(self) -> dict:
        """Get the selected disk."""
        if self.selected_disk:
            return {
                "disk": self.selected_disk['name'],
                "disk_info": self.selected_disk
            }
        return {"disk": "", "disk_info": {}}
    
    def validate(self) -> tuple[bool, str]:
        """Validate disk selection."""
        data = self.get_data()
        return validate_disk_selection(data.get("disk_info", {}))
    
    def on_page_enter(self):
        """Refresh disk list when entering the page."""
        self._load_disks()
