"""
Keyboard Layout Selection Page
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .base_page import BasePage

class KeyboardPage(BasePage):
    def __init__(self, navigate_callback):
        super().__init__(navigate_callback)
        self.setup_page()
        
    def setup_page(self):
        # Create header
        self.create_header(
            "Keyboard",
            "Select Keyboard Layout",
            "Choose your keyboard layout for optimal typing experience."
        )
        
        # Keyboard selection
        self.setup_keyboard_selection()
        
        # Setup navigation
        self.back_btn.connect("clicked", lambda x: self.navigate("timezone"))
        self.continue_btn.connect("clicked", self.on_continue)
        
    def setup_keyboard_selection(self):
        """Setup keyboard selection interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_spacing(20)
        
        # Search box
        search_row = self.create_form_row("Search:", self.create_search_entry())
        main_box.append(search_row)
        
        # Layout selection
        layout_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        layout_box.set_spacing(20)
        
        # Language list
        lang_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        lang_box.set_spacing(8)
        
        lang_label = Gtk.Label(label="Language:")
        lang_label.add_css_class("form-label")
        lang_label.set_halign(Gtk.Align.START)
        lang_box.append(lang_label)
        
        self.language_list = self.create_language_list()
        lang_box.append(self.language_list)
        
        # Layout list
        layout_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        layout_list_box.set_spacing(8)
        
        layout_label = Gtk.Label(label="Layout:")
        layout_label.add_css_class("form-label")
        layout_label.set_halign(Gtk.Align.START)
        layout_list_box.append(layout_label)
        
        self.layout_list = self.create_layout_list()
        layout_list_box.append(self.layout_list)
        
        layout_box.append(lang_box)
        layout_box.append(layout_list_box)
        
        main_box.append(layout_box)
        
        # Test area
        test_row = self.create_form_row("Test your keyboard:", self.create_test_entry())
        main_box.append(test_row)
        
        self.content_box.append(main_box)
        
    def create_search_entry(self):
        """Create search entry"""
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search for keyboard layout...")
        self.search_entry.connect("changed", self.on_search_changed)
        return self.search_entry
        
    def create_language_list(self):
        """Create language list"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        scrolled.set_hexpand(True)
        
        self.lang_listbox = Gtk.ListBox()
        self.lang_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.lang_listbox.connect("row-selected", self.on_language_selected)
        
        # Language options
        languages = [
            ("English (US)", "us"),
            ("English (UK)", "gb"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Russian", "ru"),
            ("Chinese", "cn"),
            ("Japanese", "jp"),
            ("Korean", "kr"),
            ("Arabic", "ar")
        ]
        
        for lang_name, lang_code in languages:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=lang_name)
            label.set_halign(Gtk.Align.START)
            label.set_margin_start(12)
            label.set_margin_end(12)
            label.set_margin_top(8)
            label.set_margin_bottom(8)
            row.set_child(label)
            row.lang_code = lang_code
            self.lang_listbox.append(row)
        
        # Select first by default
        self.lang_listbox.select_row(self.lang_listbox.get_row_at_index(0))
        
        scrolled.set_child(self.lang_listbox)
        return scrolled
        
    def create_layout_list(self):
        """Create layout list"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        scrolled.set_hexpand(True)
        
        self.layout_listbox = Gtk.ListBox()
        self.layout_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        
        # Default layouts for US English
        self.update_layouts("us")
        
        scrolled.set_child(self.layout_listbox)
        return scrolled
        
    def create_test_entry(self):
        """Create test entry"""
        self.test_entry = Gtk.Entry()
        self.test_entry.set_placeholder_text("Type here to test your keyboard layout...")
        return self.test_entry
        
    def update_layouts(self, lang_code):
        """Update layout list based on selected language"""
        # Clear existing layouts
        while True:
            row = self.layout_listbox.get_row_at_index(0)
            if row is None:
                break
            self.layout_listbox.remove(row)
        
        # Layout options based on language
        layout_options = {
            "us": ["QWERTY", "Dvorak", "Colemak"],
            "gb": ["QWERTY", "Dvorak"],
            "es": ["QWERTY", "Spanish"],
            "fr": ["AZERTY", "QWERTY", "Bépo"],
            "de": ["QWERTZ", "QWERTY"],
            "ru": ["Русская", "QWERTY"],
            "ar": ["Arabic", "QWERTY"]
        }
        
        layouts = layout_options.get(lang_code, ["QWERTY"])
        
        for layout_name in layouts:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=layout_name)
            label.set_halign(Gtk.Align.START)
            label.set_margin_start(12)
            label.set_margin_end(12)
            label.set_margin_top(8)
            label.set_margin_bottom(8)
            row.set_child(label)
            row.layout_name = layout_name
            self.layout_listbox.append(row)
        
        # Select first layout
        self.layout_listbox.select_row(self.layout_listbox.get_row_at_index(0))
        
    def on_language_selected(self, listbox, row):
        """Handle language selection"""
        if row:
            lang_code = row.lang_code
            self.update_layouts(lang_code)
            
    def on_search_changed(self, entry):
        """Handle search text change"""
        search_text = entry.get_text().lower()
        # Simple search implementation - in real app, this would filter the lists
        print(f"Searching for: {search_text}")
        
    def on_continue(self, button):
        """Handle continue button click"""
        selected_lang = self.lang_listbox.get_selected_row()
        selected_layout = self.layout_listbox.get_selected_row()
        
        if selected_lang and selected_layout:
            lang_code = selected_lang.lang_code
            layout_name = selected_layout.layout_name
            print(f"Selected keyboard: {lang_code} - {layout_name}")
            
        self.navigate("disk")
