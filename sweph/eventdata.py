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
        """get user input and prepare for swe"""
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        # attributes as widgets
        self.country = country
        self.city = city
        self.location = location
        self.name = name
        self.date_time = date_time
        self.timezone = None
        self.is_utc_now = False
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
            # controllder for focus lost
            focus_controller = Gtk.EventControllerFocus.new()
            widget.add_controller(focus_controller)
            focus_controller.connect(  # on focus lost
                "leave", lambda ctrl, cb=callback: cb(ctrl.get_widget())
            )

    def on_location_change(self, entry):
        """process location data (as string)
        3 allowed input formats :
        1. dms : 32 21 09 n 77 66 00 w 113 m
        2. decimal : 33.72 n 124.876 e
        3. signed decimal : -16.75 -72.678
        south & west are -ve : -16.75 -72.678"""
        location_name = entry.get_name()
        location = entry.get_text().strip()
        if location_name == "location one" and not location:
            self._notify.warning(
                f"\n\tmandatory data missing ({location_name})",
                source="eventdata",
                route=["terminal", "user"],
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
            # parse location data
            valid_chars = set("0123456789 -.nsewm")
            invalid_chars = set(location.lower()) - valid_chars
            if invalid_chars:
                raise ValueError(f"characters {sorted(invalid_chars)} not allowed")
            # break string into parts
            parts = location.lower().split()
            # detect direction : e(ast), s(outh), n(orth), w(est))
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
                    raise ValueError("missing direction indicators (n/s or e/w)")
                # split into latitude & longitude
                lat_parts = parts[: lat_dir_idx + 1]
                lon_parts = parts[lat_dir_idx + 1 : lon_dir_idx + 1]
                # get optional altitude
                alt = "0"
                if len(parts) > lon_dir_idx + 1:
                    # this code will select numeric part of altitude
                    alt = parts[lon_dir_idx + 1]
                    if not int(alt):
                        raise ValueError(
                            "altitude invalid : space between number & unit ?"
                        )
                # check if d-m-s or decimal
                try:
                    if not len(lat_parts) == len(lon_parts):
                        raise ValueError("latitude or longitude part missing")
                    elif len(lat_parts) == 2 and len(lon_parts) == 2:
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
                        if len(lat_parts) not in [3, 4] or len(lon_parts) not in [3, 4]:
                            raise ValueError("invalid deg-min-(sec) n/s e/w format")
                        lat_deg = int(lat_parts[0])
                        lat_min = int(lat_parts[1])
                        lat_sec = int(lat_parts[2]) if len(lat_parts) > 3 else 0
                        lat_dir = lat_parts[-1]

                        lon_deg = int(lon_parts[0])
                        lon_min = int(lon_parts[1])
                        lon_sec = int(lon_parts[2]) if len(lon_parts) > 3 else 0
                        lon_dir = lon_parts[-1]

                        lat = lat_deg + lat_min / 60 + lat_sec / 3600
                        lon = lon_deg + lon_min / 60 + lon_sec / 3600

                except (ValueError, IndexError) as e:
                    # re-raise to next level
                    raise ValueError(e)
            else:
                # signed decimal format
                try:
                    if len(parts) < 2:
                        raise ValueError("need at least latitude & longitude")
                    lat = float(parts[0])
                    lon = float(parts[1])
                    print(f"\n\t\tlat 2 : {lat} | lon 2 : {lon}")
                    # get optional altitude
                    alt = parts[2] if len(parts) > 2 else "0"
                    # determine direction from signs
                    lat_dir = "s" if lat < 0 else "n"
                    lon_dir = "w" if lon < 0 else "e"
                    # convert to d-m-s
                    lat_deg, lat_min, lat_sec = _decimal_to_dms(abs(lat))
                    lon_deg, lon_min, lon_sec = _decimal_to_dms(abs(lon))

                except ValueError as e:
                    # re-raise to next level
                    raise ValueError(e)
            # validate ranges & notify user on error
            if not (0 <= lat_deg <= 89):
                self._notify.warning(
                    "latitude degrees must be between 0 & 90",
                    source="eventdata",
                    route=["user"],
                )
                return
            if not (0 <= lat_min <= 59) or not (0 <= lat_sec <= 59):
                self._notify.warning(
                    "latitude minutes & seconds must be between 0 & 59",
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
                    "longitude minutes & seconds must be between 0 & 59",
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
            try:
                # validate as integer
                int(alt)
                print(f"\n\t\tint(alt) : {int(alt)} | type : {type(int(alt))}")
            except ValueError:
                self._notify.info(
                    "invalid altitude value : setting alt to 0 (string)",
                    source="eventdata",
                    route=["user"],
                    timeout=4,
                )
                alt = "0"
            # format final string
            location_formatted = (
                f"{lat_deg:02d} {lat_min:02d} {lat_sec:02d} {lat_dir} "
                f"{lon_deg:03d} {lon_min:02d} {lon_sec:02d} {lon_dir} "
                f"{alt.zfill(4)} m"
                if alt != "0"
                else f"{lat_deg:02d} {lat_min:02d} {lat_sec:02d} {lat_dir} "
                f"{lon_deg:03d} {lon_min:02d} {lon_sec:02d} {lon_dir} 0 m"
            )
            # update entry if text changed
            if location != location_formatted:
                entry.set_text(location_formatted)
            # get timezone from location
            tzf = TimezoneFinder()
            timezone_ = tzf.timezone_at(lat=lat, lng=lon)
            if timezone_:
                self.timezone = timezone_
            else:
                print("eventdata : timezone_ missing")
            self.old_location = location_formatted
            self._notify.success(
                "location valid & formatted",
                source="eventdata",
                route=["user", "terminal"],
            )
            # save data by event
            mainwindow = self._app.get_active_window()
            if location_name == "location one":
                # grab country & city
                if hasattr(mainwindow, "country_one"):
                    country = mainwindow.country_one.get_selected_item().get_string()
                if hasattr(mainwindow, "city_one"):
                    city = mainwindow.city_one.get_text()
                self.e1_chart["country"] = country
                self.e1_chart["city"] = city or ""
                # received data
                self.e1_swe["lat"] = lat
                self.e1_swe["lon"] = lon
                self.e1_swe["alt"] = int(alt)
                self.e1_chart["timezone"] = timezone_
                self.e1_chart["location"] = location_formatted
                msg_ = (
                    "event 1 location data updated"
                    # f"event 1 data updated\n\tlat : {lat} | lon : {lon} | alt : {alt}"
                    # f"\n\tlocation : {location_formatted}"
                    # f"\n\tcountry : {country} | city : {city} | timezone : {timezone_}"
                )
            else:
                # grab country & city
                if hasattr(mainwindow, "country_two"):
                    country = mainwindow.country_two.get_selected_item().get_string()
                if hasattr(mainwindow, "city_two"):
                    city = mainwindow.city_two.get_text()
                self.e2_chart["country"] = country
                self.e2_chart["city"] = city or ""
                # received data
                self.e2_swe["lat"] = lat
                self.e2_swe["lon"] = lon
                self.e2_swe["alt"] = int(alt)
                self.e2_chart["timezone"] = timezone_ or ""
                self.e2_chart["location"] = location_formatted or ""
                msg_ = (
                    "event 2 location data updated"
                    # f"event 2 data updated\n\tlat : {lat} | lon : {lon} | alt : {alt}"
                    # f"\n\tlocation : {location_formatted}"
                    # f"\n\tcountry : {country} | city : {city} | timezone : {timezone_}"
                )
            self._notify.success(
                msg_,
                source="eventdata",
                route=["terminal"],
            )
            return

        except Exception as e:
            self._notify.error(
                "\ninvalid location format : we accept"
                "\n1. deg-min-(sec) with direction : 32 21 (9) n 77 66 (11) w (alt (m))"
                "\n2. decimal with direction : 33.77 n 124.87 e (alt (m))"
                "\n3. decimal signed (s/w -ve & n/e +ve) : -16.76 72.678 (alt (m))"
                "\n\tsec & alt are optional"
                f"\nerror :\n{e}",
                source="eventdata",
                route=["terminal", "user"],
                timeout=4,
            )
            return

    def on_name_change(self, entry):
        """process title / name"""
        name_name = entry.get_name()
        name = entry.get_text().strip()
        if name_name == "name one" and not name:
            self._notify.warning(
                f"\n\tmandatory data missing ({name_name})",
                source="eventdata",
                route=["terminal", "user"],
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
                f"\n\t{name_name} too long : max 30 characters",
                source="eventdata",
                route=["terminal", "user"],
            )
            return

        self.old_name = name
        # save by event
        if name_name == "name one":
            self.e1_chart["name"] = name
            msg_ = f"event 1 name updated : {name}"
        else:
            self.e2_chart["name"] = name or ""
            msg_ = f"event 2 name updated : {name}"
        self._notify.success(
            msg_,
            source="eventdata",
            route=["terminal"],
        )

    def on_datetime_change(self, entry):
        """process date & time"""
        datetime_name = entry.get_name()
        print(f"ondatetimechange : name : {datetime_name}\n")
        date_time = entry.get_text().strip()
        # calling from ontimenow
        if self.is_utc_now:
            # get computer time
            dt_utc = datetime.now(timezone.utc).replace(microsecond=0)
            if self.timezone:
                dt_event = dt_utc.astimezone(ZoneInfo(self.timezone))
            else:
                dt_event = dt_utc
            # update datetime entry
            dt_event_str = dt_event.strftime("%Y-%m-%d %H:%M:%S")
            entry.set_text(dt_event_str)
            # save by event
            if datetime_name == "datetime one":
                self.e1_chart["datetime"] = dt_event_str
            else:
                self.e2_chart["datetime"] = dt_event_str or ""
            self._notify.debug(
                # f"parsing {datetime_name} utc ..."
                # f"\n\tparsed application time now utc : {dt_utc.strftime('%Y-%m-%d %H:%M:%S')}"
                f"\n\tset event location time now : {dt_event_str}",
                source="eventdata",
                route=["terminal"],
            )
            self.is_utc_now = False
        # not calling from ontimenow
        else:
            # event one date-time is mandatory
            if datetime_name == "datetime one" and not date_time:
                self._notify.warning(
                    f"\n\tmandatory data missing ({datetime_name})",
                    source="eventdata",
                    route=["terminal", "user"],
                )
                return
            if date_time == self.old_date_time:
                self._notify.debug(
                    "date-time not changed",
                    source="eventdata",
                    route=["terminal"],
                )
                return
            # validate datetime string
            else:
                """validate date-time data"""
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

                        return (
                            1 <= month <= 12 and 1 <= day <= day_count_for_month[month]
                        )

                    if not is_valid_date(year, month, day):
                        self._notify.warning(
                            f"{year}-{month}-{day} : date not valid"
                            "\n\tcheck month & day : ie february has 28 or 29 days",
                            source="eventdata",
                            route=["user"],
                        )
                        return

                    def is_valid_time(hour, minute, second):
                        return (
                            0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59
                        )

                    if not is_valid_time(hour, minute, second):
                        self._notify.warning(
                            f"{hour}:{minute}:{second} : time not valid",
                            source="eventdata",
                            route=["user"],
                        )
                        return
                    try:
                        """parse date-time data"""
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
                        if datetime_name == "datetime one":
                            self.e1_chart["datetime"] = dt_event_str
                        else:
                            self.e2_chart["datetime"] = dt_event_str or ""
                        self._notify.debug(
                            # f"parsing {datetime_name} event ..."
                            f"\n\tset event datetime : {dt_event}\n\tdt_utc : {dt_utc}",
                            source="eventdata",
                            route=["terminal"],
                        )

                    except ValueError as e:
                        self._notify.error(
                            f"invalid date-time\n\t{e}",
                            source="eventdata",
                            route=["terminal", "user"],
                        )
                        return

                except Exception:
                    self._notify.warning(
                        f"wrong date-time format for {datetime_name}"
                        "\n\twe only accept space-separated : yyyy mm dd HH MM SS"
                        "\n\t\tand - / . : for separators"
                        "\n\t(iso date-time, 24 hour format)",
                        source="eventdata",
                        route=["terminal", "user"],
                    )
                    return
        # all good : set new old date-time
        self.old_date_time = dt_event_str
        # calculate julian day
        jd_ut = swe.utc_to_jd(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour,
            dt_utc.minute,
            dt_utc.second,
            1,
        )
        if datetime_name == "datetime one":
            self.e1_swe["jd_ut"] = jd_ut
        else:
            self.e2_swe["jd_ut"] = jd_ut or None
        self._notify.debug(
            f"collected {datetime_name} julian day : {jd_ut}\n\n\tREADY TO ROCK",
            source="eventdata",
            route=["terminal"],
        )
        # todo set here e2 data to e1 if e2 datetime is not empty ?
        """if datetime two is not empty, user is interested in event two
           in this case datetime two is manadatory, the rest is optional, aka
           if exists > use it, else use event one data"""
        if self.e2_chart["datetime"] != "":
            self._notify.debug(
                f"datetime 2 not empty : {self.e2_chart['datetime']}"
                "merging e2 from e1 data"
            )
            self.e2_chart["country"] = (
                self.e2_chart["country"] or self.e1_chart["country"]
            )
            self.e2_chart["city"] = self.e2_chart["city"] or self.e1_chart["city"]
            self.e2_chart["location"] = (
                self.e2_chart["location"] or self.e1_chart["location"]
            )
            self.e2_chart["timezone"] = (
                self.e2_chart["timezone"] or self.e1_chart["timezone"]
            )
            self.e2_chart["name"] = self.e2_chart["name"] or self.e1_chart["name"]
            self.e2_swe["lat"] = self.e2_swe["lat"] or self.e1_swe["lat"]
            self.e2_swe["lon"] = self.e2_swe["lon"] or self.e1_swe["lon"]
            self.e2_swe["alt"] = self.e2_swe["alt"] or self.e1_swe["alt"]
            self.e2_swe["jd_ut"] = self.e2_swe["jd_ut"] or self.e1_swe["jd_ut"]
            self._notify.debug(
                "datetime 2 data merged with datetime 1 data",
                source="eventdata",
                route=["terminal"],
            )
            # debug-print all data
            self._notify.debug(
                f"event 1 data\n{self.e1_chart}\n{self.e1_swe}",
                source="eventdata",
                route=["terminal"],
            )
