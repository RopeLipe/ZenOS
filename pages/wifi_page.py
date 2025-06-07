"""
WiFi network configuration page.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gio
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
        
        # Check if we're on Ethernet connection
        self.has_ethernet = self._check_ethernet_connection()
        
        if self.has_ethernet:
            # Show Ethernet status
            ethernet_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            ethernet_card.add_css_class("card")
            ethernet_card.set_margin_bottom(16)
            
            ethernet_icon = Gtk.Image.new_from_icon_name("network-wired-symbolic")
            ethernet_icon.set_icon_size(Gtk.IconSize.LARGE)
            ethernet_card.append(ethernet_icon)
            
            ethernet_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            ethernet_title = Gtk.Label(label="Ethernet Connection Active")
            ethernet_title.add_css_class("heading")
            ethernet_title.set_halign(Gtk.Align.START)
            ethernet_info.append(ethernet_title)
            
            ethernet_desc = Gtk.Label(label="You're already connected via Ethernet")
            ethernet_desc.add_css_class("dim-label")
            ethernet_desc.set_halign(Gtk.Align.START)
            ethernet_info.append(ethernet_desc)
            
            ethernet_card.append(ethernet_info)
            self.content_box.append(ethernet_card)
        
        # Skip button
        skip_button = Gtk.Button(label="Skip WiFi Configuration")
        skip_button.add_css_class("pill")
        skip_button.connect("clicked", self._on_skip_clicked)
        skip_button.set_halign(Gtk.Align.START)
        self.content_box.append(skip_button)
        
        # Separator
        separator = Gtk.Separator()
        separator.set_margin_top(16)
        separator.set_margin_bottom(16)
        self.content_box.append(separator)
        
        # WiFi configuration box (hide if Ethernet is active)
        self.wifi_config_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        if self.has_ethernet:
            self.wifi_config_box.set_visible(False)        
        # Network selection with signal strength
        network_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        network_card.add_css_class("card")
        
        network_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        network_label = Gtk.Label(label="Available Networks:")
        network_label.set_halign(Gtk.Align.START)
        network_label.add_css_class("heading")
        network_header.append(network_label)
        
        # Refresh button with icon
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.add_css_class("circular")
        refresh_button.set_tooltip_text("Scan for networks")
        refresh_button.connect("clicked", self._on_scan_networks)
        network_header.append(refresh_button)
        
        network_card.append(network_header)
        
        # Network ComboBox with search
        self.network_combo = Gtk.ComboBoxText.new_with_entry()
        self.network_combo.set_entry_text_column(0)
        self.network_combo.get_child().set_placeholder_text("Select or search for a network...")
        self.network_combo.connect("changed", self._on_network_selected)
        network_card.append(self.network_combo)
        
        self.wifi_config_box.append(network_card)
          # Password entry with signal strength indicator
        self.password_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.password_card.add_css_class("card")
        self.password_card.set_visible(False)
        
        password_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.signal_icon = Gtk.Image()
        self.signal_icon.set_icon_size(Gtk.IconSize.NORMAL)
        password_header.append(self.signal_icon)
        
        password_label = Gtk.Label(label="Network Password:")
        password_label.set_halign(Gtk.Align.START)
        password_label.add_css_class("heading")
        password_header.append(password_label)
        
        self.password_card.append(password_header)
        
        # Password entry with eye toggle
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        password_box.add_css_class("linked")
        
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Enter WiFi password")
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
        
        self.password_card.append(password_box)
        
        self.wifi_config_box.append(self.password_card)
        
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
        
        # Skip state
        self.skip_wifi = False
    
    def _check_ethernet_connection(self):
        """Check if Ethernet connection is active."""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "TYPE,STATE", "dev"], 
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('ethernet:') and 'connected' in line:
                    return True
        except:
            pass
        return False
    
    def _on_skip_clicked(self, button):
        """Handle skip WiFi button click."""
        self.skip_wifi = True
        self.wifi_config_box.set_visible(False)
        self.hide_error()
        
        # Show skip confirmation
        self.show_message("WiFi configuration skipped. You can set up networking after installation.", "info")
    
    def _update_signal_strength(self, ssid):
        """Update signal strength icon for selected network."""
        # Get signal strength (mock implementation)
        strength = self._get_signal_strength(ssid)
        
        if strength >= 75:
            self.signal_icon.set_from_icon_name("network-wireless-signal-excellent-symbolic")
        elif strength >= 50:
            self.signal_icon.set_from_icon_name("network-wireless-signal-good-symbolic")
        elif strength >= 25:
            self.signal_icon.set_from_icon_name("network-wireless-signal-ok-symbolic")
        else:
            self.signal_icon.set_from_icon_name("network-wireless-signal-weak-symbolic")
    
    def _get_signal_strength(self, ssid):
        """Get signal strength for network (mock implementation)."""
        # In real implementation, parse nmcli output for signal strength
        import random
        return random.randint(20, 100)
      def _load_networks(self):
        """Load available WiFi networks."""
        networks = get_wifi_networks()
        
        # Clear existing items
        self.network_combo.remove_all()
        
        if networks:
            for network in networks:
                # Add signal strength indicator to network name
                strength = self._get_signal_strength(network)
                display_name = f"{network} ({self._signal_bars(strength)})"
                self.network_combo.append_text(display_name)
                self.network_combo.append_text(network)  # Store original name too
        else:
            self.network_combo.append_text("No networks found")
    
    def _signal_bars(self, strength):
        """Convert signal strength to bar representation."""
        if strength >= 75:
            return "▂▄▆█"
        elif strength >= 50:
            return "▂▄▆"
        elif strength >= 25:
            return "▂▄"
        else:
            return "▂"
      def _on_scan_networks(self, button):
        """Scan for WiFi networks."""
        button.set_sensitive(False)
        
        def scan_complete():
            button.set_sensitive(True)
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
    
    def _on_network_selected(self, combo):
        """Handle network selection."""
        text = combo.get_active_text()
        if text and text != "No networks found":
            # Extract original network name (before signal bars)
            ssid = text.split(" (")[0] if " (" in text else text
            self._update_signal_strength(ssid)
            self.password_card.set_visible(True)
            self._update_test_button()
        else:
            self.password_card.set_visible(False)
        
        self.status_label.set_visible(False)
    
    def _on_password_changed(self, entry):
        """Handle password entry changes."""
        self._update_test_button()
    
    def _on_password_toggle(self, button):
        """Toggle password visibility."""
        visible = not self.password_entry.get_visibility()
        self.password_entry.set_visibility(visible)
        
        # Update icon
        if visible:
            button.set_icon_name("view-reveal-symbolic")
            button.set_tooltip_text("Hide password")
        else:
            button.set_icon_name("view-conceal-symbolic")
            button.set_tooltip_text("Show password")
      def _update_test_button(self):
        """Update test button sensitivity."""
        text = self.network_combo.get_active_text()
        has_selection = text and text != "No networks found"
        has_password = len(self.password_entry.get_text()) > 0
        
        self.test_button.set_sensitive(has_selection and has_password)
    
    def _on_test_connection(self, button):
        """Test WiFi connection."""
        button.set_sensitive(False)
        button.set_label("Testing...")
        
        text = self.network_combo.get_active_text()
        if not text:
            return
        
        # Extract original network name
        ssid = text.split(" (")[0] if " (" in text else text
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
        if self.skip_wifi:
            return {"wifi_ssid": "", "wifi_password": ""}
        
        text = self.network_combo.get_active_text()
        if text and text != "No networks found":
            # Extract original network name
            ssid = text.split(" (")[0] if " (" in text else text
            return {
                "wifi_ssid": ssid,
                "wifi_password": self.password_entry.get_text()
            }
        
        return {"wifi_ssid": "", "wifi_password": ""}
    
    def validate(self) -> tuple[bool, str]:
        """Validate WiFi configuration."""
        if self.skip_wifi:
            return True, ""
        
        data = self.get_data()
        ssid = data.get("wifi_ssid", "")
        password = data.get("wifi_password", "")
        
        if ssid and ssid != "No networks found":
            return validate_wifi_password(password, ssid)
        elif not ssid:
            return False, "Please select a network or skip WiFi configuration"
        
        return True, ""
    
    def on_page_enter(self):
        """Refresh network list when entering page."""
        if not self.skip_wifi:
            self._load_networks()
