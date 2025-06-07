"""
Keyboard layout selection page.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .base_page import BasePage
from utils.system_utils import get_all_keymaps
import subprocess


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
        kbd_box.append(kbd_label)        # Create dropdown with search
        self.kbd_dropdown = Gtk.DropDown()
        self.kbd_dropdown.set_enable_search(True)
        self.kbd_dropdown.set_search_match_mode(Gtk.StringFilterMatchMode.SUBSTRING)
        self.kbd_dropdown.connect("notify::selected", self._on_keymap_changed)
        
        # Load keymaps
        self._load_keymaps()
        
        kbd_box.append(self.kbd_dropdown)
        self.content_box.append(kbd_box)
          # Interactive keyboard preview
        test_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        test_box.set_margin_top(20)
        
        test_label = Gtk.Label(label="Interactive Keyboard Preview:")
        test_label.set_halign(Gtk.Align.START)
        test_box.append(test_label)
        
        # Keyboard visualization container
        self.keyboard_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.keyboard_container.add_css_class("keyboard-preview")
        self.keyboard_container.set_margin_top(10)
        
        # Create keyboard layout
        self._create_keyboard_layout()
        
        test_box.append(self.keyboard_container)
        
        # Instructions
        instruction_label = Gtk.Label()
        instruction_label.set_markup(
            "<small>Press keys on your keyboard to see them highlighted in the preview above.</small>"
        )
        instruction_label.set_halign(Gtk.Align.START)
        instruction_label.add_css_class("dim-label")
        instruction_label.set_margin_top(8)
        test_box.append(instruction_label)
        
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
        self.keymaps = get_all_keymaps()
        
        # Log available keymaps for debugging
        print(f"Found {len(self.keymaps)} keyboard layouts: {self.keymaps[:10]}{'...' if len(self.keymaps) > 10 else ''}")
        
        # Create string list model
        string_list = Gtk.StringList()
        for keymap in self.keymaps:
            string_list.append(keymap)
        
        self.kbd_dropdown.set_model(string_list)
        
        # Set default to 'us' if available
        if "us" in self.keymaps:
            self.kbd_dropdown.set_selected(self.keymaps.index("us"))
      def _on_keymap_changed(self, dropdown, param):
        """Handle keymap selection change and apply it temporarily."""
        selected_index = self.kbd_dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION and selected_index < len(self.keymaps):
            selected_keymap = self.keymaps[selected_index]
            self._apply_keymap_temporarily(selected_keymap)
            # Update keyboard layout visualization
            self._create_keyboard_layout()
    
    def _create_keyboard_layout(self):
        """Create a visual keyboard layout."""
        # Define common keyboard layouts
        keyboard_layouts = {
            'us': [
                ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
                ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
                ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'"],
                ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/']
            ],
            'uk': [
                ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
                ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']'],
                ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", '#'],
                ['\\', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/']
            ],
            'de': [
                ['^', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'ß', '´'],
                ['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P', 'Ü', '+'],
                ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ö', 'Ä', '#'],
                ['<', 'Y', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '-']
            ],
            'fr': [
                ['²', '&', 'é', '"', "'", '(', '-', 'è', '_', 'ç', 'à', ')', '='],
                ['A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '^', '$'],
                ['Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'ù', '*'],
                ['<', 'W', 'X', 'C', 'V', 'B', 'N', ',', ';', ':', '!']
            ]
        }
        
        # Get current layout (default to US)
        layout = 'us'
        selected_index = self.kbd_dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION and selected_index < len(self.keymaps):
            current_keymap = self.keymaps[selected_index]
            layout = current_keymap if current_keymap in keyboard_layouts else 'us'
        
        # Clear existing keyboard
        child = self.keyboard_container.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.keyboard_container.remove(child)
            child = next_child
        
        # Create keyboard rows
        self.key_buttons = {}
        for row_keys in keyboard_layouts[layout]:
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            row_box.set_halign(Gtk.Align.CENTER)
            
            for key in row_keys:
                key_button = Gtk.Button(label=key)
                key_button.set_size_request(35, 35)
                key_button.add_css_class("keyboard-key")
                key_button.set_sensitive(False)  # Non-interactive display
                self.key_buttons[key.lower()] = key_button
                row_box.append(key_button)
            
            self.keyboard_container.append(row_box)
        
        # Add spacebar row
        spacebar_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        spacebar_row.set_halign(Gtk.Align.CENTER)
        
        # Add some modifier keys
        ctrl_btn = Gtk.Button(label="Ctrl")
        ctrl_btn.set_size_request(50, 35)
        ctrl_btn.add_css_class("keyboard-key")
        ctrl_btn.set_sensitive(False)
        spacebar_row.append(ctrl_btn)
        
        alt_btn = Gtk.Button(label="Alt")
        alt_btn.set_size_request(40, 35)
        alt_btn.add_css_class("keyboard-key")
        alt_btn.set_sensitive(False)
        spacebar_row.append(alt_btn)
        
        # Spacebar
        space_btn = Gtk.Button(label="Space")
        space_btn.set_size_request(200, 35)
        space_btn.add_css_class("keyboard-key")
        space_btn.set_sensitive(False)
        self.key_buttons[' '] = space_btn
        spacebar_row.append(space_btn)
        
        self.keyboard_container.append(spacebar_row)
        
        # Set up key press detection (simplified)
        self._setup_key_detection()
    
    def _setup_key_detection(self):
        """Set up keyboard event detection for highlighting keys."""
        # Create an invisible entry to capture key events
        self.key_capture_entry = Gtk.Entry()
        self.key_capture_entry.set_visible(False)
        self.keyboard_container.append(self.key_capture_entry)
        
        # Connect key press events
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        key_controller.connect("key-released", self._on_key_released)
        self.add_controller(key_controller)
    
    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle key press events to highlight keys."""
        key_char = chr(keyval).lower() if 32 <= keyval <= 126 else None
        if key_char and key_char in self.key_buttons:
            self.key_buttons[key_char].add_css_class("keyboard-key-pressed")
        return False
    
    def _on_key_released(self, controller, keyval, keycode, state):
        """Handle key release events to remove highlight."""
        key_char = chr(keyval).lower() if 32 <= keyval <= 126 else None
        if key_char and key_char in self.key_buttons:
            self.key_buttons[key_char].remove_css_class("keyboard-key-pressed")
        return False

    def _apply_keymap_temporarily(self, keymap: str):
        """Apply the selected keymap temporarily for testing."""
        try:
            # Apply the keymap to current session for testing
            subprocess.run(
                ["setxkbmap", keymap], 
                check=False, 
                capture_output=True, 
                timeout=5
            )
            print(f"Applied keymap temporarily: {keymap}")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Could not apply keymap {keymap}: {e}")
    
    def get_data(self) -> dict:
        """Get the selected keyboard layout."""
        selected_index = self.kbd_dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION and selected_index < len(self.keymaps):
            selected_keymap = self.keymaps[selected_index]
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
