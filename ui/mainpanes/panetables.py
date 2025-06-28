# ui/mainpanes/panetables.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


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
        self.init_page()

    def init_page(self):
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
        buffer.set_text(
            "orem ipsum is a dummy or placeholder text commonly used in graphic design, publishing, and web development. Its purpose is to permit a page layout to be designed, independently of the copy that will subsequently populate it, or to demonstrate various fonts of a typeface without meaningful text that could be distracting. Lorem ipsum is typically a corrupted version of De finibus bonorum et malorum, a 1st-century BC text by the Roman statesman and philosopher Cicero, with words altered, added, and removed to make it nonsensical and improper Latin. Wikipedialo"
        )
        scroll.set_child(text_view)
        # add the scrolled window as a new notebook page
        self.append_page(scroll, Gtk.Label.new("tab 1"))

    def positions_changed(self, event, positions):
        print(f"pos : {str(positions)[:30]}\n\n")
        if event not in self.events_data:
            self.events_data[event] = {"positions": None}
        self.events_data[event]["positions"] = positions
        # update data
        self.update_data(self.events_data[event])

    def houses_changed(self, event, houses):
        print(f"hss : {str(houses)[:30]}\n\n")
        if event not in self.events_data:
            self.events_data[event] = {"houses": None}
        self.events_data[event]["houses"] = houses
        # update data
        self.update_data(self.events_data[event])

    def aspects_changed(self, event, aspects):
        print(f"asp : {str(aspects)[:30]}\n\n")
        if event not in self.events_data:
            self.events_data[event] = {"aspects": None}
        self.events_data[event]["aspects"] = aspects
        # update data
        self.update_data(self.events_data[event])

    def vimsottari_changed(self, event, vimsottari):
        print(f"vstd : {str(vimsottari)[:30]}\n")
        if event not in self.events_data:
            self.events_data[event] = {"vimsottari": None}
        self.events_data[event]["vimsottari"] = vimsottari
        # update data
        self.update_data(self.events_data[event])

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

    def update_data(self, data):
        # process & update data in widget
        process = self.process_positions("positions")
        # process = self.process_positions(data["positions"])
        # update textview in tab 1
        page = self.get_nth_page(0)
        if page:
            scroll = page
            text_view = scroll.get_child()
            if text_view:
                buffer = text_view.get_buffer()
                buffer.set_text(process)

    def process_positions(self, positions):
        return "blah"
