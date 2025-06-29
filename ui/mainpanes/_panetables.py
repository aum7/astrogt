# ui/mainpanes/_panetables.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Tuple
from swisseph import contrib as swh
from ui.fonts.glyphs import SIGNS


class TablesWidget(Gtk.Notebook):
    """custom widget for displaying tables of data"""

    def __init__(self):
        super().__init__()
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        # add styling
        self.add_css_class("no-border")
        # self.add_css_class("notebook")
        self.set_tab_pos(Gtk.PositionType.TOP)
        self.set_scrollable(True)
        self.table_pages = {}
        self.mrg = 9
        # event data storage
        self.events_data = {}
        # event aspects storage
        self.aspects_data = {}
        # connect to signals
        signal = self.app.signal_manager
        signal._connect("positions_changed", self.positions_changed)
        signal._connect("houses_changed", self.houses_changed)
        signal._connect("e2_cleared", self.e2_cleared)
        signal._connect("aspects_changed", self.aspects_changed)

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

    def aspects_changed(self, event, data):
        """update aspects list on positions change"""
        # print(f"panetables : received aspects : {aspects}")
        self.aspects_data[event] = data
        if event in self.events_data:
            self.update_data(self.events_data[event])

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
        # get available data
        pos_dict = data.get("positions", {})
        houses_data = data.get("houses", None)
        # aspects = data.get(event, [])
        aspects = self.aspects_data.get(event, [])
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
                    text = self.make_table_content(pos_dict, cusps, ascmc, aspects)
                    buffer.set_text(text)
            else:
                # create new page if missing
                label = Gtk.Label(label=f"  {event}")
                label.set_tooltip_text("right-click tab to access context menu")
                text = self.make_table(pos_dict, cusps, ascmc, aspects)
                self.append_page(text, label)
                self.set_current_page(-1)

    def make_aspectarian(self, aspects_data):
        """draw aspectarian table"""
        if not aspects_data or not aspects_data.get("obj names"):
            return ""
        obj_names = aspects_data["obj names"]
        speeds = aspects_data["speeds"]
        name2idx = {n: i for i, n in enumerate(aspects_data["obj names"])}
        matrix = aspects_data["matrix"]
        # layout
        v_ = "\u01ef"
        h_ = "\u01ee"
        vic_spc = "\u01ac"
        # title line
        text = f" aspects {h_ * 56}\n"
        # header row
        text += f"  > {v_}"
        for name in obj_names:
            text += f"{vic_spc}{name}   {v_}"
        text += "\n"
        # horizontal bottom line : match above text = f"aspects ..."
        h_line = f"{h_ * 62}\n"
        # grid
        for row_name in obj_names:
            i = name2idx[row_name]
            speed = speeds.get(row_name, 0.0)
            retro = "R" if speed < 0 else " "
            # 1st column
            text += f" {row_name}{retro}{v_}"
            # text += f" {row_name:>2} {v_}"
            for col_name in obj_names:
                j = name2idx[col_name]
                cell = matrix[i][j]
                if i == j:
                    text += f"{vic_spc}**** {v_}"
                elif i < j:
                    # above diagonal: major aspect if present, else blank
                    if cell["major"]:
                        glyph = cell.get("glyph", "")
                        orb = cell.get("orb")
                        orb_s = f"{orb:.1f}" if orb is not None else "   "
                        a_s = "a" if cell.get("applying") else "s"
                        text += f"{glyph}{orb_s} {a_s}{v_}"
                    else:
                        text += f"{vic_spc}  -  {v_}"
                else:
                    # below diagonal: always show angle
                    angle = cell.get("angle")
                    angle_s = f"{abs(angle):5.1f}" if angle is not None else "  -   "
                    text += f"{vic_spc}{angle_s}{v_}"
            text += "\n"
        # horizontal line at end
        text += h_line
        return text

    def make_table_content(self, pos_dict, cusps, ascmc, aspects=None):
        # unchanged except:
        n_chars = 37
        v_ = "\u01ef"
        h_ = "\u01ee"
        vic_spc = "\u01ac"
        asc = "\u01bf"
        mc = "\u01c1"
        line = f"{h_ * n_chars}\n"
        # aspectarian at top
        text = self.make_aspectarian(aspects)
        text += f" positions {h_ * 29}\n"
        text += f" name {v_}      sign {vic_spc} {v_}       lat {v_}        lon {v_} house\n"
        for key, obj in pos_dict.items():
            if key == "event":
                continue
            retro = "R" if obj.get("lon speed") < 0 else " "
            text += f" {obj['name']}{retro}  {v_}"
            text += f" {self.format_dms(obj.get('lon')):10} {v_}"
            text += f"{obj.get('lat', 0):10.6f} {v_}"
            text += f"{obj.get('lon', 0):11.6f}"
            text += f"{self.which_house(obj.get('lon'), cusps)}\n"
        text += line
        # houses
        text += f" houses {h_ * 7}\n"
        text += f"    {v_}      cusp\n"
        for i, cusp in enumerate(cusps, 1):
            text += f" {i:2d} {v_} {self.format_dms(cusp):20}\n"
        text += f" cross points {h_ * 3}\n"
        text += f" {asc} :  {self.format_dms(ascendant)}\n"
        text += f" {mc} :  {self.format_dms(midheaven)}\n"
        text += line
        return text

    def find_degree_diff(self, aspects, obj1, obj2):
        """find angle difference between obj1 / obj2"""
        for aspect in aspects:
            if (aspect["obj1"] == obj1 and aspect["obj2"] == obj2) or (
                aspect["obj1"] == obj2 and aspect["obj2"] == obj1
            ):
                return abs(aspect.get("orb", 0.0) + aspect.get("aspect angle", 0.0))
        return 0.0

    def make_table(self, pos_dict, cusps, ascmc, aspects=None):
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
        text = self.make_table_content(pos_dict, cusps, ascmc, aspects)
        buffer.set_text(text)
        scroll.set_child(text_view)
        return scroll

    def which_house(self, lon: float, cusps: Tuple[float, ...]) -> str:
        """find house number for given celestial longitude"""
        v_ = "\u01ef"  # victormonolightastro
        if not cusps:
            return ""
        # build list of cusps & house numbers
        cusp_list = [(c, i + 1) for i, c in enumerate(cusps)]
        # sort & wrap around 360
        n = len(cusp_list)
        for i in range(n):
            c0, h0 = cusp_list[i]
            c1, _ = cusp_list[(i + 1) % n]
            if c0 <= c1:
                # normal interval
                if c0 <= lon < c1:
                    return f" {v_} {h0:2d}"
            else:
                # wrap interval
                if lon >= c0 or lon < c1:
                    return f" {v_} {h0:2d}"
        return ""

    def format_dms(self, lon: float) -> str:
        deg, sign, min, sec = swh.degsplit(lon)
        sign_keys = list(SIGNS.keys())
        sign_key = sign_keys[sign]
        glyph = SIGNS[sign_key][0]
        return f"{deg:2d}°{min:02d}'{sec:02d}\" {glyph}"


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
