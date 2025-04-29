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
    ico_margin = 2
    ico_toggle_event_objs.set_margin_start(ico_margin)
    ico_toggle_event_objs.set_margin_end(ico_margin)
    ico_toggle_event_objs.set_margin_top(0)
    ico_toggle_event_objs.set_margin_bottom(0)
    # next button with icon
    btn_toggle_event_objs = Gtk.Button()
    btn_toggle_event_objs.add_css_class("button-pane")
    btn_toggle_event_objs.set_child(ico_toggle_event_objs)
    btn_toggle_event_objs.set_halign(Gtk.Align.START)
    btn_toggle_event_objs.set_valign(Gtk.Align.START)
    btn_toggle_event_objs.set_tooltip_text("toggle selected objects for event 1")
    btn_toggle_event_objs.connect("clicked", toggle_event_objects, manager)
    box_button.append(btn_toggle_event_objs)
    # select all button
    btn_select_all = Gtk.Button(label="all")
    btn_select_all.set_tooltip_text("select all objects")
    btn_select_all.connect("clicked", objects_select_all, manager)
    box_button.append(btn_select_all)
    # deselect all button
    btn_select_none = Gtk.Button(label="none")
    btn_select_none.set_tooltip_text("select none object")
    btn_select_none.connect("clicked", objects_select_none, manager)
    box_button.append(btn_select_none)
    # list box for multiple selection
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
        # set tooltip on the row
        name = obj_data[0]
        tooltip = obj_data[1]
        row.set_tooltip_text(tooltip)
        # create horizontal box for each row
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        margin_ = 0
        hbox.set_margin_top(margin_)
        hbox.set_margin_bottom(margin_)
        hbox.set_margin_start(margin_)
        hbox.set_margin_end(margin_)
        # create checkbox for selection
        check = Gtk.CheckButton()
        check.connect("toggled", lambda btn, n=name: objects_toggled(btn, n, manager))
        hbox.append(check)
        # add label with the option name
        label = Gtk.Label(label=name)
        label.set_halign(Gtk.Align.START)
        # label.set_hexpand(True)
        hbox.append(label)

        row.set_child(hbox)
        manager.listbox.append(row)
    objects_select_all(check, manager)
    # add box to sub-panel
    subpnl_objects.add_widget(box_objects)
    # --- sub-panel flags --------------------
    subpnl_flags = CollapsePanel(
        title="sweph flags",
        indent=14,
        expanded=False,
    )
    subpnl_flags.set_title_tooltip(
        """ sweph calculation flags\n
average user will be interested in top 3 (4) setttings\n
only change the rest if you really know
    what you are doing (see swisseph docs)"""
    )
    # main container
    box_flags = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box_flags.set_margin_top(manager.margin_end)
    box_flags.set_margin_bottom(manager.margin_end)
    box_flags.set_margin_start(manager.margin_end)
    box_flags.set_margin_end(manager.margin_end)
    # list box for check boxes
    manager.listbox_flags = Gtk.ListBox()
    manager.listbox_flags.set_selection_mode(Gtk.SelectionMode.NONE)
    box_flags.append(manager.listbox_flags)
    # track selected flags as strings for button labels
    manager.selected_flags = set()
    manager.sweph_flag = 0
    # initial flags setup
    for flag, flags_data in SWE_FLAG.items():
        row = Gtk.ListBoxRow()
        name = flag
        selected = flags_data[0]
        tooltip = flags_data[1]
        row.set_tooltip_text(tooltip)
        # create horizontal box for each row
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        margin_ = 0
        hbox.set_margin_top(margin_)
        hbox.set_margin_bottom(margin_)
        hbox.set_margin_start(margin_)
        hbox.set_margin_end(margin_)
        # create checkbox for selection
        check = Gtk.CheckButton()
        check.set_active(selected)
        check.connect(
            "toggled", lambda btn, n=name, m=manager: flags_toggled(btn, n, m)
        )
        hbox.append(check)
        # add label with the option name
        label = Gtk.Label(label=name)
        label.set_halign(Gtk.Align.START)
        # append label to box
        hbox.append(label)

        row.set_child(hbox)
        manager.listbox_flags.append(row)
    # add box to sub-panel
    subpnl_flags.add_widget(box_flags)
    # collect flags as strings from checked checkboxes
    manager.selected_flags = {k for k, v in SWE_FLAG.items() if v[0]}
    # print(f"panelsettings : selectedflags : {manager.selected_flags}")
    # setup initial sweph flags
    manager.sweph_flag = get_sweph_flags_int()
    manager._notify.debug(
        f"swephflag : {manager.sweph_flag}",
        source="panelsettings",
        route=["terminal"],
    )
    # --- sub-panel house system --------------------
    subpnl_housesys = CollapsePanel(
        title="house system",
        indent=14,
        expanded=False,
    )
    # dropdown list for house system selection
    housesys_list = Gtk.StringList.new([f"{name}" for _, name, _ in HOUSE_SYSTEMS])
    ddn_housesys = Gtk.DropDown.new(housesys_list)
    ddn_housesys.set_margin_start(0)
    ddn_housesys.set_margin_end(0)
    ddn_housesys.set_margin_top(0)
    ddn_housesys.set_margin_bottom(0)
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
    box_chart_settings = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    box_chart_settings.set_hexpand(False)

    manager.listbox_chart = Gtk.ListBox()
    manager.listbox_chart.set_selection_mode(Gtk.SelectionMode.NONE)
    manager.listbox_chart.set_hexpand(False)
    box_chart_settings.append(manager.listbox_chart)
    manager.chart_settings = {}
    margin_ = 0
    # checkboxes
    for key in [
        "enable glyphs",
        "true mc & ic",
        "fixed asc",
        "mean node",
    ]:
        row = Gtk.ListBoxRow()
        default, tooltip = CHART_SETTINGS[key]
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        hbox.set_margin_top(margin_)
        hbox.set_margin_bottom(margin_)
        hbox.set_margin_start(margin_)
        hbox.set_margin_end(margin_)
        # create checkbox for selection
        check = Gtk.CheckButton()
        check.set_active(default)
        check.connect(
            "toggled",
            lambda btn, n=key, m=manager: chart_settings_toggled(btn, n, m),
        )
        hbox.append(check)
        # labels
        label = Gtk.Label(label=key)
        label.set_halign(Gtk.Align.START)
        # append label to box
        hbox.append(label)
        row.set_tooltip_text(tooltip)
        row.set_child(hbox)
        manager.listbox_chart.append(row)
        manager.chart_settings[key] = default
    # naksatras ring : connect all naksatra settings in 1 function
    box_naksatras = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
    box_naksatras.set_margin_top(margin_)
    box_naksatras.set_margin_bottom(margin_)
    box_naksatras.set_margin_start(margin_)
    box_naksatras.set_margin_end(margin_)
    box_naksatras.set_hexpand(False)
    box_naksatras.set_vexpand(False)
    box_naksatras.set_halign(Gtk.Align.START)
    box_naksatras.set_size_request(-1, -1)
    # naksatras ring checkbox
    chk_naksatras = Gtk.CheckButton(label="naksatras ring")
    chk_naksatras.set_active(CHART_SETTINGS["naksatras ring"][0])
    chk_naksatras.set_tooltip_text(CHART_SETTINGS["naksatras ring"][1])
    chk_naksatras.connect(
        "toggled",
        lambda btn, n="naksatras ring", m=manager: naksatras_ring(btn, n, m),
    )
    # naksatras number (27 vs 28) & 1st naksatra
    box_naksatras.append(chk_naksatras)
    # checkbox for 28 equal naksatras
    chk_28_naksatras = Gtk.CheckButton(label="28")
    chk_28_naksatras.set_active(CHART_SETTINGS["28 naksatras"][0])
    chk_28_naksatras.set_tooltip_text(CHART_SETTINGS["28 naksatras"][1])
    chk_28_naksatras.connect(
        "toggled",
        lambda btn, n="28 naksatras", m=manager: naksatras_ring(btn, n, m),
    )
    box_naksatras.append(chk_28_naksatras)
    # start naksatras ring with any naksatra
    lbl_1st_naksatra = Gtk.Label(label="1st")
    box_naksatras.append(lbl_1st_naksatra)
    # entry for 1st naksatra to start at 0 aries
    ent_1st_naksatra = Gtk.Entry()
    ent_1st_naksatra.set_text(str(CHART_SETTINGS["1st naksatra"][0]))
    ent_1st_naksatra.set_tooltip_text(CHART_SETTINGS["1st naksatra"][1])
    ent_1st_naksatra.set_alignment(0.5)
    ent_1st_naksatra.set_hexpand(False)
    ent_1st_naksatra.set_halign(Gtk.Align.START)
    # here
    # ent_1st_naksatra.set_size_request(4, -1)
    ent_1st_naksatra.set_property("width-chars", 4)
    ent_1st_naksatra.connect(
        "changed",
        lambda btn, n="1st naksatra", m=manager: naksatras_ring(btn, n, m),
    )
    box_naksatras.append(ent_1st_naksatra)
    row_naksatras = Gtk.ListBoxRow()
    row_naksatras.set_child(box_naksatras)
    # add checkbox to listbox
    manager.listbox_chart.append(row_naksatras)
    # harmonics ring
    row = Gtk.ListBoxRow()
    box_harmonics = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
    # label
    lbl_harmonics = Gtk.Label(label="harmonic rings")
    lbl_harmonics.set_margin_start(0)
    lbl_harmonics.set_margin_end(0)
    lbl_harmonics.set_margin_top(0)
    lbl_harmonics.set_margin_bottom(0)
    box_harmonics.append(lbl_harmonics)
    ent_harmonics = Gtk.Entry()
    ent_harmonics.set_text(
        " ".join(str(x) for x in CHART_SETTINGS["harmonics ring"][0])
        if isinstance(CHART_SETTINGS["harmonics ring"][0], (list, tuple))
        else str(CHART_SETTINGS["harmonics ring"][0])
    )
    ent_harmonics.set_tooltip_text(CHART_SETTINGS["harmonics ring"][1])
    ent_harmonics.set_max_length(5)
    ent_harmonics.set_width_chars(7)
    ent_harmonics.set_hexpand(False)
    ent_harmonics.set_halign(Gtk.Align.START)
    ent_harmonics.set_size_request(40, -1)
    ent_harmonics.connect("changed", harmonics_ring_changed, manager)

    box_harmonics.append(ent_harmonics)
    row.set_child(box_harmonics)
    manager.listbox_chart.append(row)
    manager.chart_settings["harmonics ring"] = ent_harmonics.get_text()
    # (basic) chart info string
    for key in [
        "chart info string",
        "chart info string extra",
    ]:
        row = Gtk.ListBoxRow()
        ent_chart_info = Gtk.Entry()
        ent_chart_info.set_text(
            CHART_SETTINGS[key][0]
            if isinstance(CHART_SETTINGS[key], tuple)
            else CHART_SETTINGS[key]
        )
        ent_chart_info.set_tooltip_text(
            CHART_SETTINGS[key if isinstance(CHART_SETTINGS[key], str) else key][1]
            if isinstance(CHART_SETTINGS[key], tuple)
            else ""
        )
        ent_chart_info.set_width_chars(40)
        ent_chart_info.set_hexpand(False)
        ent_chart_info.set_halign(Gtk.Align.START)
        ent_chart_info.set_size_request(40, -1)
        ent_chart_info.connect("changed", chart_info_string_changed, manager, key)

        row.set_child(ent_chart_info)
        manager.listbox_chart.append(row)
        manager.chart_settings[key] = ent_chart_info.get_text()

    subpnl_chart_settings.add_widget(box_chart_settings)

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
    box_settings.append(subpnl_flags)
    box_settings.append(subpnl_housesys)
    box_settings.append(subpnl_chart_settings)
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
        hbox = row.get_child()
        check = hbox.get_first_child()
        label = hbox.get_last_child()
        name = label.get_label()
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
        inner = row.get_child()
        if inner:
            child = inner.get_first_child()
            while child is not None:
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
        inner = row.get_child()
        if inner:
            child = inner.get_first_child()
            while child is not None:
                if isinstance(child, Gtk.CheckButton):
                    child.set_active(False)
                child = child.get_next_sibling()
        i += 1


