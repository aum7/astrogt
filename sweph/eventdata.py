# ruff: noqa: E402
import swisseph as swe
import re
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
from ui.helpers import _decimal_to_dms


class EventData:
    def __init__(
        self,
        name,
        country,
        city,
        location=None,
        date_time=None,
        app=None,
    ):
        """get user input and puf! puf! into sweph"""
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        # attributes
        self.country = country
        self.city = city
        self.location = location
        self.name = name
        self.date_time = date_time
        self.timezone = None
        self.is_utc = False
        # self.jd_ut = None
        self.old_name = ""
        self.old_date_time = ""
        self.old_location = ""
        # separate data by event
        self.e1_swe = {}
        self.e1_chart = {}
        self.e2_swe = {}
        self.e2_chart = {}
        # connect signals for entry completion
        for widget, callback in [
            (self.name, self.on_name_change),
            (self.location, self.on_location_change),
            (self.date_time, self.on_datetime_change),
        ]:
            widget.connect("activate", callback)  # [enter]
            focus_controller = Gtk.EventControllerFocus.new()
            widget.add_controller(focus_controller)
            focus_controller.connect(  # on focus lost
                "leave", lambda ctrl, cb=callback: cb(ctrl.get_widget())
            )

    def on_location_change(self, entry):
        """process location data (as string)
        3 allowed input formats :
        1. dms : "32 21 09 n 77 66 00 w 113 m"
        2. decimal : "33.72 n 124.876 e"
        3. signed decimal : "-16.75 -72.678"
        south & west are -ve : -16.75 -72.678"""

        location = entry.get_text().strip()
        if not location:
            self._notify.warning(
                "data missing (location)",
                source="eventdata",
                route=["user"],
            )
            return
        if location == self.old_location:
            self._notify.debug(
                "location not changed",
                source="eventdata",
                route=["terminal"],
            )
            return
        try:
            parts = location.lower().split()
            # detect direction (e, s, n, w)
            has_direction = any(d in "nsew" for d in location.lower())

            if has_direction:
                lat_dir_idx = -1
                lon_dir_idx = -1
                for i, part in enumerate(parts):
                    if part in "ns":
                        lat_dir_idx = i
                    elif part in "ew":
                        lon_dir_idx = i
                if lat_dir_idx == -1 or lon_dir_idx == -1:
                    self._notify.warning(
                        "missing direction indicators (n/s & e/w)",
                        source="eventdata",
                        route=["user"],
                    )
                    return
                # split into latitude & longitude
                lat_parts = parts[: lat_dir_idx + 1]
                lon_parts = parts[lat_dir_idx + 1 : lon_dir_idx + 1]
                # get optional altitude
                alt = "0"
                if len(parts) > lon_dir_idx + 1:
                    alt = parts[lon_dir_idx + 1]
                # check if d-m-s or decimal
                try:
                    if len(lat_parts) == 2 and len(lon_parts) == 2:
                        # decimal with direction format
                        lat = float(lat_parts[0])
                        lat_dir = lat_parts[1]
                        lon = float(lon_parts[0])
                        lon_dir = lon_parts[1]
                        # convert to deg-min-sec
                        lat_deg, lat_min, lat_sec = _decimal_to_dms(abs(lat))
                        lon_deg, lon_min, lon_sec = _decimal_to_dms(abs(lon))
                    else:
                        # d-m-s format : seconds are optional
                        if len(lat_parts) < 3 or len(lon_parts) < 3:
                            self._notify.warning(
                                "invalid deg-min-(sec) n/s e/w format",
                                source="eventdata",
                                route=["user"],
                            )
                            return False

                        lat_deg = int(lat_parts[0])
                        lat_min = int(lat_parts[1])
                        lat_sec = int(lat_parts[2]) if len(lat_parts) > 3 else 0
                        lat_dir = lat_parts[-1]

                        lon_deg = int(lon_parts[0])
                        lon_min = int(lon_parts[1])
                        lon_sec = int(lon_parts[2]) if len(lon_parts) > 3 else 0
                        lon_dir = lon_parts[-1]

                except (ValueError, IndexError) as e:
                    self._notify.error(
                        f"error parsing coordinates :\n\t{str(e)}",
                        source="eventdata",
                        route=["user"],
                    )
                    return
            else:
                # signed decimal format
                try:
                    if len(parts) < 2:
                        self._notify.warning(
                            "need min latitude & longitude",
                            source="eventdata",
                            route=["user"],
                        )
                        return False

                    lat = float(parts[0])
                    lon = float(parts[1])
                    # get optional altitude
                    alt = parts[2] if len(parts) > 2 else "/"
                    # determine direction from signs
                    lat_dir = "s" if lat < 0 else "n"
                    lon_dir = "w" if lon < 0 else "e"
                    # convert to d-m-s
                    lat_deg, lat_min, lat_sec = _decimal_to_dms(abs(lat))
                    lon_deg, lon_min, lon_sec = _decimal_to_dms(abs(lon))

                except ValueError as e:
                    self._notify.error(
                        f"invalid decimal coordinates :\n\t{str(e)}",
                        source="eventdata",
                        route=["user"],
                    )
                    return
            # validate ranges
            if not (0 <= lat_deg <= 89):
                self._notify.warning(
                    "latitude degrees must be between 0 & 90",
                    source="eventdata",
                    route=["user"],
                )
                return
            if not (0 <= lat_min <= 59) or not (0 <= lat_sec <= 59):
                self._notify.warning(
                    "minutes & seconds must be between 0 & 59",
                    source="eventdata",
                    route=["user"],
                )
                return
            if lat_dir not in ["n", "s"]:
                self._notify.warning(
                    "latitude direction must be n(orth) or s(outh)",
                    source="eventdata",
                    route=["user"],
                )
                return

            if not (0 <= lon_deg <= 179):
                self._notify.warning(
                    "longitude degrees must be between 0 and 179",
                    source="eventdata",
                    route=["user"],
                )
                return
            if not (0 <= lon_min <= 59) or not (0 <= lon_sec <= 59):
                self._notify.warning(
                    "minutes & seconds must be between 0 & 59",
                    source="eventdata",
                    route=["user"],
                )
                return
            if lon_dir not in ["e", "w"]:
                self._notify.warning(
                    "longitude direction must be e(ast) or w(est)",
                    source="eventdata",
                    route=["user"],
                )
                return
            # try to convert altitude to int if present
            try:
                alt = str(int(alt))
            except ValueError:
                self._notify.info(
                    "missing altitude value ; setting alt to 0",
                    source="eventdata",
                    route=["user"],
                    timeout=3,
                )
                alt = "0"
            # format final string
            location_formatted = (
                f"{lat_deg:02d} {lat_min:02d} {lat_sec:02d} {lat_dir} "
                f"{lon_deg:03d} {lon_min:02d} {lon_sec:02d} {lon_dir} "
                f"{alt.zfill(4)} m"
                if alt != "0"
                else f"{lat_deg:02d} {lat_min:02d} {lat_sec:02d} {lat_dir} "
                f"{lon_deg:03d} {lon_min:02d} {lon_sec:02d} {lon_dir} 0"
            )
            # update entry if text changed
            if location != location_formatted:
                entry.set_text(location_formatted)
            # get timezone from location
            tzf = TimezoneFinder()
            timezone_ = tzf.timezone_at(lat=lat, lng=lon)
            self.timezone = timezone_

            self.old_location = location_formatted
            # self._notify.success(
            #     "location valid & formatted",
            #     source="eventdata",
            #     route=["user", "terminal"],
            # )
            # save data by event
            if entry.get_name() == "location one":
                self.e1_swe["lat"] = lat
                self.e1_swe["lon"] = lon
                self.e1_swe["alt"] = alt
                self.e1_chart["timezone"] = timezone_
                self.e1_chart["location"] = location_formatted
                msg_ = {
                    f"event 1 data updated\n\tlat : {lat}\n\tlon : {lon}"
                    f"\n\talt : {alt}\n\tlocation : {location_formatted}"
                    f"\n\ttimezone : {timezone_}"
                }
            else:
                self.e2_swe["lat"] = lat
                self.e2_swe["lon"] = lon
                self.e2_swe["alt"] = alt
                self.e2_chart["timezone"] = timezone_
                self.e2_chart["location"] = location_formatted
                msg_ = {
                    f"event 2 data updated\n\tlat : {lat}\n\tlon : {lon}"
                    f"\n\talt : {alt}\n\tlocation : {location_formatted}"
                    f"\n\ttimezone : {timezone_}"
                }
            self._notify.success(
                msg_,
                source="eventdata",
                route=["terminal"],
            )

        except Exception as e:
            self._notify.error(
                "invalid location format : we accept"
                "\n1. deg-min-(sec) with direction : 32 21 (9) n 77 66 (11) w (alt)"
                "\n\tsec & alt are optional"
                "\n2. decimal with direction : 33.77 n 124.87 e (alt)"
                "\n3. decimal signed : -16.76 -72.678 (alt)"
                "\n\talt is optional"
                f"error :\n\t{str(e)}",
                source="eventdata",
                route=["user"],
            )
            return

    def on_name_change(self, entry):
        """process title / name"""
        name = entry.get_text().strip()
        if not name:
            self._notify.warning(
                "data missing (name)",
                source="eventdata",
                route=["user"],
            )
            return
        if name == self.old_name:
            self._notify.debug(
                "name not changed",
                source="eventdata",
                route=["terminal"],
            )
            return
        if len(name) > 30:
            self._notify.warning(
                "name too long : max 30 characters",
                source="eventdata",
                route=["user"],
            )
            return

        self.old_name = name
        # save by event
        if entry.get_name() == "name one":
            self.e1_chart["name"] = name
            msg_ = f"event 1 name updated : {name}"
        else:
            self.e2_chart["name"] = name
            msg_ = f"event 2 name updated : {name}"
        self._notify.success(
            msg_,
            source="eventdata",
            route=["terminal"],
        )

    def on_datetime_change(self, entry):
        """process date & time"""
        mainwindow = self._app.get_active_window()
        # country1 = getattr(mainwindow, "country_one")
        # print(f"country one : {country1.get_selected_item().get_string()}")
        # city1 = getattr(mainwindow, "city_one")
        # print(f"city one : {city1.get_text()}")

        date_time = entry.get_text().strip()
        if not date_time:
            self._notify.warning(
                "data missing (date-time)",
                source="eventdata",
                route=["user"],
            )
            return
        if date_time == self.old_date_time:
            self._notify.debug(
                "date-time not changed",
                source="eventdata",
                route=["terminal"],
            )
            return
        # validate datetime
        try:
            # check characters
            valid_chars = set("0123456789 -/.:")
            invalid_chars = set(date_time) - valid_chars
            if invalid_chars:
                self._notify.warning(
                    f"date-time : characters {sorted(invalid_chars)} not allowed",
                    source="eventdata",
                    route=["user"],
                )
                return
            # huston we have data
            is_year_negative = date_time.lstrip().startswith("-")
            # print(f"eventdata : year negative : {is_year_negative}")
            parts = [p for p in re.split("[ -/.:]+", date_time) if p]
            if len(parts) < 5 or len(parts) > 6:
                self._notify.warning(
                    "wrong data count : 6 or 5 (if no seconds) time units expected"
                    "\n\tie 1999 11 12 13 14",
                    source="eventdata",
                    route=["user"],
                )
                return
                # handle year
            try:
                year = int(parts[0])
                if is_year_negative:
                    year = -abs(year)
                # print(f"year : {year}")
                # swiseph year range
                if not -13200 <= year <= 17191:
                    self._notify.warning(
                        "year out of sweph range (-13.200 - 17.191)",
                        source="eventdata",
                        route=["user"],
                    )
                    return

            except ValueError:
                self._notify.error(
                    "invalid year format",
                    source="eventdata",
                    route=["user"],
                )
                return

            if len(parts) == 5:
                # add seconds
                parts.append("00")

            _, month, day, hour, minute, second = map(int, parts)

            # check if date_time is valid day
            def is_valid_date(year, month, day):
                day_count_for_month = [
                    # 0 added to match number with month
                    0,
                    31,
                    28,
                    31,
                    30,
                    31,
                    30,
                    31,
                    31,
                    30,
                    31,
                    30,
                    31,
                ]
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    day_count_for_month[2] = 29

                return 1 <= month <= 12 and 1 <= day <= day_count_for_month[month]

            if not is_valid_date(year, month, day):
                self._notify.warning(
                    f"{year}-{month}-{day} : date not valid"
                    "\n\tcheck month & day : ie february has 28 or 29 days",
                    source="eventdata",
                    route=["user"],
                )
                return

            def is_valid_time(hour, minute, second):
                return 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59

            if not is_valid_time(hour, minute, second):
                self._notify.warning(
                    f"{hour}:{minute}:{second} : time not valid",
                    source="eventdata",
                    route=["user"],
                )
                return

            try:
                # if year <= -10000:
                #     Y = f"-{abs(year)}"
                # elif year < 0:
                #     Y = f"-{abs(year):04d}"
                # elif year >= 0:
                #     Y = f"{year:04d}"
                # M = f"{month:02d}"
                # D = f"{day:02d}"
                # h = f"{hour:02d}"
                # m = f"{minute:02d}"
                # s = f"{second:02d}"

                # formatted = f"{Y}-{M}-{D} {h}:{m}:{s}"
                # dt_utc = None
                # parse datetime : utc vs event vs computer time
                if self.is_utc:
                    # get computer time
                    dt_utc_now = datetime.now(timezone.utc).replace(microsecond=0)
                    dt_utc = dt_utc_now
                    if self.timezone:
                        dt_event = dt_utc_now.astimezone(ZoneInfo(self.timezone))
                    # update datetime entry
                    dt_event_str = dt_event.strftime("%Y-%m-%d %H:%M:%S")
                    entry.set_text(dt_event_str)
                    if entry.name == "datetime one":
                        self.e1_chart["datetime"] = dt_event_str
                    else:
                        self.e2_chart["datetime"] = dt_event_str
                    self._notify.debug(
                        f"parsing {entry.name} utc ..."
                        f"\n\tparsed application time now utc : {dt_utc_now}"
                        f"\n\tset event location time now : {dt_event}",
                        source="eventdata",
                        route=["terminal"],
                    )
                    self.is_utc = False
                else:
                    # get datetime string
                    dt_str = entry.get_text()
                    # parse to datetime
                    dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    # convert to event location timezone
                    if self.timezone:
                        dt_event = dt_naive.astimezone(ZoneInfo(self.timezone))
                    dt_utc = dt_event.astimezone(timezone.utc)
                    # update datetime entry
                    dt_event_str = dt_event.strftime("%Y-%m-%d %H:%M:%S")
                    entry.set_text(dt_event_str)
                    if entry.name == "datetime one":
                        self.e1_chart["datetime"] = dt_event_str
                    else:
                        self.e2_chart["datetime"] = dt_event_str
                    self._notify.debug(
                        f"parsing {entry.name} event ..."
                        f"\n\tparsed & set event datetime : {dt_event}\n\tdt_utc : {dt_utc}",
                        source="eventdata",
                        route=["terminal"],
                    )
                # calculate julian day
                jd_ut = swe.utc_to_jd(year, month, day, hour, minute, second, 1)
                if entry.name == "datetime one":
                    self.e1_swe["jd_ut"] = jd_ut
                else:
                    self.e2_swe["jd_ut"] = jd_ut
                self._notify.debug(
                    f"collected {entry.name} julian day : {jd_ut}\n\n\tREADY TO ROCK",
                    source="eventdata",
                    route=["terminal"],
                )

            except ValueError as e:
                self._notify.error(
                    f"invalid date-time\n\t{e}",
                    source="eventdata",
                    route=["user"],
                )
                return

        except Exception:
            self._notify.warning(
                "wrong date-time format"
                "\nwe only accept space-separated : yyyy mm dd HH MM SS"
                "\n\tand - / . : for separators"
                "\n(iso date-time, 24 hour format)",
                source="eventdata",
                route=["user"],
            )
            return

    # def collect_event_data(self):
    #     """values from all entries needed for an event"""
    #     name_value = self.name.get_text().strip() if self.name else ""
    #     country_value = None
    #     # get country
    #     if self.country:
    #         selected = self.country.get_selected()
    #         model = self.country.get_model()
    #         if model and selected >= 0:
    #             country_value = model.get_string(selected)
    #     # get city
    #     city_value = None
    #     if self.city:
    #         city_value = self.city.get_text().strip()
    #     # check for empty values
    #     location_value = self.location.get_text().strip() if self.location else ""
    #     date_time_value = self.date_time.get_text().strip() if self.date_time else ""
    #     jd_ut_value = self.jd_ut
    #     return {
    #         "name": name_value,
    #         "country": country_value,
    #         "city": city_value,
    #         "location": location_value,
    #         "date_time": date_time_value,
    #         "jd_ut": jd_ut_value,
    #     }
