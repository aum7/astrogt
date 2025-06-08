# sweph/eventdata.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
from ui.helpers import _decimal_to_dms
from sweph.swetime import validate_datetime, naive_to_utc, utc_to_jd
from sweph.calculations.positions import calculate_positions


class EventData:
    """get event data from user input"""

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
        # attributes for date-time conversion
        self.timezone = None  # string
        self.tz_offset = None  # float
        # longitude for local apparent | mean time
        self.lon = None  # float
        # flag for no validation needed
        self.is_hotkey_now = False
        self.old_name = ""
        self.old_date_time = ""
        self.old_location = ""
        # separate data by event
        self._app.e1_sweph = {}
        self._app.e1_chart = {}
        self._app.e2_sweph = {}
        self._app.e2_chart = {}
        # connect signals for entry completion
        for widget, callback in [
            (self.name, self.on_name_change),
            (self.location, self.on_location_change),
            (self.date_time, self.on_datetime_change),
        ]:
            widget.connect("activate", callback)  # [enter]
            # controller for focus lost
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
        mainwindow = self._app.get_active_window()
        if not location:
            if location_name == "location one":
                self._notify.warning(
                    f"\n\tmandatory data missing : {location_name}",
                    source="eventdata",
                    route=["terminal", "user"],
                )
                return
            elif location_name == "location two":
                # handle empty location : erase location 2 data
                self._app.e2_chart["location"] = ""
                self._app.e2_chart["timezone"] = ""
                self._app.e2_sweph["lat"] = None
                self._app.e2_sweph["lon"] = None
                self._app.e2_sweph["alt"] = None
                self.old_location = ""
                self._notify.info(
                    f"{location_name} cleared",
                    source="eventdata",
                    route=["terminal"],
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
                    "\n\twe accept : 0123456789 -.nsewm"
                    "\n\tn / s / e / w = n(orth) / s(outh) / e(ast) / w(est) direction"
                    "\n\tm = meters (altitude)"
                )
            # break string into parts
            parts = location.lower().split()
            # detect direction : e(ast), s(outh), n(orth), w(est))
            has_direction = any(d in "nsew" for d in location.lower())

            if has_direction:
                # then : d-m-s | decimal with direction
                lat_dir_idx = -1
                lon_dir_idx = -1
                for i, part in enumerate(parts):
                    if part in "ns":
                        lat_dir_idx = i
                    elif part in "ew":
                        lon_dir_idx = i
                if lat_dir_idx == -1 or lon_dir_idx == -1:
                    raise ValueError(
                        f"{location_name} missing direction indicators (n/s or e/w)"
                    )
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
                    # re-raise to previous level
                    raise ValueError(e)
            # validate ranges & notify user on error
            try:
                if not (0 <= lat_deg <= 89):
                    raise ValueError("latitude degrees must be in 0..89 range")
                if not (0 <= lat_min <= 59) or not (0 <= lat_sec <= 59):
                    raise ValueError(
                        "latitude minutes & seconds must be in 0..59 range"
                    )
                if lat_dir not in ["n", "s"]:
                    raise ValueError("latitude direction must be n(orth) or s(outh)")
                if not (0 <= lon_deg <= 179):
                    raise ValueError("longitude degrees must be in 0..179 range")
                if not (0 <= lon_min <= 59) or not (0 <= lon_sec <= 59):
                    raise ValueError(
                        "longitude minutes & seconds must be in 0..59 range"
                    )
                if lon_dir not in ["e", "w"]:
                    raise ValueError("longitude direction must be e(ast) or w(est)")
            except ValueError as e:
                # re-raise to next level
                raise ValueError(e)
            try:
                # need pass validatng as integer
                int(alt)
                # if not int(alt):
                #     raise ValueError(f"{location_name} int(alt) : {int(alt)} failed")
            except ValueError as e:
                self._notify.info(
                    f"{location_name} : alt validation failed\n\tsetting alt to 0 string\n\terror :\n\t{e}",
                    source="eventdata",
                    route=["terminal"],
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
                    f"{location_name} timezone not received",
                    source="eventdata",
                    route=["terminal"],
                )
            self.old_location = location_formatted
            self._notify.success(
                f"{location_name} valid & formatted",
                source="eventdata",
                route=["user", "terminal"],
            )
        except Exception as e:
            self._notify.error(
                f"{location_name} invalid : we accept"
                "\n1. deg-min-(sec) with direction"
                "\n\t32 21 (9) n 77 66 (11) w (alt (m))"
                "\n2. decimal with direction"
                "\n\t33.77 n 124.87 e (alt (m))"
                "\n3. decimal signed (s & w -ve | n & e +ve)"
                "\n\t-16.76 72.678 (alt (m))"
                "\nsecond & altitude (& unit) are optional"
                f"\n\terror\n\t{e}\n",
                source="eventdata",
                route=["terminal", "user"],
                timeout=4,
            )
            return
        # needed for datetime as local apparent time
        if lon:
            self.lon = lon
        # save data by event
        if location_name == "location one":
            # grab country & city
            if hasattr(mainwindow, "country_one"):
                country = mainwindow.country_one.get_selected_item().get_string()
            if hasattr(mainwindow, "city_one"):
                city = mainwindow.city_one.get_text()
            self._app.e1_chart["country"] = country
            self._app.e1_chart["city"] = city
            self._app.e1_chart["location"] = location_formatted
            self._app.e1_chart["timezone"] = timezone_
            # received data
            self._app.e1_sweph["lat"] = lat
            self._app.e1_sweph["lon"] = lon
            self._app.e1_sweph["alt"] = int(alt)
            # msg_ = f"{location_name} updated"
        else:
            # grab country & city
            if hasattr(mainwindow, "country_two"):
                country = mainwindow.country_two.get_selected_item().get_string()
            if hasattr(mainwindow, "city_two"):
                city = mainwindow.city_two.get_text()
            self._app.e2_chart["country"] = country
            self._app.e2_chart["city"] = city
            self._app.e2_chart["location"] = location_formatted
            self._app.e2_chart["timezone"] = timezone_
            # received data
            self._app.e2_sweph["lat"] = lat
            self._app.e2_sweph["lon"] = lon
            self._app.e2_sweph["alt"] = int(alt)
            # msg_ = f"{location_name} updated"
        self._notify.success(
            f"{location_name} updated",
            source="eventdata",
            route=["terminal"],
        )
        return

    def on_name_change(self, entry):
        """process name / title"""
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
            msg_ = f"{name_name} updated : {self._app.e1_chart.get('name')}"
        else:
            self._app.e2_chart["name"] = name
            msg_ = f"{name_name} updated : {self._app.e2_chart.get('name')}"
        self._notify.success(
            msg_,
            source="eventdata",
            route=["terminal"],
        )
        return

    def on_datetime_change(self, entry):
        """process date & time"""
        datetime_name = entry.get_name()
        date_time = entry.get_text().strip()
        # we need datetime utc & for event location
        jd_ut = None
        dt_utc = None
        dt_utc_str = ""
        dt_event = None
        dt_event_str = ""
        # datetime set by hotkey time now utc : validation not needed
        if self.is_hotkey_now:
            """get utc from computer time"""
            try:
                dt_utc = datetime.now(timezone.utc).replace(microsecond=0)
                dt_utc_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
                # print(f"timenow : dt_utc_str : {dt_utc_str}")
                if self.timezone:
                    # print(f"timenow : timezone : {self.timezone}")
                    dt_event = dt_utc.astimezone(ZoneInfo(self.timezone))
                    dt_event_str = dt_event.strftime("%Y-%m-%d %H:%M:%S")
                    # print(f"timenow : dt_event_str : {dt_event_str}")
                    tz_offset_ = dt_event.utcoffset()
                    tz_offset_str = str(tz_offset_)
                    print(f"timenow : tzoffstr : {tz_offset_str}")
                    # error : invalid literal ... -1 day, 20:00:00 [workaround]
                    # parse timezone string to decimal hours
                    parts = [p for p in tz_offset_str.split(",") if p]
                    days = int(parts[0].split()[0]) if "day" in parts[0] else 0
                    h, m, s = map(int, parts[-1].strip().split(":"))
                    # convert to decimal
                    self.tz_offset = days * 24 + h + m / 60 + s / 3600
                    print(f"timenow : tz_offset : {self.tz_offset}")
                    self._notify.info(
                        f"{datetime_name} timezone : "
                        f"using time now for {self.timezone}",
                        source="eventdata",
                        route=["terminal"],
                    )
                else:
                    # copy utc string to event string for presentation
                    dt_event_str = dt_utc_str
                    self._notify.warning(
                        f"\n\t{datetime_name} no timezone : using utc now"
                        "\n\tlocation should be set to calculate timezone",
                        source="eventdata",
                        route=["terminal", "user"],
                        timeout=4,
                    )
                # calculate julian day utc
                _, jd_ut = utc_to_jd(
                    dt_utc.year,
                    dt_utc.month,
                    dt_utc.day,
                    dt_utc.hour,
                    dt_utc.minute,
                    int(dt_utc.second),
                    calendar=b"g",
                )
            except Exception as e:
                self._notify.error(
                    f"{datetime_name} (hk) time now failed\n\terror\n\t{e}\n",
                    source="eventdata",
                    route=["terminal"],
                )
                self.is_hotkey_now = False
                return
            self.is_hotkey_now = False
        else:
            """string from manual input or hotkey arrow left / right (change time)"""
            # event one date-time is mandatory
            if not date_time:
                if datetime_name == "datetime one":
                    self._notify.warning(
                        f"\n\tmandatory data missing : {datetime_name}",
                        source="eventdata",
                        route=["terminal", "user"],
                    )
                    return
                elif datetime_name == "datetime two":
                    # datetime two is optional : if deleted > clear data 2
                    if self._app.e2_chart or self._app.e2_sweph:
                        self._app.e2_chart = {}
                        self._app.e2_sweph = {}
                        # flip e2 active flag
                        self._app.e2_active = False
                        self.old_date_time = ""
                        self._notify.info(
                            f"{datetime_name}: cleared event 2 data"
                            f"\n\te2 active : {self._app.e2_active}",
                            source="eventdata",
                            route=["terminal"],
                        )
                        calculate_positions("e1")
                        return
            if date_time == self.old_date_time:
                self._notify.debug(
                    f"{datetime_name} not changed",
                    source="eventdata",
                    route=["terminal"],
                )
                return
            # data changed
            try:
                # todo grab weekday somewhere if possible
                # swisseph.day_of_week()
                #    Calculate day of week number [0;6] from Julian day number (monday is 0).
                # get datetime string, assuming naive date-time
                dt_str = entry.get_text().strip()
                # grab self.lon if 'a' in datetime (local apparent time)
                if dt_str and "a" in dt_str and self.lon:
                    result = validate_datetime(self, dt_str, lon=self.lon)
                else:
                    result = validate_datetime(self, dt_str)
                if not result:
                    raise ValueError(f"\t{datetime_name} validation failed")
                self._notify.info(
                    f"{datetime_name} manual entry valid",
                    source="eventdata",
                    route=["none"],
                )
                Y, M, D, h, m, s, calendar, _ = result
                # manual input : assume event time
                # we need timezone offset for event location
                # dt_utc_now = datetime.now(timezone.utc).replace(microsecond=0)
                if self.timezone:
                    # python datetime only goes down to year 1
                    if Y >= 1:
                        # get timezone offset from event datetime
                        dt_event = datetime(
                            Y, M, D, h, m, s, tzinfo=ZoneInfo(self.timezone)
                        )
                        # dt_utc_now.astimezone(ZoneInfo(self.timezone))
                        tz_offset_ = dt_event.utcoffset()
                        # as string
                        tz_offset_str = str(tz_offset_)
                        # error : invalid literal ... -1 day, 20:00:00 [workaround]
                        # parse timezone string to decimal hours
                        parts = [p for p in tz_offset_str.split(",") if p]
                        days_ = int(parts[0].split()[0]) if "day" in parts[0] else 0
                        h_, m_, s_ = map(int, parts[-1].strip().split(":"))
                        # convert to decimal
                        self.tz_offset = days_ * 24 + h_ + m_ / 60 + s_ / 3600
                    else:
                        self.tz_offset = 0.0
                        self._notify.info(
                            "year below 1 : using fixed utc offset",
                            source="eventdata",
                            route=["terminal"],
                        )
                    dt_event_str = f"{Y}-{M:02d}-{D:02d} {h:02d}:{m:02d}:{s:02d}"
                    # print(f"dteventstr : {dt_event_str}")
                    dt_utc = naive_to_utc(Y, M, D, h, m, s, self.tz_offset)
                    _, jd_ut = utc_to_jd(*dt_utc, calendar)
                    # print(f"utcfromnaive : {dt_utc} | type : {type(dt_utc)}")
                    # print(f"manualdt tz : jdut : {jd_ut} | tzoffset : {self.tz_offset}")
                else:
                    # take date-time string as utc : seconds is float
                    dt_utc = naive_to_utc(Y, M, D, h, m, s, 0.0)
                    _, jd_ut = utc_to_jd(*dt_utc, calendar)
                    # print(f"utcfromnaive : {dt_utc} | type : {type(dt_utc)}")
                    # print(f"manualdt utc : jdut : {jd_ut} | tzoffset : 0.0")
                    dt_event_str = f"{dt_utc[0]}-{dt_utc[1]:02d}-{dt_utc[2]:02d} {dt_utc[3]:02d}:{dt_utc[4]:02d}:{int(dt_utc[5]):02d}"
                    self._notify.info(
                        f"\n\t{datetime_name} no timezone : using utc"
                        "\n\tlocation should be set to calculate timezone",
                        source="eventdata",
                        route=["terminal", "user"],
                    )
            except Exception as e:
                self._notify.warning(
                    f"{datetime_name} error"
                    "\n\twe accept space-separated : yyyy mm dd HH MM SS"
                    "\n\t\tand - : for separators (iso date-time, 24 hour format)"
                    "\n\tand : j(ulian calendar) | a(pparent local time)"
                    f"\n\terror\n\t{e}\n",
                    source="eventdata",
                    route=["terminal", "user"],
                )
                return
        # update datetime entry
        if dt_event_str:
            entry.set_text(dt_event_str)
        # save datetime by event
        if datetime_name == "datetime one":
            self._app.e1_chart["datetime"] = dt_event_str
            msg_ = f"{datetime_name} updated : {self._app.e1_chart.get('datetime')}"
        else:
            self._app.e2_chart["datetime"] = dt_event_str
            msg_ = f"{datetime_name} updated : {self._app.e2_chart.get('datetime')}"
        self._notify.debug(
            msg_,
            source="eventdata",
            route=["none"],
        )
        # all good : set new old date-time
        self.old_date_time = dt_event_str
        if not jd_ut:
            self._notify.error(
                f"{datetime_name} failed to calculate julian day",
                source="eventdata",
                route=["terminal"],
            )
            return
        if datetime_name == "datetime one":
            self._app.e1_sweph["jd_ut"] = jd_ut
        else:
            self._app.e2_sweph["jd_ut"] = jd_ut
        self._notify.debug(
            f"{datetime_name} julian day : {jd_ut}",
            source="eventdata",
            route=["terminal"],
        )
        # if datetime two is NOT empty, user is interested in event 2
        # in this case datetime two is mandatory, the rest is optional, aka
        # if exists > use it, else use event 1 data
        if not self._app.e2_chart.get("datetime"):
            # declare event two active : needed for calculations todo ???
            self._app.e2_active = False
            self._notify.debug(
                "datetime 2 is none : user not interested in event 2 : skipping ..."
                f"\n\te2 active : {self._app.e2_active}",
                source="eventdata",
                route=["none"],
            )
        elif self._app.e2_chart.get("datetime", ""):
            self._app.e2_active = True
            self._notify.debug(
                f"\n\tdatetime 2 not empty : {self._app.e2_chart.get('datetime')} : "
                "merging e1 > e2 data"
                f"\n\te2 active : {self._app.e2_active}",
                source="eventdata",
                route=["terminal"],
            )
            if self._app.e2_chart.get("location", "") == "":
                for key in ["country", "city", "location", "timezone"]:
                    self._app.e2_chart[key] = self._app.e1_chart.get(key)
                for key in ["lat", "lon", "alt"]:
                    self._app.e2_sweph[key] = self._app.e1_sweph.get(key)
            self._notify.debug(
                "cou & cit & loc & tz + lat & lon & alt : data 1 => 2",
                source="eventdata",
                route=["terminal"],
            )
        # debug-print all data
        import json

        self._notify.debug(
            "\n----- COLLECTED DATA -----"
            f"\n\tchart 1\t{json.dumps(self._app.e1_chart, sort_keys=True, indent=6, ensure_ascii=False)}"
            f"\n\tsweph 1\t{json.dumps(self._app.e1_sweph, sort_keys=True, indent=6, ensure_ascii=False)}"
            "\n--------------------------"
            f"\n\tchart 2\t{json.dumps(self._app.e2_chart, sort_keys=True, indent=6, ensure_ascii=False)}"
            f"\n\tsweph 2\t{json.dumps(self._app.e2_sweph, sort_keys=True, indent=6, ensure_ascii=False)}"
            "\n--------------------------",
            source="eventdata",
            route=["none"],
        )
        # detect event & pass it further
        if datetime_name == "datetime one":
            event = "e1"
        else:
            event = "e2"
        self._notify.debug(
            f"{datetime_name} ({event}): calling updatepositions ...",
            source="eventdata",
            route=["none"],
        )
        calculate_positions(event)
        self._app.props.active_window.update_main_title()
        return
