import sqlite3
from typing import Optional
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk


class GeoLocation:
    def __init__(self, parent):
        self.parent = parent
        self.countries = []
        self.country_map = {}

        # self.selected_geo_data = None
        self.selected_city = None
        # self.multi_cities = None
        # self.pop_cities = None

    def get_countries(self):
        with open("user/countries.txt", "r") as f:
            for line in f:
                line = line.strip().rstrip(",")
                if line.startswith("("):
                    parts = line[1:-1].split('", ')
                    if len(parts) == 3:
                        _, name, iso3 = (
                            parts[0].strip('"'),
                            parts[1].strip('"'),
                            parts[2].strip('"'),
                        )
                    self.countries.append(name)
                    self.country_map[name] = iso3

        return sorted(self.countries)

    def get_city_from_atlas(self, ent_city, ddn_country, event_name):
        city = ent_city.get_text().strip()
        country_index = ddn_country.get_selected()
        country = ddn_country.get_model().get_string(country_index)
        iso3 = self.country_map.get(country)
        # selected_city = None
        conn = sqlite3.connect("user/atlas/atlas.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT name, latitude, longitude, elevation
            FROM GeoNames
            WHERE country = (SELECT _idx FROM CountryInfo where iso3 = ?)
            AND LOWER(name) LIKE LOWER(?)
            """,
            (iso3, f"%{city}%"),
        )
        cities = cursor.fetchall()
        conn.close()
        self.check_cities(cities)
        # return cities

    def check_cities(self, cities):
        if len(cities) == 0:
            print("get_city_from_atlas : city not found : exiting ...")
            return

        elif len(cities) == 1:
            print(f"get_city_from_atlas : found 1 city : {cities[0]}")
            self.selected_city = cities[0]

        elif len(cities) > 1:
            # print(f"get_city_from_atlas : found multiple cities :\n\t{cities}")
            self.select_city(cities)

    def select_city(self, found_cities) -> Optional[str]:
        """present list of found cities for user to select one (modal)"""
        # print(f"select_city : found_cities passed :\n\t{found_cities}")
        # present list of found cities for user to choose one
        dialog = Gtk.Dialog(
            title="select city : name latitude longitude altitude",
            modal=True,
        )
        dialog.set_transient_for(self.parent)
        dialog.set_default_size(-1, -1)

        content = dialog.get_content_area()

        scw = Gtk.ScrolledWindow()
        scw.set_propagate_natural_width(True)
        scw.set_propagate_natural_height(True)
        content.append(scw)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        listbox.connect(
            "row-activated",
            lambda listbox, row: pick_city(row),
        )

        margin_h = 7
        for city in found_cities:
            row = Gtk.ListBoxRow()
            city_str = str(city).replace("(", "").replace(")", "").replace("'", "")
            label = Gtk.Label(label=city_str)
            label.set_margin_start(margin_h)
            label.set_margin_end(margin_h)
            row.set_child(label)
            listbox.append(row)

        scw.set_child(listbox)
        dialog.present()

        def pick_city(row):
            if row and (label := row.get_child()):
                if isinstance(label, Gtk.Label):
                    self.selected_city = label.get_text()
                    print(f"pick_city : selected city : {self.selected_city}")
                    dialog.destroy()

    def format_geo_location(self, lat, lon, alt):
        # todo deg-min-sec n/s & e/w
        geo_format = f"format_geo_location : {lat} {lon} {alt}m"

        return geo_format
