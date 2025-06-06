# GTK4 Linux Installer - Enhanced with Full Logic and UI

import gi
import subprocess
import os
import random
import string
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

# --- Helper Functions ---
def get_all_locales():
    locales = set()
    try:
        with open("/usr/share/i18n/SUPPORTED", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    locale = line.split()[0]
                    locales.add(locale)
    except Exception as e:
        print("Locale error:", e)
    return sorted(locales)

def get_all_keymaps():
    try:
        result = subprocess.run(["localectl", "list-keymaps"], capture_output=True, text=True)
        return sorted(set(result.stdout.strip().split('\n')))
    except Exception as e:
        print("Keyboard error:", e)
        return []

def get_all_timezones():
    zones = []
    for root, _, files in os.walk("/usr/share/zoneinfo"):
        for name in files:
            path = os.path.join(root, name)
            if "posix" in path or "right" in path or "/Etc/" in path:
                continue
            zones.append(os.path.relpath(path, "/usr/share/zoneinfo"))
    return sorted(zones)

def get_disks():
    try:
        result = subprocess.run(["lsblk", "-o", "NAME,SIZE,TYPE", "-d", "-J"], capture_output=True, text=True)
        import json
        data = json.loads(result.stdout)
        return [f"/dev/{d['name']} ({d['size']})" for d in data['blockdevices'] if d['type'] == 'disk']
    except Exception as e:
        print("Disk error:", e)
        return []

def get_wifi_networks():
    try:
        result = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True)
        ssids = list(set(filter(None, result.stdout.strip().split('\n'))))
        return sorted(ssids)
    except Exception as e:
        print("WiFi error:", e)
        return []

# --- Pages ---
class LocalePage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

        label = Gtk.Label(label="Select your preferred language")
        self.append(label)

        self.lang_combo = Gtk.ComboBoxText()
        for lang in get_all_locales():
            self.lang_combo.append_text(lang)
        self.lang_combo.set_active(0)
        self.append(self.lang_combo)

    def get_value(self):
        return self.lang_combo.get_active_text()

class KeyboardPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

        label = Gtk.Label(label="Choose your keyboard layout")
        self.append(label)

        self.kbd_combo = Gtk.ComboBoxText()
        for keymap in get_all_keymaps():
            self.kbd_combo.append_text(keymap)
        self.kbd_combo.set_active(0)
        self.append(self.kbd_combo)

    def get_value(self):
        return self.kbd_combo.get_active_text()

class TimezonePage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

        label = Gtk.Label(label="Select your timezone")
        self.append(label)

        self.tz_combo = Gtk.ComboBoxText()
        for tz in get_all_timezones():
            self.tz_combo.append_text(tz)
        self.tz_combo.set_active(0)
        self.append(self.tz_combo)

    def get_value(self):
        return self.tz_combo.get_active_text()

class DiskPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

        label = Gtk.Label(label="Choose disk to install on (this will erase it!)")
        self.append(label)

        self.disk_combo = Gtk.ComboBoxText()
        for disk in get_disks():
            self.disk_combo.append_text(disk)
        self.disk_combo.set_active(0)
        self.append(self.disk_combo)

    def get_value(self):
        return self.disk_combo.get_active_text().split()[0]

class WiFiPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

        label = Gtk.Label(label="Choose WiFi network")
        self.append(label)

        self.wifi_combo = Gtk.ComboBoxText()
        for ssid in get_wifi_networks():
            self.wifi_combo.append_text(ssid)
        self.wifi_combo.set_active(0)
        self.append(self.wifi_combo)

        self.password = Gtk.Entry()
        self.password.set_placeholder_text("WiFi Password")
        self.password.set_visibility(False)
        self.append(self.password)

    def connect_wifi(self):
        ssid = self.wifi_combo.get_active_text()
        passwd = self.password.get_text()
        if ssid:
            subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", passwd])

    def get_value(self):
        return self.wifi_combo.get_active_text()

class UserPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

        label = Gtk.Label(label="Create a user account")
        self.append(label)

        self.username = Gtk.Entry()
        self.username.set_placeholder_text("Username")
        self.append(self.username)

        self.password = Gtk.Entry()
        self.password.set_placeholder_text("Password")
        self.password.set_visibility(False)
        self.append(self.password)

    def get_credentials(self):
        return self.username.get_text(), self.password.get_text()

# --- Installer Window ---
class InstallerWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Linux Installer")
        self.set_default_size(600, 600)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(main_box)

        self.stack = Gtk.Stack()
        main_box.append(self.stack)

        self.pages = []
        self.build_pages()
        self.current = 0

        self.stack.set_visible_child_name("page0")

        nav_box = Gtk.Box(spacing=10)
        self.next_btn = Gtk.Button(label="Next")
        self.next_btn.connect("clicked", self.on_next)
        nav_box.append(self.next_btn)
        main_box.append(nav_box)


    def build_pages(self):
        self.locale_page = LocalePage()
        self.keyboard_page = KeyboardPage()
        self.tz_page = TimezonePage()
        self.disk_page = DiskPage()
        self.wifi_page = WiFiPage()
        self.user_page = UserPage()

        self.pages = [self.locale_page, self.keyboard_page, self.tz_page, self.disk_page, self.wifi_page, self.user_page]

        for i, page in enumerate(self.pages):
            self.stack.add_named(page, f"page{i}")

    def on_next(self, btn):
        if self.current < len(self.pages) - 1:
            self.current += 1
            self.stack.set_visible_child_name(f"page{self.current}")
        else:
            self.wifi_page.connect_wifi()
            self.run_install()

    def run_install(self):
        locale = self.locale_page.get_value()
        kbd = self.keyboard_page.get_value()
        tz = self.tz_page.get_value()
        disk = self.disk_page.get_value()
        username, password = self.user_page.get_credentials()

        # Partition and format disk
        subprocess.run(["sgdisk", "--zap-all", disk])
        subprocess.run(["parted", disk, "mklabel", "gpt", "--script"])
        subprocess.run(["parted", disk, "mkpart", "primary", "ext4", "1MiB", "100%", "--script"])
        part = disk + "1"
        subprocess.run(["mkfs.ext4", part])

        # Mount partition
        subprocess.run(["mount", part, "/mnt"])

        # Debootstrap
        subprocess.run(["debootstrap", "--arch=amd64", "stable", "/mnt", "http://deb.debian.org/debian"])

        # Locale and timezone
        with open("/mnt/etc/locale.gen", "w") as f:
            f.write(locale + " UTF-8\n")
        with open("/mnt/etc/timezone", "w") as f:
            f.write(tz + "\n")

        subprocess.run(["chroot", "/mnt", "locale-gen"])
        subprocess.run(["chroot", "/mnt", "ln", "-sf", f"/usr/share/zoneinfo/{tz}", "/etc/localtime"])

        # Keymap inside chroot
        with open("/mnt/etc/vconsole.conf", "w") as f:
            f.write(f"KEYMAP={kbd}\n")

        # WiFi config
        subprocess.run(["cp", "/etc/NetworkManager/system-connections", "/mnt/etc/NetworkManager/"], stderr=subprocess.DEVNULL)

        # Create user
        subprocess.run(["chroot", "/mnt", "useradd", "-m", "-s", "/bin/bash", username])
        subprocess.run(["chroot", "/mnt", "bash", "-c", f"echo '{username}:{password}' | chpasswd"])

        # Generate fstab
        subprocess.run(["genfstab", "-U", "/mnt"], stdout=open("/mnt/etc/fstab", "w"))

        # Set random root password
        root_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        subprocess.run(["chroot", "/mnt", "bash", "-c", f"echo root:{root_pass} | chpasswd"])

        # Install bootloader
        subprocess.run(["chroot", "/mnt", "grub-install", disk])
        subprocess.run(["chroot", "/mnt", "update-grub"])

        # Unmount and reboot
        subprocess.run(["umount", "-R", "/mnt"])
        subprocess.run(["reboot"])

# --- App Entry ---
class InstallerApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.installer")

    def do_activate(self):
        win = InstallerWindow(self)
        win.present()

app = InstallerApp()
app.run()
