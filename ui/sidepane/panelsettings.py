# ui/sidepane/panelsettings.py
# ruff: noqa: E402
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.collapsepanel import CollapsePanel
from user.settings import OBJECTS, SWE_FLAG, HOUSE_SYSTEMS, CHART_SETTINGS
from sweph.setupsettings import get_sweph_flags_int


def setup_settings(manager) -> CollapsePanel:
    """setup widget for settings, ie objects, sweph flags, glyphs etc"""
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
    box_objects.set_margin_top(manager.margin_end)
    box_objects.set_margin_bottom(manager.margin_end)
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
    btn_toggle_event_objs.connect("clicked", toggle_event_objects, manager)
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
    manager.selected_objects_e1 = set()
    manager.selected_objects_e2 = set()
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
    # default to first / selected item
    ddn_housesys.set_selected(0)
    manager.selected_house_system = HOUSE_SYSTEMS[0][0]

    def house_system_changed(dropdown, _):
        idx = dropdown.get_selected()
        # todo modify to include short name for chart info
        hsys, _, _ = HOUSE_SYSTEMS[idx]
        manager.selected_house_system = hsys
        manager._notify.debug(
            f"selectedhousesystem : {manager.selected_house_system}",
            source="panelsettings",
            route=["terminal"],
        )

    ddn_housesys.connect("notify::selected", house_system_changed)
    subpnl_housesys.add_widget(ddn_housesys)
    manager._notify.debug(
        f"selectedhousesystem : {manager.selected_house_system}",
        source="panelsettings",
        route=["terminal"],
    )
    # --- sub-panel chart settings --------------------
    subpnl_chart_settings = CollapsePanel(
        title="chart settings",
        indent=14,
        expanded=True,
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
    manager.chart_settings = {}
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
        manager.chart_settings[setting] = default
    # naksatras ring : connect all naksatra settings in 1 function
    row = Gtk.ListBoxRow()
    # naksatras ring checkbox
    manager.chk_naks_ring = Gtk.CheckButton(label="naksatras ring")
    manager.chk_naks_ring.set_active(CHART_SETTINGS["naksatras ring"][0])
    manager.chk_naks_ring.connect(
        "toggled",
        lambda btn, n="naksatras ring", m=manager: (
            naksatras_ring(btn, n, m),
            manager.chk_28_naks.set_sensitive(btn.get_active()),
            manager.ent_1st_nak.set_sensitive(btn.get_active()),
        ),
    )
    row.set_tooltip_text(CHART_SETTINGS["naksatras ring"][1])
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
        lambda btn, n="28 naksatras", m=manager: naksatras_ring(btn, n, m),
    )
    manager.chk_28_naks.set_tooltip_text(CHART_SETTINGS["28 naksatras"][1])
    # start naksatras ring with any naksatra
    box_naks.append(manager.chk_28_naks)
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
        lambda btn, n="1st naksatra", m=manager: naksatras_ring(btn, n, m),
    )
    box_naks.append(manager.ent_1st_nak)
    row.set_child(box_naks)
    manager.lbx_chart_settings.append(row)
    # harmonics ring
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
    manager.chart_settings["harmonics ring"] = ent_harmonics.get_text()
    box_chart_settings.append(manager.lbx_chart_settings)
    # --- chart info string : basic & event-dependent ------------------
    # main box for chart info
    box_chart_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box_chart_info.set_margin_start(manager.margin_end)
    box_chart_info.set_margin_end(manager.margin_end)
    # listbox for chart info
    manager.lbx_chart_info = Gtk.ListBox()
    manager.lbx_chart_info.set_selection_mode(Gtk.SelectionMode.NONE)
    # track chart info strings
    manager.chart_info = {}
    # chart info string : basic
    for info in [
        "chart info string",
        "chart info string extra",
    ]:
        row = Gtk.ListBoxRow()
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
        ent_chart_info.set_width_chars(54)
        ent_chart_info.connect("activate", chart_info_string, manager, info)

        row.set_child(ent_chart_info)
        manager.lbx_chart_info.append(row)
        manager.chart_settings[info] = ent_chart_info.get_text()

    box_chart_info.append(manager.lbx_chart_info)
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
    subsubpnl_flags = CollapsePanel(
        title="extra flags",
        indent=21,
        expanded=False,
    )
    subsubpnl_flags.set_title_tooltip(
        """only change if you know what you are doing (see swisseph docs)"""
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
    manager.selected_flags = set()
    manager.sweph_flag = 0
    # collect flags from settings.py
    # only use 1-4 for 1st listbox (in sub-panel)
    for flag, flags_data in SWE_FLAG.items():
        if flag in ["sidereal zodiac", "true positions", "topocentric", "heliocentric"]:
            row = Gtk.ListBoxRow()
            name = flag
            selected = flags_data[0]
            tooltip = flags_data[1]
            row.set_tooltip_text(tooltip)
            # create checkbox for selection
            check = Gtk.CheckButton(label=name)
            check.set_active(selected)
            check.connect(
                "toggled", lambda btn, n=name, m=manager: flags_toggled(btn, n, m)
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
    for flag, flags_data in SWE_FLAG.items():
        if flag in ["sidereal zodiac", "true positions", "topocentric", "heliocentric"]:
            continue
        row = Gtk.ListBoxRow()
        name = flag
        selected = flags_data[0]
        tooltip = flags_data[1]
        row.set_tooltip_text(tooltip)
        # create checkboxes : initialize label > label-click will toggle checkbox
        check = Gtk.CheckButton(label=name)
        check.set_active(selected)
        check.connect(
            "toggled", lambda btn, n=name, m=manager: flags_toggled(btn, n, m)
        )
        row.set_child(check)
        manager.lbx_flags_extra.append(row)
    box_flags_extra.append(manager.lbx_flags_extra)
    # add box to sub-sub-panel
    subsubpnl_flags.add_widget(box_flags_extra)
    # insert sub-sub-panel into sub-panel
    subpnl_flags.add_widget(subsubpnl_flags)
    # collect flags as strings from checked checkboxes
    manager.selected_flags = {k for k, v in SWE_FLAG.items() if v[0]}
    # convert flags to integer
    manager.sweph_flag = get_sweph_flags_int()
    manager._notify.debug(
        f"swephflag : {manager.sweph_flag}",
        source="panelsettings",
        route=["terminal"],
    )
    # --- sub-panel year & month lengths --------------------
    subpnl_solar_lunar_periods = CollapsePanel(
        title="solar & lunar periods",
        indent=14,
        expanded=False,
    )
    # ------ sub-sub-panel solar year ----------
    subsubpnl_solar_year = CollapsePanel(
        title="solar year",
        indent=21,
        expanded=False,
    )
    # ------ sub-sub-panel lunar month ----------
    subsubpnl_lunar_month = CollapsePanel(
        title="lunar month",
        indent=21,
        expanded=False,
    )
    # box for sub-sub-panels
    box_solar_lunar_periods = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    # add sub-sub-panels
    box_solar_lunar_periods.append(subsubpnl_solar_year)
    box_solar_lunar_periods.append(subsubpnl_lunar_month)
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
    # box for sub-panel ayanamsa
    box_ayanamsa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    # add sub-sub-panels
    box_ayanamsa.append(subsubpnl_custom_ayanamsa)
    subpnl_ayanamsa.add_widget(box_ayanamsa)
    # --- sub-panel files ------------------------
    subpnl_files = CollapsePanel(
        title="files & paths",
        indent=14,
        expanded=False,
    )
    # main box for settings panels
    box_settings = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
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


def toggle_event_objects(button, manager):
    # toggle active event
    manager.selected_objects_event = 2 if manager.selected_objects_event == 1 else 1
    # initialize event 2 set on 1st toggle if empty
    if manager.selected_objects_event == 2 and not manager.selected_objects_e2:
        manager.selected_objects_e2 = {"sun", "moon"}
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
        manager.selected_objects_e1
        if manager.selected_objects_event == 1
        else manager.selected_objects_e2
    )
    for row in manager.listbox:
        check = row.get_child()
        name = check.get_label()
        check.set_active(name in objs)
    print(
        f"panelsettings : selected objs for e{manager.selected_objects_event} : {objs}"
    )


def objects_toggled(checkbutton, name, manager):
    # event-based selection
    if manager.selected_objects_event == 1:
        sel_objs = manager.selected_objects_e1
    else:
        sel_objs = manager.selected_objects_e2

    if checkbutton.get_active():
        sel_objs.add(name)
    else:
        sel_objs.discard(name)
    manager._notify.debug(
        f"\n\tselected objects : e{manager.selected_objects_event} : {sel_objs}",
        source="panelsettings",
        route=["terminal"],
    )


def objects_select_all(button, manager):
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


def flags_toggled(button, name, manager):
    """update selected sweph flags"""
    if button.get_active():
        # add to selected flags
        manager.selected_flags.add(name)
    else:
        # remove from selected flags
        manager.selected_flags.discard(name)
    print(f"panelsettings : flagstoggled : selectedflags : {manager.selected_flags}")
    # update sweph flags
    flags = 0
    for flag in manager.selected_flags:
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
    manager.sweph_flag = flags
    print(f"panelsettings : flagstoggled : swephflag : {manager.sweph_flag}")

    return flags


def chart_settings_toggled(button, setting, manager):
    print(f"chartsettingstoggled : {setting}")
    manager.chart_settings[setting] = button.get_active()


def naksatras_ring(button, key, manager):
    """combine show naksatras ring with checkbox for 28 vs 27 & 1st naksatra"""
    manager.naks_range = 28 if manager.chk_28_naks.get_active() else 27
    # clamp value
    try:
        value = int(manager.ent_1st_nak.get_text())
    except ValueError:
        manager._notify.warning(
            "set 1 to 27 / 28 naksatras",
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
    manager._notify.debug(
        f"naksatrasring : {key} | ring : {val_ring} | 28 : {val_28} | naks : {manager.naks_range} | 1st : {val_1st}",
        source="panelsettings",
        route=["terminal"],
    )


def harmonics_ring_changed(entry, manager):
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
            " ".join(str(x) for x in manager.chart_settings["harmonics ring"])
        )
        entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "dialog-warning")
    else:
        entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, None)
        entry.set_max_width_chars(5)
        w, _ = entry.get_preferred_size()
        entry.set_size_request(w.width, -1)
        manager.chart_settings["harmonics ring"] = text
    manager._notify.debug(
        f"harmonicsring : {manager.chart_settings['harmonics ring']}",
        source="panelsettings",
        route=["terminal"],
    )


def chart_info_string(entry, manager, info):
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
    fields = re.findall(r"\{[a-zA-Z0-9\[\]:]+\}", value)
    print(f"chartinfostring : {info} : {value}")
    print(f"allowed :{allowed[info]} {allowed['chars']}")
    print("fields : ", fields)
    if not all(field in allowed[info] for field in fields) and not all(
        char in allowed["chars"] for char in value
    ):
        # invalid input : user responsible for correct input
        entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "dialog-warning")
        manager._notify.warning(
            f"invalid chart info string : allowed :\n\t{allowed[info]} {allowed['chars']}",
            source="panelsettings",
            route=["terminal", "user"],
            timeout=5,
        )
        return
    else:
        # todo do not set empty icon > entry expands awkwardly
        entry.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, None)
        entry.set_max_width_chars(54)
    # update chart settings
    manager.chart_settings[info] = value
    # manager.chart_settings[info] = entry.get_text()
    manager._notify.success(
        f"chartinfostring : {manager.chart_settings[info]}",
        source="panelsettings",
        route=["terminal"],
    )
