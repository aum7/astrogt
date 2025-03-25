# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.collapsepanel import CollapsePanel
from sweph.eventdata import EventData
from sweph.eventlocation import EventLocation


def setup_event(event_name: str, expand: bool, manager) -> CollapsePanel:
    """setup event one & two collapsible panels, incl location sub-panel"""
    panel = CollapsePanel(
        title="event one" if event_name == "event one" else "event two",
        expanded=expand,
    )
    panel.set_margin_end(manager.margin_end)
    panel.add_title_css_class("label-event")
    lbl_event = panel.get_title()
    lbl_event.set_tooltip_text(
        """main event ie natal / event chart
click to set focus to event one
so change time will apply to it

note : location one + title one
+ time one are mandatory"""
        if event_name == "event one"
        else """secondary event ie transit / progression etc
click to set focus to event two
so change time will apply to it

note : leave location two empty
(both city + latitude & longitude)
if location two = location one"""
    )
    gesture = Gtk.GestureClick.new()
    gesture.connect(
        "pressed",
        lambda g, n, x, y: obc_event_selection(g, n, x, y, event_name, manager),
    )
    panel.add_title_controller(gesture)
    # location nested panel
    subpnl_location = CollapsePanel(
        title="location one" if event_name == "event one" else "location two",
        expanded=True if event_name == "event one" else False,
        indent=14,
    )
    lbl_country = Gtk.Label(label="country")
    lbl_country.add_css_class("label")
    lbl_country.set_halign(Gtk.Align.START)

    event_location = EventLocation(manager, app=manager._app)
    countries = event_location.get_countries()

    ddn_country = Gtk.DropDown.new_from_strings(countries)
    ddn_country.set_name("country")
    ddn_country.set_tooltip_text(
        """select country for location
in astrogt/user/ folder there is file named
countries.txt
open it with text editor & un-comment any country of interest
    (delete '# ' & save file)
comment (add '# ' & save file) uninterested country"""
    )
    ddn_country.add_css_class("dropdown")
    if event_name == "event one":
        manager.country_one = ddn_country
    else:
        manager.country_two = ddn_country

    lbl_city = Gtk.Label(label="city")
    lbl_city.add_css_class("label")
    lbl_city.set_halign(Gtk.Align.START)

    ent_city = Gtk.Entry()
    ent_city.set_name("city")

    def update_location(lat, lon, alt):
        ent_location.set_text(f"{lat} {lon} {alt}")

    event_location.set_location_callback(update_location)

    ent_city.set_placeholder_text("enter city name")
    ent_city.set_tooltip_text(
        """enter city name
if more than 1 city (within selected country) is found
user needs to select the one of interest

[enter] = accept data
[tab] / [shift-tab] = next / previous entry"""
    )
    ent_city.connect(
        "activate",
        lambda entry, country: event_location.get_selected_city(entry, country),
        ddn_country,
    )
    if event_name == "event one":
        manager.city_one = ent_city
    else:
        manager.city_two = ent_city
    # latitude & longitude of event
    lbl_location = Gtk.Label(label="latitude & longitude")
    lbl_location.add_css_class("label")
    lbl_location.set_halign(Gtk.Align.START)

    ent_location = Gtk.Entry()
    ent_location.set_name("location")
    ent_location.set_placeholder_text(
        "deg min (sec) n / s deg  min (sec) e / w",
    )
    ent_location.set_tooltip_text(
        """latitude & longitude

if country & city are filled, this field should be filled auto-magically
user can also enter or fine-tune geo coordinates manually

clearest form is :
    deg min (sec) n(orth) / s(outh) & e(ast) / w(est) (altitude m)
    32 21 09 n 77 66 w 113 m
will accept also decimal degree : 33.72 n 124.876 e
and also a sign ('-') for south & west : -16.75 -72.678
    note : positive values (without '-') are for north & east
        16.75 72.678
seconds & altitude are optional
only use [space] as separator

[enter] = accept data
[tab] / [shift-tab] = next / previous entry"""
    )
    # put widgets into sub-panel
    subpnl_location.add_widget(lbl_country)
    subpnl_location.add_widget(ddn_country)
    subpnl_location.add_widget(lbl_city)
    subpnl_location.add_widget(ent_city)
    subpnl_location.add_widget(lbl_location)
    subpnl_location.add_widget(ent_location)

    subpnl_event_name = CollapsePanel(
        title="name / title one" if event_name == "event one" else "name / title two",
        expanded=True if event_name == "event one" else False,
        indent=14,
    )
    ent_event_name = Gtk.Entry()
    ent_event_name.set_name("event_name")
    ent_event_name.set_placeholder_text(
        "event one name" if event_name == "event one" else "event two name"
    )
    ent_event_name.set_tooltip_text(
        """will be used for filename when saving
    max 30 characters

[enter] = apply data
[tab] / [shift-tab] = next / previous entry"""
    )
    # put widgets into sub-panel
    subpnl_event_name.add_widget(ent_event_name)

    subpnl_datetime = CollapsePanel(
        title="date & time one" if event_name == "event one" else "date & time two",
        indent=14,
    )

    ent_datetime = Gtk.Entry()
    ent_datetime.set_name("date_time")
    ent_datetime.set_placeholder_text("yyyy mm dd HH MM (SS)")
    ent_datetime.set_tooltip_text(
        """year month day hour minute (second)
    2010 9 11 22 55
second is optional
24 hour time format
only use [space] as separator

[enter] = apply & process data
[tab] / [shift-tab] = next / previous entry"""
    )
    ent_datetime.connect(
        "activate",
        lambda widget, en=event_name: manager.get_focused_event_data(en),
    )
    # put widgets into sub-panel
    subpnl_datetime.add_widget(ent_datetime)
    # create eventdata instance
    if event_name == "event one":
        manager.EVENT_ONE = EventData(
            ent_event_name,
            ent_datetime,
            ent_location,
            country=ddn_country,
            city=ent_city,
            app=manager._app,
        )
    else:
        manager.EVENT_TWO = EventData(
            ent_event_name,
            ent_datetime,
            ent_location,
            country=ddn_country,
            city=ent_city,
            app=manager._app,
        )
    # main box for event panels
    box_event = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    # sub-panel
    box_event.append(subpnl_location)
    box_event.append(subpnl_event_name)
    box_event.append(subpnl_datetime)

    panel.add_widget(box_event)

    return panel


