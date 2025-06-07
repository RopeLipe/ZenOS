"""
Timezone Selection Page
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .base_page import BasePage

class TimezonePage(BasePage):
    def __init__(self, navigate_callback):
        super().__init__(navigate_callback)
        self.setup_page()
        
    def setup_page(self):
        # Create header
        self.create_header(
            "Timezone",
            "Select Timezone",
            "Choose your timezone to configure the system clock correctly."
        )
        
        # Timezone selection
        self.setup_timezone_selection()
        
        # Setup navigation
        self.back_btn.connect("clicked", lambda x: self.navigate("language"))
        self.continue_btn.connect("clicked", self.on_continue)
        
    def setup_timezone_selection(self):
        """Setup timezone selection interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_spacing(16)
        
        # Region selection
        region_row = self.create_form_row("Region:", self.create_region_dropdown())
        main_box.append(region_row)
        
        # City selection
        city_row = self.create_form_row("City:", self.create_city_dropdown())
        main_box.append(city_row)
        
        # Current time display
        time_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        time_box.set_spacing(8)
        
        time_label = Gtk.Label(label="Current Time:")
        time_label.add_css_class("form-label")
        time_label.set_halign(Gtk.Align.START)
        time_box.append(time_label)
        
        self.current_time = Gtk.Label(label="12:34:56 PM")
        self.current_time.set_halign(Gtk.Align.START)
        self.current_time.add_css_class("page-subtitle")
        time_box.append(self.current_time)
        
        main_box.append(time_box)
        
        self.content_box.append(main_box)
        
    def create_region_dropdown(self):
        """Create region dropdown"""
        self.region_dropdown = Gtk.DropDown()
        
        # Region options
        regions = Gtk.StringList()
        region_names = [
            "Africa", "America", "Antarctica", "Arctic", "Asia", 
            "Atlantic", "Australia", "Europe", "Indian", "Pacific"
        ]
        
        for region in region_names:
            regions.append(region)
            
        self.region_dropdown.set_model(regions)
        self.region_dropdown.set_selected(7)  # Europe by default
        self.region_dropdown.connect("notify::selected", self.on_region_changed)
        
        return self.region_dropdown
        
    def create_city_dropdown(self):
        """Create city dropdown"""
        self.city_dropdown = Gtk.DropDown()
        
        # Default cities for Europe
        cities = Gtk.StringList()
        city_names = [
            "London", "Paris", "Berlin", "Rome", "Madrid", 
            "Amsterdam", "Brussels", "Vienna", "Prague", "Warsaw"
        ]
        
        for city in city_names:
            cities.append(city)
            
        self.city_dropdown.set_model(cities)
        self.city_dropdown.set_selected(0)  # London by default
        
        return self.city_dropdown
        
    def on_region_changed(self, dropdown, param):
        """Handle region selection change"""
        selected = dropdown.get_selected()
        region_model = dropdown.get_model()
        region_name = region_model.get_string(selected)
        
        # Update cities based on region (simplified)
        cities = Gtk.StringList()
        city_lists = {
            "Europe": ["London", "Paris", "Berlin", "Rome", "Madrid"],
            "America": ["New_York", "Los_Angeles", "Chicago", "Toronto", "Mexico_City"],
            "Asia": ["Tokyo", "Shanghai", "Mumbai", "Seoul", "Singapore"],
            "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
            "Africa": ["Cairo", "Cape_Town", "Lagos", "Nairobi", "Casablanca"]
        }
        
        city_names = city_lists.get(region_name, ["GMT"])
        for city in city_names:
            cities.append(city)
            
        self.city_dropdown.set_model(cities)
        self.city_dropdown.set_selected(0)
        
    def on_continue(self, button):
        """Handle continue button click"""
        region_idx = self.region_dropdown.get_selected()
        city_idx = self.city_dropdown.get_selected()
        
        region_model = self.region_dropdown.get_model()
        city_model = self.city_dropdown.get_model()
        
        region = region_model.get_string(region_idx)
        city = city_model.get_string(city_idx)
        
        print(f"Selected timezone: {region}/{city}")
        self.navigate("keyboard")
