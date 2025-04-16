# astronomical year 0 (1 bc) = jd 1721057.5
# ad 1 (ce) = jd 1721423.5
# 2000-01-01 12:00 = jd 2451545.0
# jd 0 = 4714-11-24 bce (gregorian) = monday 4713-01-01 bce 12:00 (julian)
import re
import swisseph as swe


def validate_datetime(manager, date_time, lon=None):
    """check characters & parse numbers & letters then validate"""
    # mean solar time, aka local mean time (lmt) - modern (utc)
    # true solar time, aka local apparent time (lat) - pre-clock
    # diff = equation of time : historical date lat => to lmt (equation of time)
    valid_chars = set("0123456789 -:ja")
    invalid_chars = set(date_time) - valid_chars
    msg_negative_year = ""
    try:
        if invalid_chars:
            raise ValueError(
                f"characters {sorted(invalid_chars)} not allowed"
                "\n\twe accept : 0123456789 -:ja"
                "\n\tj = julian calendar (gregorian = default)"
                "\n\ta = local apparent time (mean = default)"
            )
        is_year_negative = date_time.lstrip().startswith("-")
        print(f"negative year : {is_year_negative}")
        parts = [p for p in re.split(r"[- :]+", date_time) if p]
        print(f"parts : {parts}")
        # split into numbers & flags (j,a) : year-month-day are manadatory
        nums = []
        flags = []
        for p in parts:
            if isinstance(p, str) and p.isdigit():
                nums.append(int(p))
            elif isinstance(p, str) and p.isalpha():
                flags.append(p.lower())
        if len(nums) < 3:
            raise ValueError(
                "wrong data count : year-month-day are mandatory"
                "\n\tie 1999 11 12 or 1999 11 12 13 14 00"
                "\nalso allowed j (julian calendar) & a (local apparent time)"
            )
        Y = -nums[0] if is_year_negative else nums[0]
        M, D = nums[1], nums[2]
        h = nums[3] if len(nums) >= 4 else 0
        m = nums[4] if len(nums) >= 5 else 0
        s = nums[5] if len(nums) >= 6 else 0
        if is_year_negative:
            msg_negative_year = f"found negative year : {Y}\n"
        else:
            msg_negative_year = ""
        # swiseph year range
        if not -13200 <= Y <= 17191:
            raise ValueError(f"year {Y} out of sweph range (-13200 - 17191)")
        # check for calendar flag : g(regorian) is default
        calendar = b"g"
        if "j" in flags:
            calendar = b"j"
        # check for time flag : local mean time is default
        local_time = "m"  # mean
        if "a" in flags:
            local_time = "a"  # apparent
        # check if swetime is valid
        is_valid, jd, swe_corr = custom_iso_to_jd(
            manager,
            Y,
            M,
            D,
            hour=h,
            min=m,
            sec=s,
            calendar=calendar,
            local_time=local_time,
            lon=lon,
        )
        if not is_valid:
            raise ValueError(
                "_validatedatetime : swetimetojd is not valid\n"
                f"using swe_corr anyway : {swe_corr}"
            )
        corr_y, corr_m, corr_d, corr_h = swe_corr
        print(
            f"_validatedatetime : swetimetojd is valid\ncorrected values : {corr_y} | {corr_m} | {corr_d} | {corr_h}"
        )
        h_corr = int(corr_h)
        m_corr = int((corr_h - h_corr) * 60)
        s_corr = int(round((((corr_h - h_corr) * 60) - m_corr) * 60))
        manager._notify.debug(
            f"\n\tdate-time as corrected : {corr_y}-{corr_m}-{corr_d} "
            f"{h_corr}:{m_corr}:{s_corr}",
            source="helpers",
            route=["terminal"],
        )
    except ValueError as e:
        manager._notify.warning(
            f"{date_time}\n\terror\n\t{e}\n\t{msg_negative_year}",
            source="helpers",
            route=["terminal"],
        )
        return False
    return jd, corr_y, corr_m, corr_d, h_corr, m_corr, s_corr


def custom_iso_to_jd(
    manager,
    year,
    month,
    day,
    hour=0,
    min=0,
    sec=0,
    calendar=b"g",
    local_time=None,
    lon=None,
):
    """convert date-time to julian date & check if datetime is valid"""
    decimal_hour = hour + min / 60 + sec / 3600
    # convert calender bytes to int
    cal_int = bytes_to_cal_int(calendar)
    jd = swe.julday(year, month, day, decimal_hour, cal_int)
    # lat => lmt if local apparent time
    # in > tjd_lat, geolon ; out > tjd_lmt, err (string);
    if local_time == "a":
        if not lon:
            manager._notify.error("local apparent time : longitude missing")
            return False, None, (year, month, day, decimal_hour)
        jd = swe.lat_to_lmt(jd, lon)
    is_valid, jd, swe_corr = swe.date_conversion(
        year, month, day, decimal_hour, calendar
    )
    return is_valid, jd, swe_corr


def jd_to_custom_iso(jd, calendar=b"g"):
    """convert julian day to iso string"""
    # convert bytes to int
    cal_int = bytes_to_cal_int(calendar)
    Y, M, D, h_ = swe.revjul(jd, cal_int)
    h = int(h_)
    m = int((h_ - h) * 60)
    s = int(round((((h_ - h) * 60) - m) * 60))
    return f"{Y}-{M:02d}-{D:02d} {h:02d}:{m:02d}:{s:02d}"


def bytes_to_cal_int(calendar):
    # convert bytes to int
    cal_int = swe.GREG_CAL if calendar == b"g" else swe.JUL_CAL
    return cal_int