# def event_toggle_selected(manager):
#     """toggle selected event"""
#     if manager.selected_event == "event one":
#         manager.selected_event = "event two"
#         print(f"event_toggle_selected : {manager.selected_event} selected")
#         manager.clp_event_one.remove_title_css_class("label-event-selected")
#         manager.clp_event_two.add_title_css_class("label-event-selected")
#     elif manager.selected_event == "event two":
#         manager.selected_event = "event one"
#         print(f"event_toggle_selected : {manager.selected_event} selected")
#         manager.clp_event_two.remove_title_css_class("label-event-selected")
#         manager.clp_event_one.add_title_css_class("label-event-selected")


def obc_event_selection(gesture, n_press, x, y, event_name, manager):
    """handle event selection"""
    if manager.selected_event != event_name:
        manager.selected_event = event_name
        if manager.selected_event == "event one":
            # todo comment
            print(f"event_selection : {manager.selected_event} selected")
            manager.clp_event_two.remove_title_css_class("label-event-selected")
            manager.clp_event_one.add_title_css_class("label-event-selected")
        if manager.selected_event == "event two":
            # todo comment
            print(f"event_selection : {manager.selected_event} selected")
            manager.clp_event_one.remove_title_css_class("label-event-selected")
            manager.clp_event_two.add_title_css_class("label-event-selected")


# def get_focused_event_data(manager, event_name: str, widget=None) -> None:
#     """get data for focused event on datetime entry"""
#     # print("get_focused_event_data called")
#     if event_name == "event one":
#         event_one_data = (
#             manager.EVENT_ONE.get_event_data() if manager.EVENT_ONE else None
#         )
#         manager.swe_core.get_event_one_data(event_one_data)
#     elif event_name == "event two":
#         event_two_data = (
#             manager.EVENT_TWO.get_event_data() if manager.EVENT_TWO else None
#         )
#         manager.swe_core.get_event_two_data(event_two_data)


def get_selected_event_data(manager, widget=None) -> None:
    """get data for selected event"""
    # print("get_selected_event_data called")
    if manager.selected_event == "event one" and manager.EVENT_ONE:
        manager.swe_core.get_event_one_data(
            manager.EVENT_ONE.get_event_data(),
        )
    elif manager.selected_event == "event two" and manager.EVENT_TWO:
        manager.swe_core.get_event_two_data(
            manager.EVENT_TWO.get_event_data(),
        )
