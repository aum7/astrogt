from typing import Optional
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk


class UISetup:
    """mixin class for setting up ui components.
    note: this class is intended to be used with gtk.applicationwindow
    and should not be instantiated directly.
    """

    # type hints for inherited attributes
    set_title: callable
    set_default_size: callable
    set_child: callable
    grid: Gtk.Grid
    icon_size: Gtk.IconSize
    rvl_side_pane: Gtk.Revealer
    setup_side_pane: callable
    on_toggle_pane: callable

    def setup_window(self) -> None:
        """setup main window properties"""
        self.set_title("astrogt")  # type: ignore
        self.set_default_size(600, 500)  # type: ignore

    def setup_css(self) -> None:
        """setup css styling."""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("css/style.css")
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def setup_click_controller(self) -> None:
        """setup click gesture controller"""
        click_controller = Gtk.GestureClick()
        click_controller.set_button(0)
        click_controller.connect("pressed", self.on_context_menu)  # type: ignore
        self.add_controller(click_controller)  # type: ignore

    # ... (rest of the methods with return type annotations)
    def create_label(self, text: str, css_class: str) -> Gtk.Label:
        """create a label with specified text and css class"""
        label = Gtk.Label(label=text)
        label.set_halign(Gtk.Align.FILL)
        label.set_valign(Gtk.Align.FILL)
        label.add_css_class(css_class)
        return label
