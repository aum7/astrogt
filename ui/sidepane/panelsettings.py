# ui/sidepane/panelsettings.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.collapsepanel import CollapsePanel
from user.settings import OBJECTS, SWE_FLAG


def setup_settings(manager) -> CollapsePanel:
    """setup widget for settings, ie objects, glyphs etc"""
    # main panel for settings
    clp_settings = CollapsePanel(title="settings", expanded=False)
    clp_settings.set_margin_end(manager.margin_end)
    clp_settings.set_title_tooltip("""application & chart settings""")
    # main box for settings
    box_settings = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    # sub-panel objects --------------------
    subpnl_objects = CollapsePanel(
        title="objects / planets",
        indent=14,
        expanded=True,
    )
    subpnl_objects.set_title_tooltip("select objects to display on chart")
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
    # track selected objects
    manager.selected_objects = set()

    for _, obj_data in OBJECTS.items():
        row = Gtk.ListBoxRow()
        # set tooltip on the row
        name = obj_data[0]
        tooltip = obj_data[1]
        row.set_tooltip_text(tooltip)
        # create horizontal box for each row
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        margin_ = 7
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
    print(f"panelsettings : objselall : manager : {manager}")
    # add box to sub-panel
    subpnl_objects.add_widget(box_objects)
    # sub-panel flags --------------------
    subpnl_flags = CollapsePanel(
        title="sweph flags",
        indent=14,
        expanded=True,
    )
    subpnl_flags.set_title_tooltip("sweph calculation flags")
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
    # track selected flags
    manager.selected_flags = set()

    for flag, flags_data in SWE_FLAG.items():
        row = Gtk.ListBoxRow()
        name = flag
        selected = flags_data[0]
        tooltip = flags_data[1]
        row.set_tooltip_text(tooltip)
        # create horizontal box for each row
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
        margin_ = 7
        hbox.set_margin_top(margin_)
        hbox.set_margin_bottom(margin_)
        hbox.set_margin_start(margin_)
        hbox.set_margin_end(margin_)
        # create checkbox for selection
        check = Gtk.CheckButton()
        check.set_active(selected)
        check.connect("toggled", lambda btn, n=name: flags_toggled(btn, n, manager))
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

    # sub-panel house system --------------------
    subpnl_housesys = CollapsePanel(
        title="house system",
        indent=14,
        expanded=False,
    )
    # sub-panel chart settings --------------------
    subpnl_chart_settings = CollapsePanel(
        title="chart settings",
        indent=14,
        expanded=False,
    )
    # sub-panel year & month lengths --------------------
    subpnl_solar_lunar_periods = CollapsePanel(
        title="solar & lunar periods",
        indent=14,
        expanded=False,
    )
    # sub-sub-panel solar year
    subsubpnl_solar_year = CollapsePanel(
        title="solar year",
        indent=21,
        expanded=False,
    )
    # sub-sub-panel lunar month
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
    # sub-panel ayanamsa --------------------
    subpnl_ayanamsa = CollapsePanel(
        title="ayanamsa",
        indent=14,
        expanded=False,
    )
    # sub-sub-panel custom ayanamsa
    subsubpnl_custom_ayanamsa = CollapsePanel(
        title="custom ayanamsa",
        indent=21,
        expanded=False,
    )
    # box for sub-panels ayanamsa
    box_ayanamsa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    # add sub-sub-panels
    box_ayanamsa.append(subsubpnl_custom_ayanamsa)
    # sub-panel files
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


def objects_toggled(checkbutton, option_name, manager):
    if checkbutton.get_active():
        manager.selected_objects.add(option_name)
    else:
        manager.selected_objects.discard(option_name)
    manager._notify.debug(
        f"\n\tselected objects : {manager.selected_objects}",
        source="sidepane",
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
    pass
