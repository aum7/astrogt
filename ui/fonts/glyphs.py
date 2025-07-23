# ui/fonts/glyphs.py
# unicode glyphs from victormonolightastro.ttf font
PLANETS = {
    "su": "\u0180",
    "mo": "\u0181",
    "me": "\u0182",
    "ve": "\u0183",
    "ma": "\u0184",
    "ju": "\u0185",
    "sa": "\u0186",
    "ur": "\u0187",
    "ne": "\u0188",
    "pl": "\u0189",
    "rt": "\u018e",  # rahu true
    "rm": "\u018c",  # rahu mean
}
SIGNS = {  # sign, element, mode
    "ar": ("\u0192", "\u01d9", "\u01ea"),  # 01 f m
    "ta": ("\u0193", "\u01da", "\u01e9"),  # 02 e f
    "ge": ("\u0194", "\u01db", "\u01eb"),  # 03 a d
    "cn": ("\u0195", "\u01dc", "\u01ea"),  # 04 w m
    "le": ("\u0196", "\u01d9", "\u01e9"),  # 05 f f
    "vi": ("\u0197", "\u01da", "\u01eb"),  # 06 e d
    "li": ("\u0198", "\u01db", "\u01ea"),  # 07 a m
    "sc": ("\u0199", "\u01dc", "\u01e9"),  # 08 w f
    "sg": ("\u019a", "\u01d9", "\u01eb"),  # 09 f d
    "cp": ("\u019b", "\u01da", "\u01ea"),  # 10 e m
    "aq": ("\u019c", "\u01db", "\u01e9"),  # 11 a f
    "pi": ("\u019d", "\u01dc", "\u01eb"),  # 12 w d
}
ASPECTS = {
    0: ("\u019e", "conjunction"),
    60: ("\u01a2", "sextile"),
    90: ("\u01a1", "square"),
    120: ("\u01a0", "trine"),
    180: ("\u019f", "opposition"),
}
ELEMENTS = {
    "fire": "\u01d9",
    "earth": "\u01da",
    "air": "\u01db",
    "water": "\u01dc",
}
MODES = {
    "movable": "\u01ea",
    "fixed": "\u01e9",
    "dual": "\u01eb",
}
ECLIPSES = {
    "sol": "\u01ae",
    "lun": "\u01af",
}
SYZYGY = {  # prenatal lunation
    "syzn": ("\u01ec", "conjunction"),  # new moon
    "syzf": ("\u01ed", "opposition"),  # full moon
}
LOTS = {  # aka arabic parts
    "fortuna2": "\u018b",  # fortuna X
    "fortuna": "\u01e2",  # mo
    "spirit": "\u01e3",  # su
    "eros": "\u01e4",  # ve
    "necessity": "\u01e5",  # me
    "courage": "\u01e6",  # ma
    "victory": "\u01e7",  # ju
    "nemesis": "\u01e8",  # sa
}
MOON_PHASES = {
    "new": "\u01c7",
    "wax cresc": "\u01c8",  # up
    "first quart": "\u01c9",
    "wax gib": "\u01ca",
    "full": "\u01cb",
    "wan gib": "\u01cc",  # down
    "last quart": "\u01cd",
    "wan cresc": "\u01ce",
}
EXTRA = {
    "jinjang": "\u01d8",
    "house": "\u01e1",
    "retro": "\u01b8",
    "direct": "\u01b9",
    "stationary": "\u01ba",
    "natal": "\u01bb",
    "radix": "\u01bc",
    "transit": "\u01bd",
    "progressed": "\u01be",
    "asc": "\u01bf",
    "dsc": "\u01c0",
    "mc": "\u01c1",
    "ic": "\u01c2",
}


def get_lunation_glyph(name: str) -> str:
    # select conj or oppo glyph
    return EXTRA.get("jinjang", "")


def get_eclipse_glyph(name: str) -> str:
    # select eclipse glyph
    return ECLIPSES.get(name[:3], "")


def get_lot_glyph(name: str) -> str:
    # select lot glyph
    return LOTS.get(name, "")


def get_glyph(name: str, use_mean_node: bool) -> str:
    """select proper rahu glyph & return glyphs"""
    if name in ("ra", "rahu"):
        if use_mean_node:
            return PLANETS["rm"]
        else:
            return PLANETS["rt"]
    return PLANETS.get(name, "")
