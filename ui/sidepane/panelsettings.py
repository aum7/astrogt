# ui/sidepane/panelsettings.py
# ruff: noqa: E402
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.collapsepanel import CollapsePanel
from user.settings import (
    OBJECTS,
    HOUSE_SYSTEMS,
    CHART_SETTINGS,
    SWE_FLAG,
    SOLAR_YEAR,
    LUNAR_MONTH,
    AYANAMSA,
    CUSTOM_AYANAMSA,
    FILES,
)
from sweph.setupsettings import get_sweph_flags_int


def setup_settings(manager) -> CollapsePanel:
    """setup widget for settings, ie objects, sweph flags, glyphs etc"""
    app = manager._app
    # main panel for settings
    clp_settings = CollapsePanel(title="settings", expanded=True)
    clp_settings.set_margin_end(manager.margin_end)
    clp_settings.set_title_tooltip("""sweph & application & chart etc settings""")
    # main box for settings
    box_settings = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    # --- sub-panel objects --------------------
    subpnl_objects = CollapsePanel(
        title="objects / planets",
        indent=14,
        expanded=False,
    )
    subpnl_objects.set_title_tooltip(
        """select objects to calculate & display on chart
event 1 & 2 can have different objects"""
    )
    # main container
    box_objects = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box_objects.set_margin_start(manager.margin_end)
    box_objects.set_margin_end(manager.margin_end)
    # button box at top
    box_button = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    box_button.set_halign(Gtk.Align.START)
    box_objects.append(box_button)
    # select event button : objects are separate for event 1 & 2
    # use icons
    ico_toggle_event_objs = Gtk.Image.new_from_file(
        "ui/imgs/icons/hicolor/scalable/objects/event_1.svg"
    )
    ico_toggle_event_objs.set_pixel_size(30)
    ico_toggle_event_objs.set_margin_start(2)
    ico_toggle_event_objs.set_margin_end(2)
    # button with icon
    btn_toggle_event_objs = Gtk.Button()
    btn_toggle_event_objs.add_css_class("button-event")
    btn_toggle_event_objs.set_child(ico_toggle_event_objs)
    btn_toggle_event_objs.set_tooltip_text("toggle event for selected objects")
    btn_toggle_event_objs.connect("clicked", objects_toggle_event, manager)
    box_button.append(btn_toggle_event_objs)
    # select all button
    btn_select_all = Gtk.Button(label="all")
    btn_select_all.set_tooltip_text("select all objects")
    btn_select_all.connect("clicked", objects_select_all, manager)
    box_button.append(btn_select_all)
    # deselect all button
    btn_select_none = Gtk.Button(label="none")
    btn_select_none.set_tooltip_text("deselect all objects")
    btn_select_none.connect("clicked", objects_select_none, manager)
    box_button.append(btn_select_none)
    # list box for selection
    manager.listbox = Gtk.ListBox()
    # we'll manage selection with checkboxes
    manager.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
    box_objects.append(manager.listbox)
    # track selected objects per event
    app.selected_objects_e1 = set()
    app.selected_objects_e2 = set()
    manager.selected_objects_event = 1

    for _, obj_data in OBJECTS.items():
        row = Gtk.ListBoxRow()
        name = obj_data[0]
        # set tooltip on the row
        tooltip = obj_data[1]
        row.set_tooltip_text(tooltip)
        # create checkbox for selection
        check = Gtk.CheckButton(label=name)
        check.connect("toggled", lambda btn, n=name: objects_toggled(btn, n, manager))

        row.set_child(check)
        manager.listbox.append(row)
    objects_select_all(check, manager)
    # add box to sub-panel
    subpnl_objects.add_widget(box_objects)
    # --- sub-panel house system --------------------
    subpnl_housesys = CollapsePanel(
        title="house system",
        indent=14,
        expanded=False,
    )
    # dropdown list for house system selection
    housesys_list = Gtk.StringList.new([f"{name}" for _, name, _ in HOUSE_SYSTEMS])
    ddn_housesys = Gtk.DropDown.new(housesys_list)
    ddn_housesys.set_margin_start(manager.margin_end)
    ddn_housesys.set_margin_end(manager.margin_end)
    # need row closer
    ddn_housesys.add_css_class("dropdown")
    # default to first / selected item
    ddn_housesys.set_selected(0)
    app.selected_house_system = HOUSE_SYSTEMS[0][0]
    ddn_housesys.connect("notify::selected", house_system_changed, manager)
    subpnl_housesys.add_widget(ddn_housesys)
    # --- sub-panel chart settings --------------------
    subpnl_chart_settings = CollapsePanel(
        title="chart settings",
        indent=14,
        expanded=False,
    )
    subpnl_chart_settings.set_title_tooltip(
        """chart rendering & info display settings"""
    )
    # ------ sub-sub-panel : chart info -----------------
    subsubpnl_chart_info = CollapsePanel(
        title="chart info",
        indent=21,
        expanded=False,
    )
    subsubpnl_chart_info.set_title_tooltip("diy chart info string")
    # main box
    box_chart_settings = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box_chart_settings.set_margin_start(manager.margin_end)
    box_chart_settings.set_margin_end(manager.margin_end)
    # listbox with rows for settings
    manager.lbx_chart_settings = Gtk.ListBox()
    manager.lbx_chart_settings.set_selection_mode(Gtk.SelectionMode.NONE)
    app.chart_settings = {}
    # checkboxes
    for setting in [
        "enable glyphs",
        "true mc & ic",
        "fixed asc",
        "mean node",
    ]:
        row = Gtk.ListBoxRow()
        default, tooltip = CHART_SETTINGS[setting]
        # create checkbox for selection
        check = Gtk.CheckButton(label=setting)
        check.set_active(default)
        check.connect(
            "toggled",
            lambda btn, s=setting, m=manager: chart_settings_toggled(btn, s, m),
        )
        row.set_tooltip_text(tooltip)
        row.set_child(check)
        manager.lbx_chart_settings.append(row)
        app.chart_settings[setting] = default
    # naksatras ring : connect all naksatra settings in 1 function
    row = Gtk.ListBoxRow()
    # naksatras ring checkbox
    manager.chk_naks_ring = Gtk.CheckButton(label="naksatras ring")
    manager.chk_naks_ring.set_active(CHART_SETTINGS["naksatras ring"][0])
    manager.chk_naks_ring.connect(
        "toggled",
        lambda btn, k="naksatras ring", m=manager: (
            naksatras_ring(btn, k, m),
            manager.chk_28_naks.set_sensitive(btn.get_active()),
            manager.ent_1st_nak.set_sensitive(btn.get_active()),
        ),
    )
    row.set_tooltip_text(CHART_SETTINGS["naksatras ring"][1])
    app.chart_settings["naksatras ring"] = manager.chk_naks_ring.get_active()
    row.set_child(manager.chk_naks_ring)
    manager.lbx_chart_settings.append(row)
    # row for additional naksatras settings
    row = Gtk.ListBoxRow()
    # box for 28 naksatras checkbox & 1st naksatra
    box_naks = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    # checkbox for 28 equal naksatras vs standard 27
    manager.chk_28_naks = Gtk.CheckButton(label="28")
    manager.chk_28_naks.set_margin_start(14)
    manager.chk_28_naks.set_margin_end(7)
    manager.chk_28_naks.set_active(CHART_SETTINGS["28 naksatras"][0])
    manager.chk_28_naks.set_sensitive(manager.chk_naks_ring.get_active())
    manager.chk_28_naks.connect(
        "toggled",
        lambda btn, k="28 naksatras", m=manager: naksatras_ring(btn, k, m),
    )
    manager.chk_28_naks.set_tooltip_text(CHART_SETTINGS["28 naksatras"][1])
    app.chart_settings["28 naksatras"] = manager.chk_28_naks.get_active()
    box_naks.append(manager.chk_28_naks)
    # start naksatras ring with any naksatra
    lbl_1st_naks = Gtk.Label(label="1st")
    box_naks.append(lbl_1st_naks)
    manager.naks_range = 28 if manager.chk_28_naks.get_active() else 27
    # 1st naksatra to start at 0 aries
    manager.ent_1st_nak = Gtk.Entry()
    manager.ent_1st_nak.set_text(str(CHART_SETTINGS["1st naksatra"][0]))
    manager.ent_1st_nak.set_alignment(0.5)
    manager.ent_1st_nak.set_max_length(2)
    manager.ent_1st_nak.set_max_width_chars(2)
    manager.ent_1st_nak.set_tooltip_text(CHART_SETTINGS["1st naksatra"][1])
    manager.ent_1st_nak.set_sensitive(manager.chk_naks_ring.get_active())
    manager.ent_1st_nak.connect(
        "activate",
        lambda btn, k="1st naksatra", m=manager: naksatras_ring(btn, k, m),
    )
    app.chart_settings["1st naksatra"] = manager.ent_1st_nak.get_text()
    box_naks.append(manager.ent_1st_nak)
    row.set_child(box_naks)
    manager.lbx_chart_settings.append(row)
    # harmonics ring --------------------------------------
    row = Gtk.ListBoxRow()
    box_harmonics = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
    # label
    lbl_harmonics = Gtk.Label(label="harmonics ring")
    box_harmonics.append(lbl_harmonics)
    # entry for harmonics ring
    ent_harmonics = Gtk.Entry()
    ent_harmonics.set_text(
        " ".join(str(x) for x in CHART_SETTINGS["harmonics ring"][0])
        if isinstance(CHART_SETTINGS["harmonics ring"][0], (list, tuple))
        else str(CHART_SETTINGS["harmonics ring"][0])
    )
    ent_harmonics.set_tooltip_text(CHART_SETTINGS["harmonics ring"][1])
    ent_harmonics.set_alignment(0.5)
    ent_harmonics.set_max_length(5)
    ent_harmonics.set_max_width_chars(5)
    ent_harmonics.connect("activate", harmonics_ring_changed, manager)
    box_harmonics.append(ent_harmonics)
    row.set_child(box_harmonics)
    manager.lbx_chart_settings.append(row)
    app.chart_settings["harmonics ring"] = ent_harmonics.get_text()
    box_chart_settings.append(manager.lbx_chart_settings)
    # --- chart info string : basic & extra ------------------
    # main box for chart info string
    box_chart_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    box_chart_info.set_margin_start(manager.margin_end)
    box_chart_info.set_margin_end(manager.margin_end)
    # labels for both strings
    lbl_chart_info_basic = Gtk.Label(label="info per event")
    lbl_chart_info_basic.set_halign(Gtk.Align.START)
    lbl_chart_info_common = Gtk.Label(label="common info")
    lbl_chart_info_common.set_halign(Gtk.Align.START)
    # chart info string
    for info in [
        "chart info string",
        "chart info string extra",
    ]:
        box_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        ent_chart_info = Gtk.Entry()
        ent_chart_info.set_text(
            CHART_SETTINGS[info][0]
            if isinstance(CHART_SETTINGS[info], tuple)
            else CHART_SETTINGS[info]
        )
        ent_chart_info.set_tooltip_text(
            CHART_SETTINGS[info if isinstance(CHART_SETTINGS[info], str) else info][1]
            if isinstance(CHART_SETTINGS[info], tuple)
            else ""
        )
        ent_chart_info.set_max_width_chars(52)
        ent_chart_info.connect("activate", chart_info_string, info, manager)

        box_row.append(ent_chart_info)
        if info == "chart info string":
            box_chart_info.append(lbl_chart_info_basic)
        else:
            box_chart_info.append(lbl_chart_info_common)
        box_chart_info.append(box_row)
        # manager.lbx_chart_info.append(row)
        app.chart_settings[info] = ent_chart_info.get_text()

    subsubpnl_chart_info.add_widget(box_chart_info)
    subpnl_chart_settings.add_widget(box_chart_settings)
    subpnl_chart_settings.add_widget(subsubpnl_chart_info)
    # --- sub-panel flags --------------------
    subpnl_flags = CollapsePanel(
        title="sweph flags",
        indent=14,
        expanded=False,
    )
    subpnl_flags.set_title_tooltip(
        """sweph calculation flags
mouse-over for tips
more info in user/settings.py > SWE_FLAG"""
    )
    # --- sub-sub-panel for uncommon flags
    subsubpnl_flags_extra = CollapsePanel(
        title="extra flags",
        indent=21,
        expanded=False,
    )
    subsubpnl_flags_extra.set_title_tooltip(
        """only change if you know what you are doing\nsee swisseph docs for proper info"""
    )
    # main container
    box_flags = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box_flags.set_margin_start(manager.margin_end)
    box_flags.set_margin_end(manager.margin_end)
    # list box for check boxes
    manager.lbx_flags = Gtk.ListBox()
    manager.lbx_flags.set_selection_mode(Gtk.SelectionMode.NONE)
    box_flags.append(manager.lbx_flags)
    # track selected flags as strings for button labels
    app.selected_flags = set()
    app.sweph_flag = 0
    # collect flags from settings.py
    # only use 1-4 for 1st listbox (in sub-panel)
    for flag_, flags_data in SWE_FLAG.items():
        if flag_ in [
            "sidereal zodiac",
            "true positions",
            "topocentric",
            "heliocentric",
        ]:
            row = Gtk.ListBoxRow()
            flag = flag_
            selected = flags_data[0]
            tooltip = flags_data[1]
            row.set_tooltip_text(tooltip)
            # create checkbox for selection
            check = Gtk.CheckButton(label=flag)
            check.set_active(selected)
            check.connect(
                "toggled", lambda btn, f=flag, m=manager: flags_toggled(btn, f, m)
            )
            row.set_child(check)
            manager.lbx_flags.append(row)
    # add box to sub-panel
    subpnl_flags.add_widget(box_flags)
    # sub-sub-panel content
    manager.lbx_flags_extra = Gtk.ListBox()
    box_flags_extra = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box_flags_extra.set_margin_start(manager.margin_end)
    box_flags_extra.set_margin_end(manager.margin_end)
    # only use 5-10 for 2nd listbox (in sub-sub-panel)
    for flag_, flags_data in SWE_FLAG.items():
        if flag_ in [
            "sidereal zodiac",
            "true positions",
            "topocentric",
            "heliocentric",
        ]:
            continue
        row = Gtk.ListBoxRow()
        flag = flag_
        selected = flags_data[0]
        tooltip = flags_data[1]
        row.set_tooltip_text(tooltip)
        # create checkboxes : initialize label > label-click will toggle checkbox
        check = Gtk.CheckButton(label=flag)
        check.set_active(selected)
        check.connect(
            "toggled", lambda btn, f=flag, m=manager: flags_toggled(btn, f, m)
        )
        row.set_child(check)
        manager.lbx_flags_extra.append(row)
    box_flags_extra.append(manager.lbx_flags_extra)
    # add box to sub-sub-panel
    subsubpnl_flags_extra.add_widget(box_flags_extra)
    # insert sub-sub-panel into sub-panel
    subpnl_flags.add_widget(subsubpnl_flags_extra)
    # collect flags as strings from checked checkboxes
    app.selected_flags = {k for k, v in SWE_FLAG.items() if v[0]}
    # convert flags to integer
    app.sweph_flag = get_sweph_flags_int()
    manager._notify.debug(
        f"swephflag : {app.sweph_flag}",
        source="panelsettings",
        route=["terminal"],
    )
    # --- sub-panel solar year & lunar months periods --------------------
    subpnl_solar_lunar_periods = CollapsePanel(
        title="solar & lunar periods",
        indent=14,
        expanded=False,
    )
    # main box for content
    box_solar_lunar_periods = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box_solar_lunar_periods.set_margin_start(manager.margin_end)
    box_solar_lunar_periods.set_margin_end(manager.margin_end)
    # solar year label
    lbl_solar_year = Gtk.Label(label="solar year")
    lbl_solar_year.set_halign(Gtk.Align.START)
    # solar year dropdown
    app.selected_year_period = None
    year_store = Gtk.StringList()
    for _, value in SOLAR_YEAR.items():
        year_store.append(value[1])
    ddn_solar_year = Gtk.DropDown.new(year_store)
    ddn_solar_year.set_tooltip_text("""solar & lunar years in days
    gregorian\t\t365.2425
    julian\t\t\t365.25
    tropical\t\t365.24219
    sidereal\t\t365.256363
    lunar\t\t\t354.37""")
    ddn_solar_year.add_css_class("dropdown")
    ddn_solar_year.set_selected(0)
    app.selected_year_period = list(SOLAR_YEAR.values())[1]
    ddn_solar_year.connect("notify::selected", solar_year_changed, manager)
    # put widgets into main box
    box_solar_lunar_periods.append(lbl_solar_year)
    box_solar_lunar_periods.append(ddn_solar_year)
    # lunar month label
    lbl_lunar_month = Gtk.Label(label="lunar month")
    lbl_lunar_month.set_halign(Gtk.Align.START)
    # lunar month dropdown
    app.selected_month_period = None
    month_store = Gtk.StringList()
    for _, value in LUNAR_MONTH.items():
        month_store.append(value[1])
    ddn_lunar_month = Gtk.DropDown.new(month_store)
    ddn_lunar_month.set_tooltip_text("""lunar months in days
    tropical\t\t0 ari (houck)\t27.321582
    synodic\t\tnew moons\t\t29.53059
    sidereal\t\tfixed star\t\t27.321661
    anomalistic\tperig-apog\t\t27.554551
    draconic\t\tlunar nodes\t\t27.21222""")
    ddn_lunar_month.add_css_class("dropdown")
    ddn_lunar_month.set_selected(0)
    app.selected_month_period = list(LUNAR_MONTH.keys())[0]
    ddn_lunar_month.connect(
        "notify::selected", lunar_month_changed, manager
    )  # add widgets to box
    box_solar_lunar_periods.append(lbl_lunar_month)
    box_solar_lunar_periods.append(ddn_lunar_month)
    # put box into sub-panel
    subpnl_solar_lunar_periods.add_widget(box_solar_lunar_periods)
    # --- sub-panel ayanamsa --------------------
    subpnl_ayanamsa = CollapsePanel(
        title="ayanamsa",
        indent=14,
        expanded=False,
    )
    # ------- sub-sub-panel custom ayanamsa --------------
    subsubpnl_custom_ayanamsa = CollapsePanel(
        title="custom ayanamsa",
        indent=21,
        expanded=False,
    )
    subsubpnl_custom_ayanamsa.set_title_tooltip(
        "above select ayanamsa 'user-defined' to enable below settings"
    )
    # box for sub-panel ayanamsa
    box_ayanamsa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box_ayanamsa.set_margin_start(manager.margin_end)
    box_ayanamsa.set_margin_end(manager.margin_end)
    # ayanamsa select : dropdown
    app.selected_ayanamsa = None
    ayanamsa_store = Gtk.StringList()
    for key, value in AYANAMSA.items():
        ayanamsa_store.append(value[0])
    ddn_ayanamsa = Gtk.DropDown.new(ayanamsa_store)
    ddn_ayanamsa.set_tooltip_text("see AYANAMSA in user/settings.py")
    ddn_ayanamsa.add_css_class("dropdown")
    ddn_ayanamsa.set_selected(0)
    app.selected_ayanamsa = list(AYANAMSA.keys())[0]

    def ayanamsa_notify_cb(dropdown, param, manager):
        idx = dropdown.get_selected()
        key = list(AYANAMSA.keys())[idx]
        # custom = user-defined = 255
        is_user_defined = key == 255
        subsubpnl_custom_ayanamsa.toggle_sensitive(is_user_defined)
        subsubpnl_custom_ayanamsa.toggle_expand(is_user_defined)
        app.selected_ayanamsa = key
        ayanamsa_changed(dropdown, param, manager)

    ddn_ayanamsa.connect("notify::selected", ayanamsa_notify_cb, manager)
    # set initial state of sub-sub-panel custom ayanamsa
    key0 = list(AYANAMSA.keys())[ddn_ayanamsa.get_selected()]
    is_user_defined0 = key0 == 255
    subsubpnl_custom_ayanamsa.toggle_sensitive(is_user_defined0)
    subsubpnl_custom_ayanamsa.toggle_expand(is_user_defined0)
    # put into box
    box_ayanamsa.append(ddn_ayanamsa)
    # --- sub-sub-panel custom ayanamsa
    box_ayanamsa_custom = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    # box for custom ayanamsa : julian day utc & ayanamsa value
    # label
    lbl_julian_day = Gtk.Label(label="julian day utc")
    lbl_julian_day.set_halign(Gtk.Align.START)
    # entry for julian day utc
    ent_julian_day = Gtk.Entry()
    ent_julian_day.set_text(str(CUSTOM_AYANAMSA["custom julian day utc"]))
    app.custom_julian_day = float(ent_julian_day.get_text())
    ent_julian_day.set_tooltip_text("""julian day utc = custom ayanamsa reference date
    default is for 2000-01-01 12:00 utc (julian day starts at noon)
    if needed, get julian day utc online, then copy-paste the number here""")
    ent_julian_day.set_max_length(13)
    ent_julian_day.set_max_width_chars(13)
    # ent_julian_day.set_hexpand(False)
    ent_julian_day.connect(
        "activate",
        lambda entry, k="custom julian day utc", m=manager: custom_ayanamsa_changed(
            entry, k, m
        ),
    )
    # pack into container
    box_ayanamsa_custom.append(lbl_julian_day)
    box_ayanamsa_custom.append(ent_julian_day)
    # custom ayanamsa value
    # label
    lbl_ayan_value = Gtk.Label(label="ayanamsa")
    lbl_ayan_value.set_halign(Gtk.Align.START)
    # entry
    ent_ayan_value = Gtk.Entry()
    ent_ayan_value.set_text(str(CUSTOM_AYANAMSA["custom ayanamsa"]))
    app.custom_ayan = float(ent_ayan_value.get_text())
    ent_ayan_value.set_tooltip_text("""custom ayanamsa value
    default is 23.76694445 (23° 46' 01"), as per richard houck's book 'astrology of death', for 2000-01-01""")
    ent_ayan_value.set_max_width_chars(11)
    ent_ayan_value.set_hexpand(False)
    ent_ayan_value.connect(
        "activate",
        lambda entry, k="custom ayanamsa", m=manager: custom_ayanamsa_changed(
            entry, k, m
        ),
    )
    # pack widgets
    box_ayanamsa_custom.append(lbl_ayan_value)
    box_ayanamsa_custom.append(ent_ayan_value)
    subsubpnl_custom_ayanamsa.add_widget(box_ayanamsa_custom)
    box_ayanamsa.append(subsubpnl_custom_ayanamsa)
    subpnl_ayanamsa.add_widget(box_ayanamsa)
    # --- sub-panel files ------------------------
    subpnl_files = CollapsePanel(
        title="files & paths",
        indent=14,
        expanded=False,
    )
    subpnl_files.set_title_tooltip("no validation here, dont do stupid things")
    # main box for files panels
    box_files = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    box_files.set_margin_start(manager.margin_end)
    box_files.set_margin_end(manager.margin_end)
    app.files = dict(FILES)
    for key, value in FILES.items():
        tooltip = value[1]
        box_key = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box_key.set_tooltip_text(tooltip)
        lbl_key = Gtk.Label(label=key)
        lbl_key.set_halign(Gtk.Align.START)
        ent_key = Gtk.Entry()
        ent_key.set_max_width_chars(40)
        ent_key.set_text(value[0])
        # ent_key.set_hexpand(True)
        ent_key.connect(
            "activate", lambda entry, k=key, m=manager: files_changed(entry, k, m)
        )
        box_key.append(lbl_key)
        box_key.append(ent_key)
        box_files.append(box_key)
    subpnl_files.add_widget(box_files)
    # add sub-panels
    box_settings.append(subpnl_objects)
    box_settings.append(subpnl_housesys)
    box_settings.append(subpnl_chart_settings)
    box_settings.append(subpnl_flags)
    box_settings.append(subpnl_solar_lunar_periods)
    box_settings.append(subpnl_ayanamsa)
    box_settings.append(subpnl_files)

    clp_settings.add_widget(box_settings)

    return clp_settings


