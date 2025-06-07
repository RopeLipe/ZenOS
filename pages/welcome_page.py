"""
Welcome Page for the Installer
"""
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .base_page import BasePage
import os

class WelcomePage(BasePage):
    def __init__(self, navigate_callback):
        super().__init__(navigate_callback)
        self.setup_page()

    def setup_page(self):
        # Hide default navigation buttons from BasePage
        self.nav_box.set_visible(False)

        page_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        page_container.set_vexpand(True)
        page_container.set_hexpand(True)
        page_container.add_css_class("welcome-page-container")

        # Top-left "Welcome" title
        welcome_title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        welcome_title_box.set_halign(Gtk.Align.START)
        welcome_title_label = Gtk.Label(label="Welcome")
        welcome_title_label.add_css_class("welcome-page-title-top-left")
        welcome_title_label.set_halign(Gtk.Align.START)
        welcome_title_box.append(welcome_title_label)
        page_container.append(welcome_title_box)

        # Centered content
        centered_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        centered_box.set_valign(Gtk.Align.CENTER)
        centered_box.set_halign(Gtk.Align.CENTER)
        centered_box.set_vexpand(True)

        main_title = Gtk.Label(label="Meet your new desktop, Wave")
        main_title.add_css_class("welcome-main-title")
        centered_box.append(main_title)

        subtitle = Gtk.Label(label="Simply speedy & elegant.")
        subtitle.add_css_class("welcome-subtitle")
        centered_box.append(subtitle)

        # Laptop Icon (Placeholder)
        # TODO: Replace with actual image
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "laptop-wave-icon.png")
        if os.path.exists(icon_path):
            laptop_icon = Gtk.Image.new_from_file(icon_path)
        else:
            laptop_icon = Gtk.Label(label="💻") # Placeholder if image not found
            print(f"Laptop icon not found at {icon_path}, using placeholder.")
        laptop_icon.add_css_class("welcome-laptop-icon")
        laptop_icon.set_pixel_size(128) # Example size, adjust with CSS
        centered_box.append(laptop_icon)

        install_button = Gtk.Button(label="Install Now")
        install_button.add_css_class("btn-primary")
        install_button.add_css_class("welcome-install-button")
        install_button.connect("clicked", self.on_install_now)
        centered_box.append(install_button)
        
        page_container.append(centered_box)
        
        # An empty box to push content up if needed, or manage spacing
        spacer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        spacer_box.set_vexpand(True) # Allow this to take up space if centered_box is not expanding enough
        page_container.append(spacer_box)

        self.content_box.append(page_container)

    def on_install_now(self, button):
        self.navigate("language")
