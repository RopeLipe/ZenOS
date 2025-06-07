"""
Language Selec        # Left panel with title and icon
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_panel.add_css_class("language-left-panel")
        
        # Language title (above icon now)
        title_label = Gtk.Label(label="Language")
        title_label.add_css_class("language-title")
        title_label.set_halign(Gtk.Align.START)
        left_panel.append(title_label)
        
        # Language icon - Using proper language/globe icon
        icon_label = Gtk.Label(label="🌐")
        icon_label.add_css_class("language-icon")
        left_panel.append(icon_label)"

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .base_page import BasePage

class LanguagePage(BasePage):
    def __init__(self, navigate_callback):
        super().__init__(navigate_callback)
        self.setup_page()
    
    def setup_page(self):
        # Create main horizontal layout
        main_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_container.add_css_class("language-main-container")
        
        # Left panel with icon and title
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_panel.add_css_class("language-left-panel")
          # Language icon - Modern globe icon using Unicode
        icon_label = Gtk.Label(label="�")
        icon_label.add_css_class("language-icon")
        left_panel.append(icon_label)
        
        # Language title
        title_label = Gtk.Label(label="Language")
        title_label.add_css_class("language-title")
        title_label.set_halign(Gtk.Align.START)
        left_panel.append(title_label)
        
        # Right panel with selection
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_panel.add_css_class("language-right-panel")
        
        # Header section
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header_box.add_css_class("language-header")
          # Subtitle
        subtitle_label = Gtk.Label(label="Select Language")
        subtitle_label.add_css_class("page-subtitle")
        subtitle_label.set_halign(Gtk.Align.END)
        header_box.append(subtitle_label)
        
        # Description
        desc_label = Gtk.Label(label="Choose your preferred language for the installation and system.")
        desc_label.add_css_class("page-description")
        desc_label.set_halign(Gtk.Align.END)
        desc_label.set_wrap(True)
        header_box.append(desc_label)
        
        right_panel.append(header_box)
        
        # Language selection
        self.setup_language_selection(right_panel)
        
        main_container.append(left_panel)
        main_container.append(right_panel)
        
        self.content_box.append(main_container)
          # Setup navigation
        self.back_btn.set_sensitive(False)  # First page, no back button
        self.continue_btn.connect("clicked", self.on_continue)
    
    def setup_language_selection(self, parent_container):
        """Setup language selection list"""
        # Create container for the selection
        selection_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        selection_container.add_css_class("language-selection-container")
        
        # Create scrolled window for language list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        # Create list box
        self.language_list = Gtk.ListBox()
        self.language_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
          # Language options without flag emojis
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
            row.add_css_class("language-list-item")
            
            label = Gtk.Label(label=lang_name)
            label.set_halign(Gtk.Align.START)
            label.set_margin_start(16)
            label.set_margin_end(16)
            label.set_margin_top(12)
            label.set_margin_bottom(12)
            label.set_markup(f'<span font="14">{lang_name}</span>')
            
            row.set_child(label)
            row.lang_code = lang_code
            self.language_list.append(row)
        
        # Select English by default
        self.language_list.select_row(self.language_list.get_row_at_index(0))
        
        scrolled.set_child(self.language_list)
        selection_container.append(scrolled)
        parent_container.append(selection_container)
        
    def on_continue(self, button):
        """Handle continue button click"""
        selected_row = self.language_list.get_selected_row()
        if selected_row:
            selected_lang = selected_row.lang_code
            print(f"Selected language: {selected_lang}")
            self.navigate("timezone")
