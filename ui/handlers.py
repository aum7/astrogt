from typing import Dict, Any
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

    def on_context_menu(
        self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        """handle context menu events"""
        if gesture.get_current_button() == 3:
            """mouse right-click : context menu"""
            # print(f"mouse x : {x} | mouse y : {y}")
            # print("r-click")
            widget = gesture.get_widget()
            if widget is None:
                print("widget none")
                return
            root = widget.get_root()
            if root is None:
                print("root none")
                return
            # print(f"root type : {type(root)}")
            # print(f"root class name : {root.__class__.__name__}")

            print(f"x : {x} | y : {y}")
            # picked = root.pick(x, y, Gtk.PickFlags.DEFAULT)
            picked = widget.pick(x, y, Gtk.PickFlags.DEFAULT)
            if picked is None:
                print("picked none")
                return

            print(f"picked : {picked.__class__.__name__}")
            parent = picked.get_parent()
            if parent:
                print(f"picked parent : {parent.__class__.__name__}")

            # Reference overlays through the main window instance
            overlay_name = None
            if isinstance(parent, Gtk.Overlay):
                if parent == self.ovl_tl:
                    pop_ctx_tl = Gtk.PopoverMenu()
                    box_ctx_tl = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                    pop_ctx_tl.set_child(box_ctx_tl)
                    # PANE_BUTTONS items : todo: reuse / set all buttons
                    # in 1 place
                    PANE_BUTTONS: Dict[str, str] = {
                        "settings": "settings",
                        "event_one": "data & focus to event 1",
                        "event_two": "data & focus to event 2",
                        "file_save": "save file",
                        "file_load": "load file",
                    }
                    for button_name, tooltip in PANE_BUTTONS.items():
                        button = Gtk.Button()
                        button.add_css_class("button-pane")
                        button.set_tooltip_text(tooltip)

                        icon = Gtk.Image.new_from_file(
                            f"imgs/icons/pane/{button_name}.svg"
                        )
                        icon.set_icon_size(Gtk.IconSize.LARGE)
                        button.set_child(icon)

                        callback_name = f"obc_{button_name}"
                        if hasattr(self, callback_name):
                            callback = getattr(self, callback_name)
                            button.connect(
                                "clicked",
                                lambda btn, name=button_name: callback(btn, name),
                            )
                        else:
                            print("default callback for {button_name}")
                        box_ctx_tl.append(button)

                    pop_ctx_tl.set_parent(self.ovl_tl)
                    # pop_ctx_tl.set_offset(int(x), int(y))
                    pop_ctx_tl.set_offset(0, 0)
                    pop_ctx_tl.set_autohide(True)
                    pop_ctx_tl.set_has_arrow(True)
                    pop_ctx_tl.set_child_visible(True)
                    pop_ctx_tl.popup()

                elif parent == self.ovl_tr:
                    overlay_name = "ovl top right"
                elif parent == self.ovl_bl:
                    overlay_name = "ovl bottom left"
                elif parent == self.ovl_br:
                    overlay_name = "ovl bottom right"
            if overlay_name is not None:
                print(f"overlay : {overlay_name}")

    def on_toggle_pane(self, button):
        revealed = self.rvl_side_pane.get_child_revealed()
        if revealed:
            self.rvl_side_pane.set_reveal_child(False)
            self.rvl_side_pane.set_visible(False)
        else:
            self.rvl_side_pane.set_visible(True)
            self.rvl_side_pane.set_reveal_child(True)
