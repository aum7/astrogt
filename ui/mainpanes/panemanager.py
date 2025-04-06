# panemanager.py
# ruff: noqa: E402
from typing import Dict
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class PaneManager(Gtk.Stack):
    """mixin class for main panes & stack management"""

    # type hints for inherited attributes
    stack: Gtk.Stack
    stack_pages: Dict[str, Gtk.Widget]
    stack_names: Dict[str, str]

    def __init__(self, stack_manager=None, position=None, name=None):
        super().__init__()
        # track stacks per position
        self.pane_stacks = {
            "top-left": None,
            "top-right": None,
            "bottom-left": None,
            "bottom-right": None,
        }

    def setup_stacks(self, position: str) -> Gtk.Stack:
        """create & setup stack for given position"""
        if position not in self.pane_stacks:
            return None
        # needed as separate instances
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        stack.set_transition_duration(10)
        # store stack for position
        self.pane_stacks[position] = stack
        return stack

    def get_stack(self, position: str) -> Gtk.Stack:
        """get stack by position"""
        return self.pane_stacks.get(position)

    def add_page(self, widget, name, title=None):
        """add new page to pane"""
        self.add_titled(widget, name, title)