def objects_toggle_event(button, manager):
    """objects panel : toggle event for which to select objects"""
    # toggle active event
    manager.selected_objects_event = 2 if manager.selected_objects_event == 1 else 1
    # initialize event 2 set on 1st toggle if empty
    if manager.selected_objects_event == 2 and not manager._app.selected_objects_e2:
        manager._app.selected_objects_e2 = {"sun", "moon"}
    # update button icon
    img = button.get_child()
    if manager.selected_objects_event == 1:
        img.set_from_file("ui/imgs/icons/hicolor/scalable/objects/event_1.svg")
        img.set_tooltip_text("select objects for event 1")
    else:
        img.set_from_file("ui/imgs/icons/hicolor/scalable/objects/event_2.svg")
        img.set_tooltip_text("select objects for event 2")
    # update checkboxes for event set
    objs = (
        manager._app.selected_objects_e1
        if manager.selected_objects_event == 1
        else manager._app.selected_objects_e2
    )
    for row in manager.listbox:
        check = row.get_child()
        name = check.get_label()
        check.set_active(name in objs)
    manager._notify.debug(
        f"selected objects for e{manager.selected_objects_event}\n\t{objs}",
        source="panelsettings",
        route=["none"],
    )


def objects_select_all(button, manager):
    """objects panel : select all objects"""
    list_box = manager.listbox
    i = 0
    while True:
        row = list_box.get_row_at_index(i)
        if row is None:
            break
        child = row.get_child()
        if isinstance(child, Gtk.CheckButton):
            child.set_active(True)
        child = child.get_next_sibling()
        i += 1


