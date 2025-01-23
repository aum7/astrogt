from typing import Dict, Any
import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SidePaneManager:
    """mixin class for managing the side pane
    note: this class is intended to be used with gtk.applicationwindow
    and should not be instantiated directly
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """ensure proper mixin init"""
        super().__init_subclass__(**kwargs)

    PANE_BUTTONS: Dict[str, str] = {
        "settings": "settings",
        "event_one": "data & focus to event 1",
        "event_two": "data & focus to event 2",
        "file_save": "save file",
        "file_load": "load file",
    }
    icons_folder: str
    icons_list: list[str]
    icon_size: Gtk.IconSize

    def init_side_pane(self) -> None:
        """initialize side pane properties"""
        self.icons_folder = "imgs/icons/pane/"
        self.icons_list = sorted(
            [f for f in os.listdir(self.icons_folder) if f.endswith(".svg")]
        )
        self.icon_size = Gtk.IconSize.LARGE

    def setup_side_pane(self):
        box_side_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        for button_name, tooltip in self.PANE_BUTTONS.items():
            button = Gtk.Button()
            button.add_css_class("button-pane")
            button.set_tooltip_text(tooltip)

            icon = self.create_pane_icon(f"{button_name}.svg")
            icon.set_icon_size(self.icon_size)
            button.set_child(icon)

            callback_name = f"obc_{button_name}"
            if hasattr(self, callback_name):
                callback = getattr(self, callback_name)
                button.connect(
                    "clicked",
                    lambda btn, name=button_name: callback(btn, name),
                )
            else:
                button.connect("clicked", self.obc_default, button_name)

            box_side_pane.append(button)

        return box_side_pane

    def create_pane_icon(self, icon_name):
        return Gtk.Image.new_from_file(f"{self.icons_folder}{icon_name}")

    # Button handlers
    def obc_default(self, widget, data):
        print(f"{data} clicked : obc_default()")

    def obc_settings(self, widget, data):
        print(f"{data} clicked")

    def obc_event_one(self, widget, data):
        print(f"{data} clicked")

    def obc_event_two(self, widget, data):
        print(f"{data} clicked")

    def obc_file_save(self, widget, data):
        print(f"{data} clicked")

    def obc_file_load(self, widget, data):
        print(f"{data} clicked")
