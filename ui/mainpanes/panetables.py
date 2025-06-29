# ui/mainpanes/panepositions.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from swisseph import contrib as swh
from ui.fonts.glyphs import SIGNS
from user.settings import HOUSE_SYSTEMS
from typing import Tuple


class Tables(Gtk.Notebook):
    def __init__(self):
        super().__init__()
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        # connect signals
        signal = self.app.signal_manager
        # event data widget
        signal._connect("positions_changed", self.positions_changed)
        signal._connect("houses_changed", self.houses_changed)
        signal._connect("aspects_changed", self.aspects_changed)
        # vimsottari dasa widget
        signal._connect("vimsottari_changed", self.vimsottari_changed)
        # if user not interested in event 2
        signal._connect("e2_cleared", self.e2_cleared)
        # data for events' positions and houses
        self.events_data = {}
        # mapping event to page widget
        self.page_widgets = {}
        # vimsottari fold level
        self.current_lvl = 1
        # styling and scroll options
        self.add_css_class("no-border")
        self.set_tab_pos(Gtk.PositionType.TOP)
        self.set_scrollable(True)
        self.margin = 9
        # formatting symbols
        self.v_sym = "\u01ef"
        self.h_sym = "\u01ee"
        self.vic_spc = "\u01ac"
        self.asc = "\u01bf"
        self.mc = "\u01c1"

    def event_data_widget(self, event: str, content: str):
        # create a scrollable text view for an event
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(False)
        scroll.set_vexpand(True)
        text_view = Gtk.TextView()
        text_view.set_margin_top(self.margin)
        text_view.set_margin_bottom(self.margin)
        text_view.set_margin_start(self.margin)
        text_view.set_margin_end(self.margin)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.add_css_class("table-text")
        buffer = text_view.get_buffer()
        buffer.set_text(content)
        scroll.set_child(text_view)
        # add page with event label as tab title
        self.append_page(scroll, Gtk.Label.new(event))
        self.page_widgets[event] = scroll

    def positions_changed(self, event: str, positions: dict):
        # update event with positions data
        if event not in self.events_data:
            self.events_data[event] = {}
        self.events_data[event]["positions"] = positions
        self.update_event_data(event)

    def houses_changed(self, event: str, houses: tuple):
        # store houses data and update if positions already exist
        if event not in self.events_data:
            self.events_data[event] = {}
        self.events_data[event]["houses"] = houses
        self.update_event_data(event)

    def aspects_changed(self, event, aspects):
        if event not in self.events_data:
            self.events_data[event] = {"aspects": None}
        self.events_data[event]["aspects"] = aspects
        self.update_event_data(event)

    def vimsottari_changed(self, event, vimsottari):
        if event not in self.events_data:
            self.events_data[event] = {"vimsottari": None}
        self.events_data[event]["vimsottari"] = vimsottari
        # print(f"vmst : {str(self.events_data[event].get('vimsottari'))[:800]}")
        content = self.make_vimsottari_raw(vimsottari)
        # print(f"vmch : {str(content)[:300]}")
        self.update_vimsottari("vimsottari", content)

    def e2_cleared(self, event):
        pass
        # if event == "e2":
        #     if event in self.events_data:
        #         # remove tab if exists
        #         for i in range(self.get_n_pages()):
        #             page = self.get_nth_page(i)
        #             label = self.get_tab_label_text(page)
        #             if label.strip() == event:
        #                 self.remove_page(i)
        #                 break
        #         # remove e2 from data storage
        #         del self.events_data[event]
        #         if event in self.table_pages:
        #             del self.table_pages[event]
        #         self.notify.info(
        #             f"cleared table for {event}",
        #             source="panetables",
        #             route=["terminal", "user"],
        #         )

    def update_event_data(self, event: str):
        # assure data exists
        if (
            event not in self.events_data
            or "positions" not in self.events_data[event]
            or not self.events_data[event]["positions"]
            or "houses" not in self.events_data[event]
            or not self.events_data[event]["houses"]
        ):
            self.notify.error(
                f"positions or houses missing for {event}",
                source="panetables",
                route=["terminal"],
            )
            return

        pos = self.events_data[event].get("positions")
        # get houses data if available
        houses = self.events_data[event].get("houses")
        aspects = self.make_aspects(event)
        content = str(aspects)
        if houses:
            cusps, ascmc = houses
        else:
            cusps = ()  # [], []
        if ascmc:
            self.ascendant = ascmc[0]
            self.midheaven = ascmc[1]
        # build header string with house column added
        header = (
            f"positions {self.h_sym * 29}\n"
            f" name {self.v_sym}      sign {self.vic_spc} "
            f"{self.v_sym}        lat {self.v_sym}         lon "
            f"{self.v_sym} hs\n"
        )
        content += header
        # loop through positions and calculate houses if possible
        for key, obj in pos.items():
            if key == "event":
                continue
            retro = "R" if obj.get("lon speed", 0) < 0 else " "
            lon = obj.get("lon", 0)
            # calculate house if cusps are available
            house = self.which_house(lon, tuple(cusps)) if cusps else ""
            separ = f"{self.h_sym * 37}\n"
            ln_pos = (
                f" {obj.get('name', '')}{retro}  {self.v_sym} "
                f"{self.format_dms(lon):10} {self.v_sym} "
                f"{obj.get('lat', 0):10.6f} {self.v_sym} "
                f"{lon:11.6f} {self.v_sym} {house}\n"
            )
            content += ln_pos
        # houses
        if cusps:
            if hasattr(self.app, "selected_house_sys_str"):
                if isinstance(self.app.selected_house_sys_str, bytes):
                    selected = self.app.selected_house_sys_str.decode("ascii")
                else:
                    selected = self.app.selected_house_sys_str
            else:
                selected = ""
            conversion = None
            for sys in HOUSE_SYSTEMS:
                if sys[2] == selected.lower():
                    conversion = sys[0]
                    break
            else:
                selected = ""
                conversion = None
            ln_csps = ""
            if conversion in ["E", "D", "W"]:
                # print(f"selected_hsys : {self.app.selected_house_sys_str}")
                # if selected in ["eqa", "eqm", "whs"]:
                ln_csps += (
                    f" cross points {self.h_sym * 3}\n"
                    f" {self.asc} :  {self.format_dms(self.ascendant)}\n"
                    f" {self.mc} :  {self.format_dms(self.midheaven)}\n"
                )
            else:
                ln_csps += f" houses {self.h_sym * 7}\n"
                ln_csps += f"    {self.v_sym}      cusp\n"
                for i, cusp in enumerate(cusps, 1):
                    ln_csps += f" {i:2d} {self.v_sym} {self.format_dms(cusp):20}\n"
                ln_csps += (
                    f" cross points {self.h_sym * 3}\n"
                    f" {self.asc} :  {self.format_dms(self.ascendant)}\n"
                    f" {self.mc} :  {self.format_dms(self.midheaven)}\n"
                )
            ln_csps += separ
            content += ln_csps
        # update page widget if exists, else create one
        if event in self.page_widgets:
            scroll = self.page_widgets[event]
            text_view = scroll.get_child()
            buffer = text_view.get_buffer()
            buffer.set_text(content)
        else:
            self.event_data_widget(event, content)

    def make_aspects(self, event):
        aspects = self.events_data[event].get("aspects")
        if (
            event not in self.events_data
            or "aspects" not in self.events_data[event]
            or not self.events_data[event]["aspects"]
        ):
            self.notify.error(
                f"aspects missing for {event}",
                source="panetables",
                route=["terminal"],
            )
            return

        obj_names = aspects["obj names"]
        speeds = aspects["speeds"]
        name2idx = {n: i for i, n in enumerate(aspects["obj names"])}
        matrix = aspects["matrix"]
        # title line
        text = f" aspects {self.h_sym * 56}\n"
        # header row
        text += f"  > {self.v_sym}"
        for name in obj_names:
            text += f"{self.vic_spc}{name}   {self.v_sym}"
        text += "\n"
        # horizontal bottom line : match above text = f"aspects ..."
        self.h_line = f"{self.h_sym * 62}\n"
        # grid
        for row_name in obj_names:
            i = name2idx[row_name]
            speed = speeds.get(row_name, 0.0)
            retro = "R" if speed < 0 else " "
            # 1st column
            text += f" {row_name}{retro}{self.v_sym}"
            # text += f" {row_name:>2} {v_}"
            for col_name in obj_names:
                j = name2idx[col_name]
                cell = matrix[i][j]
                if i == j:
                    text += f"{self.vic_spc}**** {self.v_sym}"
                elif i < j:
                    # above diagonal: major aspect if present, else blank
                    if cell["major"]:
                        glyph = cell.get("glyph", "")
                        orb = cell.get("orb")
                        orb_s = f"{orb:.1f}" if orb is not None else "   "
                        a_s = "a" if cell.get("applying") else "s"
                        text += f"{glyph}{orb_s} {a_s}{self.v_sym}"
                    else:
                        text += f"{self.vic_spc}  -  {self.v_sym}"
                else:
                    # below diagonal: always show angle
                    angle = cell.get("angle")
                    angle_s = f"{abs(angle):5.1f}" if angle is not None else "  -   "
                    text += f"{self.vic_spc}{angle_s}{self.v_sym}"
            text += "\n"
        # horizontal line at end
        text += self.h_line
        return text

    def vimsottari_widget(self, event: str, content: str):
        # create a scrollable text view for an event

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(False)
        scroll.set_vexpand(True)
        text_view = Gtk.TextView()
        text_view.set_margin_top(self.margin)
        text_view.set_margin_bottom(self.margin)
        text_view.set_margin_start(self.margin)
        text_view.set_margin_end(self.margin)
        # text_view.set_wrap_mode(Gtk.WrapMode.CHAR)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.add_css_class("table-text")
        buffer = text_view.get_buffer()
        buffer.set_text(content)
        scroll.set_child(text_view)
        # add page with event label as tab title
        # self.append_page(scroll, Gtk.Label.new(event))
        self.insert_page(scroll, Gtk.Label.new(event), -1)
        pg_idx = self.get_n_pages() - 1
        self.set_current_page(pg_idx)
        self.page_widgets[event] = scroll

    def update_vimsottari(self, event: str, content: str):  # Optional[str] = None):
        # print(f"upvms : {content[:600]}")
        # update page widget if exists, else create one
        if event in self.page_widgets:
            scroll = self.page_widgets[event]
            text_view = scroll.get_child()
            buffer = text_view.get_buffer()
            buffer.set_text(content)
        else:
            self.vimsottari_widget(event, content)

    def toggle_lvl(self, event):
        # cycle toggle level: 1->2->3->4->1
        if self.current_lvl == 1:
            self.current_lvl = 2
        elif self.current_lvl == 2:
            self.current_lvl = 3
        elif self.current_lvl == 3:
            self.current_lvl = 4
        else:
            self.current_lvl = 1
        new_content = self.make_vimsottari(event, self.current_lvl)
        # assume event 'vimsottari' is the target page
        self.update_vimsottari("vimsottari", new_content)

    def make_vimsottari(self, event, lvl):
        # generate content string based on level
        vmst = self.events_data[event].get("vimsottari")
        out = ""
        if vmst:
            if lvl == 1:
                # lvl 1: show major periods only
                for entry in vmst:
                    out += f"{entry['lord'].upper()} ({entry['years']} yrs)\n"
                    out += f"from: {entry['from']} to: {entry['to']}\n\n"
            elif lvl == 2:
                # lvl 2: add current antar (simulate first sub if exists)
                for entry in vmst:
                    out += f"{entry['lord'].upper()} ({entry['years']} yrs)\n"
                    if "sub" in entry and len(entry["sub"]) > 0:
                        anta = entry["sub"][0]
                        out += (
                            "   antar: "
                            + f"{anta['lord'].upper()} "
                            + f"({anta['years']} yrs)\n"
                        )
                    out += f"from: {entry['from']} to: {entry['to']}\n\n"
            elif lvl == 3:
                # lvl 3: add current pratyantar (simulate first sub of antar)
                for entry in vmst:
                    out += f"{entry['lord'].upper()} ({entry['years']} yrs)\n"
                    if "sub" in entry and len(entry["sub"]) > 0:
                        anta = entry["sub"][0]
                        out += (
                            "   antar: "
                            + f"{anta['lord'].upper()} "
                            + f"({anta['years']} yrs)\n"
                        )
                        if "sub" in anta and len(anta["sub"]) > 0:
                            praty = anta["sub"][0]
                            out += (
                                "      pratyantar: "
                                + f"{praty['lord'].upper()} "
                                + f"({praty['years']} yrs)\n"
                            )
                    out += f"from: {entry['from']} to: {entry['to']}\n\n"
            elif lvl == 4:
                # lvl 4: fully unfold all details recursively
                def recurse(entries, indent=0):
                    res = ""
                    pad = "    " * indent
                    for e in entries:
                        res += pad + f"{e['lord'].upper()} " + f"({e['years']} yrs)\n"
                        res += pad + f"from: {e['from']} to: {e['to']}\n"
                        if "sub" in e and e["sub"]:
                            res += recurse(e["sub"], indent + 1)
                        res += "\n"
                    return res

                out = recurse(vmst)
        return out

    def make_vimsottari_raw(self, data) -> str:
        # prepare string from raw vimsottari data (list/dict) using default level 1
        out = ""
        if data and isinstance(data, list):
            for entry in data:
                out += f"{entry['lord'].upper()} " + f"({entry['years']} yrs)\n"
                out += f"from: {entry['from']} to: {entry['to']}\n\n"
        elif data and isinstance(data, dict):
            out += (
                f"{data.get('lord', '').upper()} " + f"({data.get('years', 0)} yrs)\n"
            )
            out += f"from: {data.get('from')} to: {data.get('to')}\n\n"
        return out

    def which_house(self, lon: float, cusps: Tuple[float, ...]) -> str:
        # determine which house a celestial longitude falls in
        if not cusps:
            return ""
        cusp_list = [(c, i + 1) for i, c in enumerate(cusps)]
        n = len(cusp_list)
        for i in range(n):
            c0, h0 = cusp_list[i]
            c1, _ = cusp_list[(i + 1) % n]
            if c0 <= c1:
                if c0 <= lon < c1:
                    return f"{h0:2d}"
            else:
                if lon >= c0 or lon < c1:
                    return f"{h0:2d}"
        return ""

    def format_dms(self, lon: float) -> str:
        # convert lon to dms string using pyswisseph
        deg, sign, min, sec = swh.degsplit(lon)
        sign_keys = list(SIGNS.keys())
        sign_key = sign_keys[sign]
        glyph = SIGNS[sign_key][0]
        return f"{deg:2d}°{min:02d}'{sec:02d}\" {glyph}"
