"""
Timezone selection page.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .base_page import BasePage
from utils.system_utils import get_all_timezones
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
          # Timezone selection with improved layout
        tz_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        # Left side - dropdown
        tz_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        tz_box.set_hexpand(True)
        
        tz_label = Gtk.Label(label="Time Zone:")        tz_label.set_halign(Gtk.Align.START)
        tz_box.append(tz_label)
        
        # Create dropdown with search
        self.tz_dropdown = Gtk.DropDown()
        self.tz_dropdown.set_enable_search(True)
        self.tz_dropdown.connect("notify::selected", self._on_timezone_changed)
        
        # Load timezones
        self._load_timezones()
        
        tz_box.append(self.tz_dropdown)
        tz_container.append(tz_box)
        
        # Right side - auto-detect button (smaller and better positioned)
        detect_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        detect_container.set_valign(Gtk.Align.END)
        
        # Small auto-detect button
        detect_button = Gtk.Button(label="Auto-Detect")
        detect_button.connect("clicked", self._on_auto_detect)
        detect_button.set_size_request(100, -1)
        detect_button.add_css_class("modern-button")
        detect_container.append(detect_button)
        
        tz_container.append(detect_container)
        self.content_box.append(tz_container)
        
        # Current time display
        time_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        time_box.set_margin_top(20)
        
        time_label = Gtk.Label(label="Current time in selected timezone:")
        time_label.set_halign(Gtk.Align.START)
        time_box.append(time_label)
          self.time_display = Gtk.Label()
        self.time_display.set_halign(Gtk.Align.START)
        self.time_display.add_css_class("monospace")
        time_box.append(self.time_display)
        
        self.content_box.append(time_box)
          
        # Set up timer for live time updates
        GLib.timeout_add_seconds(1, self._update_time_display_timer)
        
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
        
        # Interactive timezone map
        map_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        map_box.set_margin_top(20)
        
        map_label = Gtk.Label(label="Or click on the map to select your timezone:")
        map_label.set_halign(Gtk.Align.START)
        map_box.append(map_label)
        
        # Create map canvas
        map_frame = Gtk.Frame()
        map_frame.add_css_class("card")
        map_frame.set_size_request(800, 400)
        
        self.map_drawing_area = Gtk.DrawingArea()
        self.map_drawing_area.set_draw_func(self._draw_world_map)
        
        # Add click handler for map
        map_click = Gtk.GestureClick()
        map_click.connect("pressed", self._on_map_clicked)
        self.map_drawing_area.add_controller(map_click)
        
        map_frame.set_child(self.map_drawing_area)
        map_box.append(map_frame)
        
        self.content_box.append(map_box)

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
        if selected_index != Gtk.INVALID_LIST_POSITION and hasattr(self, 'timezones') and selected_index < len(self.timezones):
            selected_timezone = self.timezones[selected_index]
            return {"timezone": selected_timezone}
        return {"timezone": ""}
    
    def validate(self) -> tuple[bool, str]:
        """Validate timezone selection."""
        data = self.get_data()
        if not data.get("timezone"):
            return False, "Please select a time zone"
        return True, ""

    def _draw_world_map(self, widget, cr, width, height):
        """Draw a simple world map outline (placeholder for actual map)."""
        cr.set_source_rgb(1, 1, 1)  # White background
        cr.paint()
        
        cr.set_source_rgb(0, 0, 0)  # Black color for map outline
        cr.set_line_width(0.5)
        
        # Draw continents (simplified)
        continents = [
            # Africa
            [ (20, 150), (60, 180), (100, 150), (80, 100), (20, 150) ],
            # Europe
            [ (120, 80), (160, 50), (200, 80), (180, 120), (120, 80) ],
            # Asia
            [ (220, 50), (260, 20), (300, 50), (280, 90), (220, 50) ],
            # North America
            [ (20, 10), (60, -20), (100, 10), (80, 50), (20, 10) ],
            # South America
            [ (120, 100), (160, 70), (200, 100), (180, 140), (120, 100) ],
            # Australia
            [ (220, 150), (260, 120), (300, 150), (280, 190), (220, 150) ]
        ]
        
        for continent in continents:
            cr.move_to(*continent[0])
            for point in continent[1:]:
                cr.line_to(*point)
            cr.close_path()
        
        cr.stroke()
        
        # Draw timezone lines (simplified)
        cr.set_line_width(0.2)
        for x in range(0, width, 20):
            cr.move_to(x, 0)
            cr.line_to(x, height)
        for y in range(0, height, 20):
            cr.move_to(0, y)
            cr.line_to(width, y)
        
        cr.stroke()
        
        # Draw selected timezone region (if any)
        try:
            selected_tz = self.get_data().get("timezone", "UTC")
            if selected_tz and hasattr(self, 'timezones'):
                index = self.timezones.index(selected_tz)
                if index != -1:
                    # Highlight the region for the selected timezone
                    cr.set_source_rgba(1, 0, 0, 0.5)  # Red with transparency
                    cr.set_line_width(0)
                    
                    # Draw a simple circle around the approximate region
                    cr.arc(width / 2, height / 2, 70, 0, 2 * 3.1416)
                    cr.fill()
        except:
            pass

    def _draw_world_map(self, area, cr, width, height, user_data):
        """Draw a simplified world map with timezone regions."""
        import math
        
        # Clear background
        cr.set_source_rgb(0.95, 0.95, 0.95)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        # Define timezone regions as rectangles (simplified)
        # Format: (x, y, width, height, timezone, color)
        self.timezone_regions = [
            # Americas
            (50, 150, 80, 120, "America/New_York", (0.8, 0.9, 1.0)),
            (130, 140, 60, 130, "America/Chicago", (0.7, 0.8, 0.9)),
            (190, 130, 70, 140, "America/Denver", (0.6, 0.7, 0.8)),
            (260, 120, 80, 150, "America/Los_Angeles", (0.5, 0.6, 0.7)),
            
            # Europe/Africa
            (400, 100, 60, 100, "Europe/London", (1.0, 0.9, 0.8)),
            (460, 90, 50, 110, "Europe/Paris", (0.9, 0.8, 0.7)),
            (510, 85, 45, 115, "Europe/Berlin", (0.8, 0.7, 0.6)),
            (420, 200, 80, 120, "Africa/Cairo", (0.7, 0.8, 0.9)),
            
            # Asia/Oceania
            (570, 80, 50, 100, "Asia/Moscow", (0.9, 0.7, 0.8)),
            (620, 90, 60, 90, "Asia/Dubai", (0.8, 0.6, 0.7)),
            (680, 100, 70, 80, "Asia/Kolkata", (0.7, 0.5, 0.6)),
            (750, 80, 60, 100, "Asia/Shanghai", (0.6, 0.4, 0.5)),
            (810, 90, 50, 90, "Asia/Tokyo", (0.5, 0.3, 0.4)),
            (780, 220, 70, 80, "Australia/Sydney", (0.4, 0.2, 0.3)),
        ]
        
        # Draw regions
        for x, y, w, h, tz, color in self.timezone_regions:
            # Scale to fit canvas
            scale_x = width / 900
            scale_y = height / 400
            
            rx = x * scale_x
            ry = y * scale_y
            rw = w * scale_x
            rh = h * scale_y
            
            # Draw region
            cr.set_source_rgb(*color)
            cr.rectangle(rx, ry, rw, rh)
            cr.fill()
            
            # Draw border
            cr.set_source_rgb(0.3, 0.3, 0.3)
            cr.set_line_width(1)
            cr.rectangle(rx, ry, rw, rh)
            cr.stroke()
            
            # Draw timezone label
            cr.set_source_rgb(0, 0, 0)
            cr.select_font_face("Sans", 0, 0)
            cr.set_font_size(10)
            
            # Extract city name from timezone
            city = tz.split('/')[-1].replace('_', ' ')
            text_extents = cr.text_extents(city)
            text_x = rx + (rw - text_extents.width) / 2
            text_y = ry + (rh + text_extents.height) / 2
            
            cr.move_to(text_x, text_y)
            cr.show_text(city)
    
    def _on_map_clicked(self, gesture, n_press, x, y):
        """Handle clicks on the timezone map."""
        if not hasattr(self, 'timezone_regions'):
            return
        
        # Get canvas dimensions
        width = self.map_drawing_area.get_width()
        height = self.map_drawing_area.get_height()
        
        # Check which region was clicked
        for rx, ry, rw, rh, tz, color in self.timezone_regions:
            # Scale coordinates
            scale_x = width / 900
            scale_y = height / 400
            
            region_x = rx * scale_x
            region_y = ry * scale_y
            region_w = rw * scale_x
            region_h = rh * scale_y
            
            # Check if click is within region
            if (region_x <= x <= region_x + region_w and 
                region_y <= y <= region_y + region_h):
                
                # Find timezone in dropdown and select it
                if hasattr(self, 'timezones') and tz in self.timezones:
                    index = self.timezones.index(tz)
                    self.tz_dropdown.set_selected(index)
                    break

        # ...existing code...