def objects_select_none(button, manager):
    """objects panel : deselect all objects"""
    list_box = manager.listbox
    i = 0
    while True:
        row = list_box.get_row_at_index(i)
        if row is None:
            break
        child = row.get_child()
        if isinstance(child, Gtk.CheckButton):
            child.set_active(False)
        child = child.get_next_sibling()
        i += 1


def objects_toggled(checkbutton, name, manager):
    """objects panel : toggle selected objects per event"""
    if manager.selected_objects_event == 1:
        sel_objs = manager._app.selected_objects_e1
    else:
        sel_objs = manager._app.selected_objects_e2

    if checkbutton.get_active():
        sel_objs.add(name)
    else:
        sel_objs.discard(name)
    manager._notify.debug(
        f"\n\tselected objects : e{manager.selected_objects_event} : {sel_objs}",
        source="panelsettings",
        route=["none"],
    )


def house_system_changed(dropdown, _, manager):
    """house system panel : dropdown selection"""
    idx = dropdown.get_selected()
    # todo modify to include short name for chart info
    hsys, _, short_name = HOUSE_SYSTEMS[idx]
    manager._app.selected_house_system = hsys
    manager.selected_house_sys_str = short_name
    manager._notify.debug(
        f"selectedhousesystem : {manager._app.selected_house_system}"
        f"\t{manager.selected_house_sys_str}",
        source="panelsettings",
        route=["terminal"],
    )


