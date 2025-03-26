# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Dict
from ui.collapsepanel import CollapsePanel
from ui.helpers import _create_icon


PANE_BUTTONS: Dict[str, str] = {
    "settings": "settings",
    "file_save": "save file",
    "file_load": "load file",
}


def setup_tools(manager) -> CollapsePanel:
    """setup widget for tools buttons, ie save & load file"""
    clp_tools = CollapsePanel(title="tools", expanded=False)
    clp_tools.set_margin_end(manager.margin_end)
    clp_tools.set_title_tooltip("""buttons for file load & save etc""")

    box_tools = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

    for button_name, tooltip in PANE_BUTTONS.items():
        button = Gtk.Button()
        button.add_css_class("button-pane")
        button.set_tooltip_text(tooltip)
        # get proper icon
        icon = _create_icon(
            manager,
            "ui/imgs/icons/hicolor/scalable/sidepane/",
            f"{button_name}.svg",
        )
        icon.set_icon_size(Gtk.IconSize.NORMAL)
        button.set_child(icon)

        callback_name = f"obc_{button_name}"
        if hasattr(manager, callback_name):
            callback = getattr(manager, callback_name)
            button.connect("clicked", callback, button_name)
        else:
            button.connect("clicked", manager.obc_default, button_name)

        box_tools.append(button)

    clp_tools.add_widget(box_tools)

    return clp_tools
