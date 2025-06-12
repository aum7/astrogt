# ui/mainpanes/panetables.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from swisseph import contrib as swh
from typing import Tuple


class TablesWidget(Gtk.Notebook):
    """custom widget for displaying tables of data"""

    def __init__(self):
        super().__init__()
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        # add styling
        self.add_css_class("no-border")
        self.set_tab_pos(Gtk.PositionType.TOP)
        self.set_scrollable(True)
        self.table_pages = {}
        self.mrg = 9
        # event data storage
        self.events_data = {}
        # connect to signals
        signal = self.app.signal_manager
        signal._connect("positions_changed", self.positions_changed)
        signal._connect("houses_changed", self.houses_changed)
        signal._connect("e2_cleared", self.e2_cleared)

    def positions_changed(self, event, positions_data):
        # callback for signal
        if event not in self.events_data:
            self.events_data[event] = {
                "event": event,
                "positions": None,
                "houses": None,
            }
        self.events_data[event]["positions"] = positions_data
        self.update_data(self.events_data[event])

    def houses_changed(self, event, houses_data):
        # callback for signal
        if event not in self.events_data:
            self.events_data[event] = {
                "event": event,
                "positions": None,
                "houses": None,
            }
        self.events_data[event]["houses"] = houses_data
        self.update_data(self.events_data[event])

    def e2_cleared(self, event):
        # callback
        if event == "e2":
            if event in self.events_data:
                # remove tab if exists
                for i in range(self.get_n_pages()):
                    page = self.get_nth_page(i)
                    label = self.get_tab_label_text(page)
                    if label.strip() == event:
                        self.remove_page(i)
                        break
                # remove e2 from data storage
                del self.events_data[event]
                if event in self.table_pages:
                    del self.table_pages[event]
                self.notify.info(
                    f"cleared table for {event}",
                    source="panetables",
                    route=["terminal", "user"],
                )

    def update_data(self, data):
        """update positions on event data change"""
        if "event" not in data:
            return
        event = data["event"]
        self.table_pages[event] = data
        existing_page = None
        for i in range(self.get_n_pages()):
            page_label = self.get_tab_label_text(self.get_nth_page(i))
            if page_label.strip() == f"{event}":
                existing_page = self.get_nth_page(i)
                break
        # get positions & houses
        pos_dict = data.get("positions", {})
        houses_data = data.get("houses", None)
        # debug
        if houses_data is None:
            self.notify.debug(
                f"updatedata : housesdata : {houses_data}",
                source="panetables",
                route=["none"],
            )
            return
        try:
            cusps, ascmc = houses_data
        except Exception as e:
            self.notify.error(
                f"housesdata for {event} failed\n\terror : {e}",
                source="panetables",
                route=["terminal"],
            )
            return
        if pos_dict:
            if existing_page:
                scroll = existing_page
                text_view = scroll.get_child()
                if isinstance(text_view, Gtk.TextView):
                    buffer = text_view.get_buffer()
                    text = self.make_table_content(pos_dict, cusps, ascmc)
                    buffer.set_text(text)
            else:
                # create new page if missing
                label = Gtk.Label(label=f"  {event}")
                label.set_tooltip_text("right-click tab to access context menu")
                text = self.make_table(pos_dict, cusps, ascmc)
                self.append_page(text, label)
                self.set_current_page(-1)

    def make_table_content(self, pos_dict, cusps, ascmc):
        """create text content for positions & houses"""
        if ascmc:
            ascendant = ascmc[0]
            midheaven = ascmc[1]
        self.notify.debug(
            f"maketablecontent :\n\tcusps : {cusps} | type : {type(cusps)}\n\tascmc : {ascmc} | type : {type(ascmc)}",
            source="panetables",
            route=["none"],
        )
        # dashes : u2014 full width ; u2012 monospace-specific ; u2015 longer
        # u2017 double bottom u2502 vertical full
        n_chars = 37
        v_ = "\u01ef"  # victormonolightastro
        h_ = "\u01ee"  # victormonolightastro
        vic_spc = "\u01ac"  # custom [space] to match glyphs (582 font width)
        asc = "\u01bf"
        mc = "\u01c1"
        line = f"{h_ * n_chars}\n"
        # text to display in tables
        text = f" positions {h_ * 29}\n"
        # header row
        text += f" name {v_}      sign {vic_spc} {v_}       lat {v_}        lon {v_} house\n"
        for key, obj in pos_dict.items():
            if key == "event":
                continue
            # print(f"{obj['name']} : {obj.get('lon speed')}")
            retro = "R" if obj.get("lon speed") < 0 else " "
            # objects
            text += f" {obj['name']}{retro}  {v_}"
            text += f" {self.format_dms(obj.get('lon')):10} {v_}"
            text += f"{obj.get('lat', 0):10.6f} {v_}"
            text += f"{obj.get('lon', 0):11.6f}"
            # text += f"{obj.get('lon speed', 0):11.6f}"
            text += f"{self.which_house(obj.get('lon'), cusps)}\n"
        text += line
        # add houses below objects positions
        text += f" houses {h_ * 7}\n"
        # header row
        text += f"    {v_}      cusp\n"
        for i, cusp in enumerate(cusps, 1):
            # add cusp degree : lon > sign
            text += f" {i:2d} {v_} {self.format_dms(cusp):20}\n"
        text += f" cross points {h_ * 3}\n"
        text += f" {asc} :  {self.format_dms(ascendant)}\n"
        text += f" {mc} :  {self.format_dms(midheaven)}\n"
        text += line
        return text

    def make_table(self, pos_dict, cusps, ascmc):
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
        text = self.make_table_content(pos_dict, cusps, ascmc)
        buffer.set_text(text)
        scroll.set_child(text_view)
        return scroll

    def which_house(self, lon: float, cusps: Tuple[float, ...]) -> str:
        """find house number for given celestial longitude"""
        v_ = "\u01ef"  # victormonolightastro
        if not cusps:
            return ""
        for i in range(len(cusps) - 1):
            if cusps[i] <= lon < cusps[i + 1]:
                return f" {v_} {i + 1:2d}"
        # check for wrap around house 12 to 1
        if lon >= cusps[-1] or lon < cusps[0]:
            return f" {v_} 12"
        return ""

    def format_dms(self, lon: float) -> str:
        deg, sign, min, sec = swh.degsplit(lon)
        signs = [
            "\u0192",  # 01 aries
            "\u0193",
            "\u0194",
            "\u0195",
            "\u0196",
            "\u0197",
            "\u0198",
            "\u0199",
            "\u019a",
            "\u019b",
            "\u019c",
            "\u019d",  # 12 pisces
        ]
        return f"{deg:2d}°{min:02d}'{sec:02d}\" {signs[sign]}"


def draw_tables():
    """factory function to create tables widget"""
    return TablesWidget()


def update_tables(data=None):
    """update object positions & houses"""
    # get main window reference
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    if data is None:
        notify.debug(
            "received no data : exiting ...",
            source="panetables",
            route=["terminal"],
        )
        return
    if app and app.props.active_window:
        win = app.props.active_window
        if hasattr(win, "tables"):
            # update all pane widgets with new data
            for table in win.tables.values():
                table.update_data(data)