def chart_settings_toggled(button, setting, manager):
    """chart settings panel : update chart settings"""
    print(f"chartsettingstoggled : {setting}")
    manager._app.chart_settings[setting] = button.get_active()


def naksatras_ring(button, key, manager):
    """chart settings panel : combine show naksatras ring with checkbox for 28 vs 27 & 1st naksatra"""
    manager.naks_range = 28 if manager.chk_28_naks.get_active() else 27
    # clamp value
    try:
        value = int(manager.ent_1st_nak.get_text())
    except ValueError:
        manager._notify.warning(
            "set naksatra 1 to 27 / 28",
            source="panelsettings",
            route=["terminal", "user"],
        )
        value = 1
    value = max(1, min(manager.naks_range, value))
    manager.ent_1st_nak.set_text(str(value))
    # present value
    val_ring = manager.chk_naks_ring.get_active()
    val_28 = manager.chk_28_naks.get_active()
    val_1st = manager.ent_1st_nak.get_text()
    # todo save values to settings
    manager._app.chart_settings["naksatras ring"] = val_ring
    manager._app.chart_settings["28 naksatras"] = val_28
    manager._app.chart_settings["1st naksatra"] = val_1st
    manager._notify.debug(
        f"naksatrasring : {key} | ring : {val_ring} | 28 : {val_28} | naks : {manager.naks_range} | 1st : {val_1st}",
        source="panelsettings",
        route=["terminal"],
    )


