# ui/mainpanes/panetables.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


def tables(positions):
    """create a table of planetary positions"""
    # table = Gtk.Grid()
    table = Gtk.ListStore(str, str)
    for body, value in positions:
        table.append([body, f"{value:.6f}"])
    view = Gtk.TreeView(model=table)
    for idx, title in enumerate(("body", "value")):
        rend = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(title, rend, text=idx)
        view.append_column(col)
    scw_pos = Gtk.ScrolledWindow()
    scw_pos.set_child(view)
    return scw_pos
