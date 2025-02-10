# set preferences for swisseph calculations
SWE_SETTINGS = {
    # fonts for glyphs = astro_font & for ie tables = mono_font
    "astro_font": "/ui/fonts/osla/open_sans_light_astro.ttf",
    "mono_font": "/ui/fonts/victor/VictorMonoNerdFont-Light.ttf",
    # event data for chart info
    # 1:event|2:weekday|3:date|4:time|5:city|6:country|7:lat|8:lon|
    # data same for both charts
    # 1:house system|2:zodiac|3:ayanamsa name|4:ayanamsa value
    # TODO : need below ?
    event_data_1_: StringProperty(default="")
    event_data_2_: StringProperty(default="")
    ayanamsa_event_1_: StringProperty(default="")
    ayanamsa_event_2_: StringProperty(default="")
    # increase / decrease time with hotkeys
    time_change_call_: BoolProperty(default=False)
    time_change_: EnumProperty(
        name="",
        # name="time change",
        description="increase or decrease time with hotkeys\nup / down arrow to change time unit\nleft / right arrow to decrease / increase (time back / forward)\nNOTE: use 'debug' panel (enable blender 'developer mode') to see which time unit is selected",
        items=[
            ("2592000", "30 days", ""),
            ("604800", "1 week", ""),
            ("86400", "1 day", ""),
            ("43200", "12 hours", ""),
            ("3600", "1 hour", ""),
            ("600", "10 minutes", ""),
            ("60", "1 minute", ""),
            ("10", "10 seconds", ""),
            ("1", "1 second", ""),
        ],
    )
    # time change direction
    time_forward_: BoolProperty(
        name="time direction",
        description="time direction backward (False) or forward (True)",
        default=True,
    )
    # toggle glyphs visibility shortcut
    update_glyphs_enable: BoolProperty(default=True)

    def update_glyphs(self, context):
        if not self.update_glyphs_enable:
            return
        try:
            bpy.ops.hotkey.glyphs()
        except Exception as e:
            msg_ = f"ba_props: update_glyphs: ERROR\n{str(e)}"
            print(msg_)

    # set 'name' to empty if / when many toggles are present
    glyphs: BoolProperty(
        name="glyphs",
        description="toggle GLYPHS visibility",
        default=False,
        update=update_glyphs,
    )

    # toggle glyphs visibility shortcut
    update_markers_enable: BoolProperty(default=True)

    def update_markers(self, context):
        if not self.update_markers_enable:
            return
        try:
            bpy.ops.hotkey.markers()
        except Exception as e:
            msg_ = f"ba_props: update_markers: ERROR\n{str(e)}"
            print(msg_)
        except NameError as e:
            msg_ = f"ba_props: update_markers: ERROR\n{str(e)}"
            print(msg_)

    markers: BoolProperty(
        name="markers",
        description="toggle MARKERS visibility",
        default=False,
        update=update_markers,
    )
    filename_f: StringProperty(
        name="",
        description="construct your own 'filename' format: allowed fields:\n1: {event} name | 2: event {date} | 3: {time}: separate fields with '_' underscore\nfor short time format (no seconds) use {time[:5]}\nsee default value [mouse-over-backspace] as example",
        default=r"{event}_{date}_{time[:5]}",
    )
    run_clock_1_: BoolProperty(default=False)
    run_clock_2_: BoolProperty(default=False)
    link_comp_: StringProperty(default="link")
    # datetime
    # TODO : need loc_dt ?
    loc_dt_1_: StringProperty()  # local timezone-aware datetime string, for file name
    utc_dt_1_: StringProperty()  # utc timezone-aware datetime string, for utc jd
    utc_jd_1_: StringProperty()  # utc julian day, for swe calculations
    loc_dt_2_: StringProperty()
    utc_dt_2_: StringProperty()
    utc_jd_2_: StringProperty()
    # location : saved from event.coordinates
    lat_1_: StringProperty()
    lon_1_: StringProperty()
    lat_2_: StringProperty()
    lon_2_: StringProperty()
    # houses
    asc_1_: StringProperty()
    mc_1_: StringProperty()
    asc_2_: StringProperty()
    mc_2_: StringProperty()
    # sweph
    sweph_flags_: IntProperty()
    # house_flags_: IntProperty()  # TODO need this ?

    # countries / location
    countries_file: StringProperty(
        name="countries",
        description="path to countries list, to be used for timezone calculations\nsee '/data/countries.txt' file; modify it as you see fit, and point here the path to the file itself",
        default="/data/countries.txt",
        subtype="FILE_PATH",
    )

    # one list for both events
    def countries_list(self, context):
        countries_list = []
        try:
            with open(self.countries_file, "r") as file:
                lines = file.readlines()
                # parse the file
                for line in lines:
                    # skip line if it is commented
                    if line.startswith("#"):
                        continue
                    line = line.strip()
                    # if line.startswith("(") and line.endswith("),"):
                    line = line[1:-2]
                    # print(f"line : {line}\n")
                    parts = [p.strip().strip('"') for p in line.split('",')]
                    if len(parts) == 3:
                        countries_list.append((parts[0], parts[1], parts[2]))
        except Exception as e:
            msg = f"ba_props: countries_list: error reading or parsing 'data/countries.txt' file:\n{e}"
            print(msg)

        return countries_list

    # --- event 1 ---
    # prevent circular code with pause flag
    update_event_1_enable: BoolProperty(default=True)

    def update_event_1(self, context):
        self.which_event_ = 1
        # flag to prevent circular code
        if not self.update_event_1_enable:
            return
        try:
            bpy.ops.event.one()
        except Exception as e:
            msg = f"ba_props: update_event_1: event.one error:\n{str(e)}"
            print(msg)

    event_1: StringProperty(
        name="",
        description="event / person name: a key to save in user database\nuse 'dummy' for temporary / test charts",
        default="dummy",
        update=update_event_1,
    )
    # datetime
    update_dt_1_enable: BoolProperty(default=True)
    # dt_local_str_old: StringProperty(default="")

    def update_dt_1(self, context):
        bapp = bpy.data.scenes["zodiac"].bapp

        self.which_event_ = 1
        if not self.update_dt_1_enable:
            return
        try:
            bpy.ops.event.dt()
        except Exception as e:
            msg = f"ba_props: update_dt_1: event.dt error:\n{str(e)}"
            print(msg)

    # for chart info only
    weekday_1: StringProperty(default="")
    # ui datetime properties
    year_1: IntProperty(
        name="",
        description="year",
        default=2024,
        min=1,
        max=3000,
        update=update_dt_1,
    )
    month_1: IntProperty(
        name="",
        description="month",
        default=1,
        min=0,
        max=13,
        update=update_dt_1,
    )
    day_1: IntProperty(
        name="",
        description="day",
        default=1,
        min=0,
        max=32,
        update=update_dt_1,
    )
    hour_1: IntProperty(
        name="",
        description="hour",
        default=12,
        min=-1,
        max=24,
        update=update_dt_1,
    )
    min_1: IntProperty(
        name="",
        description="minute",
        default=0,
        min=-1,
        max=60,
        update=update_dt_1,
    )
    sec_1: IntProperty(
        name="",
        description="second",
        default=0,
        min=-1,
        max=60,
        update=update_dt_1,
    )
    # location 1
    update_location_1_enable: BoolProperty(default=True)
    # updating ie city_1 while 'loc_2_equal_1' will set 'which_event_' = 2 : fix
    call_from_location_1: BoolProperty(default=False)
    multiple_locations: StringProperty(default="")
    selected_location: StringProperty(default="")
    selection_complete: BoolProperty(default=False)

    def update_location_1(self, context):
        self.which_event_ = 1
        self.call_from_location_1 = True
        # print(f"ba_props:\n\tupdate_location_1: CALLED\n")
        if not self.update_location_1_enable:
            return
        try:
            bpy.ops.event.location()
        except RuntimeError:
            print(f"ba_props: update_location_1: RUNTIME ERROR")
        except Exception as e:
            msg = f"ba_props: update_location_1: event.location ERROR"
            print(msg)

    city_1: StringProperty(
        name="",
        description="write event location - city name\nused for timezone, latitude & longitude calculation\nuse english name, and make sure the city matches the country",
        default="helsinki",
        update=update_location_1,
    )
    country_1: EnumProperty(
        name="",
        description="select country of the city\nused for timezone, latitude & longitude calculation\nadd or remove a country: open '/data/countries.txt' file, un/comment a country you don't/need, and save file",
        items=countries_list,
        update=update_location_1,
    )
    coordinates_insert_1: BoolProperty(
        name="insert coordinates",
        description="insert latitude & longitude automatically\nunchecked: latitude & longitude are set manually by user, when precise coordinates are required (acquired ie via online map)",
        default=False,
        update=update_location_1,
    )
    tz_1: StringProperty(
        name="timezone",
        description=tz_description,
        default="Europe/Helsinki",
    )
    # coordinates
    update_coordinates_1_enable: BoolProperty(default=True)

    def update_coordinates_1(self, context):
        self.which_event_ = 1
        if not self.update_coordinates_1_enable:
            return
        try:
            bpy.ops.event.coordinates()
        except Exception as e:
            msg = f"ba_props: update_coordinates_1: event.coordinates error"
            print(msg)

    # coordinates
    lat_deg_1: IntProperty(
        name="",
        description="latitude degree",
        default=60,
        min=0,
        max=179,
        update=update_coordinates_1,
    )
    lat_min_1: IntProperty(
        name="",
        description="latitude minute",
        default=12,
        min=0,
        max=59,
        update=update_coordinates_1,
    )
    lat_sec_1: IntProperty(
        name="",
        description="latitude second",
        default=15,
        min=0,
        max=59,
        update=update_coordinates_1,
    )
    lat_dir_1: StringProperty(
        name="",
        description="latitude direction : n(orth) or s(outh)",
        default="n",
        maxlen=1,
        update=update_coordinates_1,
    )
    lon_deg_1: IntProperty(
        name="",
        description="longitude degree",
        default=24,
        min=0,
        max=179,
        update=update_coordinates_1,
    )
    lon_min_1: IntProperty(
        name="",
        description="longitude minute",
        default=55,
        min=0,
        max=59,
        update=update_coordinates_1,
    )
    lon_sec_1: IntProperty(
        name="",
        description="longitude second",
        default=26,
        min=0,
        max=59,
        update=update_coordinates_1,
    )
    lon_dir_1: StringProperty(
        name="",
        description="longitude direction : e(ast) or w(est)",
        default="e",
        maxlen=1,
        update=update_coordinates_1,
    )
    alt_1: IntProperty(
        name="",
        description="location altitude in meters above sea",
        default=0,
        update=update_coordinates_1,
    )

    # --- event 2 ---
    # prevent circular code with pause flag
    update_event_2_enable: BoolProperty(default=True)

    def update_event_2(self, context):
        self.which_event_ = 2
        if not self.update_event_2_enable:
            return
        try:
            bpy.ops.event.two()
        except Exception as e:
            msg = f"ba_props: update_event_2: event.two error:\n{str(e)}"
            print(msg)

    event_2: StringProperty(
        name="",
        description="event / person name: a key to save in user database\nuse 'dummy 2' for temporary / test charts\nNOTE: set event type with right-most button",
        default="dummy 2",
        update=update_event_2,
    )
    # datetime
    update_dt_2_enable: BoolProperty(default=True)

    def update_dt_2(self, context):
        self.which_event_ = 2
        if not self.update_dt_2_enable:
            return
        try:
            bpy.ops.event.dt()
        except Exception as e:
            msg = f"ba_props: update_dt_2: event.dt error:\n{e}"
            print(msg)

    # for chart info only
    weekday_2: StringProperty(default="")
    year_2: IntProperty(
        name="",
        description="year",
        default=2024,
        min=-3000,
        max=3000,
        update=update_dt_2,
    )
    month_2: IntProperty(
        name="",
        description="month",
        default=1,
        min=1,
        max=12,
        update=update_dt_2,
    )
    day_2: IntProperty(
        name="",
        description="day",
        default=1,
        min=1,
        max=31,
        update=update_dt_2,
    )
    hour_2: IntProperty(
        name="",
        description="hour",
        default=12,
        min=0,
        max=23,
        update=update_dt_2,
    )
    min_2: IntProperty(
        name="",
        description="minute",
        default=0,
        min=0,
        max=59,
        update=update_dt_2,
    )
    sec_2: IntProperty(
        name="",
        description="second",
        default=0,
        min=0,
        max=59,
        update=update_dt_2,
    )
    # location 2
    update_location_2_enable: BoolProperty(default=True)

    def update_location_2(self, context):
        self.which_event_ = 2
        # print(f"ba_props:\n\tupdate_location_2: CALLED\n")
        if not self.update_location_2_enable:
            return
        try:
            bpy.ops.event.location()
        except RuntimeError:
            print(f"ba_props: update_location_2: RUNTIME ERROR")
        except Exception as e:
            msg = f"ba_props: update_location_2: event.location error"
            print(msg)

    loc_2_equal_1: BoolProperty(
        name="equal to location 1",
        description="event 2 location is equal to event 1 location",
        default=True,
        update=update_location_2,
    )
    city_2: StringProperty(
        name="",
        description="write event location - city name\nused for timezone, latitude & longitude calculation\nuse english name, and make sure the city matches the country",
        default="",
        update=update_location_2,
    )
    country_2: EnumProperty(
        name="",
        description="select country of the city\nused for timezone, latitude & longitude calculation",
        items=countries_list,
        update=update_location_2,
    )
    coordinates_insert_2: BoolProperty(
        name="insert coordinates",
        description="insert latitude & longitude automatically\nunchecked: latitude & longitude are set manually by user, when precise coordinates are required (acquired ie via online map)\n NOTE: if above 'equal to location 1' is seleced, this one is also set to selected",
        default=False,
        update=update_location_2,
    )
    tz_2: StringProperty(
        name="timezone",
        description=tz_description,
        default="",
    )
    # coordinates
    update_coordinates_2_enable: BoolProperty(default=True)

    def update_coordinates_2(self, context):
        self.which_event_ = 2
        if not self.update_coordinates_2_enable:
            return
        try:
            bpy.ops.event.coordinates()
        except Exception as e:
            msg = f"ba_props: update_coordinates_2: event.coordinates error"
            print(msg)

    lat_deg_2: IntProperty(
        name="",
        description="latitude degree",
        default=60,
        min=0,
        max=179,
        update=update_coordinates_2,
    )
    lat_min_2: IntProperty(
        name="",
        description="latitude minute",
        default=12,
        min=0,
        max=59,
        update=update_coordinates_2,
    )
    lat_sec_2: IntProperty(
        name="",
        description="latitude second",
        default=15,
        min=0,
        max=59,
        update=update_coordinates_2,
    )
    lat_dir_2: StringProperty(
        name="",
        description="latitude direction : n(orth) or s(outh)",
        default="n",
        maxlen=1,
        update=update_coordinates_2,
    )
    lon_deg_2: IntProperty(
        name="",
        description="longitude degree",
        default=24,
        min=0,
        max=179,
        update=update_coordinates_2,
    )
    lon_min_2: IntProperty(
        name="",
        description="longitude minute",
        default=55,
        min=0,
        max=59,
        update=update_coordinates_2,
    )
    lon_sec_2: IntProperty(
        name="",
        description="longitude second",
        default=26,
        min=0,
        max=59,
        update=update_coordinates_2,
    )
    lon_dir_2: StringProperty(
        name="",
        description="longitude direction : e(ast) or w(est)",
        default="e",
        maxlen=1,
        update=update_coordinates_2,
    )
    alt_2: IntProperty(
        name="",
        description="location altitude in meters above sea",
        default=0,
        update=update_coordinates_2,
    )

    # --- chart data ---
    chart_info_text: StringProperty()

    # chart info formatting
    def update_chart_info(self, context):
        try:
            ba_ops.set_chart_info(self, "load")
        except Exception as e:
            msg_ = f"ba_props: update_chart_info: ERROR:\n{str(e)}"
            print(msg_)

    chart_info_f: StringProperty(
        name="",
        description="construct your own 'chart info' format: allowed fields:\n1: {event} name | 2: weekday {wday} | 3: event {date} | 4: {time} | 5: {city} |\n6: country {ctry} | 7: {lat}itude | 8: {lon}gitude\nadd '\\n' for new line: for short time format (no seconds) use {time[:5]}\nsee default value [mouse-over-backspace] as example",
        default=r"{event}\n{date}\n{wday} {time[:5]}\n{city} @ {ctry}\n{lat}\n{lon}",
        update=update_chart_info,
    )

    # various text
    def update_chart_text(self, context):
        try:
            # print(f"ba_props: update_chart_text: CALLING chart.text")
            bpy.ops.chart.text()
        except Exception as e:
            msg = f"ba_props: update_chart_text: chart.text error\n{str(e)}"
            print(msg)

    chart_info_2_f: StringProperty(
        name="",
        description="additional 'chart info' format: allowed fields:\n1: house system {hsys} | 2: {zod}iac | 3: ayanamsa name {aynm} | 4: ayanamsa value {ayvl}\nadd '\\n' for new line: see default value [mouse-over-backspace] as example\nNOTE: no auto-formating > showing ayanamsa name & value for 'tropical zodiac' makes no sense",
        default=r"{hsys} | {zod}\n{aynm} | {ayvl}",
        update=update_chart_text,
    )
    show_chart_info: BoolProperty(
        name="info",
        description="show 'chart info' auto-text\nbasic common chart info",
        default=True,
        update=update_chart_text,
    )
    chart_info_size: FloatProperty(
        name="size",
        description="'chart info' text size",
        default=0.9,
        max=1.3,
        min=0.3,
        update=update_chart_text,
    )
    show_chart_info_2: BoolProperty(
        name="info 2",
        description="show additional 'chart info 2' text",
        default=False,
        update=update_chart_text,
    )
    chart_info_2_offset: FloatProperty(
        name="offset",
        description="'chart info 2' vertical offset",
        default=0.0,
        max=9.0,
        min=-2.0,
        update=update_chart_text,
    )
    chart_info_2_size: FloatProperty(
        name="size",
        description="'chart info 2' size",
        default=0.8,
        max=1.3,
        min=0.3,
        update=update_chart_text,
    )
    show_text: BoolProperty(
        name="text",
        description="show extra 'text'",
        default=False,
        update=update_chart_text,
    )
    text_offset: FloatProperty(
        name="offset",
        description="extra 'text' vertical offset",
        default=0.0,
        max=3.0,
        min=-1.0,
        update=update_chart_text,
    )
    text_size: FloatProperty(
        name="size",
        description="extra 'text' size",
        default=0.9,
        max=1.3,
        min=0.3,
        update=update_chart_text,
    )
    show_notes: BoolProperty(
        name="notes",
        description="show 'notes' text",
        default=False,
        update=update_chart_text,
    )
    notes_size: FloatProperty(
        name="size",
        description="'notes' text size",
        default=1.0,
        max=1.3,
        min=0.3,
        update=update_chart_text,
    )

    # --- harmonics ring ---
    def update_ring_harmonics(self, context):
        try:
            bpy.ops.chart.ring_harmonics()
        except Exception as e:
            msg = f"ba_props: update_ring_harmonics: chart.ring_harmonics error:\n{str(e)}"
            print(msg)

    ring_harmonics: IntProperty(
        name="harmonics",
        description="harmonics division ring\n0 hide | 1 egypt. terms (bounds)\n7, 9 (navamsa), 11 etc\nnot all harmonics are available; add them if you need them ;)\n!!! those are simple divisions, similar but NOT all equal to varga",
        default=0,  # hiden
        min=0,
        max=60,
        update=update_ring_harmonics,
    )

    # --- dials panel ---
    def update_dials(self, context):
        try:
            bpy.ops.chart.ring_dials()
        except Exception as e:
            msg = f"ba_props: update_dials: chart.ring_dials error\n{str(e)}"
            print(msg)

    show_vimsottari: BoolProperty(
        name="dasa-bhukti",
        description="show dasa-bhukti (vimsottari) dial",
        default=False,
        update=update_dials,
    )
    rotate_vimsottari: FloatProperty(
        name="rotate dasa-bhukti",
        description="rotate dasa-bhukti (vimsottari) dial",
        default=0.0,
        update=update_dials,
    )
    show_number: BoolProperty(
        name="numbers (#)",
        description="show numbers dial (#)",
        default=False,
        update=update_dials,
    )
    number_number: IntProperty(
        name="number (#)",
        description="divide into this number (#)",
        default=7,
        update=update_dials,
    )
    rotate_number: FloatProperty(
        name="rotate numbers (#)",
        description="rotate numbers dial (#)",
        default=0.0,
        update=update_dials,
    )
    show_roulette_37: BoolProperty(
        name="roulette 37",
        description="show roulette (eu / 37) dial",
        default=False,
        update=update_dials,
    )
    rotate_roulette_37: FloatProperty(
        name="rotate roulette 37",
        description="rotate roulette (eu / 37) dial",
        default=0.0,
        update=update_dials,
    )
    show_ej: BoolProperty(
        name="eurojackpot",
        description="show eurojackpot (50 / 12) dial",
        default=False,
        update=update_dials,
    )
    rotate_ej: FloatProperty(
        name="rotate eurojackpot",
        description="rotate eurojackpot (50 / 12) dial",
        default=0.0,
        update=update_dials,
    )

    # --- zodiac & houses ---
    def update_naksatras(self, context):
        try:
            bpy.ops.chart.naksatras()
        except Exception as e:
            msg = f"ba_props: update_naksatras: chart.naksatras error:\n{str(e)}"
            print(msg)

    show_naksatras: BoolProperty(
        name="naksatras",
        description="shown naksatras ring on chart",
        default=True,
        update=update_naksatras,
    )
    naksatras_28: BoolProperty(
        name="28 naksatras",
        description="use 28 (equaly-divided !), not common 27 naksatras",
        default=True,
        update=update_naksatras,
    )

    def update_ayanamsa(self, context):
        try:
            bpy.ops.sweph.sidereal()
        except Exception as e:
            msg = f"ba_props: update_ayanamsa: sweph.sidereal error\n{str(e)}"
            print(msg)

    # !!! UN/COMMENT ANY AYANAMSA THAT YOU NEED !!!
    # un/comment > delete '# ', indent properly > 8 spaces, and save file
    # also arrange order as you please > move line up / down, and save file
    ayanamsas = [
        ("17", "17: Galact. Center 0 Sag", "glc (17)"),  # SIDM_GALCENT_0SAG
        (
            "45",
            "45: Krishnamurti-Senthilathiban",
            "kms (45)",
        ),  # SIDM_KRISHNAMURTI_VP291
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
    ayanamsa_enum: EnumProperty(
        name="ayanamsa",
        description="select ayanamsa for sideral zodiac\nthere are more in 'ba_props.py' file",
        items=ayanamsas,
        update=update_ayanamsa,
    )
    # custom ayanamsa props
    utc_custom_julian_day: StringProperty(
        name="julian day",
        description="julian day utc > reference date for custom ayanamsa calculation\ndefault is for 2000-01-01 12:00 utc\nif needed, get julian day utc online, then copy-paste the number here",
        default="2451545.00000",
        update=update_ayanamsa,
    )
    custom_ayanamsa: StringProperty(
        name="ayanamsa",
        description="user-defined custom ayanamsa\nmust be decimal degrees\ndefault is 23.76694444 (23° 46' 01\"), as per richard houck's book 'astrology of death', for 2000-01-01",
        default="23.76694444",
        update=update_ayanamsa,
    )

    # --- houses ---
    # flag to prevent recursive calls
    update_houses_enable: BoolProperty(default=True)

    def update_houses(self, context):
        # flag to prevent circular code
        if not self.update_houses_enable:
            return
        try:
            bpy.ops.sweph.houses_one()
        except Exception as e:
            msg = f"ba_props: update_houses: sweph.houses_one error:\n{str(e)}"
            print(msg)

    show_houses: BoolProperty(
        name="houses",
        description="show houses on chart\nif disabled, set house system to ie porphyry, to show proper ascendant & midheaven",
        default=True,
        update=update_houses,
    )
    # add or remove houses as you please
    # https://astrorigin.com/pyswisseph/sphinx/programmers_manual/house_cusp_calculation.html?highlight=houses#swisseph.houses
    # below are most popular 7 out of 24+; arrange as you please
    house_systems = [
        ("E", "eqa: equal asc", "eqa"),
        ("O", "prp: porphyry", "prp"),
        ("P", "plc: placidus", "plc"),
        ("R", "rgm: regiomontanus", "rgm"),
        ("C", "cmp: campanus", "cmp"),
        ("K", "kch: koch", "kch"),
        ("W", "whs: whole sign", "whs"),  # makes no sense to draw it, same as signs
    ]
    house_enum: EnumProperty(
        name="house sys",
        description="select house system, 7 available out of 24+\nsee 'house_systems' property in 'ba_props.py' file for more info",
        items=house_systems,
        default="E",
        update=update_houses,
    )
    true_mc_ic: BoolProperty(
        name="true mc / ic",
        description="show true midheaven & imum coeli when equal or whole house system is selected\ntrue mc / ic can differ by upto 2 signs in those cases",
        default=True,
        update=update_houses,
    )

    # fixed ascendant
    def update_fixed_asc(self, context):
        try:
            bpy.ops.chart.fixed_asc()
        except Exception as e:
            msg = f"ba_props: update_fixed_asc: chart.fixed_asc error:\n{str(e)}"
            print(msg)

    fixed_asc: BoolProperty(
        name="fixed asc (east / left)",
        description="rotate whole chart so ascendant is fixed at left (east)\nunchecked: aries (mesha) 0° is fixed at left",
        default=True,
        update=update_fixed_asc,
    )

    # --- miscellaneous properties ---
    print_info: BoolProperty(
        name="print info",
        description="print debug / info in terminal / console",
        default=False,
    )
    # TODO : set path to blender's python executable, for automatic
    # dependencies installation
    # blender_python_path: StringProperty(
    #     name="path to blender's python executable",
    #     description="ie on linux it could be /your/blender-4.1.1/4.1/python/bin/python3.11\nneeded for automatic installation of required python libraries\nthey can also be installed manually by user > see 'readme.txt'",
    #     default="manual install",
    # )

    def update_ephe_path(self, context):
        try:
            bpy.ops.sweph.ephe_init()
        except Exception as e:
            msg = f"ba_props: update_ephe_path: sweph.ephe_init error:\n{str(e)}"
            print(msg)

    ephe_path: StringProperty(
        name="ephe",
        description="path to ephemerides folder, with min semo_18.se1 & sepl_18.se1 files, or a complete ephe folder\nhere: https://github.com/aloistr/swisseph/tree/master/ephe",
        default="None",
        subtype="DIR_PATH",
        update=update_ephe_path,
    )
    events_db: StringProperty(
        name="eventsdb",
        description="path to event / birth charts '/data/eventsdb/' database folder; inside go saved charts",
        default="/data/eventsdb/",
        subtype="DIR_PATH",
    )
    atlas_file: StringProperty(
        name="atlas",
        description="path to '/data/atlas.db' file - includes all cities on earth (with 1000+ population)",
        default="/data/atlas.db",
        subtype="FILE_PATH",
    )

    # use mean or true node
    def update_true_node(self, context):
        try:
            bpy.ops.sweph.planets_one()
        except Exception as e:
            msg = f"ba_props: update_true_node: sweph.planets_one error\n{str(e)}"
            print(msg)

    true_node: BoolProperty(
        name="true node",
        description="use true node\nunchecked: use mean node\nre-run code to update",
        default=True,
        update=update_true_node,
    )

    def update_flags(self, context):
        try:
            bpy.ops.sweph.flags()
            # bpy.ops.sweph.planets_one()
        except Exception as e:
            msg = f"ba_props: update_flags: sweph.flags error:\n{str(e)}"
            print(msg)

    # --- sweph flags ---
    sidereal_zodiac: BoolProperty(  # FLG_SIDEREAL
        name="sidereal zodiac",
        description="use sidereal (jyotisa) zodiac\nunchecked: use tropical (western) zodiac",
        default=True,
        update=update_flags,
    )
    nutation: BoolProperty(  # FLG_NONUT
        name="nutation",
        description="use nutation for calculations\na small irregularity in the precession of the equinoxes",
        default=True,
        update=update_flags,
    )
    heliocentric: BoolProperty(  # FLG_HELCTR
        name="heliocentric positions",
        description="calculate heliocentric positions\nastrology uses geocentric positions",
        default=False,
        update=update_flags,
    )
    true_positions: BoolProperty(  # FLG_TRUEPOS
        name="true positions",
        description="calculate true, not apparent (visible from earth) positions\njourney of the light from a planet to the earth takes some time",
        default=True,
        update=update_flags,
    )
    topocentric: BoolProperty(  # FLG_TOPOCTR
        name="topocentric positions",
        description="calculate topocentric positions, viewed from latitude & longitude of event\nunchecked: calculate geocentric (default, used traditionally in astrology) positions, viewed from center of the earth",
        default=False,
        update=update_flags,
    )
    equatorial: BoolProperty(  # FLG_EQUATORIAL
        name="equatorial positions",
        description="return equatorial positions (right ascension & declination)\nunchecked: return ecliptic (default, latitude & longitude) positions",
        default=False,
        update=update_flags,
    )
    cartesian: BoolProperty(  # FLG_XYZ
        name="cartesian coordinates",
        description="return cartesian (x, y, z) coordinates\nunchecked: return polar (default) coordinates",
        default=False,
        update=update_flags,
    )
    radians: BoolProperty(  # FLG_RADIANS
        name="radians",
        description="return radians unit\nunchecked: return degrees (default) unit",
        default=False,
        update=update_flags,
    )

    # prediction panel
    def update_prediction(self, context):
        try:
            bpy.ops.sweph.prediction()
        except Exception as e:
            msg = f"ba_props: update_prediction: sweph.prediction error:\n{str(e)}"
            print(msg)

    transit: BoolProperty(
        # name="",
        name="tr",
        description="calculate & show TRANSIT",
        default=False,
        update=update_prediction,
    )
    returns: BoolProperty(
        # name="",
        name="rt",
        description="calculate & show solar / lunar RETURNS",
        default=False,
        update=update_prediction,
    )
    progressions: BoolProperty(
        # name="",
        name="pg",
        description="calculate & show PROGRESSIONS",
        default=False,
        update=update_prediction,
    )
    directions: BoolProperty(
        # name="",
        name="dr",
        description="calculate & show DIRECTIONS",
        default=False,
        update=update_prediction,
    )
    profections: BoolProperty(
        # name="",
        name="pf",
        description="calculate & show PROFECTION point",
        default=False,
        update=update_prediction,
    )
    dasa_bhukti: BoolProperty(
        # name="",
        name="db",
        description="calculate & show DASA-BHUKTI point",
        default=False,
        update=update_prediction,
    )
    syzygy: BoolProperty(
        # name="",
        name="sz",
        description="calculate & show SYZYGY (pre-natal lunation) point",
        default=False,
        update=update_prediction,
    )
    # --- time constants ---
    year_length: EnumProperty(
        name="year length",
        description="(solar) year lengths in days",
        items=[
            ("365.2425", "365.2425 (gregorian)", ""),
            ("365.25", "365.25 (julian)", ""),
            ("365.24219", "365.24219 (tropical)", ""),
            ("365.256363", "365.256363 (sidereal)", ""),
            ("354.37", "354.37 (lunar)", ""),
        ],
    )
    month_length: EnumProperty(
        name="month length",
        description="(lunar) month lengths",
        items=[
            ("27.321582", "27.321582 days (tropical); 0 aries (houck)", ""),
            ("29.53059", "29.53059 days (synodic); new moons", ""),
            ("27.321661", "27.321661 days (sidereal)", ""),
            ("27.554551", "27.554551 days (anomalistic); perigee - apogee", ""),
            ("27.21222", "27.21222 days (draconic); lunar nodes", ""),
        ],
    )

    # fixed stars
    def update_fixed_stars(self, context):
        try:
            bpy.ops.sweph.fixed_stars_one()
            # print(f"ba_props: update_fixed_stars: stars_list: {self.stars_list}")
        except Exception as e:
            msg = f"ba_props: update_fixed_stars: sweph.fixed_stars_one error\n{str(e)}"
            print(msg)

    def fixed_stars_list(self, context):
        fixed_stars_list = []
        try:
            with open(self.fixed_stars_file, "r") as file:
                lines = file.readlines()
                # parse the file
                for line in lines:
                    # skip line if it is commented
                    if line.startswith("#"):
                        continue
                    line = line.strip()
                    if line.startswith("(") and line.endswith("),"):
                        line = line[1:-2]
                        # print(f"line : {line}\n")
                        parts = [p.strip().strip('"') for p in line.split('",')]
                        if len(parts) == 3:
                            fixed_stars_list.append((parts[0], parts[1], parts[2]))
        except Exception as e:
            msg = f"ba_props: fixed_stars_list: error reading or parsing fixed_stars_file:\n{e}"
            print(msg)
        fixed_stars_ = fixed_stars_list
        # print(f"ba_props: fixed_stars_list: self.fixed_stars_: {fixed_stars_}\n")

        return fixed_stars_list

    fixed_stars_ = []
    # auto calculate & show fixed stars > if fixed_stars_list not empty
    fixed_stars_file: StringProperty(
        name="fixed stars file",
        description="path to fixed stars list, to be used for stars calculations\nexample is in '/data/fixedstars.txt'; make a copy (ie 'fixedstarsbestof.txt'), modify it as you see fit, and point here the path to the file itself",
        default="/data/fixedstarslist.txt",
        subtype="FILE_PATH",
        update=update_fixed_stars,
    )
    fixed_stars_enum: EnumProperty(
        name="fixed stars",
        description="fixed stars list, with few categories listed\nfor reference, used for fixed stars calculations\nmodify '/data/fixedstars.txt' file, save it, then click on any item to update this list\nNOTE: to disable stars drawing on chart, comment out all stars in your 'fixedstars.txt' file",
        items=fixed_stars_list,
        update=update_fixed_stars,
    )

    # 'clock mode'
    def update_clock_interval(self, context):
        if self.run_clock_1_:
            # temporary off : event.one_clock will toggle back on
            self.run_clock_1_ = False
            msg_ = f"ba_props: update_clock_interval: UPDATED"
            msg_ += f"\n\tcalling event.one_clock"
            if self.print_info:
                print(msg_)
            bpy.ops.event.one_clock()
        if self.run_clock_2_:
            # temporary off : event.two_clock will toggle back on
            self.run_clock_2_ = False
            msg_ = f"ba_props: update_clock_interval: UPDATED"
            msg_ += f"\n\tcalling event.two_clock"
            if self.print_info:
                print(msg_)
            bpy.ops.event.two_clock()

    clock_interval: IntProperty(
        name="",
        description="clock interval: update clock every x seconds\nNOTE: restart 'clock mode' if needed",
        default=60,
        min=1,
        soft_max=60,
        update=update_clock_interval,
    )


        }
# --- code archive ---
# validate day
# def is_valid_date(year, month, day):
#     day_count_for_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
#     if year%4==0 and (year%100 != 0 or year%400==0):
#         day_count_for_month[2] = 29
#     return (1 <= month <= 12 and 1 <= day <= day_count_for_month[month])
