import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from .eventhandlers import WindowHandlers
from .sidepane import SidePaneManager
from .uisetup import UISetup


class MainWindow(Gtk.ApplicationWindow, WindowHandlers, SidePaneManager, UISetup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize side pane
        self.init_pane()
        # Setup window components
        self.setup_window()
        self.setup_css()
        self.setup_revealer()
        self.setup_click_controller()
        self.setup_panes()
