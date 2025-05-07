# ui/mainpanes/panetables.py
# ruff: noqa: E402
# import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from swisseph import contrib as swh
from typing import Tuple
from sweph.calculations.houses import calculate_houses


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
        self.mrg = 9

    def update_data(self, positions):
        """update positions on event data change"""
        if "event" in positions:
            # store current
            current_page = self.get_current_page()
            event = positions["event"]
            self.table_pages[event] = positions
            # rebuild tables with data changed
            # e2_active = self._app.e2_active
            # print(f"panetables : datetime 2 active : {e2_active}")
            pages_to_remove = []
            for i in range(self.get_n_pages()):
                page_label = self.get_tab_label_text(self.get_nth_page(i))
                if page_label.startswith(event) or (
                    not self._app.e2_active and page_label.startswith("e2")
                ):
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
                # test grid : use text view with ultra-makeup as default
                # grid = self.make_table_grid(event_positions)
                # label = Gtk.Label(label=f"{event} grid")
                # label.set_tooltip_text("right-click tab to access context menu")
                # self.append_page(grid, label)
                # extra space = avoid sidepane toggle button
                label = Gtk.Label(label=f"  {event} text")
                label.set_tooltip_text("right-click tab to access context menu")
                text = self.make_table_text(event_positions)
                self.append_page(text, label)
            # set focus to updated event page
            self.set_current_page(current_page)

    def make_table_grid(self, pos_dict):
        """existing as test object : create grid with positions data"""
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
        """create text with positions & houses data"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(False)
        scroll.set_vexpand(True)

        text_view = Gtk.TextView()
        text_view.set_margin_top(self.mrg)
        text_view.set_margin_bottom(self.mrg)
        text_view.set_margin_start(self.mrg)
        text_view.set_margin_end(self.mrg)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.add_css_class("table-text")
        buffer = text_view.get_buffer()
        # get houses tuple
        houses = calculate_houses()
        cusps, _ = houses if houses else ((), ())
        # print(
        #     f"panetables : maketabletext : houses :\n\tcusps : {cusps}\n\tascmc : {ascmc}"
        # )
        # dashes : u2014 full width ; u2012 monospace-specific ; u2015 longer
        # u2017 double bottom
        n_chars = 53
        h_ = "\u2502"
        v_ = "\u2014"
        line = f"{v_ * n_chars}\n"

        # which house is object in
        def which_house(lon: float, cusps: Tuple[float, ...]) -> str:
            """find house number for given celestial longitude"""
            if not cusps:
                return ""
            for i in range(len(cusps) - 1):
                if cusps[i] <= lon < cusps[i + 1]:
                    return f" {h_} {i + 1:2d}"
            # check for wrap around house 12 to 1
            if lon >= cusps[-1] or lon < cusps[0]:
                return f" {h_} 12"
            return ""

        def format_dms(lon: float) -> str:
            deg, sign, min, sec = swh.degsplit(lon)
            signs = [
                "♈",
                "♉",
                "♊",
                "♋",
                "♌",
                "♍",
                "♎",
                "♏",
                "♐",
                "♑",
                "♒",
                "♓",
            ]
            return f"{deg:2d}°{min:02d}'{sec:02d}\" {signs[sign]}"

        # d_btm = "\u2017"
        # line_double = f"{d_btm * n_chars}\n"
        # text = line
        text = f" positions {v_ * 42}\n"
        # header row
        text += f" name {h_}         sign {h_}       lat {h_}        lon {h_} house\n"
        for _, obj in pos_dict.items():
            # objects
            text += f" {obj['name']:4} {h_}"
            # text += f" {swh.degsplit(obj.get('lon')):15.0f}"
            text += f" {format_dms(obj.get('lon')):10} {h_}"
            text += f"{obj.get('lat', 0):10.6f} {h_}"
            text += f"{obj.get('lon', 0):11.6f}"
            text += f"{which_house(obj.get('lon'), cusps)}\n"
        text += line
        # add houses below objects positions
        text += f" houses {v_ * 11}\n"
        # header row
        text += f"    {h_}         cusp\n"
        for i, cusp in enumerate(cusps, 1):
            # todo add cusp degree : lon > sign
            text += f" {i:2d} {h_} {format_dms(cusp):20}\n"
        text += line
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
