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
        # add styling
        self.add_css_class("no-border")
        self.set_tab_pos(Gtk.PositionType.TOP)
        self.set_scrollable(True)
        self.table_pages = {}
        self._positions = {}

    def update_data(self, positions):
        """update positions on event data change"""
        if "event" in positions:
            # store current
            current_page = self.get_current_page()
            event = positions["event"]
            self.table_pages[event] = positions
            # rebuild tables with data changed
            pages_to_remove = []
            for i in range(self.get_n_pages()):
                page_label = self.get_tab_label_text(self.get_nth_page(i))
                if page_label.startswith(event):
                    pages_to_remove.append(i)
            for i in reversed(pages_to_remove):
                self.remove_page(i)
            # get objects positions
            event_positions = {
                k: v
                for k, v in positions.items()
                if k != "event" and isinstance(k, str) and k.isdigit()
            }
            if event_positions:
                grid = self.make_table_grid(event_positions)
                label = Gtk.Label(label=f"{event} grid")
                label.set_tooltip_text(
                    "select this tab to access right-click context menu"
                )
                self.append_page(grid, label)
                label = Gtk.Label(label=f"{event} text")
                label.set_tooltip_text(
                    "select grid tab to access right-click context menu"
                )
                text = self.make_table_text(event_positions)
                self.append_page(text, label)
            # set focus to updated event page
            self.set_current_page(current_page)

    def make_table_grid(self, pos_dict):
        """create grid with positions data"""
        # scrolled window for overflowing cells
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        # grid as table with cells
        grid = Gtk.Grid()
        # set styling
        grid.add_css_class("table-grid")
        fields = [
            "name",
            "lat",
            "lon",
            "dist",
            # "lat speed",
            # "lon speed",
            # "dist speed",
        ]
        # add header
        for j, field in enumerate(fields):
            label = Gtk.Label(label=field, xalign=1.0)
            label.add_css_class("table-grid-header")
            grid.attach(label, j, 0, 1, 1)
        # add data rows
        for i, obj in enumerate(pos_dict.values(), 1):
            for j, key in enumerate(fields):
                value = obj.get(key, "")
                if isinstance(value, float):
                    value = f"{value:.3f}"
                label = Gtk.Label(label=str(value), xalign=1.0)
                grid.attach(label, j, i, 1, 1)
        scroll.set_child(grid)
        return scroll

    def make_table_text(self, pos_dict):
        """create text with positions data"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(False)
        scroll.set_vexpand(True)

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.add_css_class("table-text")
        buffer = text_view.get_buffer()

        text_line = "-" * 30 + "\n"
        text = text_line
        text += " positions :\n"
        # header row
        text += " name | lat       | lon\n"
        for _, obj in pos_dict.items():
            text += f" {obj['name']:4} "
            text += f" {obj.get('lat', 0):10.6f} "
            text += f" {obj.get('lon', 0):11.6f}\n"
        text += text_line
        buffer.set_text(text)
        scroll.set_child(text_view)
        return scroll


def draw_tables():
    """factory function to create tables widget"""
    return TablesWidget()


def update_tables(positions=None):
    """get object positions for tables"""
    # get main window reference
    _app = Gtk.Application.get_default()
    _notify = _app.notify_manager
    if positions is None:
        _notify.debug(
            f"received none positions : {positions} : exiting ...",
            source="panetables",
            route=["terminal"],
        )
        return
    if _app and _app.props.active_window:
        win = _app.props.active_window
        if hasattr(win, "tables"):
            # update all pane widgets with new data
            for table in win.tables.values():
                table.update_data(positions)
                # # solving tables not showing todo delete
                # # get parent stack
                # stack = table.get_parent()
                # if stack:
                #     # show tables page
                #     stack.set_visible_child(table)