def harmonics_ring_changed(entry, manager):
    """chart settings panel : harmonics ring : 0, 1, 7, 9, 11 harmonics : add if needed - also add calculations"""
    text = entry.get_text().strip()
    nums = text.split()
    valid_nums = {0, 1, 7, 9, 11}
    if (
        not nums
        or not all(n.isdigit() and int(n) in valid_nums for n in nums)
        or not (1 <= len(nums) <= 2)
    ):
        # invalid input todo just notify user : using icons is erratic
        entry.set_text(
            " ".join(str(x) for x in manager._app.chart_settings["harmonics ring"])
        )
        entry.add_css_class("entry-warning")
    else:
        entry.remove_css_class("entry-warning")
        manager._app.chart_settings["harmonics ring"] = text
    manager._notify.debug(
        f"harmonicsring : {manager._app.chart_settings['harmonics ring']}",
        source="panelsettings",
        route=["terminal"],
    )


def chart_info_string(entry, info, manager):
    """chart settings panel : chart info string to display in chart"""
    import re

    allowed = {
        "chart info string": {
            "{event}",
            "{date}",
            "{wday}",
            "{time}",
            "{time[:5]}",
            "{ctry}",
            "{city}",
            "{lat}",
            "{lon}",
        },
        "chart info string extra": {
            "{hsys}",
            "{zod}",
            "{aynm}",
            "{ayvl}",
        },
        "chars": "\\n @|-:",
    }
    value = entry.get_text()
    fields = re.findall(r"\{[a-zA-Z0-9:]+\}", value)
    # fields = re.findall(r"\{[a-zA-Z0-9\[\]:]+\}", value)
    if not all(field in allowed[info] for field in fields) and not all(
        char in allowed["chars"] for char in value
    ):
        # invalid input : user responsible for correct input
        entry.add_css_class("entry-warning")
        manager._notify.warning(
            f"invalid chart info string :"
            f"\n\tallowed :\t{' '.join(allowed[info])} {allowed['chars']}"
            f"\n\treceived :\t{value}",
            # f"\n\treceived :\t{' '.join(fields)}",
            source="panelsettings",
            route=["terminal", "user"],
            timeout=5,
        )
        return
    else:
        entry.remove_css_class("entry-warning")
    # update chart settings
    manager._app.chart_settings[info] = value
    manager._notify.success(
        f"chartinfostring : {manager._app.chart_settings[info]}",
        source="panelsettings",
        route=["terminal", "user"],
        timeout=4,
    )


