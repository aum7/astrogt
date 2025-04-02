# ruff: noqa: E402
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
from ui.helpers import _decimal_to_dms, _validate_datetime


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
        # flag for no validation needed
        self.is_hotkey_arrow = False
        # self.jd_ut = None
        self.old_name = ""
        self.old_date_time = ""
        self.old_location = ""
        # separate data by event
        self._app.e1_swe = {}
        self._app.e1_chart = {}
        self._app.e2_swe = {}
        self._app.e2_chart = {}
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
                f"\n\tmandatory data missing : {location_name}",
                source="eventdata",
                route=["terminal", "user"],
            )
            return
        if location == self.old_location:
            self._notify.debug(
                f"{location_name} not changed",
                source="eventdata",
                route=["terminal"],
            )
            return
        try:
            # parse location data
            valid_chars = set("0123456789 -.nsewm")
            invalid_chars = set(location.lower()) - valid_chars
            if invalid_chars:
                raise ValueError(
                    f"{location_name} characters {sorted(invalid_chars)} not allowed"
                )
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
                            f"{location_name} altitude invalid : space between number & unit ?"
                        )
                # check if d-m-s or decimal
                try:
                    if not len(lat_parts) == len(lon_parts):
                        raise ValueError(
                            f"{location_name} latitude or longitude part missing"
                        )
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
                            raise ValueError(
                                f"{location_name} invalid deg-min-(sec) n/s e/w format"
                            )
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
                        raise ValueError(
                            f"{location_name} : need at least latitude & longitude"
                        )
                    lat = float(parts[0])
                    lon = float(parts[1])
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
                    f"{location_name}\n\tlatitude degrees must be between 0 & 90",
                    source="eventdata",
                    route=["user"],
                )
                return
            if not (0 <= lat_min <= 59) or not (0 <= lat_sec <= 59):
                self._notify.warning(
                    f"{location_name}\n\tlatitude minutes & seconds must be between 0 & 59",
                    source="eventdata",
                    route=["user"],
                )
                return
            if lat_dir not in ["n", "s"]:
                self._notify.warning(
                    f"{location_name}\n\tlatitude direction must be n(orth) or s(outh)",
                    source="eventdata",
                    route=["user"],
                )
                return
            if not (0 <= lon_deg <= 179):
                self._notify.warning(
                    f"{location_name}\n\tlongitude degrees must be between 0 and 179",
                    source="eventdata",
                    route=["user"],
                )
                return
            if not (0 <= lon_min <= 59) or not (0 <= lon_sec <= 59):
                self._notify.warning(
                    f"{location_name}\n\tlongitude minutes & seconds must be between 0 & 59",
                    source="eventdata",
                    route=["user"],
                )
                return
            if lon_dir not in ["e", "w"]:
                self._notify.warning(
                    f"{location_name}\n\tlongitude direction must be e(ast) or w(est)",
                    source="eventdata",
                    route=["user"],
                )
                return
            try:
                # validate as integer
                int(alt)
                if not int(alt):
                    self._notify.error(
                        f"{location_name} int(alt) : {int(alt)} failed",
                        source="eventdata",
                        route=["terminal", "user"],
                        timeout=4,
                    )
            except ValueError:
                self._notify.info(
                    f"{location_name}\n\tinvalid altitude value : setting alt to 0 (string)",
                    source="eventdata",
                    route=["terminal", "user"],
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
                self._notify.debug(
                    "timezone_ missing",
                    source="eventdata",
                    route=["terminal"],
                )
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
                self._app.e1_chart["country"] = country
                self._app.e1_chart["city"] = city or ""
                # received data
                self._app.e1_swe["lat"] = lat
                self._app.e1_swe["lon"] = lon
                self._app.e1_swe["alt"] = int(alt)
                self._app.e1_chart["timezone"] = timezone_
                self._app.e1_chart["location"] = location_formatted
                msg_ = (
                    # "event 1 location data updated"
                    "event 1 location updated"
                    f"\n\tlat : {self._app.e1_swe.get('lat')} "
                    f"| lon : {self._app.e1_swe.get('lon')} "
                    f"| alt : {self._app.e1_swe.get('alt')}"
                    f"\n\tlocation : {self._app.e1_chart.get('location')}"
                    f"\n\tcountry : {self._app.e1_chart.get('country')} "
                    f"| city : {self._app.e1_chart.get('city')} "
                    f"| timezone : {self._app.e1_chart.get('timezone')}"
                )
            else:
                # grab country & city
                if hasattr(mainwindow, "country_two"):
                    country = mainwindow.country_two.get_selected_item().get_string()
                if hasattr(mainwindow, "city_two"):
                    city = mainwindow.city_two.get_text()
                self._app.e2_chart["country"] = country
                self._app.e2_chart["city"] = city or ""
                # received data
                self._app.e2_swe["lat"] = lat
                self._app.e2_swe["lon"] = lon
                self._app.e2_swe["alt"] = int(alt)
                self._app.e2_chart["timezone"] = timezone_ or ""
                self._app.e2_chart["location"] = location_formatted or ""
                msg_ = (
                    # "event 2 location data updated"
                    "event 2 location updated"
                    f"\n\tlat : {self._app.e2_swe.get('lat')} "
                    f"| lon : {self._app.e2_swe.get('lon')} "
                    f"| alt : {self._app.e2_swe.get('alt')}"
                    f"\n\tlocation : {self._app.e2_chart.get('location')}"
                    f"\n\tcountry : {self._app.e2_chart.get('country')} "
                    f"| city : {self._app.e2_chart.get('city')} "
                    f"| timezone : {self._app.e2_chart.get('timezone')}"
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
                f"\n\tmandatory data missing : {name_name}",
                source="eventdata",
                route=["terminal", "user"],
            )
            return
        if name == self.old_name:
            self._notify.debug(
                f"{name_name} not changed",
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
            self._app.e1_chart["name"] = name
            msg_ = f"event 1 name updated : {self._app.e1_chart.get('name')}"
        else:
            self._app.e2_chart["name"] = name or ""
            msg_ = f"event 2 name updated : {self._app.e2_chart.get('name')}"
        self._notify.success(
            msg_,
            source="eventdata",
            route=["terminal"],
        )

    def on_datetime_change(self, entry):
        """process date & time"""
        datetime_name = entry.get_name()
        date_time = entry.get_text().strip()
        # we need datetime utc & for event location
        dt_utc = None
        dt_event = None
        # calling from ontimenow
        if self.is_utc_now:
            """get computer time"""
            dt_utc = datetime.now(timezone.utc).replace(microsecond=0)
            if self.timezone:
                dt_event = dt_utc.astimezone(ZoneInfo(self.timezone))
                self._notify.info(
                    f"\n\t{datetime_name} timezone found"
                    f"\n\tusing utc now : "
                    f"\n\t{dt_event.strftime('%Y-%m-%d %H:%M:%S')}"
                    "\n\tlocation should be set to calculate timezone",
                    source="eventdata",
                    route=["terminal", "user"],
                )
            else:
                dt_event = dt_utc
                self._notify.info(
                    f"\n\t{datetime_name} no timezone found"
                    f"\n\tusing utc now : "
                    f"\n\t{dt_event.strftime('%Y-%m-%d %H:%M:%S')}"
                    "\n\tlocation should be set to calculate timezone",
                    source="eventdata",
                    route=["terminal", "user"],
                )
            self.is_utc_now = False
        # datetime changed with hotkey arrow left / right : validation not needed
        elif self.is_hotkey_arrow:
            try:
                # get datetime string
                dt_str = entry.get_text()
                # datetime string should be valid iso format
                # parse to datetime
                dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                # convert to event location timezone
                if self.timezone:
                    dt_event = dt_naive.replace(tzinfo=ZoneInfo(self.timezone))
                    dt_utc = dt_event.astimezone(timezone.utc)
                else:
                    dt_event = dt_naive.replace(tzinfo=timezone.utc)
                    dt_utc = dt_event
                    self._notify.info(
                        f"\n\t{datetime_name} no timezone : using utc"
                        "\n\tlocation should be set to calculate timezone",
                        source="eventdata",
                        route=["terminal", "user"],
                    )
            except Exception as e:
                self._notify.warning(
                    f"\twrong {datetime_name}\n\terror\n\t{e}",
                    source="eventdata",
                    route=["terminal", "user"],
                )
                return
            self.is_hotkey_arrow = False
        # string from manual input
        else:
            # event one date-time is mandatory
            if datetime_name == "datetime one" and not date_time:
                self._notify.warning(
                    f"\n\tmandatory data missing ({datetime_name})",
                    source=f"eventdata : {datetime_name}",
                    route=["terminal", "user"],
                )
                return
            # data changed
            if date_time == self.old_date_time:
                self._notify.debug(
                    "date-time not changed",
                    source=f"eventdata : {datetime_name}",
                    route=["terminal"],
                )
                return
            try:
                # validate datetime string from manual input
                # dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                result = _validate_datetime(self, date_time)
                if not result:
                    raise ValueError("datetime validation failed")
                self._notify.info(
                    "manual entry valid",
                    source="eventdata",
                    route=["terminal"],
                )
                Y, M, D, h, m, s = result
                # manual input : assume event time
                dt_naive = datetime(Y, M, D, h, m, s)
                if self.timezone:
                    dt_event = dt_naive.replace(tzinfo=ZoneInfo(self.timezone))
                    dt_utc = dt_event.astimezone(timezone.utc)
                else:
                    dt_event = dt_naive.replace(tzinfo=timezone.utc)
                    dt_utc = dt_event
                    self._notify.info(
                        f"\n\t{datetime_name} no timezone : using utc"
                        "\n\tlocation should be set to calculate timezone",
                        source="eventdata",
                        route=["terminal", "user"],
                    )
            except Exception as e:
                self._notify.warning(
                    f"\twrong {datetime_name}"
                    "\n\twe accept space-separated : yyyy mm dd HH MM SS"
                    "\n\t\tand - : for separators (iso date-time, 24 hour format)"
                    f"\n\terror\n\t{e}",
                    source="eventdata",
                    route=["terminal", "user"],
                )
                return
        # update datetime entry
        if dt_event:
            dt_event_str = dt_event.strftime("%Y-%m-%d %H:%M:%S")
        entry.set_text(dt_event_str)
        if datetime_name == "datetime one":
            self._app.e1_chart["datetime"] = dt_event_str
            msg_ = f"{datetime_name} updated : {self._app.e1_chart.get('datetime')}"
        else:
            self._app.e2_chart["datetime"] = dt_event_str
            msg_ = f"{datetime_name} updated : {self._app.e2_chart.get('datetime')}"
        self._notify.debug(
            msg_,
            source="eventdata",
            route=["terminal"],
        )
        # all good : set new old date-time
        self.old_date_time = dt_event_str
        # calculate julian day
        if dt_utc:
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
            self._app.e1_swe["jd_ut"] = jd_ut
            jd_ut_ = self._app.e1_swe.get("jd_ut")
            if (
                jd_ut_ is not None
                and isinstance(jd_ut_, (tuple, list))
                and len(jd_ut_) > 1
            ):
                msg_ = f"{datetime_name} julian day updated : {jd_ut_[1]}"
        else:
            self._app.e2_swe["jd_ut"] = jd_ut or None
            jd_ut_ = self._app.e2_swe.get("jd_ut")
            if (
                jd_ut_ is not None
                and isinstance(jd_ut_, (tuple, list))
                and len(jd_ut_) > 1
            ):
                msg_ = f"{datetime_name} julian day updated : {jd_ut_[1]}"
        self._notify.debug(
            f"{msg_}\n\tREADY TO ROCK",
            source="eventdata",
            route=["terminal"],
        )
        """if datetime two is not empty, user is interested in event two
           in this case datetime two is manadatory, the rest is optional, aka
           if exists > use it, else use event one data"""
        if self._app.e2_chart.get("datetime") is None:
            self._notify.debug(
                "datetime 2 is none : user not interested : extiting ...",
                source="eventdata",
                route=["terminal"],
            )
        elif self._app.e2_chart.get("datetime", "") != "":
            self._notify.debug(
                f"\n\tdatetime 2 not empty : {self._app.e2_chart.get('datetime')} : "
                "merging e2 from e1 data",
                source="eventdata",
                route=["terminal"],
            )
            self._app.e2_chart["country"] = self._app.e2_chart.get(
                "country"
            ) or self._app.e1_chart.get("country")
            self._app.e2_chart["city"] = self._app.e2_chart.get(
                "city"
            ) or self._app.e1_chart.get("city")
            self._app.e2_chart["location"] = self._app.e2_chart.get(
                "location"
            ) or self._app.e1_chart.get("location")
            self._app.e2_chart["timezone"] = self._app.e2_chart.get(
                "timezone"
            ) or self._app.e1_chart.get("timezone")
            self._app.e2_chart["name"] = self._app.e2_chart.get(
                "name"
            ) or self._app.e1_chart.get("name")
            self._app.e2_swe["lat"] = self._app.e2_swe.get(
                "lat"
            ) or self._app.e1_swe.get("lat")
            self._app.e2_swe["lon"] = self._app.e2_swe.get(
                "lon"
            ) or self._app.e1_swe.get("lon")
            self._app.e2_swe["alt"] = self._app.e2_swe.get(
                "alt"
            ) or self._app.e1_swe.get("alt")
            self._app.e2_swe["jd_ut"] = self._app.e2_swe.get(
                "jd_ut"
            ) or self._app.e1_swe.get("jd_ut")
            self._notify.debug(
                "datetime 2 data merged with datetime 1 data",
                source="eventdata",
                route=["terminal"],
            )
        # debug-print all data
        import json

        self._notify.debug(
            "\n\n----- COLLECTED DATA -----"
            f"\nchart 1\t{json.dumps(self._app.e1_chart, sort_keys=True, indent=4)}"
            f"\n  swe 1\t{json.dumps(self._app.e1_swe, sort_keys=True, indent=4)}"
            "\n--------------------------"
            f"\nchart 2\t{json.dumps(self._app.e2_chart, sort_keys=True, indent=4)}"
            f"\n  swe 2\t{json.dumps(self._app.e2_swe, sort_keys=True, indent=4)}"
            "\n--------------------------",
            source="eventdata",
            route=["terminal"],
        )
        # pad year with leading zeros if year has less than 4 digits
        # try:
        #     year_part, rest = dt_str.split("-", 1)
        #     print(f"year_part : {year_part} | rest : {rest}")
        # except ValueError:
        # invalid format, let strptime raise an error below
        #     pass
        # else:
        #     if len(year_part) < 4:
        #         print(f"len(year_part) : {len(year_part)}")
        #         year_part = year_part.zfill(4)
        #         print(f"year_part padded : {year_part}")
        #         dt_str = f"{year_part}-{rest}"
        #         print(f"dt_str padded : {dt_str}")
        # todo manage years > 0 & negative years
        # fmts = ("%Y-%m-%d %H:%M:%S", "%Y %m %d %H %M %S")
        # for fmt in fmts:
        #     try:
        #         dt = datetime.datetime.strptime(date_time_str, fmt)
        #         return dt
        #     except ValueError:
        #         continue
        # return None
