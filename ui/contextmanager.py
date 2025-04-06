# contextmanager.py
# ruff: noqa: E402
from typing import Any, Dict, Callable
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk  # type: ignore
from ui.collapsepanel import CollapsePanel
from ui.helpers import _buttons_from_dict


class ContextManager:
    """mixin class for right-click context menu management"""

    # type hints for inherited attributes
    rvl_side_pane: Gtk.Revealer
    get_stack: Callable
    ovl_tl: Gtk.Overlay
    ovl_tr: Gtk.Overlay
    ovl_bl: Gtk.Overlay
    ovl_br: Gtk.Overlay
    TOOLS_BUTTONS: Dict[str, str]

    def setup_context_controllers(self) -> None:
        """setup right-click context menu / controllers for panes"""
        # 4 panes = 4 overlays
        self.overlays = {
            self.ovl_tl: "top-left",
            self.ovl_tr: "top-right",
            self.ovl_bl: "bottom-left",
            self.ovl_br: "bottom-right",
        }
        for overlay in self.overlays:
            context_controller = Gtk.GestureClick()
            context_controller.set_button(3)  # r-click
            context_controller.connect("begin", self.on_gesture_begin)
            context_controller.connect("pressed", self.on_context_menu)
            overlay.add_controller(context_controller)

    def on_gesture_begin(self, gesture: Gtk.GestureClick, sequence: Any) -> None:
        """handle gesture begin to prevent drag"""
        # mouse drag gives gtk.error
        # Gtk-WARNING **: 19:02:06.608: Broken accounting of active state for widget 0x20de5cb0(GtkPopover)
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def on_context_menu(
        self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        """handle right-click context menu events"""
        widget = gesture.get_widget()
        if not widget:
            return
        # print(f"x : {x} | y : {y}")
        picked = widget.pick(x, y, Gtk.PickFlags.DEFAULT)
        if not picked:
            return
        parent = picked.get_parent()
        grandparent = parent.get_parent()
        # if not parent:
        # if not parent or parent not in self.overlays:
        if not grandparent or grandparent not in self.overlays:
            return
        # get position of clicked overlay
        pos = self.overlays[grandparent]
        # crate popover todo redesign create_popover_menu()
        pop_ctx, _ = self.create_popover_menu()
        # add stack switcher for current pane
        self.add_switcher(pos, self.ctxbox_stack)
        # create pane buttons
        for button in _buttons_from_dict(
            self,
            buttons_dict=self.TOOLS_BUTTONS,
            icons_path="tools/",
            pop_context=True,
            pos=self.overlays[grandparent],
        ):
            self.ctxbox_tools.append(button)

        rect = Gdk.Rectangle()
        rect.x = int(x + 30)
        rect.y = int(y)
        rect.width = 1
        rect.height = 1

        pop_ctx.set_parent(grandparent)
        pop_ctx.set_pointing_to(rect)
        pop_ctx.set_position(Gtk.PositionType.BOTTOM)
        pop_ctx.set_autohide(True)
        pop_ctx.set_has_arrow(True)

        pop_ctx.popup()

    def create_popover_menu(self) -> tuple[Gtk.Popover, Gtk.Box]:
        """create popover menu with proper setup"""
        pop_ctx = Gtk.Popover()
        box_ctx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_ctx.set_margin_start(4)
        box_ctx.set_margin_end(4)
        box_ctx.set_margin_top(4)
        box_ctx.set_margin_bottom(4)
        indent_pnl = 0
        spacing_box = 4
        # collapsible panel(s) : stack switchers on top
        self.ctxclp_stack = CollapsePanel(
            title="panes", expanded=True, indent=indent_pnl
        )
        # box for switchers
        self.ctxbox_stack = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=spacing_box
        )
        self.ctxclp_stack.add_widget(self.ctxbox_stack)
        box_ctx.append(self.ctxclp_stack)
        # tool buttons
        self.ctxclp_tools = CollapsePanel(
            title="tools", expanded=False, indent=indent_pnl
        )
        self.ctxbox_tools = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing_box
        )
        self.ctxclp_tools.add_widget(self.ctxbox_tools)
        box_ctx.append(self.ctxclp_tools)

        pop_ctx.set_child(box_ctx)

        return pop_ctx, box_ctx

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
        box.append(switcher)

    def update_switchers(self, position: str) -> None:
        """update stack switchers in context menu for current pane"""
        # clear existing content
        if hasattr(self, "ctxbox_stack"):
            while child := self.ctxbox_stack.get_first_child():
                self.ctxbox_stack.remove(child)
            # get stacks for position
            stack = self.get_stack(position)
            if not stack:
                # show placeholder
                label = Gtk.Label()
                label.set_text("no stacks available")
                label.set_halign(Gtk.Align.START)
                self.ctxbox_stack.append()
                return
            # create & add stack switchers
            switcher = Gtk.StackSwitcher()
            switcher.set_stack(stack)
            switcher.set_halign(Gtk.Align.START)
            self.ctxbox_stack.append(switcher)

    def get_stack_for_position(self, position: str) -> Dict[str, Gtk.Stack]:
        """get stacks for specific position"""
        # implement this method
        stacks = {}
        # example implementation
        if hasattr(self, f"stacks_{position}"):
            stacks = getattr(self, f"stacks_{position}")
        return stacks

    def handle_context_action(
        self, button: Gtk.Button, action: str, position: str
    ) -> None:
        """handle pane actions (with position context)"""
        callback_name = f"obc_{action}"
        if hasattr(self, callback_name):
            callback = getattr(self, callback_name)
            # print(f"{action} triggered from {position}")
            callback(button, f"{action}_{position}")

    # # widget hierarchy
    # current = picked
    # while current:
    #     # print(f"current hierarchy : {typeqcurrent).__name__}")
    #     print(f"current hierarchy : {current.__class__.__name__}")
    #     current = current.get_parent()
    # button.set_tooltip_text(f"parent : {self.overlays[parent]}\n{tooltip}")
