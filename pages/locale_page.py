"""
Language and locale selection page.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .base_page import BasePage
from utils.system_utils import get_all_locales


class LocalePage(BasePage):
    """Page for selecting system language and locale."""
    
    def __init__(self):
        super().__init__(
            "Select Language", 
            "Choose your preferred language and regional settings."
        )
        
        # Language selection
        lang_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        lang_label = Gtk.Label(label="Language:")
        lang_label.set_halign(Gtk.Align.START)
        lang_box.append(lang_label)
        
        # Create dropdown with search
        self.lang_dropdown = Gtk.DropDown()
        self.lang_dropdown.set_enable_search(True)
        
        # Load locales
        self._load_locales()
        
        lang_box.append(self.lang_dropdown)
        self.content_box.append(lang_box)
        
        # Additional info
        info_label = Gtk.Label()
        info_label.set_markup(
            "<small>The selected language will be used for the system interface "
            "and default regional settings like date format and number formatting.</small>"
        )
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.START)
        info_label.add_css_class("dim-label")
        info_label.set_margin_top(16)
        self.content_box.append(info_label)
    
    def _load_locales(self):
        """Load available locales into the dropdown."""
        locales = get_all_locales()
        
        # Create string list model
        string_list = Gtk.StringList()
        for locale in locales:
            string_list.append(locale)
        
        self.lang_dropdown.set_model(string_list)
        
        # Set default to English if available
        default_locales = ["en_US.UTF-8", "en_GB.UTF-8", "C.UTF-8"]
        for default in default_locales:
            if default in locales:
                self.lang_dropdown.set_selected(locales.index(default))
                break
    
    def get_data(self) -> dict:
        """Get the selected locale."""
        selected_index = self.lang_dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION:
            model = self.lang_dropdown.get_model()
            selected_locale = model.get_string(selected_index)
            return {"locale": selected_locale}
        return {"locale": ""}
    
    def validate(self) -> tuple[bool, str]:
        """Validate locale selection."""
        data = self.get_data()
        if not data.get("locale"):
            return False, "Please select a language"
        return True, ""