def flags_toggled(button, flag, manager):
    """flags panel : update selected sweph flags"""
    if button.get_active():
        # add to selected flags
        manager._app.selected_flags.add(flag)
    else:
        # remove from selected flags
        manager._app.selected_flags.discard(flag)
    # update sweph flags
    flags = 0
    for flag in manager._app.selected_flags:
        if flag == "sidereal zodiac":
            flags |= swe.FLG_SIDEREAL
        if flag == "true positions":
            flags |= swe.FLG_TRUEPOS
        if flag == "topocentric":
            flags |= swe.FLG_TOPOCTR
        if flag == "heliocentric":
            flags |= swe.FLG_HELCTR
        if flag == "default flag":
            flags |= swe.FLG_SWIEPH | swe.FLG_SPEED
        if flag == "no nutation":
            flags |= swe.FLG_NONUT
        if flag == "no abberation":
            flags |= swe.FLG_NOABERR
        if flag == "no deflection":
            flags |= swe.FLG_NOGDEFL
        if flag == "equatorial":
            flags |= swe.FLG_EQUATORIAL
        if flag == "cartesian":
            flags |= swe.FLG_XYZ
        if flag == "radians":
            flags |= swe.FLG_RADIANS
    manager._app.sweph_flag = flags
    manager._notify.debug(
        f"flagstoggled :"
        f"\n\tselected flags : {manager._app.selected_flags}"
        f"\n\tsweph flag : {manager._app.sweph_flag}",
        source="panelsettings",
        route=["terminal"],
    )


