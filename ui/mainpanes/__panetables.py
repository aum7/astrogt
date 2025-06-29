# ui/mainpanes/panetables.py
# ruff: noqa: E402
# import time
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from swisseph import contrib as swh
from ui.fonts.glyphs import SIGNS
from typing import Tuple


class Tables(Gtk.Notebook):
    def __init__(self):
        super().__init__()
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        # connect to signals
        signal = self.app.signal_manager
        signal._connect("positions_changed", self.positions_changed)
        signal._connect("houses_changed", self.houses_changed)
        signal._connect("e2_cleared", self.e2_cleared)
        signal._connect("aspects_changed", self.aspects_changed)
        signal._connect("vimsottari_changed", self.vimsottari_changed)
        # event data storage
        self.events_data = {}
        # mapping event to page content
        self.table_pages = {}
        # add styling
        self.add_css_class("no-border")
        self.set_tab_pos(Gtk.PositionType.TOP)
        self.set_scrollable(True)
        self.mrg = 9
        # self.init_page()
        # formatting : custom victormonolightastro.ttf font
        self.v_ = "\u01ef"
        self.h_ = "\u01ee"
        self.vic_spc = "\u01ac"
        self.asc = "\u01bf"
        self.mc = "\u01c1"

    def positions_changed(self, event, positions):
        if event not in self.events_data:
            self.events_data[event] = {"positions": None}
        self.events_data[event]["positions"] = positions
        # update data
        self.update_data(event)

    def houses_changed(self, event, houses):
        if event not in self.events_data:
            self.events_data[event] = {"houses": None}
        self.events_data[event]["houses"] = houses
        # self.posi_hous(event)
        # update data
        self.update_data(event)

    def aspects_changed(self, event, aspects):
        # print(f"asp : {str(aspects)[:30]}\n\n")
        if event not in self.events_data:
            self.events_data[event] = {"aspects": None}
        self.events_data[event]["aspects"] = aspects
        # update data
        self.update_data(event)

    def vimsottari_changed(self, event, vimsottari):
        # print(f"vstd : {str(vimsottari)[:30]}\n")
        if event not in self.events_data:
            self.events_data[event] = {"vimsottari": None}
        self.events_data[event]["vimsottari"] = vimsottari
        # update data
        self.update_data(event)

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

    def page_widget(self, event, content):
        # main widget for tables : scrollable
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
        buffer.set_text(content)
        scroll.set_child(text_view)
        # add the scrolled window as a new notebook page
        self.append_page(scroll, Gtk.Label.new(f"{event}"))

    def posi_hous(self, event):
        # print(f"posihous : {str(data)}")
        pos = self.events_data[event]["positions"]
        hss = self.events_data[event]["houses"]
        if hss:
            cusps, _ = hss
        line = f"{self.h_ * 37}\n"
        text = f" positions {self.h_ * 29}\n"
        text += f" name {self.v_}      sign {self.vic_spc} {self.v_}       lat {self.v_}        lon {self.v_} house\n"
        for key, obj in pos.items():
            if key == "event":
                continue
            retro = "R" if obj.get("lon speed") < 0 else " "
            text += f" {obj['name']}{retro}  {self.v_}"
            text += f" {self.format_dms(obj.get('lon')):10} {self.v_}"
            text += f"{obj.get('lat', 0):10.6f} {self.v_}"
            text += f"{obj.get('lon', 0):11.6f}"
            text += f"{self.which_house(obj.get('lon'), cusps)}\n"
        text += line
        self.page_widget(event, text)

    def update_data(self, event):
        # process & update data in widget
        process = self.posi_hous(event)
        # process = self.process_positions(data["positions"])
        # update textview in tab 1
        page = self.get_nth_page(0)
        if page:
            scroll = page
            text_view = scroll.get_child()
            if text_view:
                buffer = text_view.get_buffer()
                buffer.set_text(process)

    # def process_positions(self, positions):
    #     return "blah"

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
