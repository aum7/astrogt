import sqlite3


def get_countries():
    countries = []
    with open("user/countries.txt", "r") as f:
        for line in f:
            line.strip()
            if line.startswith("("):
                _, name, iso3 = eval(line)
                countries.append((name, iso3))
    print(f"countries available : {countries}")
    return sorted(countries)


def get_cities(country_iso3, city_name):
    conn = sqlite3.connect("user/atlas/atlas.db")
