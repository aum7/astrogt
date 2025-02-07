from typing import Any, Dict
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk


class WindowHandlers:
    """mixin class for window event handlers.
    note: this class is intended to be used with gtk.applicationwindow
    and should not be instantiated directly.
    """

    # type hints for inherited attributes
    rvl_side_pane: Gtk.Revealer
    ovl_tl: Gtk.Overlay
    ovl_tr: Gtk.Overlay
    ovl_bl: Gtk.Overlay
    ovl_br: Gtk.Overlay
    PANE_BUTTONS: Dict[str, str]

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

        pop_ctx, box_ctx = self.create_popover_menu()

        for button_name, tooltip in self.PANE_BUTTONS.items():
            button = Gtk.Button()
            button.add_css_class("button-pane")
            button.set_tooltip_text(f"{tooltip}")

            icon = Gtk.Image.new_from_file(
                f"imgs/icons/pane/{button_name}.svg",
            )
            icon.set_icon_size(Gtk.IconSize.NORMAL)
            button.set_child(icon)

            callback_name = f"obc_{button_name}"
            if hasattr(self, callback_name):
                callback = getattr(self, callback_name)
                button.connect(
                    "clicked",
                    lambda btn, name=button_name, pos=self.overlays[
                        parent
                    ]: self.handle_context_action(
                        btn,
                        name,
                        pos,
                    ),
                )
            box_ctx.append(button)

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

    def create_popover_menu(self) -> tuple[Gtk.Popover, Gtk.Box]:
        """create popover menu with proper setup"""
        pop_ctx = Gtk.Popover()

        box_ctx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_ctx.set_margin_start(4)
        box_ctx.set_margin_end(4)
        box_ctx.set_margin_top(4)
        box_ctx.set_margin_bottom(4)

        pop_ctx.set_child(box_ctx)

        return pop_ctx, box_ctx

    def handle_context_action(
        self, button: Gtk.Button, action: str, position: str
    ) -> None:
        """handle pane actions (with position context)"""
        callback_name = f"obc_{action}"
        if hasattr(self, callback_name):
            callback = getattr(self, callback_name)
            print(f"{action} triggered from {position}")
            callback(button, f"{action}_{position}")

    def on_toggle_pane(self, button):
        revealed = self.rvl_side_pane.get_child_revealed()
        if revealed:
            self.rvl_side_pane.set_reveal_child(False)
            self.rvl_side_pane.set_visible(False)
        else:
            self.rvl_side_pane.set_visible(True)
            self.rvl_side_pane.set_reveal_child(True)

        # # widget hierarchy
        # current = picked
        # while current:
        #     # print(f"current hierarchy : {type(current).__name__}")
        #     print(f"current hierarchy : {current.__class__.__name__}")
        #     current = current.get_parent()
        # button.set_tooltip_text(f"parent : {self.overlays[parent]}\n{tooltip}")
