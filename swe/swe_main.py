import swisseph as swe
import os

# from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
# current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
# print(f"parent dir : {parent_dir}")
ephe_path = os.path.join(parent_dir, "ephe")
swe.set_ephe_path(ephe_path)

RANGE_START = 1800
RANGE_END = 2399


# def get_solec_data(date_jd):
#     flags = swe.FLG_DEFAULTEPH
#     # flags = swe.FLG_SWIEPH
#     eclflag, tret = swe.sol_eclipse_when_glob(date_jd, flags, 0)
#     eclipse_time = tret[0]  # max eclipse
#     eclflags, geopos, attr = swe.sol_eclipse_where(eclipse_time, flags)
#     # attr[9] = saros series number
#     # attr[10] = saros series member number
#     return {
#         "date": swe.revjul(eclipse_time),
#         "saros_series": int(attr[9]),
#         "saros_member": int(attr[10]),
#         "eclipse_type": eclflag,
#         "magnitude": attr[0],  # fraction of solar diameter covered by moon
#         "longitude": geopos[0],  # long of max eclipse
#         "latitude": geopos[1],  # lat of max eclipse
#     }


# def get_lunec_data(date_jd):
#     flags = swe.FLG_DEFAULTEPH
#     eclflag, tret = swe.lun_eclipse_when(date_jd, flags, 0)

#     eclipse_time = tret[0]  # max eclipse
#     # at specfic location
#     rflags, attr = swe.lun_eclipse_how(eclipse_time, (0, 0, 0), flags)
#     return {
#         "date": swe.revjul(eclipse_time),
#         "saros_series": int(attr[9]),
#         "saros_member": int(attr[10]),
#         "eclipse_type": eclflag,
#         "magnitude": attr[0],
#     }

flags = swe.FLG_SWIEPH | swe.FLG_SPEED


def get_previous_solec(jd_start):
    y, _, _, _ = swe.revjul(jd_start)
    if not RANGE_START <= y <= RANGE_END:
        raise ValueError(f"year must be between {RANGE_START} & {RANGE_END}")
    eclflag, tret = swe.sol_eclipse_when_glob(jd_start, flags, backwards=True)
    eclipse_time = tret[0]
    eclfag, geopos, attr = swe.sol_eclipse_where(eclipse_time, flags)

    return {
        "date": swe.revjul(eclipse_time),
        "jd": eclipse_time,
        "saros_series": int(attr[9]),
        "saros_member": int(attr[10]),
        "eclipse_type": eclflag,
        "magnitude": attr[0],
        "longitude": geopos[0],
        "latitude": geopos[1],
    }


def get_previous_lunec(jd_start):
    y, _, _, _ = swe.revjul(jd_start)
    if not RANGE_START <= y <= RANGE_END:
        raise ValueError(f"year must be between {RANGE_START} & {RANGE_END}")
    eclflag, tret = swe.lun_eclipse_when(jd_start, flags, backwards=True)

    eclipse_time = tret[0]
    rflags, attr = swe.lun_eclipse_how(eclipse_time, (0, 0, 0), flags)

    return {
        "date": swe.revjul(eclipse_time),
        "jd": eclipse_time,
        "saros_series": int(attr[9]),
        "saros_member": int(attr[10]),
        "eclipse_type": eclflag,
        "magnitude": attr[0],
        # "longitude": geopos[0],
        # "latitude": geopos[1],
    }


def format_eclipse_type(eclflag):
    """convert eclipse flag to human-readable"""
    # definitions
    ECL_CENTRAL = 1
    ECL_NONCENTRAL = 2
    ECL_TOTAL = 4
    ECL_ANNULAR = 8
    ECL_PARTIAL = 16
    ECL_ANNULAR_TOTAL = 32
    ECL_HYBRID = 32
    ECL_PENUMBRAL = 64

    types = []

    if eclflag & ECL_TOTAL:
        types.append("total")
    elif eclflag & ECL_ANNULAR:
        types.append("annular")
    elif eclflag & ECL_PARTIAL:
        types.append("partial")
    elif eclflag & ECL_ANNULAR_TOTAL:
        types.append("hybrid")
    elif eclflag & ECL_PENUMBRAL:
        types.append("penumbral")
    elif eclflag & ECL_CENTRAL:
        types.append("central")
    elif eclflag & ECL_NONCENTRAL:
        types.append("non-central")

    if not types:
        return f"unknown flag : {eclflag}"
    # eclipse_types = {
    #     swe.ECL_CENTRAL: "central",  # 1
    #     swe.ECL_NONCENTRAL: "non-central",  # 2
    #     swe.ECL_TOTAL: "total",  # 4
    #     swe.ECL_ANNULAR: "annular",  # 8
    #     swe.ECL_PARTIAL: "partial",  # 16
    #     swe.ECL_ANNULAR_TOTAL: "annular-total",  # 32
    #     swe.ECL_HYBRID: "hybrid",  # 32
    #     swe.ECL_PENUMBRAL: "penumbral",  # 64
    # }
    # result = []
    # for flag, desc in eclipse_types.items():
    #     if eclflag == flag:
    #         result.append(desc)
    #         break
    # if not result:
    #     return f"unknown eclipse type (flag : {eclflag})"
    # print(f"eclflag : {eclflag}")
    return " - ".join(types)


def format_data(date_tuple):
    """format date (tuple) into string"""
    year, month, day, hours = date_tuple
    hour = int(hours)
    minutes = int((hours - hour) * 60)
    seconds = int(((hours - hour) * 60 - minutes) * 60)
    return (
        f"{year:04d}-{month:02d}-{day:02d} {hour:02d} : {minutes:02d} : {seconds:02d}"
    )


def get_eclipse_before_date(year, month, day, hour, minute):
    if not RANGE_START <= year <= RANGE_END:
        raise ValueError(f"year {year} outside valid range ({RANGE_START}-{RANGE_END})")
    jd_target = swe.julday(year, month, day, hour + minute / 60.0)
    # get previous solar eclipse
    solar = get_previous_solec(jd_target)
    # get previous lunar eclipse
    lunar = get_previous_lunec(jd_target)

    return solar, lunar


if __name__ == "__main__":
    year = 1975
    month = 2
    day = 8
    hour = 13
    minute = 10

    try:
        solec, lunec = get_eclipse_before_date(year, month, day, hour, minute)
        print(
            f"prev solec from {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} (utc)"
        )
        print(f"date utc : {solec['date']}")
        print(f"julian day : {solec['jd']:.6f}")
        print(f"type : {format_eclipse_type(solec['eclipse_type'])}")
        print(f"saros series : {solec['saros_series']}")
        print(f"saros member : {solec['saros_member']}")
        print(f"magnitude : {solec['magnitude']}")
        print(
            f"max eclipse place : {solec['longitude']:.4f}° - {solec['latitude']:.4f}°"
        )

        print(
            f"\nprev lunec from {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} (utc)"  # type: ignore
        )
        print(f"date : {lunec['date']}")
        print(f"type : {format_eclipse_type(lunec['eclipse_type'])}")
        print(f"saros series : {lunec['saros_series']}")
        print(f"saros member : {lunec['saros_member']}")
        print(f"magnitude : {lunec['magnitude']}")
        # print(
        #     f"max eclipse place : {lunec['longitude']:.4f}° - {lunec['latitude']:.4f}°"
        # ) type: ignore

    except Exception as e:
        print(f"error : {e}")

swe.close()
