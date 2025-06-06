"""
Timezone selection page.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .base_page import BasePage
from utils.system_utils import get_a    def get_data(self) -> dict:
        """Get the selected timezone."""
        selected_index = self.tz_dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION and hasattr(self, 'timezones') and selected_index < len(self.timezones):
            selected_timezone = self.timezones[selected_index]
            return {"timezone": selected_timezone}
        return {"timezone": ""}ones
from datetime import datetime
import subprocess
try:
    import zoneinfo
except ImportError:
    # Fallback for older Python versions
    zoneinfo = None


class TimezonePage(BasePage):
    """Page for selecting system timezone."""
    
    def __init__(self):
        super().__init__(
            "Time Zone", 
            "Select your time zone to ensure correct time settings."
        )
        
        # Timezone selection
        tz_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        tz_label = Gtk.Label(label="Time Zone:")
        tz_label.set_halign(Gtk.Align.START)
        tz_box.append(tz_label)
        
        # Create dropdown with search
        self.tz_dropdown = Gtk.DropDown()
        self.tz_dropdown.set_enable_search(True)
        self.tz_dropdown.connect("notify::selected", self._on_timezone_changed)
        
        # Load timezones
        self._load_timezones()
        
        tz_box.append(self.tz_dropdown)
        self.content_box.append(tz_box)
        
        # Current time display
        time_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        time_box.set_margin_top(20)
        
        time_label = Gtk.Label(label="Current time in selected timezone:")
        time_label.set_halign(Gtk.Align.START)
        time_box.append(time_label)
        
        self.time_display = Gtk.Label()
        self.time_display.set_halign(Gtk.Align.START)        self.time_display.add_css_class("monospace")
        time_box.append(self.time_display)
        
        self.content_box.append(time_box)
        
        # Initialize time display
        self._update_time_display()
        
        # Set up timer for live time updates
        GLib.timeout_add_seconds(1, self._update_time_display_timer)
        
        # Auto-detect button
        detect_button = Gtk.Button(label="Auto-detect Time Zone")
        detect_button.connect("clicked", self._on_auto_detect)
        detect_button.set_halign(Gtk.Align.START)
        detect_button.set_margin_top(12)
        self.content_box.append(detect_button)
        
        # Additional info
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small>The time zone setting affects system time, log timestamps, "
            "and scheduled tasks. Choose the zone that matches your location.</small>"
        )
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.START)
        info_label.add_css_class("dim-label")
        info_label.set_margin_top(16)
        self.content_box.append(info_label)
        
        # Update time display initially
        self._update_time_display()
      def _load_timezones(self):
        """Load available timezones into the dropdown."""
        self.timezones = get_all_timezones()
        
        # Create string list model
        string_list = Gtk.StringList()
        for timezone in self.timezones:
            string_list.append(timezone)
        
        self.tz_dropdown.set_model(string_list)
        
        # Try to detect current timezone or set to UTC
        try:
            result = subprocess.run(["timedatectl", "show", "--property=Timezone", "--value"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                current_tz = result.stdout.strip()
                if current_tz in self.timezones:
                    self.tz_dropdown.set_selected(self.timezones.index(current_tz))
                    return
        except:
            pass
        
        # Fallback to UTC
        if "UTC" in self.timezones:
            self.tz_dropdown.set_selected(self.timezones.index("UTC"))
    
    def _on_timezone_changed(self, dropdown, param):
        """Handle timezone selection change."""
        # Add a small delay to ensure the selection is updated
        GLib.timeout_add(100, self._update_time_display)
    
    def _update_time_display_timer(self):
        """Timer callback for updating time display."""
        if hasattr(self, 'time_display') and self.time_display:
            self._update_time_display()
        return True  # Continue the timer
    
    def _update_time_display(self):
        """Update the current time display for selected timezone."""
        # Check if time_display exists
        if not hasattr(self, 'time_display') or not self.time_display:
            return False
            
        try:
            selected_tz = self.get_data().get("timezone", "UTC")
            if selected_tz:
                # Use a more robust time display method
                import zoneinfo
                from datetime import datetime
                
                try:
                    tz = zoneinfo.ZoneInfo(selected_tz)
                    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
                    self.time_display.set_text(f"{current_time}")
                except:
                    # Fallback to system time if timezone conversion fails
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.time_display.set_text(f"{current_time} (System Time)")
            else:
                self.time_display.set_text("No timezone selected")
        except Exception as e:
            if hasattr(self, 'time_display') and self.time_display:
                self.time_display.set_text("Unable to display time")
            print(f"Error updating time display: {e}")
        
        return False  # For one-time GLib.timeout_add calls
    
    def _on_auto_detect(self, button):
        """Auto-detect the current timezone."""
        try:
            # Try multiple methods to detect timezone
            methods = [
                ["timedatectl", "show", "--property=Timezone", "--value"],
                ["cat", "/etc/timezone"],
                ["readlink", "/etc/localtime"]
            ]
            
            for method in methods:
                try:
                    result = subprocess.run(method, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        detected_tz = result.stdout.strip()
                        
                        # Handle symlink case
                        if detected_tz.startswith("/usr/share/zoneinfo/"):
                            detected_tz = detected_tz.replace("/usr/share/zoneinfo/", "")
                        
                        # Check if timezone exists in our list
                        model = self.tz_dropdown.get_model()
                        for i in range(model.get_n_items()):
                            if model.get_string(i) == detected_tz:
                                self.tz_dropdown.set_selected(i)
                                return
                except:
                    continue
            
            # If we get here, auto-detection failed
            self.show_error("Could not auto-detect timezone")
            
        except Exception as e:
            self.show_error(f"Auto-detection failed: {str(e)}")
    
    def get_data(self) -> dict:
        """Get the selected timezone."""
        selected_index = self.tz_dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION:
            model = self.tz_dropdown.get_model()
            selected_tz = model.get_string(selected_index)
            return {"timezone": selected_tz}
        return {"timezone": ""}
    
    def validate(self) -> tuple[bool, str]:
        """Validate timezone selection."""
        data = self.get_data()
        if not data.get("timezone"):
            return False, "Please select a time zone"
        return True, ""
