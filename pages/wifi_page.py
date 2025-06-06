"""
WiFi network configuration page.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .base_page import BasePage
from utils.system_utils import get_wifi_networks
from utils.validation import validate_wifi_password
import subprocess


class WiFiPage(BasePage):
    """Page for WiFi network configuration."""
    
    def __init__(self):
        super().__init__(
            "Network Configuration", 
            "Configure your WiFi connection (optional)."
        )
        
        # Skip option
        skip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.skip_wifi = Gtk.CheckButton(label="Skip WiFi configuration")
        self.skip_wifi.connect("toggled", self._on_skip_toggled)
        skip_box.append(self.skip_wifi)
        
        skip_info = Gtk.Label(label="You can configure networking after installation")
        skip_info.add_css_class("dim-label")
        skip_box.append(skip_info)
        
        self.content_box.append(skip_box)
        
        # Separator
        separator = Gtk.Separator()
        separator.set_margin_top(16)
        separator.set_margin_bottom(16)
        self.content_box.append(separator)
        
        # WiFi configuration box
        self.wifi_config_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Network selection
        network_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        network_label = Gtk.Label(label="Available Networks:")
        network_label.set_halign(Gtk.Align.START)
        network_box.append(network_label)
        
        # Refresh button
        refresh_button = Gtk.Button(label="Scan for Networks")
        refresh_button.connect("clicked", self._on_scan_networks)
        refresh_button.set_halign(Gtk.Align.START)
        network_box.append(refresh_button)
        
        # Network dropdown
        self.network_dropdown = Gtk.DropDown()
        self.network_dropdown.set_enable_search(True)
        self.network_dropdown.connect("notify::selected", self._on_network_selected)
        network_box.append(self.network_dropdown)
        
        self.wifi_config_box.append(network_box)
        
        # Password entry
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        password_label = Gtk.Label(label="Network Password:")
        password_label.set_halign(Gtk.Align.START)
        password_box.append(password_label)
        
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Enter WiFi password")
        self.password_entry.set_visibility(False)
        self.password_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        password_box.append(self.password_entry)
        
        # Show password toggle
        show_password = Gtk.CheckButton(label="Show password")
        show_password.connect("toggled", self._on_show_password_toggled)
        password_box.append(show_password)
        
        self.wifi_config_box.append(password_box)
        
        # Test connection button
        self.test_button = Gtk.Button(label="Test Connection")
        self.test_button.connect("clicked", self._on_test_connection)
        self.test_button.set_halign(Gtk.Align.START)
        self.test_button.set_sensitive(False)
        self.wifi_config_box.append(self.test_button)
        
        # Connection status
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_visible(False)
        self.wifi_config_box.append(self.status_label)
        
        self.content_box.append(self.wifi_config_box)
        
        # Additional info
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small>WiFi configuration is optional but recommended for downloading "
            "updates during installation. If you skip this step, you can configure "
            "networking after the installation is complete.</small>"
        )
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.START)
        info_label.add_css_class("dim-label")
        info_label.set_margin_top(16)
        self.content_box.append(info_label)
        
        # Load initial network list
        self._load_networks()
    
    def _on_skip_toggled(self, checkbox):
        """Handle skip WiFi toggle."""
        skip = checkbox.get_active()
        self.wifi_config_box.set_sensitive(not skip)
        self.hide_error()
    
    def _load_networks(self):
        """Load available WiFi networks."""
        networks = get_wifi_networks()
        
        # Create string list model
        string_list = Gtk.StringList()
        
        if networks:
            for network in networks:
                string_list.append(network)
        else:
            string_list.append("No networks found")
        
        self.network_dropdown.set_model(string_list)
        
        # Enable/disable based on network availability
        has_networks = len(networks) > 0 and networks[0] != "No networks found"
        self.network_dropdown.set_sensitive(has_networks)
        self._update_test_button()
    
    def _on_scan_networks(self, button):
        """Scan for WiFi networks."""
        button.set_sensitive(False)
        button.set_label("Scanning...")
        
        def scan_complete():
            button.set_sensitive(True)
            button.set_label("Scan for Networks")
            self._load_networks()
            return False
        
        # Schedule scan completion (in real implementation, this would be async)
        GLib.timeout_add(2000, scan_complete)
        
        # Trigger actual network scan
        try:
            subprocess.run(["nmcli", "dev", "wifi", "rescan"], 
                         capture_output=True, timeout=10)
        except:
            pass  # Ignore scan errors
    
    def _on_network_selected(self, dropdown, param):
        """Handle network selection."""
        self._update_test_button()
        self.status_label.set_visible(False)
    
    def _on_show_password_toggled(self, checkbox):
        """Toggle password visibility."""
        self.password_entry.set_visibility(checkbox.get_active())
    
    def _update_test_button(self):
        """Update test button sensitivity."""
        selected_index = self.network_dropdown.get_selected()
        has_selection = selected_index != Gtk.INVALID_LIST_POSITION
        has_password = len(self.password_entry.get_text()) > 0
        
        if has_selection:
            model = self.network_dropdown.get_model()
            selected_network = model.get_string(selected_index)
            is_valid_network = selected_network != "No networks found"
            self.test_button.set_sensitive(is_valid_network and has_password)
        else:
            self.test_button.set_sensitive(False)
    
    def _on_test_connection(self, button):
        """Test WiFi connection."""
        button.set_sensitive(False)
        button.set_label("Testing...")
        
        selected_index = self.network_dropdown.get_selected()
        if selected_index == Gtk.INVALID_LIST_POSITION:
            return
        
        model = self.network_dropdown.get_model()
        ssid = model.get_string(selected_index)
        password = self.password_entry.get_text()
        
        def test_complete(success, message):
            button.set_sensitive(True)
            button.set_label("Test Connection")
            
            self.status_label.set_text(message)
            if success:
                self.status_label.add_css_class("success")
                self.status_label.remove_css_class("error")
            else:
                self.status_label.add_css_class("error")
                self.status_label.remove_css_class("success")
            self.status_label.set_visible(True)
            return False
        
        # Simulate connection test (in real implementation, this would be async)
        try:
            result = subprocess.run([
                "nmcli", "dev", "wifi", "connect", ssid, "password", password
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                GLib.timeout_add(1000, lambda: test_complete(True, "✓ Connection successful"))
            else:
                error_msg = result.stderr.strip() if result.stderr else "Connection failed"
                GLib.timeout_add(1000, lambda: test_complete(False, f"✗ {error_msg}"))
        except Exception as e:
            GLib.timeout_add(1000, lambda: test_complete(False, f"✗ Connection test failed: {str(e)}"))
    
    def get_data(self) -> dict:
        """Get WiFi configuration data."""
        if self.skip_wifi.get_active():
            return {"wifi_ssid": "", "wifi_password": ""}
        
        selected_index = self.network_dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION:
            model = self.network_dropdown.get_model()
            ssid = model.get_string(selected_index)
            if ssid != "No networks found":
                return {
                    "wifi_ssid": ssid,
                    "wifi_password": self.password_entry.get_text()
                }
        
        return {"wifi_ssid": "", "wifi_password": ""}
    
    def validate(self) -> tuple[bool, str]:
        """Validate WiFi configuration."""
        if self.skip_wifi.get_active():
            return True, ""
        
        data = self.get_data()
        ssid = data.get("wifi_ssid", "")
        password = data.get("wifi_password", "")
        
        if ssid and ssid != "No networks found":
            return validate_wifi_password(password, ssid)
        elif not ssid:
            return False, "Please select a network or choose to skip WiFi configuration"
        
        return True, ""
    
    def on_page_enter(self):
        """Refresh network list when entering page."""
        if not self.skip_wifi.get_active():
            self._load_networks()
