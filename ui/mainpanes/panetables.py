# ui/mainpanes/panetables.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


def pane_tables(positions=None, _notify=None):
    """get object positions for tables"""
    if positions is None:
        positions = {}
    if _notify:
        _notify.debug(
            f"received positions : {positions}",
            source="panetables",
            route=["none"],
        )
    # store positions
    pane_tables._positions = positions
    return draw_tables()


def draw_tables():
    """draw tables previously calculated in pane_tables"""
    notebook = Gtk.Notebook()
    notebook.set_tab_pos(Gtk.PositionType.LEFT)
    notebook.set_scrollable(True)
    positions = getattr(pane_tables, "_positions", {})

    def make_table(pos_dict):
        """setup positions into presentable text"""
        text = ""
        for code, obj in pos_dict.items():
            text += f"{code} : {obj}\n"
        print(text)
        return Gtk.Label(label=text)
        # return Gtk.Label(label=text, xalign=0)
        # print(f"panetables : maketable positions dict :\n\t{pos_dict}")
        # grid = Gtk.Grid()
        # grid.set_column_spacing(8)
        # grid.set_row_spacing(4)
        # fields = [
        #     "name",
        #     "lat",
        #     "lon",
        #     "dist",
        #     "lat speed",
        #     "lon speed",
        #     "dist speed",
        # ]
        # for i, obj in enumerate(pos_dict.values(), 1):
        #     print(f"panetables : obj : {obj}")
        #     for j, key in enumerate(fields):
        #         value = obj.get(key)
        #         if isinstance(value, float):
        #             value = round(value, 3)
        #         # grid.attach(Gtk.Label(label=str(value)), j, i, 1, 1)
        #         grid.attach(Gtk.Label(label=str(value), xalign=0), j, i, 1, 1)
        # return grid

    if "event" in positions:
        # lbl_event = positions["event"]
        lbl_event = str(positions["event"])
        event_positions = {k: v for k, v in positions.items() if isinstance(k, int)}
        # print(f"panetables : event-positions\n\t{event_positions}")
        if event_positions:
            widget = make_table(event_positions)
            page = notebook.append_page(widget, Gtk.Label(label=lbl_event))
            print(f"page : {page}")
    return notebook