def flags_toggled(button, name, manager):
    """update selected sweph flags"""
    if button.get_active():
        # update checkbox
        manager.selected_flags.add(name)
    else:
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


# helper : toggled checkboxes
def chart_settings_toggled(button, key, manager):
    manager.chart_settings[key] = button.get_active()


def naksatras_ring(button, key, manager):
    """combine show naksatras ring with checkbox for 28 vs 27 & 1st naksatra"""
    manager._notify.debug(
        f"naksatrasring : {key} : {[button.get_active() if isinstance(button, Gtk.CheckButton) else None]}",
        source="panelsettings",
        route=["terminal"],
    )


# helper : harmonics ring changed
def harmonics_ring_changed(entry, manager):
    text = entry.get_text().strip()
    nums = text.split()
    if not all(n.isdigit() for n in nums) or not (1 <= len(nums) <= 2):
        # invalid input
        # entry.set_text(" ".join(str(x) for x in manager.chart_settings["harmonics ring"]))
        entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "dialog-warning")
    else:
        entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
        manager.chart_settings["harmonics ring"] = text


# helper : chart info string changed
def chart_info_string_changed(entry, manager, key):
    manager.chart_settings[key] = entry.get_text()
    manager._notify.debug(
        f"chartinfostring : {manager.chart_settings[key]}",
        source="panelsettings",
        route=["terminal"],
    )
