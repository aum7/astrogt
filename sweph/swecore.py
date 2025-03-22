# ruff: noqa: E402
import os
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SweCore:
    """note : swisseph calculations need be closed at the end of computations"""

    # swiss ephemeris path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ephe_path = os.path.join(current_dir, "ephe")
    swe.set_ephe_path(ephe_path)
    # event one
    event_one_name = ""
    event_one_country = ""
    event_one_city = ""
    event_one_location = ""
    event_one_date_time = ""
    # event two
    event_two_name = ""
    event_two_country = ""
    event_two_city = ""
    event_two_location = ""
    event_two_date_time = ""

    def __init__(self, get_application=None):
        print("initialising swisseph ...")
        # close swe after initialisation
        swe.close()
        self._get_application = get_application or Gtk.Application.get_default()

    def notify_user(self, message, level="info", **kwargs):
        """show app notification"""
        if self._get_application and hasattr(self._get_application, "notify_manager"):
            if level == "info":
                self._get_application.notify_manager.info(message=message, **kwargs)
            elif level == "warning":
                self._get_application.notify_manager.warning(message=message, **kwargs)
            elif level == "error":
                self._get_application.notify_manager.error(message=message, **kwargs)
            elif level == "success":
                self._get_application.notify_manager.success(message=message, **kwargs)
            elif level == "debug":
                self._get_application.notify_manager.debug(message=message, **kwargs)
            else:
                print(f"unknown level : {level}")
        else:
            print(f"swecore : notification failed\n{message}")

    @classmethod
    def swe_ready_data(cls):
        """prepare event data for swe calculations"""
        # event one
        e1_name = cls.event_one_name
        e1_country = cls.event_one_country
        e1_city = cls.event_one_city
        e1_location = cls.event_one_location
        e1_datetime = cls.event_one_date_time
        # event two
        e2_name = cls.event_two_name
        e2_country = cls.event_two_country
        e2_city = cls.event_two_city
        e2_location = cls.event_two_location
        e2_datetime = cls.event_two_date_time

        cls().notify_user(
            message=f"swisseph data ready : {e1_name}",
            source="swecore",
            level="debug",
        )

        return {
            e1_name: [e1_country, e1_city, e1_location, e1_datetime],
            e2_name: [e2_country, e2_city, e2_location, e2_datetime],
        }

    @classmethod
    def get_events_data(cls, event_one=None, event_two=None):
        """process event data using swisseph ; parent window / widget (optional)"""

        # @classmethod
        def has_data_changed(self, event_data, event_type):
            changed = False
            if event_type == "event_one":
                if (
                    event_data["name"] != self.event_one_name
                    or event_data["date_time"] != self.event_one_date_time
                    or event_data["country"] != self.event_one_country
                    or event_data["city"] != self.event_one_city
                    or event_data["location"] != self.event_one_location
                ):
                    changed = True
            elif event_type == "event_two":
                if (
                    event_data["name"] != self.event_two_name
                    or event_data["date_time"] != self.event_two_date_time
                    or event_data["country"] != self.event_two_country
                    or event_data["city"] != self.event_two_city
                    or event_data["location"] != self.event_two_location
                ):
                    changed = True
            return changed

        if event_one:
            print("processing event one :")
            if (
                not event_one["name"]
                or not event_one["date_time"]
                or not event_one["country"]
                or not event_one["city"]
                or not event_one["location"]
            ):
                cls().notify_user(
                    message="event one : data missing",
                    source="swecore",
                )
                return {}
            # check if data has changed
            if has_data_changed(cls(), event_one, "event_one"):
                cls().notify_user(
                    message="event one : data changed",
                    source="swecore",
                )
                # data received
                cls.event_one_name = event_one["name"]
                cls.event_one_date_time = event_one["date_time"]
                cls.event_one_country = event_one["country"]
                cls.event_one_city = event_one["city"]
                cls.event_one_location = event_one["location"]
                # process data
                cls.swe_ready_data()

                cls().notify_user(
                    message=f"event one data received :"
                    f"\n\tname : {event_one['name']}"
                    f"\n\tdatetime : {event_one['date_time']}"
                    f"\n\tcountry : {event_one['country']}"
                    f"\n\tcity : {event_one['city']}"
                    f"\n\tlocation : {event_one['location']}",
                    source="swecore",
                )
        if event_two:
            print("processing event two :")
            # for event two only datetime is mandatory
            if not event_two["date_time"]:
                cls().notify_user(
                    message="event two : datetime missing",
                    source="swecore",
                    timeout=0.7,
                )
                # return {}

            if not event_two["name"]:
                event_two["name"] = cls.event_one_name
            # if location not provided, use event one location
            if not event_two["country"]:
                event_two["country"] = cls.event_one_country
            if not event_two["city"]:
                event_two["city"] = cls.event_one_city
            if not event_two["location"]:
                event_two["location"] = cls.event_one_location
            # check if data has changed
            if has_data_changed(cls(), event_two, "event_two"):
                cls().notify_user(
                    message="event two : data changed ...",
                    source="swecore",
                )
                # data received
                cls.event_two_name = event_two["name"]
                cls.event_two_date_time = event_two["date_time"]
                cls.event_two_country = event_two["country"]
                cls.event_two_city = event_two["city"]
                cls.event_two_location = event_two["location"]
                # process data
                cls().swe_ready_data()

                cls().notify_user(
                    message=f"event two data received :"
                    f"\n\tname : {event_two['name']}"
                    f"\n\tdatetime : {event_two['date_time']}"
                    f"\n\tcountry : {event_two['country']}"
                    f"\n\tcity : {event_two['city']}"
                    f"\n\tlocation : {event_two['location']}",
                    source="swecore",
                )
        # todo test print
        # window.get_application().notify_manager.debug(
        #     message="\n"
        #     f"swecore.event_one_name : {SweCore.event_one_name}"
        #     f"\nswecore.event_one_date_time : {SweCore.event_one_date_time}"
        #     f"\nswecore.event_one_country : {SweCore.event_one_country}"
        #     f"\nswecore.event_one_city : {SweCore.event_one_city}"
        #     f"\nswecore.event_one_location : {SweCore.event_one_location}"
        #     f"\n\nswecore.event_two_name : {SweCore.event_two_name}"
        #     f"\nswecore.event_two_date_time : {SweCore.event_two_date_time}"
        #     f"\nswecore.event_two_country : {SweCore.event_two_country}"
        #     f"\nswecore.event_two_city : {SweCore.event_two_city}"
        #     f"\nswecore.event_two_location : {SweCore.event_two_location}",
        #     source="swecore",
        # )
