# ui/mainpanes/panemanager.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Dict  # Callable


class PanesManager(Gtk.Stack):
    """mixin class for main panes & stack management"""

    # type hints for inherited attributes
    stack: Gtk.Stack
    STACK_BUTTONS: Dict[str, str] = {
        "astro": "astrology chart",
        "tables": "tables & editor etc",
        # "editor": "text editor",
        # "graph": "data graph",
    }

    def __init__(self, stack_manager=None, position=None, name=None):
        super().__init__()
        # track stacks per position
        self.pane_stacks = {
            "top-left": None,
            "top-right": None,
            "bottom-left": None,
            "bottom-right": None,
        }

    def add_switcher(self, position: str, box: Gtk.Box) -> None:
        """add stack switcher for current pane to menu"""
        # get stack for current pane position
        stack = self.get_stack(position)
        if not stack:
            # show placeholder
            label = Gtk.Label()
            label.set_text("no stack available")
            label.set_halign(Gtk.Align.START)
            box.append(label)
            return
        # create & add stack switcher
        switcher = Gtk.StackSwitcher()
        switcher.set_stack(stack)
        switcher.set_halign(Gtk.Align.START)
        # set icons
        keys = list(self.STACK_BUTTONS.keys())
        i = 0
        child = switcher.get_first_child()
        while child and i < len(keys):
            # print(f"key : {keys[i]}")
            key = keys[i]
            icon_path = f"ui/imgs/icons/hicolor/scalable/stack/{key}.svg"
            icon = Gtk.Image.new_from_file(icon_path)
            icon.set_tooltip_text(self.STACK_BUTTONS[key])
            icon.set_pixel_size(22)
            child.set_child(icon)
            child = child.get_next_sibling()
            i += 1
        box.append(switcher)

    def setup_stacks(self, position: str) -> Gtk.Stack:
        """create & setup stack for given position"""
        if position not in self.pane_stacks:
            return None
        # needed as separate instances
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.NONE)
        stack.set_transition_duration(0)
        # store stack for position
        self.pane_stacks[position] = stack
        return stack

    def get_stack(self, position: str) -> Gtk.Stack:
        """get stack by position"""
        return self.pane_stacks.get(position)
