# noqa: E405
# mon 250113-2022 utc
# hello world
import sys
import gi
import swisseph as swe

# from swisseph import contrib as swh
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw  # type: ignore

css_provider = Gtk.CssProvider()
css_provider.load_from_path("css/style.css")
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class AstrogtApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("astrogt")
        self.set_default_size(600, 500)

        self.grid = Gtk.Grid()
        self.set_child(self.grid)
        # revealer from left
        self.rvl_side_pane = Gtk.Revealer()
        self.rvl_side_pane.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.rvl_side_pane.set_transition_duration(3000)
        self.rvl_side_pane.set_reveal_child(True)
        # self.rvl_side_pane.set_visible(True)
        # if revealed = open > remove borders via .css KO
        # self.rvl_side_pane.add_css_class("side-pane-open")
        # add frame
        self.frm_side_pane = Gtk.Frame()
        self.frm_side_pane.add_css_class("frame")
        # test label for revealer
        self.lbl_side_pane = Gtk.Label(label="side pane")
        self.lbl_side_pane.set_halign(Gtk.Align.START)
        # self.lbl_side_pane.set_hexpand(True)
        self.lbl_side_pane.set_valign(Gtk.Align.START)
        # self.lbl_side_pane.set_valign(Gtk.Align.CENTER)
        # self.lbl_side_pane.set_vexpand(True)
        # attach to revealer
        self.frm_side_pane.set_child(self.lbl_side_pane)
        self.rvl_side_pane.set_child(self.frm_side_pane)
        # test button for revealer
        self.btn_toggle_pane = Gtk.Button(label="=")
        self.btn_toggle_pane.set_halign(Gtk.Align.START)
        self.btn_toggle_pane.set_valign(Gtk.Align.START)
        self.btn_toggle_pane.connect("clicked", self.on_toggle_pane)
        #  for paned
        # top left
        self.lbl_pane_tl = Gtk.Label(label="top left")
        # self.lbl_pane_tl.set_hexpand(True)
        # self.lbl_pane_tl.set_vexpand(True)
        self.lbl_pane_tl.set_halign(Gtk.Align.FILL)
        self.lbl_pane_tl.set_valign(Gtk.Align.FILL)
        self.lbl_pane_tl.add_css_class("label-tl")
        # label top right
        self.lbl_pane_tr = Gtk.Label(label="top right")
        # self.lbl_pane_tr.set_hexpand(True)
        # self.lbl_pane_tr.set_vexpand(True)
        self.lbl_pane_tr.set_halign(Gtk.Align.FILL)
        self.lbl_pane_tr.set_valign(Gtk.Align.FILL)
        self.lbl_pane_tr.add_css_class("label-tl")
        # label bottom left
        self.lbl_pane_bl = Gtk.Label(label="bottom left")
        # self.lbl_pane_bl.set_hexpand(True)
        # self.lbl_pane_bl.set_vexpand(True)
        self.lbl_pane_bl.set_halign(Gtk.Align.FILL)
        self.lbl_pane_bl.set_valign(Gtk.Align.FILL)
        self.lbl_pane_bl.add_css_class("label-br")
        # label bottom right
        self.lbl_pane_br = Gtk.Label(label="bottom right")
        # self.lbl_pane_br.set_hexpand(True)
        # self.lbl_pane_br.set_vexpand(True)
        self.lbl_pane_br.set_halign(Gtk.Align.FILL)
        self.lbl_pane_br.set_valign(Gtk.Align.FILL)
        self.lbl_pane_br.add_css_class("label-br")
        # paned main
        self.pnd_main_v = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.pnd_main_v.set_hexpand(True)
        self.pnd_main_v.set_vexpand(True)
        # self.pnd_main_v = Gtk.Paned.new(orientation=Gtk.Orientation.VERTICAL)
        # self.pnd_main_v.set_wide_handle(True)
        # overlay will un-clip frame's child
        self.ovl_tl = Gtk.Overlay()
        self.ovl_tl.set_child(self.lbl_pane_tl)
        self.ovl_tl.add_overlay(self.btn_toggle_pane)
        self.ovl_tr = Gtk.Overlay()
        self.ovl_tr.set_child(self.lbl_pane_tr)
        self.ovl_bl = Gtk.Overlay()
        self.ovl_bl.set_child(self.lbl_pane_bl)
        self.ovl_br = Gtk.Overlay()
        self.ovl_br.set_child(self.lbl_pane_br)
        # add label to ovl_tl
        # frames for h paned
        self.frm_top_start_child = Gtk.Frame()
        self.frm_top_start_child.add_css_class("frame")
        self.frm_top_start_child.set_child(self.ovl_tl)
        # self.frm_top_start_child.set_child(self.btn_toggle_pane)
        # self.frm_top_start_child.set_child(self.lbl_pane_tl)
        self.frm_top_end_child = Gtk.Frame()
        self.frm_top_end_child.add_css_class("frame")
        self.frm_top_end_child.set_child(self.ovl_tr)
        # self.frm_top_end_child.set_child(self.lbl_pane_tr)
        self.frm_btm_start_child = Gtk.Frame()
        self.frm_btm_start_child.add_css_class("frame")
        self.frm_btm_start_child.set_child(self.ovl_bl)
        self.frm_btm_end_child = Gtk.Frame()
        self.frm_btm_end_child.add_css_class("frame")
        self.frm_btm_end_child.set_child(self.ovl_br)
        # panded top
        self.pnd_top_h = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.pnd_top_h.set_hexpand(True)
        self.pnd_top_h.set_vexpand(True)
        # self.pnd_top_h.set_halign(Gtk.Align.FILL)
        # self.pnd_top_h = Gtk.Paned.new(orientation=Gtk.Orientation.HORIZONTAL)
        # self.pnd_top_h.set_wide_handle(True)
        self.pnd_top_h.set_start_child(self.frm_top_start_child)
        # self.pnd_top_h.set_start_child(self.btn_toggle_pane)
        # self.pnd_top_h.set_start_child(self.lbl_pane_tl)
        self.pnd_top_h.set_resize_start_child(True)
        self.pnd_top_h.set_end_child(self.frm_top_end_child)
        # self.pnd_top_h.set_end_child(self.lbl_pane_tr)
        self.pnd_top_h.set_resize_end_child(True)
        # paned bottom
        self.pnd_btm_h = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        # self.pnd_btm_h = Gtk.Paned.new(orientation=Gtk.Orientation.HORIZONTAL)
        # self.pnd_btm_h.set_wide_handle(True)
        self.pnd_btm_h.set_start_child(self.frm_btm_start_child)
        self.pnd_btm_h.set_end_child(self.frm_btm_end_child)

        self.pnd_main_v.set_start_child(self.pnd_top_h)
        self.pnd_main_v.set_resize_start_child(True)
        # self.pnd_main_v.set_shrink_start_child(False)
        self.pnd_main_v.set_end_child(self.pnd_btm_h)
        self.pnd_main_v.set_resize_end_child(True)
        # self.pnd_main_v.set_shrink_end_child(False)

        self.grid.attach(self.rvl_side_pane, 0, 0, 1, 1)
        self.grid.attach(self.pnd_main_v, 1, 0, 1, 1)

    def on_toggle_pane(self, button):
        revealed = self.rvl_side_pane.get_child_revealed()
        if revealed:
            # hide child
            self.rvl_side_pane.set_reveal_child(False)
            # hide pane
            self.rvl_side_pane.set_visible(False)
        else:
            # show pane
            self.rvl_side_pane.set_visible(True)
            # show child
            self.rvl_side_pane.set_reveal_child(True)


app = AstrogtApp(application_id="com.astrogt.app")
app.run(sys.argv)


# file_ = os.path.join(__file__)
# dir_ = os.path.join(os.path.dirname(__file__))
# print(f"dirname : {dir_}")
# print(f"file : {file_}")
