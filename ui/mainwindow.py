from typing import Any, Type
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from .handlers import WindowHandlers
from .sidepane import SidePaneManager
from .uisetup import UISetup


class MainWindow(
    Gtk.ApplicationWindow,
    WindowHandlers,
    SidePaneManager,
    UISetup,
):
    """main application window, combining ui, handlers & panes"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """initialize the main window.
        args:
            *args: variable length argument list.
            **kwargs: arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        # initialize side pane
        self.init_side_pane()
        # setup revealer
        self.setup_revealer()
        # setup window components
        self.setup_window()
        self.setup_css()
        self.setup_click_controller()
        # self.setup_main_panes()
