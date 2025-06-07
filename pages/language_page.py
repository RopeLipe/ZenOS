"""
Language Selection Page
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .base_page import BasePage

class LanguagePage(BasePage):
    def __init__(self, navigate_callback):
        super().__init__(navigate_callback)
        self.setup_page()
        
    def setup_page(self):
        # Create header
        self.create_header(
            "Language",
            "Select Language",
            "Choose your preferred language for the installation and system."
        )
        
        # Language selection
        self.setup_language_selection()
        
        # Setup navigation
        self.back_btn.set_sensitive(False)  # First page, no back button
        self.continue_btn.connect("clicked", self.on_continue)
        
    def setup_language_selection(self):
        """Setup language selection list"""
        # Create scrolled window for language list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(300)
        
        # Create list box
        self.language_list = Gtk.ListBox()
        self.language_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        
        # Language options
        languages = [
            ("English", "en"),
            ("Español", "es"),
            ("Français", "fr"),
            ("Deutsch", "de"),
            ("Italiano", "it"),
            ("Português", "pt"),
            ("Русский", "ru"),
            ("中文", "zh"),
            ("日本語", "ja"),
            ("한국어", "ko"),
            ("العربية", "ar"),
            ("हिन्दी", "hi")
        ]
        
        for lang_name, lang_code in languages:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=lang_name)
            label.set_halign(Gtk.Align.START)
            label.set_margin_start(16)
            label.set_margin_end(16)
            label.set_margin_top(12)
            label.set_margin_bottom(12)
            row.set_child(label)
            row.lang_code = lang_code
            self.language_list.append(row)
        
        # Select English by default
        self.language_list.select_row(self.language_list.get_row_at_index(0))
        
        scrolled.set_child(self.language_list)
        self.content_box.append(scrolled)
        
    def on_continue(self, button):
        """Handle continue button click"""
        selected_row = self.language_list.get_selected_row()
        if selected_row:
            selected_lang = selected_row.lang_code
            print(f"Selected language: {selected_lang}")
            self.navigate("timezone")
