"""
Pages package for GTK4 Installer
"""

from .language_page import LanguagePage
from .timezone_page import TimezonePage
from .keyboard_page import KeyboardPage
from .disk_page import DiskPage
from .wifi_page import WifiPage
from .user_page import UserPage

__all__ = [
    'LanguagePage',
    'TimezonePage', 
    'KeyboardPage',
    'DiskPage',
    'WifiPage',
    'UserPage'
]
