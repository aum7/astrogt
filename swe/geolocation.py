import sqlite3
from math import modf
from typing import Optional
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk


class GeoLocation:
    def __init__(self, parent):
        self.parent = parent
        self.countries = []
        self.country_map = {}
        self._selected_city = ""

    @property
    def selected_city(self):
        return self._selected_city

    @selected_city.setter
    def selected_city(self, value):
        self._selected_city = value
        if value:
            self.format_geo_location(value)
            # formatted = self.format_geo_location(value)
            # print(f"formatted geolocation : {formatted}")

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

    def get_city_from_atlas(self, ent_city, ddn_country, event_name, ent_geolocation):
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
        # store entries for later update
        self.current_entries = {
            "city": ent_city,
            "geolocation": ent_geolocation,
        }
        self.check_cities(cities)

    def check_cities(self, cities):
        if len(cities) == 0:
            print("check_cities : city not found : exiting ...")
            return

        elif len(cities) == 1:
            print(f"check_cities : found 1 city : {cities[0]}")
            str_city, lat, lon, alt = cities[0]
            city = f"{str_city}, {lat}, {lon}, {alt}"
            self.selected_city = city

        elif len(cities) > 1:
            # print(f"check_cities : found multiple cities :\n\t{cities}")
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
                    # print(f"pick_city : {self.selected_city} selected")
                    # print(f"self.selected_city type : {type(self.selected_city)}")
                    dialog.destroy()

    def format_geo_location(self, location):
        """if single city is found : location = tuple
        if multiple cities : location = string
        we want string as result"""
        # south & west -ve : -16.75 -72.678
        # print(f"location : {location}")
        self.direction_lat = self.direction_lon = ""
        self.name = ""
        self.lat = self.lon = 0.0
        self.lat_deg = self.lat_min = self.lat_sec = ""
        self.lon_deg = self.lon_min = self.lon_sec = ""
        self.alt = ""
        if isinstance(location, str):
            print("format_geo_location : location = string")
            self.name, self.lat, self.lon, alt = location.split(",")
            self.alt = alt.strip()
        elif isinstance(location, tuple):
            # todo do we need this ?
            print("format_geo_location : location = tuple")
            self.name, self.lat, self.lon, alt = location
            self.alt = str(alt).strip()

        if float(self.lat) <= 0:
            self.direction_lat = "s"
        else:
            self.direction_lat = "n"
        if float(self.lon) <= 0:
            self.direction_lon = "w"
        else:
            self.direction_lon = "e"

        lat_abs = abs(float(self.lat))
        lat_deg, lat_min, lat_sec = self.decimal_to_dms(lat_abs)
        self.lat_deg = str(lat_deg)
        self.lat_min = str(lat_min)
        self.lat_sec = str(lat_sec)

        lon_abs = abs(float(self.lon))
        lon_deg, lon_min, lon_sec = self.decimal_to_dms(lon_abs)
        self.lon_deg = str(lon_deg)
        self.lon_min = str(lon_min)
        self.lon_sec = str(lon_sec)

        # construct desired format
        loc_result = f"{self.lat_deg.zfill(2)} {self.lat_min.zfill(2)} {self.lat_sec.zfill(2)} {self.direction_lat} {self.lon_deg.zfill(3)} {self.lon_min.zfill(2)} {self.lon_sec.zfill(2)} {self.direction_lon} {self.alt.zfill(4)} m"
        print(loc_result)
        # update entries
        if hasattr(self, "current_entries"):
            self.current_entries["city"].set_text(self.name.strip())
            self.current_entries["geolocation"].set_text(loc_result)

        return loc_result

    def decimal_to_dms(self, decimal):
        """convert decimal number to degree-minute-second"""
        min_, deg_ = modf(decimal)
        deg = int(deg_)
        min = int(min_ * 60)
        sec_, _ = modf(min_ * 60)
        sec = int(sec_ * 60)
        # print(f"decimal_to_dms : d-m-s : {deg} - {min} - {sec}")

        return deg, min, sec
