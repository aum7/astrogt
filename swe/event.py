import gi

gi.require_version("Gtk", "4.0")  # or '3.0' depending on your GTK version
from gi.repository import Gtk
from datetime import datetime
import pytz


class EventEntryData:
    def __init__(self, event_name, date_time, location):
        """get user input and puf! puf! into sweph"""
        self.event_name = event_name
        self.date_time = date_time
        self.location = location
        # signals jummy!
        self.event_name.connect("activate", self.on_name_change)
        self.date_time.connect("activate", self.on_date_time_change)
        self.location.connect("activate", self.on_location_change)

    def on_name_change(self, entry):
        """process name"""
        name = entry.get_text().strip()
        print(f"event name : {name}")

    def on_date_time_change(self, entry):
        """process date & time"""
        date_time = entry.get_text().strip()
        print(f"event date time : {date_time}")

    def on_location_change(self, entry):
        """process location"""
        location = entry.get_text().strip()
        print(f"event location : {location}")

    def get_event_data(self):
        """values from all entries for an event"""
        return {
            "name": self.event_name.get_text().strip(),
            "date_time": self.date_time.get_text().strip(),
            "location": self.location.get_text().strip(),
        }

    def clear_entries(self):
        """clear all entries"""
        self.event_name.set_text("")
        self.date_time.set_text("")
        self.location.set_text("")

    def set_current_utc(self):
        current_utc = datetime.now(pytz.UTC)
        formatted_utc = current_utc.strftime("%Y-%m-%d %H:%M:%S")
        self.date_time.set_text(formatted_utc)
        print(f"current utc : {formatted_utc}")
