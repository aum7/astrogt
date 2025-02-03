import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class EventWidget(Gtk.Box):
    """widget for user data input"""

    def __init__(self, event_name: str):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.event_name = event_name
        self.add_css_class("event-widget")
        self.set_spacing(5)
        margin_hor = margin_ver = 5
        self.set_margin_start(margin_hor)
        self.set_margin_end(margin_hor)
        self.set_margin_top(margin_ver)
        self.set_margin_bottom(margin_ver)

        self.set_visible(True)
        self.set_hexpand(True)
        self.set_vexpand(True)
        # setup widget components
        self.setup_datetime()
        self.setup_location()

    def setup_datetime(self):
        box_datetime = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_datetime.set_spacing(5)
        box_datetime.set_visible(True)

        lbl_datetime = Gtk.Label(label="datetime")
        lbl_datetime.set_visible(True)

        ent_datetime = Gtk.Entry()
        ent_datetime.set_visible(True)
        ent_datetime.set_hexpand(True)
        ent_datetime.set_vexpand(True)
        ent_datetime.set_placeholder_text(
            "event date & time : yyyy MM dd hh mm ss (year month day hour minute second)"
        )
        box_datetime.append(lbl_datetime)
        box_datetime.append(ent_datetime)

        self.append(box_datetime)

    def setup_location(self):
        box_location = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
