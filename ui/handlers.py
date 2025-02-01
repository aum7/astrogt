from typing import Any, Dict  # Callable, Any
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Graphene, Gtk


class WindowHandlers:
    """mixin class for window event handlers.
    note: this class is intended to be used with gtk.applicationwindow
    and should not be instantiated directly.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """ensure proper mixin initialization"""
        super().__init_subclass__(**kwargs)

    # type hints for inherited attributes
    rvl_side_pane: Gtk.Revealer
    ovl_tl: Gtk.Overlay
    ovl_tr: Gtk.Overlay
    ovl_bl: Gtk.Overlay
    ovl_br: Gtk.Overlay

    PANE_BUTTONS: Dict[str, str]

    # default r-click
    def on_context_menu_default(
        self,
        gesture: Gtk.GestureClick,
        n_press: int,
        x: float,
        y: float,
    ) -> None:
        """handle context menu other than top-left (astro chart)"""
        widget = gesture.get_widget()
        if not widget or gesture.get_current_button == 3:
            return
        print("context menu not top-left")
        # overlay_name = None
        # elif parent == self.ovl_tr:
        #     overlay_name = "ovl top right"
        # elif parent == self.ovl_bl:
        #     overlay_name = "ovl bottom left"
        # elif parent == self.ovl_br:
        #     overlay_name = "ovl bottom right"
        # if overlay_name is not None:
        #     print(f"overlay : {overlay_name}")

    def setup_click_ctrlr_tl(self) -> None:
        """setup top left right-click context menu / controller"""
        click_ctrlr_tl = Gtk.GestureClick()
        click_ctrlr_tl.set_button(3)  # r-click
        click_ctrlr_tl.connect(
            "pressed",
            self.on_context_menu,
        )
        # ovl_tl.add_controller(click_ctrlr_tl)
        self.ovl_tl.add_controller(click_ctrlr_tl)

    def on_context_menu(
        self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        """handle right-click context menu events"""
        widget = gesture.get_widget()
        if not widget:
            print("widget none")
            return
        print(f"widget : {widget.__class__.__name__}")
        # print(f"root class name : {root.__class__.__name__}")
        print(f"x : {x} | y : {y}")
        picked = widget.pick(x, y, Gtk.PickFlags.DEFAULT)
        if not picked:
            print("picked none")
            return
        print(f"picked : {picked.__class__.__name__}")
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)
        # # widget hierarchy
        # current = picked
        # while current:
        #     # print(f"current hierarchy : {type(current).__name__}")
        #     print(f"current hierarchy : {current.__class__.__name__}")
        #     current = current.get_parent()
        parent = picked.get_parent()
        print(f"parent : {parent.__class__.__name__ if parent else 'none'}")
        print(f"is parent self.ovl_tl ? {parent == self.ovl_tl}")
        if not parent or parent != self.ovl_tl:
            print("no parent or not overlay top-left")
            return
        print(f"parent : {parent.__class__.__name__}")
        # claim the event to prevent propagation
        # gesture.set_state(Gtk.EventSequenceState.CLAIMED)
        # reference overlays through the main window instance
        # if not isinstance(parent, Gtk.Overlay):
        #     return
        # if isinstance(parent, Gtk.Overlay):
        # if widget == self.ovl_tl:
        # if parent == self.ovl_tl:
        pop_ctx_tl = Gtk.PopoverMenu()
        box_ctx_tl = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        pop_ctx_tl.set_child(box_ctx_tl)
        # PANE_BUTTONS items : todo: reuse / set all buttons
        # in 1 place
        # PANE_BUTTONS: Dict[str, str] = {
        #     "settings": "settings",
        #     "event_one": "data & focus to event 1",
        #     "event_two": "data & focus to event 2",
        #     "file_save": "save file",
        #     "file_load": "load file",
        # }
        for button_name, tooltip in self.PANE_BUTTONS.items():
            button = Gtk.Button()
            button.add_css_class("button-pane")
            button.set_tooltip_text(tooltip)

            icon = Gtk.Image.new_from_file(f"imgs/icons/pane/{button_name}.svg")
            icon.set_icon_size(Gtk.IconSize.NORMAL)
            button.set_child(icon)

            callback_name = f"obc_{button_name}"
            if hasattr(self, callback_name):
                callback = getattr(self, callback_name)
                button.connect(
                    "clicked",
                    lambda btn, name=button_name: callback(
                        btn,
                        name,
                    ),
                )
            # else:
            box_ctx_tl.append(button)

        rect = Gdk.Rectangle()
        rect.x = int(x + 30)
        rect.y = int(y)
        rect.width = 1
        rect.height = 1
        pop_ctx_tl.set_parent(parent)
        # pop_ctx_tl.set_parent(widget)
        pop_ctx_tl.set_pointing_to(rect)
        pop_ctx_tl.set_position(Gtk.PositionType.BOTTOM)
        # pop_ctx_tl.set_offset(int(x), int(y))
        pop_ctx_tl.set_autohide(True)
        pop_ctx_tl.set_has_arrow(False)
        pop_ctx_tl.popup()

    def on_toggle_pane(self, button):
        revealed = self.rvl_side_pane.get_child_revealed()
        if revealed:
            self.rvl_side_pane.set_reveal_child(False)
            self.rvl_side_pane.set_visible(False)
        else:
            self.rvl_side_pane.set_visible(True)
            self.rvl_side_pane.set_reveal_child(True)