def solar_year_changed(dropdown, _, manager):
    """solar & lunar period panel : select solar year period"""
    idx = dropdown.get_selected()
    manager._app.selected_year_period = list(SOLAR_YEAR.values())[idx][0]
    manager._notify.debug(
        f"sol & lun period panel :\n\tsolar year :\t{manager._app.selected_year_period} | "
        f"{list(SOLAR_YEAR.keys())[idx]}",
        source="panelsettings",
        route=["terminal"],
    )


def lunar_month_changed(dropdown, _, manager):
    """solar & lunar period panel : select lunar month period"""
    idx = dropdown.get_selected()
    manager._app.selected_month_period = list(LUNAR_MONTH.values())[idx][0]
    manager._notify.debug(
        f"sol & lun period panel :\n\tlunar month :\t{manager._app.selected_month_period} | "
        f"{list(LUNAR_MONTH.keys())[idx]}",
        source="panelsettings",
        route=["terminal"],
    )


def ayanamsa_changed(dropdown, _, manager):
    """ayanamsa panel : select ayanamsa for sidereal zodiac"""
    idx = dropdown.get_selected()
    manager._app.selected_ayanamsa = list(AYANAMSA.keys())[idx]
    manager._notify.debug(
        f"ayanamsa panel : selected : {manager._app.selected_ayanamsa}",
        source="panelsettings",
        route=["terminal"],
    )


