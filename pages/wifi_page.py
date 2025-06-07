"""
WiFi Setup Page
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from .base_page import BasePage

class WifiPage(BasePage):
    def __init__(self, navigate_callback):
        super().__init__(navigate_callback)
        self.setup_page()
        
    def setup_page(self):
        # Create header
        self.create_header(
            "Network",
            "Connect to WiFi",
            "Connect to a wireless network to download updates and additional software."
        )
        
        # WiFi setup
        self.setup_wifi_interface()
        
        # Setup navigation
        self.back_btn.connect("clicked", lambda x: self.navigate("disk"))
        self.continue_btn.connect("clicked", self.on_continue)
        
        # Skip button for wired connections
        skip_btn = Gtk.Button(label="Skip (Use Wired)")
        skip_btn.add_css_class("btn-secondary")
        skip_btn.connect("clicked", lambda x: self.navigate("user"))
        self.nav_box.prepend(skip_btn)
        
    def setup_wifi_interface(self):
        """Setup WiFi interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_spacing(20)
        
        # WiFi toggle and refresh
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        control_box.set_spacing(12)
        
        # WiFi enable toggle
        self.wifi_switch = Gtk.Switch()
        self.wifi_switch.set_active(True)
        self.wifi_switch.connect("state-set", self.on_wifi_toggled)
        
        wifi_label = Gtk.Label(label="WiFi Enabled")
        wifi_label.add_css_class("form-label")
        
        # Refresh button
        refresh_btn = Gtk.Button(label="🔄 Refresh")
        refresh_btn.add_css_class("btn-secondary")
        refresh_btn.connect("clicked", self.on_refresh_networks)
        
        control_box.append(wifi_label)
        control_box.append(self.wifi_switch)
        control_box.append(refresh_btn)
        
        main_box.append(control_box)
        
        # Available networks
        networks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        networks_box.set_spacing(8)
        
        networks_label = Gtk.Label(label="Available Networks:")
        networks_label.add_css_class("form-label")
        networks_label.set_halign(Gtk.Align.START)
        networks_box.append(networks_label)
        
        self.networks_list = self.create_networks_list()
        networks_box.append(self.networks_list)
        
        main_box.append(networks_box)
        
        # Connection status
        self.status_label = Gtk.Label(label="Not connected")
        self.status_label.add_css_class("info-text")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.append(self.status_label)
        
        # Password entry (initially hidden)
        self.password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.password_box.set_spacing(8)
        self.password_box.set_visible(False)
        
        password_row = self.create_form_row("WiFi Password:", self.create_password_entry())
        connect_btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        self.connect_btn = Gtk.Button(label="Connect")
        self.connect_btn.add_css_class("btn-primary")
        self.connect_btn.connect("clicked", self.on_connect_wifi)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.add_css_class("btn-secondary")
        cancel_btn.connect("clicked", self.on_cancel_connection)
        
        connect_btn_row.append(self.connect_btn)
        connect_btn_row.append(cancel_btn)
        connect_btn_row.set_spacing(12)
        
        self.password_box.append(password_row)
        self.password_box.append(connect_btn_row)
        
        main_box.append(self.password_box)
        
        self.content_box.append(main_box)
        
        # Start network scan
        self.scan_networks()
        
    def create_networks_list(self):
        """Create WiFi networks list"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        
        self.networks_listbox = Gtk.ListBox()
        self.networks_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.networks_listbox.connect("row-selected", self.on_network_selected)
        
        scrolled.set_child(self.networks_listbox)
        return scrolled
        
    def create_password_entry(self):
        """Create WiFi password entry"""
        self.wifi_password = Gtk.Entry()
        self.wifi_password.set_visibility(False)
        self.wifi_password.set_placeholder_text("Enter WiFi password")
        self.wifi_password.connect("activate", lambda x: self.on_connect_wifi(None))
        return self.wifi_password
        
    def scan_networks(self):
        """Simulate network scanning"""
        # Clear existing networks
        while True:
            row = self.networks_listbox.get_row_at_index(0)
            if row is None:
                break
            self.networks_listbox.remove(row)
        
        # Add loading indicator
        loading_row = Gtk.ListBoxRow()
        loading_label = Gtk.Label(label="🔄 Scanning for networks...")
        loading_label.set_margin_start(12)
        loading_label.set_margin_end(12)
        loading_label.set_margin_top(12)
        loading_label.set_margin_bottom(12)
        loading_row.set_child(loading_label)
        self.networks_listbox.append(loading_row)
        
        # Simulate scan delay
        GLib.timeout_add_seconds(2, self.populate_networks)
        
    def populate_networks(self):
        """Populate with mock network data"""
        # Remove loading indicator
        while True:
            row = self.networks_listbox.get_row_at_index(0)
            if row is None:
                break
            self.networks_listbox.remove(row)
        
        # Mock WiFi networks
        networks = [
            {"ssid": "HomeNetwork_5G", "signal": "▂▄▆█", "security": "WPA2", "strength": 85},
            {"ssid": "CoffeeShop_WiFi", "signal": "▂▄▆▇", "security": "Open", "strength": 70},
            {"ssid": "Neighbor_WiFi", "signal": "▂▄▇", "security": "WPA3", "strength": 60},
            {"ssid": "Office_Guest", "signal": "▂▄", "security": "WPA2", "strength": 45},
            {"ssid": "Mobile_Hotspot", "signal": "▂", "security": "WPA2", "strength": 30},
        ]
        
        for network in networks:
            row = Gtk.ListBoxRow()
            row.set_margin_start(12)
            row.set_margin_end(12)
            row.set_margin_top(8)
            row.set_margin_bottom(8)
            
            network_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            network_box.set_spacing(12)
            
            # Network info
            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            info_box.set_spacing(2)
            
            # SSID
            ssid_label = Gtk.Label(label=network["ssid"])
            ssid_label.set_halign(Gtk.Align.START)
            ssid_label.add_css_class("page-subtitle")
            info_box.append(ssid_label)
            
            # Security info
            security_label = Gtk.Label(label=f"Security: {network['security']}")
            security_label.set_halign(Gtk.Align.START)
            security_label.add_css_class("info-text")
            info_box.append(security_label)
            
            network_box.append(info_box)
            
            # Signal strength
            signal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            signal_box.set_valign(Gtk.Align.CENTER)
            
            signal_label = Gtk.Label(label=network["signal"])
            signal_label.add_css_class("page-subtitle")
            signal_box.append(signal_label)
            
            strength_label = Gtk.Label(label=f"{network['strength']}%")
            strength_label.add_css_class("info-text")
            signal_box.append(strength_label)
            
            network_box.append(signal_box)
            
            row.set_child(network_box)
            row.network_info = network
            self.networks_listbox.append(row)
        
        return False  # Don't repeat timeout
        
    def on_wifi_toggled(self, switch, state):
        """Handle WiFi toggle"""
        if state:
            self.scan_networks()
            self.status_label.set_text("WiFi enabled, scanning...")
        else:
            # Clear networks list
            while True:
                row = self.networks_listbox.get_row_at_index(0)
                if row is None:
                    break
                self.networks_listbox.remove(row)
            
            self.status_label.set_text("WiFi disabled")
            self.password_box.set_visible(False)
        
    def on_refresh_networks(self, button):
        """Handle refresh button click"""
        if self.wifi_switch.get_active():
            self.scan_networks()
            
    def on_network_selected(self, listbox, row):
        """Handle network selection"""
        if not row or not hasattr(row, 'network_info'):
            return
            
        network = row.network_info
        
        if network["security"] == "Open":
            # Open network, connect immediately
            self.password_box.set_visible(False)
            self.connect_to_network(network, "")
        else:
            # Secured network, show password entry
            self.password_box.set_visible(True)
            self.wifi_password.set_text("")
            self.wifi_password.grab_focus()
            
    def on_connect_wifi(self, button):
        """Handle connect button click"""
        selected_row = self.networks_listbox.get_selected_row()
        if not selected_row or not hasattr(selected_row, 'network_info'):
            return
            
        network = selected_row.network_info
        password = self.wifi_password.get_text()
        
        if network["security"] != "Open" and not password:
            self.show_error("Please enter the WiFi password.")
            return
            
        self.connect_to_network(network, password)
        
    def on_cancel_connection(self, button):
        """Handle cancel button click"""
        self.password_box.set_visible(False)
        self.networks_listbox.unselect_all()
        
    def connect_to_network(self, network, password):
        """Simulate network connection"""
        self.status_label.set_text(f"Connecting to {network['ssid']}...")
        self.connect_btn.set_sensitive(False)
        
        # Simulate connection delay
        GLib.timeout_add_seconds(3, self.on_connection_complete, network)
        
    def on_connection_complete(self, network):
        """Handle connection completion"""
        self.status_label.set_text(f"Connected to {network['ssid']}")
        self.password_box.set_visible(False)
        self.connect_btn.set_sensitive(True)
        
        # Enable continue button
        self.continue_btn.set_sensitive(True)
        
        return False  # Don't repeat timeout
        
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
        
    def on_continue(self, button):
        """Handle continue button click"""
        # Check if connected
        status_text = self.status_label.get_text()
        if "Connected to" in status_text:
            network_name = status_text.replace("Connected to ", "")
            print(f"Connected to WiFi: {network_name}")
        else:
            print("Continuing without WiFi connection")
            
        self.navigate("user")
