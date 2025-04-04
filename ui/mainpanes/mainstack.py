# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class MainStack(Gtk.Stack):
    """main stack widget where all widgets with data presentation live"""

    def __init__(self):
        super().__init__()
        # configure stack properties
        self.set_transition_type(Gtk.StackTransitionType.NONE)
        self.set_transition_duration(0)

    def add_page(self, widget, name, title=None):
        """add a new party page to stack"""
        # self.add_named(widget, name)
        self.add_titled(widget, name, title)
