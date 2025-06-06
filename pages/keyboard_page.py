"""
Keyboard layout selection page.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .base_page import BasePage
from utils.system_utils import get_all_keymaps


class KeyboardPage(BasePage):
    """Page for selecting keyboard layout."""
    
    def __init__(self):
        super().__init__(
            "Keyboard Layout", 
            "Select your keyboard layout for the system."
        )
        
        # Keyboard layout selection
        kbd_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        kbd_label = Gtk.Label(label="Keyboard Layout:")
        kbd_label.set_halign(Gtk.Align.START)
        kbd_box.append(kbd_label)
        
        # Create dropdown with search
        self.kbd_dropdown = Gtk.DropDown()
        self.kbd_dropdown.set_enable_search(True)
        
        # Load keymaps
        self._load_keymaps()
        
        kbd_box.append(self.kbd_dropdown)
        self.content_box.append(kbd_box)
        
        # Test area
        test_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        test_box.set_margin_top(20)
        
        test_label = Gtk.Label(label="Test your keyboard:")
        test_label.set_halign(Gtk.Align.START)
        test_box.append(test_label)
        
        self.test_entry = Gtk.Entry()
        self.test_entry.set_placeholder_text("Type here to test your keyboard layout...")
        test_box.append(self.test_entry)
        
        self.content_box.append(test_box)
        
        # Additional info
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small>Choose the keyboard layout that matches your physical keyboard. "
            "You can test it using the text field above.</small>"
        )
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.START)
        info_label.add_css_class("dim-label")
        info_label.set_margin_top(16)
        self.content_box.append(info_label)
    
    def _load_keymaps(self):
        """Load available keyboard layouts into the dropdown."""
        keymaps = get_all_keymaps()
        
        # Create string list model
        string_list = Gtk.StringList()
        for keymap in keymaps:
            string_list.append(keymap)
        
        self.kbd_dropdown.set_model(string_list)
        
        # Set default to 'us' if available
        if "us" in keymaps:
            self.kbd_dropdown.set_selected(keymaps.index("us"))
    
    def get_data(self) -> dict:
        """Get the selected keyboard layout."""
        selected_index = self.kbd_dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION:
            model = self.kbd_dropdown.get_model()
            selected_keymap = model.get_string(selected_index)
            return {"keyboard": selected_keymap}
        return {"keyboard": ""}
    
    def validate(self) -> tuple[bool, str]:
        """Validate keyboard layout selection."""
        data = self.get_data()
        if not data.get("keyboard"):
            return False, "Please select a keyboard layout"
        return True, ""
    
    def on_page_enter(self):
        """Focus the test entry when page becomes visible."""
        self.test_entry.grab_focus()
