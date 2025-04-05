# contextmanager.py
# ruff: noqa: E402
from typing import Any, Dict
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
        if not parent or parent not in self.overlays:
            return
        # todo redesign create_popover_menu()
        pop_ctx, box_ctx = self.create_popover_menu(parent)
        # pop_ctx, box_ctx = self.create_popover_menu(parent)

        # create pane buttons
        for button in _buttons_from_dict(
            self,
            buttons_dict=self.TOOLS_BUTTONS,
            icons_path="sidepane",
            pop_context=True,
            pos=self.overlays[parent],
        ):
            box_ctx.append(button)
            self.ctxclp_tools.append(box_ctx)
            # self.ctxbox_tools.append(button)

        rect = Gdk.Rectangle()
        rect.x = int(x + 30)
        rect.y = int(y)
        rect.width = 1
        rect.height = 1

        pop_ctx.set_parent(parent)
        pop_ctx.set_pointing_to(rect)
        pop_ctx.set_position(Gtk.PositionType.BOTTOM)
        pop_ctx.set_autohide(True)
        pop_ctx.set_has_arrow(False)

        pop_ctx.popup()

    def create_popover_menu(self, parent) -> tuple[Gtk.Popover, Gtk.Box]:
        """create popover menu with proper setup"""
        pop_ctx = Gtk.Popover(parent)
        box_ctx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_ctx.set_margin_start(4)
        box_ctx.set_margin_end(4)
        box_ctx.set_margin_top(4)
        box_ctx.set_margin_bottom(4)
        indent_pnl = 0
        spacing_box = 4
        # collapsible panel(s) : stack switchers on top
        self.ctxclp_main_panes = CollapsePanel(
            title="main panes", expanded=False, indent=indent_pnl
        )
        # box for switchers
        self.ctxbox_main_panes = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=spacing_box
        )
        self.ctxclp_main_panes.append(self.ctxbox_main_panes)
        box_ctx.append(self.ctxbox_main_panes)
        # tool buttons
        self.ctxclp_tools = CollapsePanel(
            title="tools", expanded=False, indent=indent_pnl
        )
        self.ctxbox_tools = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing_box
        )
        self.ctxclp_tools.append(self.ctxbox_tools)
        box_ctx.append(self.ctxclp_tools)

        pop_ctx.set_child(box_ctx)

        return pop_ctx, box_ctx

    def handle_context_action(
        self, button: Gtk.Button, action: str, position: str
    ) -> None:
        """handle pane actions (with position context)"""
        callback_name = f"obc_{action}"
        if hasattr(self, callback_name):
            callback = getattr(self, callback_name)
            # print(f"{action} triggered from {position}")
            callback(button, f"{action}_{position}")

    def get_stack_for_position(self, position: str) -> Dict[str, Gtk.Stack]:
        """get stacks for specific position"""
        # implement this method
        stacks = {}
        # example implementation
        if hasattr(self, f"stacks_{position}"):
            stacks = getattr(self, f"stacks_{position}")
        return stacks

    # # widget hierarchy
    # current = picked
    # while current:
    #     # print(f"current hierarchy : {typeqcurrent).__name__}")
    #     print(f"current hierarchy : {current.__class__.__name__}")
    #     current = current.get_parent()
    # button.set_tooltip_text(f"parent : {self.overlays[parent]}\n{tooltip}")
