import re


class EventData:
    def __init__(self, event_name, date_time, location):
        """get user input and puf! puf! into sweph"""
        self.event_name = event_name
        self.date_time = date_time
        self.location = location
        # backup data lol
        self.old_name = ""
        self.old_date_time = ""
        self.old_location = ""

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
        # print(f"on_dt_change : date_time : {date_time}")
        # validate datetime
        try:
            # check characters
            valid_chars = set("0123456789 -/.:")
            invalid_chars = set(date_time) - valid_chars
            if invalid_chars:
                print(f"on_dt_change : unaccepted characters : {sorted(invalid_chars)}")
                return
            # huston we have data
            is_year_negative = date_time.lstrip().startswith("-")
            # print(f"eventdata : year negative : {is_year_negative}")

            parts = [p for p in re.split("[ -/.:]+", date_time) if p]
            # print(f"parts : {parts}")

            if len(parts) < 5 or len(parts) > 6:
                print(
                    """wrong data count : 6 or 5 (no seconds) time units expected
    ie 1999 11 12 13 14"""
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
                    print("year out of sweph range (-13.200 - 17.191)")
                    return

            except ValueError:
                print("invalid year format")
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
                print(f"{year}-{month}-{day} : date is NOT valid : fix & try again")
                print("\tcheck month & day : february has 28 or 29 days")

                return

            def is_valid_time(hour, minute, second):
                return 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59

            if not is_valid_time(hour, minute, second):
                print(f"{hour}:{minute}:{second} : time is NOT valid : fix & try again")

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
                print(f"formatted dt : \n\t{formatted}")
                entry.set_text(formatted)
                date_time_formatted = f"{year} {month} {day} {hour} {minute} {second}"
                print(f"final date_time : \n\t{date_time_formatted}")

                # return dt

            except ValueError as e:
                print(f"invalid date-time : {str(e)}")

                return

        except Exception as e:
            print(
                """wrong date-time format
    we only accept space-separated : yyyy mm dd HH MM SS
    and - / . : for separators"""
            )
            print(f"error : {str(e)}")

            return

    def on_location_change(self, entry):
        """process location"""
        location = entry.get_text().strip()
        if not location or location == self.old_location:
            return

        self.old_location = location
        # print(f"eventdata : event location : {location}")

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
