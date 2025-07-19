# ui/mainpanes/tables.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Tuple
from swisseph import contrib as swh
from ui.fonts.glyphs import SIGNS
from ui.helpers import _decimal_to_ra as decra
from user.settings import HOUSE_SYSTEMS
from sweph.calculations.retro import calculate_retro
from sweph.swetime import jd_to_custom_iso as jdtoiso


class Tables(Gtk.Notebook):
    def __init__(self):
        super().__init__()
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        # connect signals
        signal = self.app.signal_manager
        # styling and scroll options
        self.add_css_class("no-border")
        self.set_tab_pos(Gtk.PositionType.TOP)
        self.set_scrollable(True)
        self.margin = 3
        # data for events' positions and houses
        self.events_data = {}
        # mapping event to page widget
        self.page_widgets = {}
        # vimsottari fold level
        self.app.current_lvl = 1
        self.current_event = None
        # formatting symbols : victormonolightastro.ttf
        self.v_sym = "\u01ef"
        self.h_sym = "\u01ee"
        self.vic_spc = "\u01ac"
        self.asc = "\u01bf"
        self.mc = "\u01c1"
        self.order = ("su", "mo", "me", "ve", "ma", "ju", "sa", "ur", "ne", "pl", "ra")
        # event data widget
        signal._connect("positions_changed", self.positions_changed)
        signal._connect("houses_changed", self.houses_changed)
        signal._connect("aspects_changed", self.aspects_changed)
        # vimsottari dasa widget
        signal._connect("vimsottari_changed", self.vimsottari_changed)
        # p3 table
        signal._connect("p3_changed", self.p3_changed)
        # if user not interested in event 2
        signal._connect("e2_cleared", self.e2_cleared)

    def event_data_widget(self, event: str, content: str):
        # create a scrollable text view for an event
        scroll = Gtk.ScrolledWindow()
        scroll.set_name(f"data_scroll_{event}")
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

    def positions_changed(self, event: str):
        # update event with positions data
        if event not in self.events_data:
            self.events_data[event] = {"positions": None}
        if event == "e1":
            self.events_data[event]["positions"] = (
                self.app.e1_positions if hasattr(self.app, "e1_positions") else None
            )
        elif event == "e2":
            self.events_data[event]["positions"] = (
                self.app.e2_positions if hasattr(self.app, "e2_positions") else None
            )
        self.update_event_data(event)

    def houses_changed(self, event: str):
        # store houses data and update if positions already exist
        if event not in self.events_data:
            self.events_data[event] = {"houses": None}
        if event == "e1":
            self.events_data[event]["houses"] = (
                self.app.e1_houses if hasattr(self.app, "e1_houses") else None
            )
        elif event == "e2":
            self.events_data[event]["houses"] = (
                self.app.e2_houses if hasattr(self.app, "e2_houses") else None
            )
        self.update_event_data(event)

    def aspects_changed(self, event, aspects):
        # todo only 1 set of aspects : event 1
        if event not in self.events_data:
            self.events_data[event] = {"aspects": None}
        self.events_data[event]["aspects"] = aspects
        self.update_event_data(event)

    def vimsottari_changed(self, event, vimsottari):
        # receives table as plain text
        if event not in self.events_data:
            self.events_data[event] = {"vimsottari": None}
        self.events_data[event]["vimsottari"] = vimsottari
        self.current_event = event
        # print(f"vmst chg : {str(self.events_data[event].get('vimsottari'))[:800]}")
        self.update_vimsottari("vimsottari", vimsottari)

    def p3_changed(self, event):
        self.p3_pos = getattr(self.app, "p3_pos", None)
        self.p3_retro = calculate_retro("p3")
        self.update_p3(event)

    def update_p3(self, event):
        p3_pos = getattr(self, "p3_pos", None)
        msg = ""
        if not p3_pos:
            self.notify.error(
                "missing p3 positions : exiting ...",
                source="tables",
                route=["terminal", "user"],
            )
            return
        # msg += f"p3changed : p3pos :\n\t{p3_pos}\n"
        separ = f"{self.h_sym * 20}\n"
        content = ""
        p3_date = next(
            (f.get("date") for f in p3_pos if f.get("name") == "p3date"), None
        )
        if p3_date:
            content += (
                " all time is utc\n"
                " tas & tmc - true asc & mc (experimental)\n"
                f"{separ}"
                f" p3 date : {p3_date.strip()}\n"
            )
        content += separ
        # header
        header = f" obj {self.v_sym}        sign\n"
        content += header
        # sort objects for table
        pos_sorted = sorted(
            p3_pos,
            key=lambda obj: self.order.index(obj["name"])
            if obj.get("name") in self.order
            else len(self.order),
        )
        for obj in pos_sorted:
            name = obj.get("name", "")
            if name in ("p3date", "p3jdut"):
                continue
            lon = obj.get("lon", 0)
            retro_info = next((r for r in self.p3_retro if r.get("name") == name), None)
            direction = retro_info["direction"] if retro_info else ""
            # dont show direct indicator
            if direction == "D":
                direction = ""
            name_with_dir = f"{name}{direction}"
            ln_pos = f" {name_with_dir:3} {self.v_sym} {self.format_dms(lon):10}\n"
            if name == "tas":
                ln_pos = (
                    f" {self.h_sym * 2} {self.v_sym}\n"
                    f" {name_with_dir:3} {self.v_sym} {self.format_dms(lon):10}\n"
                )
            content += ln_pos
        content += separ
        content += " planetary stations :\n"
        # additional retro data
        if self.p3_retro:
            retro_sorted = sorted(
                self.p3_retro,
                key=lambda r: self.order.index(r["name"])
                if r.get("name") in self.order
                else len(self.order),
            )
            for retro in retro_sorted:
                if "name" not in retro:
                    continue
                name = retro["name"]
                prev_st = jdtoiso(retro.get("prevstation"))
                next_st = jdtoiso(retro.get("nextstation"))
                content += f" {name}\n"
                content += f"   prev : {prev_st}\n"
                content += f"   next : {next_st}\n"
        self.notify.debug(
            msg,
            source="tables",
            route=[""],
        )
        event = "p3"
        if event in self.page_widgets:
            scroll = self.page_widgets[event]
            text_view = scroll.get_child()
            buffer = text_view.get_buffer()
            buffer.set_text(content)
        else:
            self.p3_widget(event, content)

    def p3_widget(self, event: str, content: str):
        # create a scrollable text view for tertiary progression
        scroll = Gtk.ScrolledWindow()
        scroll.set_name(f"data_scroll_{event}")
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
        self.set_current_page(self.get_n_pages() - 1)

    def e2_cleared(self, event):
        """
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
        """
        pass

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
                f"positions or houses missing for {event} : exiting ...",
                source="panetables",
                route=[""],  # todo need this ???
            )
            return
        pos = self.events_data[event].get("positions")
        # print(f"panetables pos : {pos}")
        pos_map = {k: v for k, v in pos.items() if isinstance(k, int)}
        # print(f"panetables posmap : {pos_map}")
        # get houses data if available
        houses = self.events_data[event].get("houses")
        aspects = self.make_aspects(event)
        content = str(aspects)
        if houses:
            cusps, ascmc = houses
        else:
            cusps = ()
        if ascmc:
            self.ascendant = ascmc[0]
            self.midheaven = ascmc[1]
            self.armc = ascmc[2]
        # build header string with house column added
        header = (
            f" positions {self.h_sym * 29}\n"
            f" name {self.v_sym}      sign {self.vic_spc} "
            f"{self.v_sym}        lat {self.v_sym}         lon "
            f"{self.v_sym} hs\n"
        )
        content += header
        separ = f"{self.h_sym * 36}\n"
        # loop through positions and calculate houses if possible
        for _, obj in pos_map.items():
            retro = "R" if obj.get("lon speed", 0) < 0 else " "
            lon = obj.get("lon", 0)
            # calculate house if cusps are available
            house = self.which_house(lon, tuple(cusps)) if cusps else ""
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
            hsys_char = None
            for sys in HOUSE_SYSTEMS:
                if sys[2] == selected.lower():
                    hsys_char = sys[0]
                    break
            else:
                selected = ""
                hsys_char = None
            ln_csps = ""
            raH, raM, raS = decra(self.armc)
            if hsys_char in ["E", "D", "W"]:
                # print(f"selected_hsys : {self.app.selected_house_sys_str}")
                # if selected in ["eqa", "eqm", "whs"]:
                ln_csps += (
                    f" cross points {self.h_sym * 3}\n"
                    f" {self.asc} :  {self.format_dms(self.ascendant)}\n"
                    f" {self.mc} :  {self.format_dms(self.midheaven)}\n"
                    f" ra : {int(raH):02d}h{int(raM):02d}m{int(raS):02d}s\n"
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
                    f" ra : {int(raH):02d}h{int(raM):02d}m{int(raS):02d}s\n"
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
        scroll.set_name(f"vimso_scroll_{event}")
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
        self.insert_page(scroll, Gtk.Label.new(event), -1)
        self.page_widgets[event] = scroll
        self.set_current_page(self.get_n_pages() - 1)

    def update_vimsottari(self, event: str, content: str):
        # print(f"upd vmst : {content[:600]}")
        if event in self.page_widgets:
            # print("vimsottari_widget : updating table")
            scroll = self.page_widgets[event]
            text_view = scroll.get_child()
            buffer = text_view.get_buffer()
            buffer.set_text(content)
        else:
            # print("vimsottari_widget : creating new page")
            self.vimsottari_widget(event, content)

    # def toggle_vimso(self, gesture=None, n_press=0, x=0, y=0):
    def toggle_vimso(self):
        # cycle toggle level: 1->2->3->4->5->1
        event = "e1"  # self.current_event
        # print(f"toggle_vimso  {event} called")
        if self.app.current_lvl == 1:
            self.app.current_lvl = 2
        elif self.app.current_lvl == 2:
            self.app.current_lvl = 3
        elif self.app.current_lvl == 3:
            self.app.current_lvl = 4
        elif self.app.current_lvl == 4:
            self.app.current_lvl = 5
        else:
            self.app.current_lvl = 1
        # print(f"current_lvl : {self.app.current_lvl}")
        # update vimsottari for new level
        if event and event in self.events_data:
            # emit signal to force recalculation
            self.app.signal_manager._emit(
                "luminaries_changed",
                event,
                # "luminaries_changed", "vimsottari", self.app.last_luminaries
            )

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
