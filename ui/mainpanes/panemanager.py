# stackmanager.py
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
        self.set_transition_type(Gtk.StackTransitionType.NONE)
        self.set_transition_duration(0)
        # track stacks per position
        self.stacks = {
            "top-left": {},
            "top-right": {},
            "bottom-left": {},
            "bottom-right": {},
        }
        self.box_main_panes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        # frame reference : external or override
        # self.frm_top_start_child = None
        # self.frm_top_end_child = None
        # self.frm_btm_start_child = None
        # self.frm_btm_end_child = None
        # self.frames = {
        #     "top-left": self.frm_top_start_child,
        #     "top-right": self.frm_top_end_child,
        #     "bottom-left": self.frm_btm_start_child,
        #     "bottom-right": self.frm_btm_end_child,
        # }

    def register_stack(self, position: str, name: str, stack: Gtk.Stack) -> None:
        """register a stack with its position and name"""
        if position in self.stacks:
            self.stacks[position][name] = stack

    def setup_stacks(self, position: str, name: str) -> Gtk.Stack:
        """create & setup stack for given position"""
        # if position not in self.frames:
        #     return None
        # needed as separate instances
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.NONE)
        stack.set_transition_duration(0)
        return stack

    def get_stack(self, position: str) -> Dict[str, Gtk.Stack]:
        """get all stacks by position"""
        return self.stacks.get(position, {})

    def get_stack_for_position(self, position: str) -> Dict[str, Gtk.Stack]:
        """alias to get_stack for consistency with context manager"""
        return self.get_stack(position)

    def update_switchers(self, position: str) -> None:
        """update switchers in collapse panel"""
        while child := self.box_main_panes.get_first_child():
            self.ctxbox_main_panes.remove(child)
        # get stacks for position
        stacks = self.get_stack_for_position(position)
        # if not stacks:
        #     # add placeholder text
        #     label = Gtk.Label()
        #     label.set_text("no stacks available")
        #     label.set_halign(Gtk.Align.START)
        #     self.box_switchers.append(label)
        #     return
        # add switchers to panel
        for stack_name, stack in stacks.items():
            # label
            label = Gtk.Label()
            label.set_text(stack_name)
            label.set_halign(Gtk.Align.START)
            label.add_css_class("heading-small")
            self.ctxbox_main_panes.append(label)
            # create and add switcher
            switcher = Gtk.StackSwitcher()
            switcher.set_stack(stack)
            self.ctxbox_main_panes.append(switcher)
            # add separator
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            self.ctxbox_main_panes.append(separator)

    def add_page(self, widget, name, title=None):
        """add new page to pane"""
        self.add_titled(widget, name, title)
