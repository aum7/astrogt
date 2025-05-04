# ui/mainpanes/panetables.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class TablesWidget(Gtk.Notebook):
    """custom widget for displaying tables of data"""

    def __init__(self):
        super().__init__()
        self._app = Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        self.set_tab_pos(Gtk.PositionType.LEFT)
        self.set_scrollable(True)
        self._positions = {}

    def update_data(self, positions):
        """update positions on event data change"""
        self._positions = positions
        # remove existing pages
        while self.get_n_pages() > 0:
            self.remove_page(-1)
        # rebuild tables
        if "event" in positions:
            event_positions = {k: v for k, v in positions.items() if isinstance(k, int)}
            if event_positions:
                grid = self.make_table(event_positions)
                self.append_page(grid, Gtk.Label(label=str(positions["event"])))

    def make_table(self, pos_dict):
        """create grid with positions data"""
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(4)
        fields = [
            "name",
            "lat",
            "lon",
            "dist",
            "lat speed",
            "lon speed",
            "dist speed",
        ]
        # add header
        for j, field in enumerate(fields):
            grid.attach(Gtk.Label(label=field, xalign=0), j, 0, 1, 1)
        # add data rows
        for i, obj in enumerate(pos_dict.values(), 1):
            for j, key in enumerate(fields):
                value = obj.get(key, "")
                if isinstance(value, float):
                    value = f"{value:.3f}"
                grid.attach(Gtk.Label(label=str(value), xalign=0), j, i, 1, 1)
        return grid


def draw_tables():
    """factory function to create tables widget"""
    return TablesWidget()


def update_tables(positions=None):
    """get object positions for tables"""
    # get main window reference
    _app = Gtk.Application.get_default()
    _notify = _app.notify_manager
    if positions is None:
        positions = {}
    _notify.debug(
        f"received positions : {positions}",
        source="panetables",
        route=["none"],
    )
    if _app and _app.props.active_window:
        win = _app.props.active_window
        if hasattr(win, "tables"):
            # update all pane widgets with new data
            for table in win.tables.values():
                table.update_data(positions)
