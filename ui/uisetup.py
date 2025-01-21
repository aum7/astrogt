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

    def create_label(self, text: str, css_class: str) -> Gtk.Label:
        """create a label with specified text and css class"""
        label = Gtk.Label(label=text)
        label.set_halign(Gtk.Align.FILL)
        label.set_valign(Gtk.Align.FILL)
        label.add_css_class(css_class)
        return label

    def setup_revealer(self):
        # initialize the revealer
        self.rvl_side_pane = Gtk.Revealer()
        self.rvl_side_pane.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_RIGHT,
        )
        self.rvl_side_pane.set_transition_duration(3000)
        self.rvl_side_pane.set_reveal_child(True)
        # set the side pane content
        self.frm_side_pane = Gtk.Frame()
        self.frm_side_pane.add_css_class("frame")
        self.frm_side_pane.set_child(self.setup_side_pane())
        # set the revealer's child
        self.rvl_side_pane.set_child(self.frm_side_pane)

    def setup_menu_button(self):
        ico_menu = Gtk.Image.new_from_file("imgs/icons/menu.svg")
        ico_menu.set_icon_size(self.icon_size)
        icon_hmargin = icon_vmargin = 0
        ico_menu.set_margin_start(icon_hmargin)
        ico_menu.set_margin_end(icon_hmargin)
        ico_menu.set_margin_top(icon_vmargin)
        ico_menu.set_margin_bottom(icon_vmargin)

        self.btn_toggle_pane = Gtk.Button()
        self.btn_toggle_pane.add_css_class("button-pane")
        self.btn_toggle_pane.set_child(ico_menu)
        self.btn_toggle_pane.set_halign(Gtk.Align.START)
        self.btn_toggle_pane.set_valign(Gtk.Align.START)
        self.btn_toggle_pane.set_tooltip_text(
            """toggle side pane
    shift-click to center all panes [todo]"""
        )
        # make sure we're connecting to the correct method
        self.btn_toggle_pane.connect("clicked", self.on_toggle_pane)
