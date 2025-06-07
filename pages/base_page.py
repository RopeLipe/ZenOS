"""
Base Page Class for Installer Pages
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class BasePage(Gtk.Box):
    def __init__(self, navigate_callback, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.navigate = navigate_callback
        self.add_css_class("installer-page")
        
        # Main content area
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_box.set_vexpand(True)
        self.append(self.content_box)
        
        # Navigation buttons area
        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.nav_box.set_homogeneous(True)
        self.nav_box.set_spacing(20)
        self.nav_box.add_css_class("nav-buttons")
        self.append(self.nav_box)
        
        # Back button
        self.back_btn = Gtk.Button(label="Back")
        self.back_btn.add_css_class("btn-secondary")
        self.nav_box.append(self.back_btn)
        
        # Continue button
        self.continue_btn = Gtk.Button(label="Continue")
        self.continue_btn.add_css_class("btn-primary")
        self.nav_box.append(self.continue_btn)
    
    def create_header(self, title, subtitle, description):
        """Create page header with title, subtitle and description"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header_box.set_spacing(8)
        
        # Title
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("page-title")
        title_label.set_halign(Gtk.Align.START)
        header_box.append(title_label)
        
        # Subtitle
        subtitle_label = Gtk.Label(label=subtitle)
        subtitle_label.add_css_class("page-subtitle")
        subtitle_label.set_halign(Gtk.Align.START)
        header_box.append(subtitle_label)
        
        # Description
        desc_label = Gtk.Label(label=description)
        desc_label.add_css_class("page-description")
        desc_label.set_halign(Gtk.Align.START)
        desc_label.set_wrap(True)
        header_box.append(desc_label)
        
        self.content_box.append(header_box)
        return header_box
    
    def create_form_row(self, label_text, widget):
        """Create a form row with label and widget"""
        row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        row_box.set_spacing(8)
        row_box.add_css_class("form-row")
        
        # Label
        label = Gtk.Label(label=label_text)
        label.add_css_class("form-label")
        label.set_halign(Gtk.Align.START)
        row_box.append(label)
        
        # Widget
        row_box.append(widget)
        
        return row_box
