# user/settings.py
# set default preferences : for sweph calculations & app settings
# recommended to setup before application start : usually once per user
# do not modify while application is running : results unknown
# settings can be changed in application > sidepane > settings panel
# some info / description is provided below as comments, details are in
# original sweph documentation, ie swephprg.pdf & swisseph.pdf at
# https://github.com/aloistr/swisseph/tree/master/doc
OBJECTS = {
    0: ("su", "sun", "sy", "surya"),
    1: ("mo", "moon", "ca", "candra"),
    2: ("me", "mercury", "bu", "budha"),
    3: ("ve", "venus", "sk", "sukra"),
    4: ("ma", "mars", "ma", "mangala"),
    5: ("ju", "jupiter", "gu", "guru"),
    6: ("sa", "saturn", "sa", "sani"),
    7: ("ur", "uranus", "ur", "uranus"),
    8: ("ne", "neptune", "ne", "neptune"),
    9: ("pl", "pluto", "pl", "pluto"),
    11: ("ra", "true node", "ra", "rahu"),
}
SWE_FLAG = {
    # default flags for sweph calculations
    # all flags are duplicated & commented as backup ; user can toggle them in
    # settings panel which will update uncommented flags / values (this file)
    # --- use sidereal (jyotisa) zodiac : else use tropical (western) zodiac
    # FLG_SIDEREAL vs FLG_TROPICAL (default)
    # "sidereal zodiac": (True, "use sideral (vs tropical) zodiac"),
    "sidereal zodiac": (True, "use sideral (vs tropical) zodiac"),
    # --- calculate true, not apparent (visible from earth) positions
    # journey of the light from a planet to the earth takes some time
    # FLG_TRUEPOS
    # "true positions": (True, "calculate true (vs apparent) positions"),
    "true positions": (True, "calculate true (vs apparent) positions"),
    # --- calculate topocentric positions, viewed from latitude & longitude of
    # event ; else calculate geocentric positions (default, used traditionally
    # in astrology), viewed from center of the earth
    # if true : call swe_set_topo(geo_lon, geo_lat, altitude_above_sea) todo
    # FLG_TOPOCTR
    # "topocentric": (True, "calculate topocentric (vs geocentric) positions"),
    "topocentric": (True, "calculate topocentric (vs geocentric) positions"),
    # --- calculate heliocentric positions : astrology uses geocentric positions
    # FLG_HELCTR
    # "heliocentric": (False, "calculate heliocentric (vs geocentric) positions"),
    "heliocentric": (False, "calculate heliocentric (vs geocentric) positions"),
    # --- use default sweph ephemeris & speed calculations
    # "default flag": (True, "use default (sweph ephemeris & speed calculations)"),
    "default flag": (True, "use default (sweph ephemeris & speed calculations)"),
    # --- do NOT use nutation : small irregularity in the precession of the equinoxes
    # use mean equinox of date
    # FLG_NONUT
    # "no nutation": (
    #     True,
    #     "do NOT use nutation (small irregularity in precession of the equinoxes)",
    # ),
    "no nutation": (
        True,
        "do NOT use nutation if checked (small irregularity in equinoxes precession)",
    ),
    # --- astrometric (not used = FLG_NOABERR | FLG_NOGDEFL > both below)
    # the light-time correction is computed, but annual aberration and
    # light-deflection by the sun neglected
    # FLG_ASTROMETRIC
    # --- no abberation : small irregularity in the motion of the moons
    # FLG_NOABERR
    # "no aberration": (False, "do NOT use aberration (small irregularity of moon)"),
    "no abberation": (
        False,
        "do NOT use aberration if checked (small irregularity of moon)",
    ),
    # --- no gravity deflection
    # FLG_NOGDEFL
    # "no deflection": (False, "do NOT use gravitational deflection"),
    "no deflection": (False, "do NOT use gravitational deflection if checked"),
    # --- return equatorial positions (right ascension & declination)
    # else return ecliptic (default, latitude & longitude) positions
    # FLG_EQUATORIAL
    # "equatorial": (False, "return equatorial (vs ecliptic) positions"),
    "equatorial": (False, "return equatorial (vs ecliptic) positions"),
    # --- return cartesian (x, y, z) else polar (default) coordinates
    # FLG_XYZ
    # "cartesian": (False, "return cartesian (x, y, z vs polar degrees) coordinates"),
    "cartesian": (False, "return cartesian (x, y, z vs polar degrees) coordinates"),
    # --- return radian else degree (default) units
    # FLG_RADIANS
    # "radians": (False, "return radian (vs degree) units"),
    "radians": (False, "return radian (vs degree) units"),
}
# add or remove houses as you please
# https://astrorigin.com/pyswisseph/sphinx/programmers_manual/house_cusp_calculation.html?highlight=houses#swisseph.houses
# below are most popular 7 out of 24+; arrange line up or down as you please
HOUSE_SYSTEMS = [
    ("E", "eqa : equal asc", "eqa"),
    ("D", "eqm : equal mc", "eqm"),
    ("O", "prp : porphyry", "prp"),
    ("P", "plc : placidus", "plc"),
    ("R", "rgm : regiomontanus", "rgm"),
    ("C", "cmp : campanus", "cmp"),
    ("K", "kch : koch", "kch"),
    ("W", "whs : whole sign", "whs"),  # makes no sense to draw it, same as signs
]
CHART_SETTINGS = {
    # --- toggle glyphs visibility (shortcut)
    "enable glyphs": (True, "toggle glyphs visibility"),
    # --- show true midheaven & imum coeli when equal or whole house system is
    # selected : true mc / ic can differ by upto 2 signs in those cases
    "true mc & ic": (
        True,
        "show true mc & ic when equal or whole house system is selected",
    ),
    # --- rotate whole chart so ascendant is fixed at left (east)
    # else aries (mesha) 0° is fixed at left
    "fixed asc": (
        False,
        "rotate chart so ascendant is fixed at left (east)\nelse aries 0° is fixed at left (default)",
    ),
    # --- use mean node else true node
    "mean node": (False, "calculate mean node (vs default true node)"),
    # --- naksatras MEGA-ring ! lol
    "naksatras ring": (
        True,
        """show naksatras ring
1  asv\t2  bha\t3  krt
4  roh\t5  mrg\t6  ard
7  pun\t8  pus\t9  asl
10 mag\t11 pph\t12 uph
13 has\t14 cit\t15 sva
16 vis\t17 anu\t18 jye
19 mul\t20 pas\t21 uas
22 sra\t23 dha\t24 sat
25 pbh\t26 ubh\t27 rev""",
    ),
    # --- use 28 (all equal = no mini abhijt) else standard 27 naksatras
    "28 naksatras": (
        True,
        """use 28 (all equal = no mini abhijit) vs standard 27 naksatras
1  asv\t2  bha\t3  krt\t4  roh
5  mrg\t6  ard\t7  pun\t8  pus
9  asl\t10 mag\t11 pph\t12 uph
13 has\t14 cit\t15 sva\t16 vis
17 anu\t18 jye\t19 mul\t20 pas
21 uas\t22 abh\t23 sra\t24 dha
25 sat\t26 pbh\t27 ubh\t28 rev""",
    ),
    # --- start naksatras ring with naksatra
    "1st naksatra": (
        1,
        "start naksatras ring with any naksatra\nrotate relative to 0° aries\n1 = asvini (standard)\n19 = mula\n22 = abhijit if 28 naksatras etc",
    ),
    # --- harmonics division ring : 0 hide | 1 egypt. terms (bounds)
    # 7, 9 (navamsa), 11 etc ; not all harmonics are available ;
    # add them if you need them | 2 rings are possible
    # !!! those are simple divisions, similar but NOT all equal to varga
    "harmonics ring": (
        (0),
        "harmonics ring\n0 : do NOT show | 1 : egypt. terms (bounds)\n7, 9, 11 : simple harmonics *similar* to varga\n2 rings possible ie [1 9] will show terms & navamsa",
    ),
    # --- event data to be presented in chart info
    # construct your own 'chart info' format
    # allowed fields: 1: {event} name | 2: weekday {wday} | 3: event {date} |
    # 4: {time} | 5: {city} | 6: country {ctry} | 7: {lat}itude |
    # 8: {lon}gitude ; for short time format (no seconds) use {time[:5]}
    "chart info string": (
        r"{event}\n{date}\n{wday} {time[:5]}\n{city} @ {ctry}\n{lat}\n{lon}",
        r"""construct your own 'chart info' format : allowed fields :
    1: {event} name | 2: weekday {wday} |
    3: event {date} | 4: {time} |
    5: {city} | 6: country {ctry} |
    7: {lat}itude | 8: {lon}gitude
for short time format (no seconds) use {time[:5]}
\n = new line
example : {event}\n{date}\n{wday} {time[:5]}\n{city} @ {ctry}\n{lat}\n{lon} """,
    ),
    # - data same for both charts
    # additional 'chart info' format: allowed fields: 1: house system {hsys} |
    # 2: {zod}iac | 3: ayanamsa name {aynm} | 4: ayanamsa value {ayvl}
    "chart info string extra": (
        r"{hsys} | {zod}\n{aynm} | {ayvl}",
        r"""additional 'chart info' format : allowed fields :
    1: house system {hsys} | 2: {zod}iac |
    3: ayanamsa name {aynm} | 4: ayanamsa value {ayvl}
    example : {hsys} | {zod}\n{aynm} | {ayvl}
    \n = new line""",
    ),
}
# --- time constants ---
# (solar) year lengths in days
SOLAR_YEAR = {
    "gre": (365.2425, "gregorian"),
    "jul": (365.25, "julian"),
    "trp": (365.24219, "tropical"),
    "sid": (365.256363, "sidereal"),
    "lun": (354.37, "lunar"),
}
# lunar month lengths
LUNAR_MONTH = {
    "sid": (27.321661, "sidereal\t\tfixed star"),
    "trp": (27.321582, "tropical\t\t0 ari (houck)"),
    "syn": (29.53059, "synodic\t\tnew moons"),
    "anm": (27.554551, "anomalistic\tperigee-apogee"),
    "drc": (27.21222, "draconic\tlunar nodes"),
}
# !!! UNCOMMENT ANY AYANAMSA THAT YOU NEED !!!
# uncomment > delete '# ', indent properly, and save file
# also arrange order as you please > move line up / down & save file
AYANAMSA = {
    17: ("Galact. Center 0 Sag", "glc (17)"),  # SIDM_GALCENT_0SAG
    45: ("Krishnamurti-Senthilathiban", "kms (45)"),  # SIDM_KRISHNAMURTI_VP291
    # 0: ("Fagan/Bradley", "fbr (00)"),  # SIDM_FAGAN_BRADLEY
    # 1: ("Lahiri 1", "lhr (01)"),  # SIDM_LAHIRI
    # 2: ("De Luce", "dlc (02)"),  # SIDM_DELUCE
    # 3: ("Raman", "rmn (03)"),  # SIDM_RAMAN
    # 4: ("Usha/Shashi", "uss (04)"),  # SIDM_USHASHASHI
    # 5: ("Krishnamurti", "kmr (05)"),  # SIDM_KRISHNAMURTI
    # 6: ("Djwhal Khul", "dwk (06)"),  # SIDM_DJWHAL_KHUL
    # 7: ("Yukteshwar", "ykt (07)"),  # SIDM_YUKTESHWAR
    # 8: ("J.N. Bhasin", "jnb (08)"),  # SIDM_JN_BHASIN
    # 9: ("Babylonian/Kugler 1", "bk1 (09)"),  # SIDM_BABYL_KUGLER1
    # 10: ("Babylonian/Kugler 2", "bk2 (10)"),  # SIDM_BABYL_KUGLER2
    # 11: ("Babylonian/Kugler 3", "bk3 (11)"),  # SIDM_BABYL_KUGLER3
    # 12: ("Babylonian/Huber", "bhb (12)"),  # SIDM_BABYL_HUBER
    # 13: ("Babylonian/Eta Piscium", "bep (13)"),  # SIDM_BABYL_ETPSC
    # 14: ("Babylonian/Aldebaran 15 Tau", "bat (14)"),  # SIDM_ALDEBARAN_15TAU
    # 15: ("Hipparchos", "hpc (15)"),  # SIDM_HIPPARCHOS
    # 16: ("Sassanian", "snn (16)"),  # SIDM_SASSANIAN
    # 18: ("J2000", "j20 (18)"),  # SIDM_J2000
    # 19: ("J1900", "j19 (19)"),  # SIDM_J1900
    # 20: ("B1950", "b50 (20)"),  # SIDM_B1950
    # 21: ("Suryasiddhanta", "ssd (21)"),  # SIDM_SURYASIDDHANTA
    # 22: ("Suryasiddhanta, mean Sun", "ssm (22)"),  # SIDM_SURYASIDDHANTA_MSUN
    # 23: ("Aryabhata", "ary (23)"),  # SIDM_ARYABHATA
    # 24: ("Aryabhata, mean Sun", "arm (24)"),  # SIDM_ARYABHATA_MSUN
    # 25: ("SS Revati", "ssr (25)"),  # SIDM_SS_REVATI
    # 26: ("SS Citra", "ssc (26)"),  # SIDM_SS_CITRA
    # 27: ("True Citra", "tct (27)"),  # SIDM_TRUE_CITRA
    # 28: ("True Revati", "trv (28)"),  # SIDM_TRUE_REVATI
    29: ("True Pushya (PVRN Rao)", "tps (29)"),  # SIDM_TRUE_PUSHYA
    # 30: ("Galactic Center (Gil Brand)", "gcb (30)"),  # SIDM_GALCENT_RGBRAND
    # 31: ("Galactic Equator (IAU1958)", "gei (31)"),  # SIDM_GALEQU_IAU1958
    # 32: ("Galactic Equator", "geq (32)"),  # SIDM_GALEQU_TRUE
    # 33: ("Galactic Equator mid-Mula", "gem (33)"),  # SIDM_GALEQU_MULA
    # 34: ("Skydram (Mardyks)", "skm (34)"),  # SIDM_GALALIGN_MARDYKS
    # 35: ("True Mula (Chandra Hari)", "tmh (35)"),  # SIDM_TRUE_MULA
    # 36: ("Dhruva/GC/Mula (Wilhelm)", "gcw (36)"),  # SIDM_GALCENT_MULA_WILHELM
    # 37: ("Aryabhata 522", "ary (37)"),  # SIDM_ARYABHATA_522
    # 38: ("Babylonian/Britton", "bbb (38)"),  # SIDM_BABYL_BRITTON
    # 39: ("Vedic Sheoran", "vsh (39)"),  # SIDM_TRUE_SHEORAN
    # 40: ("Cochrane (Gal.Center 0 Cap)", "gcc (40)"),  # SIDM_GALCENT_COCHRANE
    41: ("Galactic Equator (Fiorenza)", "gef (41)"),  # SIDM_GALEQU_FIORENZA
    # 42: ("Vettius Valens", "vvl (42)"),  # SIDM_VALENS_MOON
    # 43: ("Lahiri 1940", "lh2 (43)"),  # SIDM_LAHIRI_1940
    # 44: ("Lahiri VP285", "lh3 (44)"),  # SIDM_LAHIRI_VP285
    # 46: ("Lahiri ICRC", "lh4 (46)"),  # SIDM_LAHIRI_ICRC
    255: ("user-defined (below)", "usr"),  # SIDM_USER
}
CUSTOM_AYANAMSA = {
    # custom user-defined ayanamsa properties
    # julian day utc > reference date for custom ayanamsa calculation
    # default is for 2000-01-01 12:00 utc (julian day starts at noon)
    # if needed, get julian day utc online, then copy-paste the number here
    "custom julian day utc": 2451545.00000,
    # user-defined custom ayanamsa : must be decimal degrees
    # default is 23.76694445 (23° 46' 01"), as per richard houck's book
    # 'astrology of death', for 2000-01-01
    "custom ayanamsa": 23.76694444,
}
FILES = {
    # --- path to ephemerides folder, with min semo_18.se1 & sepl_18.se1 files, or
    # a complete ephe folder https://github.com/aloistr/swisseph/tree/master/ephe
    # todo separate path for linux & mswindows : do we need to ?
    "ephe path\t": (
        "/sweph/ephe/",
        "path to ephemeride folder, with min semo_18.se1 & sepl_18.se1 files, "
        "or a complete ephe folder https://github.com/aloistr/swisseph/tree/master/ephe ",
    ),
    # --- fonts for glyphs = astro_font & for ie tables = mono_font
    "astro font\t": (
        "/ui/fonts/osla/open_sans_light_astro.ttf",
        "font with glyphs for astro chart etc",
    ),
    "mono font\t": (
        "/ui/fonts/victor/VictorMonoNerdFont-Light.ttf",
        "mono-spaced font for pretty tables etc",
    ),
    # --- path to events / birth charts database folder; inside go saved charts
    "events db\t": (
        "/user/eventsdb/",
        "path to event / birth charts database folder ; inside go saved charts",
    ),
    # --- construct your own 'filename' format: allowed fields
    # 1: {event} name | 2: event {date} | 3: {time}
    # separate fields with '_' underscore ; for short time format (no seconds)
    # use {time[:5]} ; see default value as example
    "filename\t": (
        r"{event}_{date}_{time[:5]}",
        "construct your own 'filename' format: allowed fields"
        "\n\t1: {event} name | 2: event {date} | 3: {time}"
        "\nseparate fields with '_' underscore ; for short time format "
        "(no seconds) use {time[:5]}"
        "\nexample : {event}_{date}_{time[:5]}",
    ),
}
