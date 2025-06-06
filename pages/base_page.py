"""
Base page class for installer pages.
Provides common functionality and styling.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import Any, Optional, Callable


class BasePage(Gtk.Box):
    """Base class for all installer pages."""
    
    def __init__(self, title: str, description: str = ""):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.title = title
        self.description = description
        self._setup_styling()
        self._setup_layout()
    
    def _setup_styling(self):
        """Set up consistent styling for all pages."""
        self.set_margin_top(30)
        self.set_margin_bottom(30)
        self.set_margin_start(40)
        self.set_margin_end(40)
        self.set_hexpand(True)
        self.set_vexpand(True)
    
    def _setup_layout(self):
        """Set up the basic layout with title and description."""
        # Title
        title_label = Gtk.Label()
        title_label.set_markup(f"<span size='x-large' weight='bold'>{self.title}</span>")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_margin_bottom(8)
        self.append(title_label)
        
        # Description (if provided)
        if self.description:
            desc_label = Gtk.Label(label=self.description)
            desc_label.set_halign(Gtk.Align.START)
            desc_label.set_wrap(True)
            desc_label.set_margin_bottom(20)
            desc_label.add_css_class("dim-label")
            self.append(desc_label)
        
        # Content area (to be filled by child classes)
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.append(self.content_box)
        
        # Error label (initially hidden)
        self.error_label = Gtk.Label()
        self.error_label.set_visible(False)
        self.error_label.add_css_class("error")
        self.error_label.set_wrap(True)
        self.append(self.error_label)
    
    def show_error(self, message: str):
        """Display an error message on the page."""
        self.error_label.set_text(message)
        self.error_label.set_visible(True)
    
    def hide_error(self):
        """Hide the error message."""
        self.error_label.set_visible(False)
    
    def get_data(self) -> dict:
        """Get the data from this page. Override in child classes."""
        return {}
    
    def validate(self) -> tuple[bool, str]:
        """Validate page data. Override in child classes."""
        return True, ""
    
    def on_page_enter(self):
        """Called when the page becomes visible. Override in child classes."""
        pass
    
    def on_page_leave(self) -> bool:
        """Called when leaving the page. Return False to prevent navigation."""
        is_valid, error = self.validate()
        if not is_valid:
            self.show_error(error)
            return False
        self.hide_error()
        return True


class LoadingPage(BasePage):
    """Special page for showing loading/progress information."""
    
    def __init__(self, title: str = "Installing System"):
        super().__init__(title, "Please wait while the system is being installed...")
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_margin_top(20)
        self.progress_bar.set_margin_bottom(10)
        self.content_box.append(self.progress_bar)
        
        # Progress label
        self.progress_label = Gtk.Label(label="Preparing...")
        self.progress_label.set_halign(Gtk.Align.START)
        self.content_box.append(self.progress_label)
        
        # Details expander
        self.details_expander = Gtk.Expander(label="Show Details")
        self.details_text = Gtk.TextView()
        self.details_text.set_editable(False)
        self.details_text.set_cursor_visible(False)
        self.details_text.set_monospace(True)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        scrolled.set_child(self.details_text)
        
        self.details_expander.set_child(scrolled)
        self.content_box.append(self.details_expander)
    
    def update_progress(self, message: str, percent: int):
        """Update the progress display."""
        if percent >= 0:
            self.progress_bar.set_fraction(percent / 100.0)
            self.progress_bar.set_text(f"{percent}%")
        else:
            self.progress_bar.set_fraction(0)
            self.progress_bar.set_text("Error")
        
        self.progress_label.set_text(message)
        
        # Add to details log
        buffer = self.details_text.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, f"{message}\n")
        
        # Auto-scroll to bottom
        mark = buffer.get_insert()
        self.details_text.scroll_mark_onscreen(mark)


class ConfirmationPage(BasePage):
    """Page for showing installation summary and confirmation."""
    
    def __init__(self):
        super().__init__(
            "Confirm Installation", 
            "Please review your settings before proceeding. This will erase the selected disk!"
        )
        
        # Warning box
        warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        warning_box.add_css_class("warning")
        warning_box.set_margin_top(10)
        warning_box.set_margin_bottom(20)
        
        warning_icon = Gtk.Image.new_from_icon_name("dialog-warning")
        warning_icon.set_icon_size(Gtk.IconSize.LARGE)
        warning_box.append(warning_icon)
        
        warning_label = Gtk.Label()
        warning_label.set_markup("<b>Warning:</b> This will permanently erase all data on the selected disk!")
        warning_label.set_wrap(True)
        warning_box.append(warning_label)
        
        self.content_box.append(warning_box)
        
        # Summary area
        self.summary_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.content_box.append(self.summary_box)
    
    def update_summary(self, config: dict):
        """Update the installation summary."""
        # Clear existing summary
        child = self.summary_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.summary_box.remove(child)
            child = next_child
        
        # Add summary items
        summary_items = [
            ("Language", config.get('locale', 'Not set')),
            ("Keyboard Layout", config.get('keyboard', 'Not set')),
            ("Timezone", config.get('timezone', 'Not set')),
            ("Installation Disk", config.get('disk', 'Not set')),
            ("Username", config.get('username', 'Not set')),
            ("WiFi Network", config.get('wifi_ssid', 'Not configured')),
        ]
        
        for label, value in summary_items:
            item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            
            label_widget = Gtk.Label(label=f"{label}:")
            label_widget.set_halign(Gtk.Align.START)
            label_widget.set_size_request(150, -1)
            label_widget.add_css_class("dim-label")
            item_box.append(label_widget)
            
            value_widget = Gtk.Label(label=value)
            value_widget.set_halign(Gtk.Align.START)
            value_widget.set_hexpand(True)
            item_box.append(value_widget)
            
            self.summary_box.append(item_box)