def custom_ayanamsa_changed(entry, key, manager):
    """ayanamsa panel : combine custom julian day utc & custom ayanamsa value : both float"""
    # --- custom julian day
    if key == "custom julian day utc":
        custom_julian_day = entry.get_text().strip()
        # need be float
        try:
            entry.remove_css_class("entry-warning")
            custom_jd = float(custom_julian_day)
        except ValueError:
            entry.add_css_class("entry-warning")
            manager._notify.warning(
                f"invalid custom julian day utc : {custom_julian_day}",
                source="panelsettings",
                route=["terminal", "user"],
                timeout=4,
            )
            return
        if manager._app.custom_julian_day == custom_jd:
            manager._notify.debug(
                "custom julian day not changed : exiting ...",
                source="panelsettings",
                route=["terminal"],
            )
            return
        manager._app.custom_julian_day = custom_jd
        manager._notify.debug(
            f"customjulday : {manager._app.custom_julian_day}",
            source="panelsettings",
            route=["terminal"],
        )
    # --- custom ayanamsa value
    if key == "custom ayanamsa":
        custom_ayan_string = entry.get_text().strip()
        # need be float
        try:
            entry.remove_css_class("entry-warning")
            custom_ayan = float(custom_ayan_string)
        except ValueError:
            entry.add_css_class("entry-warning")
            manager._notify.warning(
                f"invalid custom ayanamsa value : {custom_ayan_string}",
                source="panelsettings",
                route=["terminal", "user"],
                timeout=4,
            )
            return
        if manager._app.custom_ayan == custom_ayan:
            manager._notify.debug(
                "custom julian day not changed : exiting ...",
                source="panelsettings",
                route=["terminal"],
            )
            return
        manager._app.custom_ayan = custom_ayan
        manager._notify.debug(
            f"customayanamsa : {manager._app.custom_ayan}",
            source="panelsettings",
            route=["terminal"],
        )


def files_changed(entry, key, manager):
    value = entry.get_text().strip()
    if manager._app.files[key] == value:
        return
    manager._app.files[key] = value
    manager._notify.debug(
        f"files panel : {key} = {value}",
        source="panelsettings",
        route=["terminal"],
    )
