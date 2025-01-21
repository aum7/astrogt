import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


class WindowHandlers:
    """Mixin class for window event handlers.

    Note: This class is intended to be used with Gtk.ApplicationWindow
    and should not be instantiated directly.
    """

    # Type hints for inherited attributes
    rvl_side_pane: Gtk.Revealer
    ovl_tl: Gtk.Overlay
    ovl_tr: Gtk.Overlay
    ovl_bl: Gtk.Overlay
    ovl_br: Gtk.Overlay

    def on_context_menu(
        self, gesture: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        """Handle context menu events."""
        if gesture.get_current_button() == 3:
            print("r-click")
            widget = gesture.get_widget()
            if widget is None:
                print("widget none")
                return
            # ... rest of the method:
            print("r-click")
            widget = gesture.get_widget()
            if widget is None:
                print("widget none")
                return

            root = widget.get_root()
            if root is None:
                print("root none")
                return

            wx, wy = widget.translate_coordinates(root, x, y)
            if wx is None or wy is None:
                print("coordinates translation failed")
                return

            picked = root.pick(wx, wy, Gtk.PickFlags.DEFAULT)
            if picked is None:
                print("picked none")
                return

            print(f"picked : {picked.__class__.__name__}")
            parent = picked.get_parent()
            if parent:
                print(f"picked parent : {parent.__class__.__name__}")

            # Reference overlays through the main window instance
            overlay_name = None
            if isinstance(parent, Gtk.Overlay):
                if parent == self.ovl_tl:
                    overlay_name = "ovl top left"
                elif parent == self.ovl_tr:
                    overlay_name = "ovl top right"
                elif parent == self.ovl_bl:
                    overlay_name = "ovl bottom left"
                elif parent == self.ovl_br:
                    overlay_name = "ovl bottom right"
            print(f"overlay : {overlay_name}")

    def on_toggle_pane(self, button):
        revealed = self.rvl_side_pane.get_child_revealed()
        if revealed:
            self.rvl_side_pane.set_reveal_child(False)
            self.rvl_side_pane.set_visible(False)
        else:
            self.rvl_side_pane.set_visible(True)
            self.rvl_side_pane.set_reveal_child(True)
