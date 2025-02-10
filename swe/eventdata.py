import re
import pytz
from datetime import datetime


class EventData:
    def __init__(self, event_name, date_time, location):
        """get user input and puf! puf! into sweph"""
        # self.event_name = event_name.get_text().strip()
        self.event_name = event_name
        self.date_time = date_time
        self.location = location
        # backup data lol
        self.old_name = ""
        self.old_date_time = ""
        self.old_location = ""
        # connect signals for entry completion
        for widget, callback in [
            (self.event_name, self.on_name_change),
            (self.date_time, self.on_date_time_change),
            (self.location, self.on_location_change),
        ]:
            widget.connect("activate", callback)  # [enter]

    def on_name_change(self, entry):
        """process name"""
        name = entry.get_text().strip()
        if not name or name == self.old_name:
            return
        if len(name) > 30:
            print("name too long : max 30 characters")
            return

        self.old_name = name
        print(f"event name : {name}")

    def on_date_time_change(self, entry):
        """process date & time"""
        date_time = entry.get_text().strip()
        if not date_time or date_time == self.old_date_time:
            return

        self.old_date_time = date_time
        # validate datetime
        try:
            # check characters
            valid_chars = set("0123456789 -/.:")
            invalid_chars = set(date_time) - valid_chars
            if invalid_chars:
                print(f"dt_change : unaccepted characters : {sorted(invalid_chars)}")
                return
            # huston we have data
            is_year_negative = date_time.lstrip().startswith("-")
            if not is_year_negative:
                # try formatted version for +ve years
                try:
                    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                    print(f"event dt : {dt}")
                    return

                except ValueError:
                    pass

            else:
                parts = [p for p in re.split("[ -/.:]+", date_time) if p]
                # print(f"parts : {parts}")
            if len(parts) in [5, 6]:
                print(
                    "wrong data count : 6 or 5 (no seconds) time units expected\nie 1999 11 12 13 14"
                )
                return
            # handle year
            try:
                year = int(parts[0])
                # swiseph year range
                if not -13200 <= year <= 17191:
                    print("year out of sweph range (-13.200 - 17.191)")
                    return

            except ValueError:
                print("invalid year format")
                return

            if len(parts) == 5:
                # add seconds
                parts.append("00")

            try:
                year, month, day, hour, minute, second = map(int, parts)
                dt = datetime(year, month, day, hour, minute, second)
                formatted = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
                # formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                print(f"formatted event dt : {formatted}")

            except ValueError as e:
                print(f"invalid date-time : {str(e)}")
                return

        except Exception:
            print(
                """wrong date-time format
    we only accept space-separated : yyyy mm dd HH MM SS
    and - / . : for separators"""
            )
            return

    def on_location_change(self, entry):
        """process location"""
        location = entry.get_text().strip()
        if not location or location == self.old_location:
            return

        self.old_location = location
        print(f"eventdata : event location : {location}")

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
        print(f"current utc : {formatted_utc}")
