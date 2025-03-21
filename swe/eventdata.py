# ruff: noqa: E402
import re
import pytz
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from math import modf
from datetime import datetime


class EventData:
    def __init__(self, event_name, date_time, location, get_application=None):
        """get user input and puf! puf! into sweph"""
        self.event_name = event_name
        self.date_time = date_time
        self.location = location
        self.old_name = ""
        self.old_date_time = ""
        self.old_location = ""
        self.get_application = get_application

        # focus wrapper
        def focus_wrapper(widget, pspec, callback):
            if not widget.has_focus():
                callback(widget)

        # connect signals for entry completion
        for widget, callback in [
            (self.event_name, self.on_name_change),
            (self.date_time, self.on_date_time_change),
            (self.location, self.on_location_change),
        ]:
            widget.connect("activate", callback)  # [enter]
            widget.connect(
                "notify::has-focus",
                lambda w, p, cb=callback: focus_wrapper(w, p, cb),
            )  # focus lost ?

    def notify_user(self, message, **kwargs):
        app = (
            self.get_application()
            if self.get_application
            else Gtk.get_application_default()
        )
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message=message, **kwargs)
        else:
            print(f"eventdata : {message}")

    def on_name_change(self, entry):
        """process title / name"""
        name = entry.get_text().strip()
        if not name or name == self.old_name:
            return
        if len(name) > 30:
            if hasattr(self, "get_application") and self.get_application:
                self.get_application().notify_manager.warning(
                    "name too long : max 30 characters"
                )
            else:
                print("name too long : max 30 characters")
            return

        self.old_name = name
        # print(f"event name : {name}")

    def on_date_time_change(self, entry):
        """process date & time"""
        date_time = entry.get_text().strip()
        if not date_time or date_time == self.old_date_time:
            return
        # validate datetime
        try:
            # check characters
            valid_chars = set("0123456789 -/.:")
            invalid_chars = set(date_time) - valid_chars
            if invalid_chars:
                self.notify_user(
                    f"date-time : characters {sorted(invalid_chars)} not allowed",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return
            # huston we have data
            is_year_negative = date_time.lstrip().startswith("-")
            # print(f"eventdata : year negative : {is_year_negative}")
            parts = [p for p in re.split("[ -/.:]+", date_time) if p]
            # print(f"parts : {parts}")
            if len(parts) < 5 or len(parts) > 6:
                self.notify_user(
                    "wrong data count : 6 or 5 (if no seconds) time units expected"
                    "\n\tie 1999 11 12 13 14",
                    level="warning",
                    source="eventdata",
                    do_log=False,
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
                    self.notify_user(
                        "year out of sweph range (-13.200 - 17.191)",
                        level="warning",
                        source="eventdata",
                        do_log=False,
                    )
                    return

            except ValueError:
                self.notify_user(
                    "invalid year format",
                    level="error",
                    source="eventdata",
                    do_log=False,
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
                self.notify_user(
                    f"{year}-{month}-{day} : date not valid"
                    "\ncheck month & day : february has 28 or 29 days",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return

            def is_valid_time(hour, minute, second):
                return 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59

            if not is_valid_time(hour, minute, second):
                self.notify_user(
                    f"{hour}:{minute}:{second} : time not valid",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return

            try:
                if year <= -10000:
                    y_ = f"-{abs(year)}"
                elif year < 0:
                    y_ = f"-{abs(year):04d}"
                elif year >= 0:
                    y_ = f"{year:04d}"
                m_ = f"{month:02d}"
                d_ = f"{day:02d}"
                h_ = f"{hour:02d}"
                mi_ = f"{minute:02d}"
                s_ = f"{second:02d}"

                formatted = f"{y_}-{m_}-{d_} {h_}:{mi_}:{s_}"
                # print(f"formatted dt : \n\t{formatted}")
                entry.set_text(formatted)
                date_time_final = f"{year} {month} {day} {hour} {minute} {second}"
                # print(f"final date_time : \n\t{date_time_final}")

                entry.set_text(formatted)
                return formatted, date_time_final

            except ValueError as e:
                self.notify_user(
                    f"invalid date-time : {str(e)}",
                    level="error",
                    source="eventdata",
                    do_log=False,
                )
                return

        except Exception:
            self.notify_user(
                "wrong date-time format"
                "\nwe only accept space-separated : yyyy mm dd HH MM SS"
                "\nand - / . : for separators",
                level="error",
                source="eventdata",
                do_log=False,
            )
            return

    def on_location_change(self, entry):
        """process location data (as string)
        3 allowed input formats :
        1. dms : "32 21 09 n 77 66 00 w 113 m"
        2. decimal : "33.72 n 124.876 e"
        3. signed decimal : "-16.75 -72.678"
        south & west are -ve : -16.75 -72.678"""

        location = entry.get_text().strip()
        if not location or location == self.old_location:
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
                    self.notify_user(
                        "missing direction indicators (n/s & e/w)",
                        source="eventdata",
                        level="warning",
                        do_log=False,
                    )
                    return False
                # split into latitude & longitude
                lat_parts = parts[: lat_dir_idx + 1]
                lon_parts = parts[lat_dir_idx + 1 : lon_dir_idx + 1]
                # get optional altitude
                alt = "/"
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
                        lat_deg, lat_min, lat_sec = self.decimal_to_dms(abs(lat))
                        lon_deg, lon_min, lon_sec = self.decimal_to_dms(abs(lon))
                    else:
                        # d-m-s format : seconds are optional
                        if len(lat_parts) < 3 or len(lon_parts) < 3:
                            self.notify_user(
                                "invalid deg-min-(sec) n/s e/w format",
                                source="eventdata",
                                level="warning",
                                do_log=False,
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
                    self.notify_user(
                        f"error parsing coordinates :\n\t{str(e)}",
                        source="eventdata",
                        level="error",
                        do_log=False,
                    )
                    return False
            else:
                # signed decimal format
                try:
                    if len(parts) < 2:
                        self.notify_user(
                            "need min latitude & longitude",
                            level="warning",
                            source="eventdata",
                            do_log=False,
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
                    lat_deg, lat_min, lat_sec = self.decimal_to_dms(abs(lat))
                    lon_deg, lon_min, lon_sec = self.decimal_to_dms(abs(lon))

                except ValueError as e:
                    self.notify_user(
                        f"invalid decimal coordinates :\n\t{str(e)}",
                        level="error",
                        source="eventdata",
                        do_log=False,
                    )
                    return False
            # validate ranges
            if not (0 <= lat_deg <= 89):
                self.notify_user(
                    "latitude degrees must be between 0 & 90",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return False
            if not (0 <= lat_min <= 59) or not (0 <= lat_sec <= 59):
                self.notify_user(
                    "minutes & seconds must be between 0 & 59",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return False
            if lat_dir not in ["n", "s"]:
                self.notify_user(
                    "latitude direction must be n(orth) or s(outh)",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return False

            if not (0 <= lon_deg <= 179):
                self.notify_user(
                    "longitude degrees must be between 0 and 179",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return False
            if not (0 <= lon_min <= 59) or not (0 <= lon_sec <= 59):
                self.notify_user(
                    "minutes & seconds must be between 0 & 59",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return False
            if lon_dir not in ["e", "w"]:
                self.notify_user(
                    "longitude direction must be e(ast) or w(est)",
                    level="warning",
                    source="eventdata",
                    do_log=False,
                )
                return False
            # try to convert altitude to int if present
            try:
                alt = str(int(alt))
            except ValueError:
                self.notify_user(
                    "missing altitude value ; setting alt to /",
                    source="eventdata",
                    level="info",
                    do_log=False,
                )
                # print("invalid altitude value ; setting alt to /")
                alt = "/"
            # format final string
            location_formatted = (
                f"{lat_deg:02d} {lat_min:02d} {lat_sec:02d} {lat_dir} "
                f"{lon_deg:03d} {lon_min:02d} {lon_sec:02d} {lon_dir} "
                f"{alt.zfill(4)} m"
                if alt != "/"
                else f"{lat_deg:02d} {lat_min:02d} {lat_sec:02d} {lat_dir} "
                f"{lon_deg:03d} {lon_min:02d} {lon_sec:02d} {lon_dir} /"
            )
            # update entry if text changed
            if location != location_formatted:
                entry.set_text(location_formatted)

            self.old_location = location_formatted
            self.notify_user(
                "location valid & formatted",
                source="eventdata",
                level="success",
                do_log=False,
            )
            return True

        except Exception as e:
            self.notify_user(
                "invalid location format : we accept :"
                "\n1. deg-min-(sec) with direction : 32 21 (9) n 77 66 (11) w (alt)"
                "\n\tsec & alt are optional"
                "\n2. decimal with direction : 33.77 n 124.87 e (alt)"
                "\n3. decimal signed : -16.76 -72.678 (alt)"
                "\n\talt is optional"
                f"error :\n\t{str(e)}",
                level="error",
                source="eventdata",
                do_log=False,
            )
            return False

    def decimal_to_dms(self, decimal):
        """convert decimal number to degree-minute-second"""
        min_, deg_ = modf(decimal)
        sec_, _ = modf(min_ * 60)
        deg = int(deg_)
        min = int(min_ * 60)
        sec = int(sec_ * 60)
        # print(f"decimal_to_dms : d-m-s : {deg} - {min} - {sec}")

        return deg, min, sec

    def get_event_data(self):
        """values from all entries needed for an event"""
        return {
            "name": self.event_name.get_text().strip(),
            "date_time": self.date_time.get_text().strip(),
            "location": self.location.get_text().strip(),
        }

    def set_current_utc(self):
        current_utc = datetime.now(pytz.UTC)
        formatted_utc = current_utc.strftime("%Y-%m-%d %H:%M:%S")
        self.date_time.set_text(formatted_utc)
        # print(f"current utc : {formatted_utc}")
