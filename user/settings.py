# user/settings.py
# set default preferences : for sweph calculations & app settings
OBJECTS = {
    "su": ("sun", "surya", "sy", 0),
    "mo": ("moon", "candra", "ca", 1),
    "me": ("mercury", "budha", "bu", 2),
    "ve": ("venus", "sukra", "sk", 3),
    "ma": ("mars", "mangala", "ma", 4),
    "ju": ("jupiter", "guru", "gu", 5),
    "sa": ("saturn", "sani", "sa", 6),
    "ur": ("uranus", "uranus", "ur", 7),
    "ne": ("neptune", "neptune", "ne", 8),
    "pl": ("pluto", "pluto", "pl", 9),
    "ra": ("mean node", "rahu", "ra", 10),
}
SWE_FLAG = {
    # --- use default sweph ephemeris & speed calculations
    "default flag": (True, "use default (sweph ephemeris & speed calculations)"),
    # --- use sidereal (jyotisa) zodiac : else use tropical (western) zodiac
    # FLG_SIDEREAL vs FLG_TROPICAL (default)
    "sidereal zodiac": (True, "use sideral (vs tropical) zodiac"),
    # --- do NOT use nutation : small irregularity in the precession of the equinoxes
    # FLG_NONUT
    "no nutation": (
        True,
        "do NOT use nutation (small irregularity in precession of the equinoxes)",
    ),
    # --- calculate heliocentric positions : astrology uses geocentric positions
    # FLG_HELCTR
    "heliocentric": (False, "calculate heliocentric (vs geocentric) positions"),
    # --- calculate true, not apparent (visible from earth) positions
    # journey of the light from a planet to the earth takes some time
    # FLG_TRUEPOS
    "true positions": (True, "calculate true (vs apparent) positions"),
    # --- calculate topocentric positions, viewed from latitude & longitude of
    # event ; else calculate geocentric positions (default, used traditionally
    # in astrology), viewed from center of the earth
    # FLG_TOPOCTR
    "topocentric": (False, "calculate topocentric (vs geocentric) positions"),
    # --- return equatorial positions (right ascension & declination)
    # else return ecliptic (default, latitude & longitude) positions
    # FLG_EQUATORIAL
    "equatorial": (False, "return equatorial (vs ecliptic) positions"),
    # --- return cartesian (x, y, z) else polar (default) coordinates
    # FLG_XYZ
    "cartesian": (False, "return cartesian (x, y, z vs polar degrees) coordinates"),
    # --- return radian else degree (default) units
    # FLG_RADIANS
    "radians": (False, "return radian (vs degree) units"),
}
# add or remove houses as you please
# https://astrorigin.com/pyswisseph/sphinx/programmers_manual/house_cusp_calculation.html?highlight=houses#swisseph.houses
# below are most popular 7 out of 24+; arrange as you please
HOUSE_SYSTEMS = [
    ("E", "eqa: equal asc", "eqa"),
    ("O", "prp: porphyry", "prp"),
    ("P", "plc: placidus", "plc"),
    ("R", "rgm: regiomontanus", "rgm"),
    ("C", "cmp: campanus", "cmp"),
    ("K", "kch: koch", "kch"),
    ("W", "whs: whole sign", "whs"),  # makes no sense to draw it, same as signs
]
CHART_SETTINGS = {
    # toggle glyphs visibility shortcut
    "enable_glyphs": True,
    # harmonics division ring : 0 hide | 1 egypt. terms (bounds)
    # 7, 9 (navamsa), 11 etc ; not all harmonics are available ;
    # add them if you need them | 2 rings are possible
    # !!! those are simple divisions, similar but NOT all equal to varga
    "harmonics_ring": {0},
    # show true midheaven & imum coeli when equal or whole house system is
    # selected : true mc / ic can differ by upto 2 signs in those cases
    "true_mc_ic": True,
    # rotate whole chart so ascendant is fixed at left (east)
    # else aries (mesha) 0° is fixed at left
    "fixed_asc": False,
    # use true node else mean node
    "true_node": True,
    # event data for chart info
    # construct your own 'chart info' format
    # allowed fields: 1: {event} name | 2: weekday {wday} | 3: event {date} |
    # 4: {time} | 5: {city} | 6: country {ctry} | 7: {lat}itude |
    # 8: {lon}gitude ; for short time format (no seconds) use {time[:5]}
    "chart_info_string": r"{event}\n{date}\n{wday} {time[:5]}\n{city} @ {ctry}\n{lat}\n{lon}",
    # data same for both charts
    # additional 'chart info' format: allowed fields: 1: house system {hsys} |
    # 2: {zod}iac | 3: ayanamsa name {aynm} | 4: ayanamsa value {ayvl}
    "chart_info_string_extra": r"{hsys} | {zod}\n{aynm} | {ayvl}",
}
# --- time constants ---
# (solar) year lengths in days
SOLAR_YEAR = {
    "gre": ("365.2425", "365.2425 (gregorian)", ""),
    "jul": ("365.25", "365.25 (julian)", ""),
    "trp": ("365.24219", "365.24219 (tropical)", ""),
    "sid": ("365.256363", "365.256363 (sidereal)", ""),
    "lun": ("354.37", "354.37 (lunar)", ""),
}
# lunar month lengths
LUNAR_MONTH = {
    "trp": ("27.321582", "27.321582 days (tropical); 0 aries (houck)", ""),
    "syn": ("29.53059", "29.53059 days (synodic); new moons", ""),
    "sid": ("27.321661", "27.321661 days (sidereal)", ""),
    "anm": ("27.554551", "27.554551 days (anomalistic); perigee - apogee", ""),
    "drc": ("27.21222", "27.21222 days (draconic); lunar nodes", ""),
}
# !!! UN/COMMENT ANY AYANAMSA THAT YOU NEED !!!
# un/comment > delete '# ', indent properly, and save file
# also arrange order as you please > move line up / down & save file
AYANAMSA = [
    ("17", "17: Galact. Center 0 Sag", "glc (17)"),  # SIDM_GALCENT_0SAG
    ("45", "45: Krishnamurti-Senthilathiban", "kms (45)"),  # SIDM_KRISHNAMURTI_VP291
    ("0", "00: Fagan/Bradley", "fbr (00)"),  # SIDM_FAGAN_BRADLEY
    ("1", "01: Lahiri 1", "lhr (01)"),  # SIDM_LAHIRI
    # ("2", "02: De Luce", "dlc (02)"),  # SIDM_DELUCE
    ("3", "03: Raman", "rmn (03)"),  # SIDM_RAMAN
    # ("4", "04: Usha/Shashi", "uss (04)"),  # SIDM_USHASHASHI
    # ("5", "05: Krishnamurti", "kmr (05)"),  # SIDM_KRISHNAMURTI
    # ("6", "06: Djwhal Khul", "dwk (06)"),  # SIDM_DJWHAL_KHUL
    # ("7", "07: Yukteshwar", "ykt (07)"),  # SIDM_YUKTESHWAR
    # ("8", "08: J.N. Bhasin", "jnb (08)"),  # SIDM_JN_BHASIN
    # ("9", "09: Babylonian/Kugler 1", "bk1 (09)"),  # SIDM_BABYL_KUGLER1
    # ("10", "10: Babylonian/Kugler 2", "bk2 (10)"),  # SIDM_BABYL_KUGLER2
    # ("11", "11: Babylonian/Kugler 3", "bk3 (11)"),  # SIDM_BABYL_KUGLER3
    # ("12", "12: Babylonian/Huber", "bhb (12)"),  # SIDM_BABYL_HUBER
    # ("13", "13: Babylonian/Eta Piscium", "bep (13)"),  # SIDM_BABYL_ETPSC
    # ("14", "14: Babylonian/Aldebaran 15 Tau", "bat (14)"),  # SIDM_ALDEBARAN_15TAU
    # ("15", "15: Hipparchos", "hpc (15)"),  # SIDM_HIPPARCHOS
    # ("16", "16: Sassanian", "snn (16)"),  # SIDM_SASSANIAN
    # ("18", "18: J2000", "j20 (18)"),  # SIDM_J2000
    # ("19", "19: J1900", "j19 (19)"),  # SIDM_J1900
    # ("20", "20: B1950", "b50 (20)"),  # SIDM_B1950
    # ("21", "21: Suryasiddhanta", "ssd (21)"),  # SIDM_SURYASIDDHANTA
    # ("22", "22: Suryasiddhanta, mean Sun", "ssm (22)"),  # SIDM_SURYASIDDHANTA_MSUN
    # ("23", "23: Aryabhata", "ary (23)"),  # SIDM_ARYABHATA
    # ("24", "24: Aryabhata, mean Sun", "arm (24)"),  # SIDM_ARYABHATA_MSUN
    # ("25", "25: SS Revati", "ssr (25)"),  # SIDM_SS_REVATI
    # ("26", "26: SS Citra", "ssc (26)"),  # SIDM_SS_CITRA
    # ("27", "27: True Citra", "tct (27)"),  # SIDM_TRUE_CITRA
    # ("28", "28: True Revati", "trv (28)"),  # SIDM_TRUE_REVATI
    # ("29", "29: True Pushya (PVRN Rao)", "tps (29)"),  # SIDM_TRUE_PUSHYA
    # ("30", "30: Galactic Center (Gil Brand)", "gcb (30)"),  # SIDM_GALCENT_RGBRAND
    # ("31", "31: Galactic Equator (IAU1958)", "gei (31)"),  # SIDM_GALEQU_IAU1958
    # ("32", "32: Galactic Equator", "geq (32)"),  # SIDM_GALEQU_TRUE
    # ("33", "33: Galactic Equator mid-Mula", "gem (33)"),  # SIDM_GALEQU_MULA
    # ("34", "34: Skydram (Mardyks)", "skm (34)"),  # SIDM_GALALIGN_MARDYKS
    # ("35", "35: True Mula (Chandra Hari)", "tmh (35)"),  # SIDM_TRUE_MULA
    ("36", "36: Dhruva/GC/Mula (Wilhelm)", "gcw (36)"),  # SIDM_GALCENT_MULA_WILHELM
    # ("37", "37: Aryabhata 522", "ary (37)"),  # SIDM_ARYABHATA_522
    # ("38", "38: Babylonian/Britton", "bbb (38)"),  # SIDM_BABYL_BRITTON
    # ("39", "39: Vedic Sheoran", "vsh (39)"),  # SIDM_TRUE_SHEORAN
    # ("40", "40: Cochrane (Gal.Center 0 Cap)", "gcc (40)"),  # SIDM_GALCENT_COCHRANE
    # ("41", "41: Galactic Equator (Fiorenza)", "gef (41)"),  # SIDM_GALEQU_FIORENZA
    # ("42", "42: Vettius Valens", "vvl (42)"),  # SIDM_VALENS_MOON
    # ("43", "43: Lahiri 1940", "lh2 (43)"),  # SIDM_LAHIRI_1940
    # ("44", "44: Lahiri VP285", "lh3 (44)"),  # SIDM_LAHIRI_VP285
    # ("46", "46: Lahiri ICRC", "lh4 (46)"),  # SIDM_LAHIRI_ICRC
    ("255", "user-defined (setup in 'settings')", "usr"),  # SIDM_USER
]
CUSTOM_AYANAMSA = {
    # custom user-defined ayanamsa properties
    # julian day utc > reference date for custom ayanamsa calculation
    # default is for 2000-01-01 12:00 utc (julian day starts at noon)
    # if needed, get julian day utc online, then copy-paste the number here
    "custom_utc_julian_day": "2451545.00000",
    # user-defined custom ayanamsa : must be decimal degrees
    # default is 23.76694445 (23° 46' 01"), as per richard houck's book
    # 'astrology of death', for 2000-01-01
    "custom_ayanamsa": "23.76694444",
}
FILES = {
    # --- path to ephemerides folder, with min semo_18.se1 & sepl_18.se1 files, or
    # a complete ephe folder https://github.com/aloistr/swisseph/tree/master/ephe
    "ephe_path": "/swe/ephe/",
    # --- fonts for glyphs = astro_font & for ie tables = mono_font
    "astro_font": "/ui/fonts/osla/open_sans_light_astro.ttf",
    "mono_font": "/ui/fonts/victor/VictorMonoNerdFont-Light.ttf",
    # --- construct your own 'filename' format: allowed fields
    # 1: {event} name | 2: event {date} | 3: {time}
    # separate fields with '_' underscore ; for short time format (no seconds)
    # use {time[:5]} ; see default value as example
    "custom_filename": r"{event}_{date}_{time[:5]}",
    # --- path to events / birth charts database folder; inside go saved charts
    "events_db": "/user/eventsdb/",
}
