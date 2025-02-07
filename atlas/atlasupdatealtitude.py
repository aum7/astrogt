import sqlite3
import requests
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_cities(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # cur.execute(
    #     "SELECT _idx, name, latitude, longitude FROM GeoNames WHERE elevation = 0 AND 102303 < _idx AND _idx < 102927 ORDER BY _idx"
    # )
    cur.execute(
        "SELECT _idx, name, latitude, longitude FROM GeoNames WHERE elevation = 0 ORDER BY _idx"
    )
    # cur.execute(
    #     "SELECT _idx, name, latitude, longitude FROM GeoNames WHERE elevation IS NULL ORDER BY _idx"
    # )
    # cur.execute(
    #        "SELECT _idx, name, latitude, longitude, timezone FROM GeoNames WHERE elevation IS NULL ORDER BY _idx"
    #    )
    cities = cur.fetchall()
    conn.close()
    return cities


def get_elevations(locations):
    locations_str = "|".join([f"{lat},{lon}" for lat, lon in locations])
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={locations_str}"
    logging.info(f"Requesting elevations from API: {url}")  # Add this line for logging
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        elevations = response.json()["results"]
        return [elevation["elevation"] for elevation in elevations]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching elevations: {e}")
        return [None] * len(locations)


def update_elevation(db_path, city_id, elevation):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "UPDATE GeoNames SET elevation = ? WHERE _idx = ?", (elevation, city_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error updating database: {e}")
    finally:
        conn.close()


def save_cities_to_file(cities, filename):
    with open(filename, "w") as file:
        for city in cities:
            file.write(f"{city[0]}, {city[1]}, {city[2]}, {city[3]}\n")


def main(db_path):
    cities = get_cities(db_path)
    save_cities_to_file(cities, "cities.txt")  # Save cities to a text file
    # batch_size = 100  # Adjust batch size according to your needs and API limitations
    # for i in range(0, len(cities), batch_size):
    #     batch = cities[i : i + batch_size]
    #     locations = [(lat, lon) for _, _, lat, lon in batch]
    #     elevations = get_elevations(locations)
    #     for (city_id, name, lat, lon), elevation in zip(batch, elevations):
    #         if elevation is not None:
    #             update_elevation(db_path, city_id, elevation)
    #             logging.info(
    #                 f"Updated city: {name} (ID: {city_id}) with elevation: {elevation} meters"
    #             )
    #         else:
    #             logging.warning(
    #                 f"Failed to get elevation for city: {name} (ID: {city_id})"
    #             )
    #     time.sleep(1)  # To avoid hitting the API rate limit
    #


if __name__ == "__main__":
    db_path = (
        "/media/aumhren/susaTera/3.astro/_archive/pyswisseph.bu/atlas.db.bu/atlas.db"
    )
    main(db_path)
