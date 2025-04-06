# paneltools.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.collapsepanel import CollapsePanel
from ui.helpers import _buttons_from_dict


def setup_tools(manager) -> CollapsePanel:
    """setup widget for tools buttons, ie save & load file"""
    clp_tools = CollapsePanel(title="tools", expanded=False)
    clp_tools.set_margin_end(manager.margin_end)
    clp_tools.set_title_tooltip("""buttons for file load & save etc""")

    box_tools = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    # sidepane buttons (file_load etc)
    for button in _buttons_from_dict(
        manager, buttons_dict=manager.TOOLS_BUTTONS, icons_path="tools/"
    ):
        box_tools.append(button)

    clp_tools.add_widget(box_tools)

    return clp_tools
