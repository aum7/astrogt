import sqlite3

# from typing import Optional
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class EventLocation:
    def __init__(self, parent):
        self.parent = parent
        self.countries = []
        self.country_map = {}
        self.selected_city = ""
        self.entry = None
        self.location_callback = None

    def set_location_callback(self, callback):
        self.location_callback = callback

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

    def get_city_from_atlas(
        self,
        ent_city,
        ddn_country,
    ):
        # store entry reference
        self.entry = ent_city
        city = ent_city.get_text().strip()
        country_index = ddn_country.get_selected()
        country = ddn_country.get_model().get_string(country_index)
        iso3 = self.country_map.get(country)

        try:
            # todo hardcoded
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
            self.check_cities(sorted(cities))

        except Exception as e:
            print(f"eventlocation : atlas db error :\n\t{str(e)}\n")

    def check_cities(self, cities):
        if len(cities) == 0:
            print("check_cities : city not found : exiting ...")
            return

        elif len(cities) == 1:
            # print(f"check_cities : found 1 city : {cities[0]}")
            city, lat, lon, alt = cities[0]
            city_str = f"{city}, {lat}, {lon}, {alt}"
            self.selected_city = city_str
            self.update_entries(city_str)

        elif len(cities) > 1:
            # print(f"check_cities : found multiple cities :\n\t{cities}")
            self.show_city_dialog(cities)

    def update_entries(self, city_str):
        if not city_str:
            return

        parts = city_str.split(", ")
        if len(parts) >= 4:
            city_name = parts[0]
            lat, lon, alt = parts[1:4]

            if self.entry:
                self.entry.set_text(city_name)

            if self.location_callback:
                print("update_entries : calling self.location_callback")
                self.location_callback(lat, lon, alt)

    def show_city_dialog(self, found_cities):
        """present list of found cities for user to select one (modal)"""
        # print(f"select_city : found_cities passed :\n\t{found_cities}")
        dialog = Gtk.Dialog(
            title="select city : name | latitude | longitude | altitude",
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

        def pick_city(listbox_, row):
            if row and (label := row.get_child()):
                if isinstance(label, Gtk.Label):
                    selected = label.get_text()
                    # print(f"pick_city : {selected} selected")
                    self.selected_city = selected
                    print(f"pick_city : {self.selected_city} selected")
                    self.update_entries(selected)
                    dialog.close()

        listbox.connect("row-activated", pick_city)

        margin_h = 7
        for city in found_cities:
            row = Gtk.ListBoxRow()
            city_str = f"{city[0]}, {city[1]}, {city[2]}, {city[3]}"
            label = Gtk.Label(label=city_str)
            label.set_margin_start(margin_h)
            label.set_margin_end(margin_h)
            row.set_child(label)
            listbox.append(row)

        scw.set_child(listbox)
        dialog.present()

    def get_selected_city(self, entry, dropdown):
        print(f"1st-get_selected_city : {self.selected_city}")
        selected_city = self.selected_city
        print(f"2nd-get_selected_city : selected_city : {selected_city}")
        self.get_city_from_atlas(entry, dropdown)
        print(
            f"3rd-get_selected_city : {self.selected_city} after get_city_from_atlas()"
        )

        # selected_ = selected_city.split()
        # print(f"get_selected_city : selected_city : {selected_city}")
        # if self.selected_city:
        #     entry.set_text(self.selected_city.split(", ")[0])

        return self.selected_city
