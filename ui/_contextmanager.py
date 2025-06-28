# ui/contextmanager.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk  # type: ignore
from typing import Dict, Callable
from ui.collapsepanel import CollapsePanel
from ui.helpers import _buttons_from_dict


class ContextManager:
    """mixin class for right-click context menu management"""

    # type hints for inherited attributes
    rvl_side_pane: Gtk.Revealer
    notify: Callable
    frm_top_left: Gtk.Frame
    frm_top_right: Gtk.Frame
    frm_bottom_left: Gtk.Frame
    frm_bottom_right: Gtk.Frame
    TOOLS_BUTTONS: Dict[str, str]

    def setup_context_controllers(self) -> None:
        """setup right-click context menu / controllers for panes"""
        # 4 panes = 4 gtk.frame
        self.frames = {
            self.frm_top_left: "top-left",
            self.frm_top_right: "top-right",
            self.frm_bottom_left: "bottom-left",
            self.frm_bottom_right: "bottom-right",
        }
        for frame in self.frames:
            context_controller = Gtk.GestureClick()
            context_controller.set_button(3)  # r-click
            # context_controller.connect("begin", self.on_gesture_begin)
            context_controller.connect("pressed", self.on_context_menu)
            frame.add_controller(context_controller)

    # def on_gesture_begin(self, gesture: Gtk.GestureClick, sequence: Any) -> None:
    #     """handle gesture begin to prevent drag"""
    # mouse drag gives gtk.error todo below solution not working
    # Gtk-WARNING **: 19:02:06.608: Broken accounting of active state for widget 0x20de5cb0(GtkPopover)
    # gesture.set_state(Gtk.EventSequenceState.CLAIMED)

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
        # traverse up till gtk.frame = main widget for custom widgets
        current = picked
        while current:
            parent = current.get_parent()
            if not parent:
                break
            if parent in self.frames:
                # frame found : get position of clicked overlay
                # pos = self.frames[parent]
                # crate popover todo redesign create_popover_menu()
                pop_ctx, _ = self.create_popover_menu()
                # create pane buttons
                for button in _buttons_from_dict(
                    self,
                    buttons_dict=self.TOOLS_BUTTONS,
                    icons_path="tools/",
                    pop_context=True,
                    pos=self.frames[parent],
                ):
                    self.ctxbox_tools.append(button)

                # rectangle for anchoring popover
                rect = Gdk.Rectangle()
                rect.x = int(x)
                rect.y = int(y)
                rect.width = 1
                rect.height = 1

                pop_ctx.set_parent(parent)
                pop_ctx.set_pointing_to(rect)
                pop_ctx.set_position(Gtk.PositionType.BOTTOM)
                pop_ctx.set_autohide(True)
                pop_ctx.set_has_arrow(True)

                pop_ctx.popup()
                return
            current = parent
        self.notify.error(
            "frame container not found",
            source="contextmanager",
            route=["terminal"],
        )

    def create_popover_menu(self) -> tuple[Gtk.Popover, Gtk.Box]:
        """create popover menu with proper setup"""
        pop_ctx = Gtk.Popover()
        # main box for popover content
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
            title="tools", expanded=True, indent=indent_pnl
        )
        self.ctxbox_tools = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing_box
        )
        self.ctxclp_tools.add_widget(self.ctxbox_tools)
        box_ctx.append(self.ctxclp_tools)

        pop_ctx.set_child(box_ctx)
        # todo resize popover dynamically
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
