# ruff: noqa: E402
from typing import Dict, Callable
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk  # type: ignore


class HotkeyManager:
    """global hotkeys manager for keyboard + mouse combinations"""

    def __init__(self, window: Gtk.Window) -> None:
        self.window = window
        self.hotkey_map: Dict[str, Callable] = {}
        self.active_modifiers = {
            Gdk.KEY_Control_L: False,
            Gdk.KEY_Shift_L: False,
            # Gdk.KEY_Alt_L: False,
        }
        # store reference to window methods
        self.actions = {
            "toggle_pane": getattr(window, "on_toggle_pane", None),
            "center_panes": self._center_all_panes,
        }
        # self.key_controller = Gtk.EventControllerKey()  # added
        self.setup_controllers()
        # self.setup_focus_handlers()  # added

    def setup_controllers(self) -> None:
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        key_controller.connect("key-released", self.on_key_released)
        self.window.add_controller(key_controller)

    # def setup_focus_handlers(self) -> None:
    #     """workaround for hotkeys not working when focus is lost"""
    #     self.window.connect("notify::has-focus", self.on_focus_changed)

    # def on_focus_changed(self, window, pspec) -> None:
    #     if window.get_has_focus():
    #         print("window has focus")
    #         if self.key_controller not in window.list_controllers():
    #             window.add_controller(self.key_controller)
    #     else:
    #         print("window has no focus")

    def intercept_button_controller(self, button: Gtk.Button, action_name: str) -> None:
        """intercept button click events"""
        # remove existing controllers
        controllers = button.observe_controllers()
        for controller in controllers:
            if isinstance(controller, Gtk.GestureClick):
                button.remove_controller(controller)
        # add new controller
        click_controller = Gtk.GestureClick()
        click_controller.connect(
            "pressed",
            lambda gesture, n_press, x, y: self._handle_button_press(
                gesture,
                n_press,
                x,
                y,
                button,
                action_name,
            ),
        )
        button.add_controller(click_controller)

    def _handle_button_press(self, gesture, n_press, x, y, button, action_name):
        """handle button press with modifier awareness"""
        # check for modifiers
        if self.active_modifiers[Gdk.KEY_Shift_L]:
            if action_name == "toggle_pane":
                # handle shift-click
                self._center_all_panes()
                gesture.set_state(Gtk.EventSequenceState.CLAIMED)

                return
        # no modifier or different action, trigger default action
        if action_name in self.actions and self.actions[action_name]:
            self.actions[action_name](button)

    def on_key_pressed(self, controller, keyval, keycode, state) -> bool:
        if keyval == Gdk.KEY_Control_L:
            self.active_modifiers[Gdk.KEY_Control_L] = True
        elif keyval == Gdk.KEY_Shift_L:
            self.active_modifiers[Gdk.KEY_Shift_L] = True
        # elif keyval == Gdk.KEY_Alt_L:
        #     self.active_modifiers[Gdk.KEY_Alt_L] = True

        shortcut = self._create_keyboard_shortcut(keyval, state)
        return self._trigger_hotkey(shortcut)

    def on_key_released(self, controller, keyval, keycode, state) -> None:
        if keyval == Gdk.KEY_Control_L:
            self.active_modifiers[Gdk.KEY_Control_L] = False
        elif keyval == Gdk.KEY_Shift_L:
            self.active_modifiers[Gdk.KEY_Shift_L] = False
        # elif keyval == Gdk.KEY_Alt_L:
        #     self.active_modifiers[Gdk.KEY_Alt_L] = False

    def register_hotkey(self, shortcut: str, callback: Callable) -> None:
        self.hotkey_map[shortcut.lower()] = callback

    def unregister_hotkey(self, shortcut: str) -> None:
        if shortcut.lower() in self.hotkey_map:
            del self.hotkey_map[shortcut.lower()]

    def _create_keyboard_shortcut(self, keyval: int, state: Gdk.ModifierType) -> str:
        key_name = Gdk.keyval_name(keyval)
        if not key_name:
            return ""

        parts = []
        if self.active_modifiers[Gdk.KEY_Control_L]:
            parts.append("ctrl")
        if self.active_modifiers[Gdk.KEY_Shift_L]:
            parts.append("shift")
        # if self.active_modifiers[Gdk.KEY_Alt_L]:
        #     parts.append("alt")

        parts.append(key_name.lower())
        return "+".join(parts)

    def _trigger_hotkey(self, shortcut: str) -> bool:
        if shortcut and shortcut in self.hotkey_map:
            self.hotkey_map[shortcut]()
            return True

        return False

    def _center_all_panes(self) -> None:
        """center all 4 main panes"""
        if (
            hasattr(self.window, "pnd_main_v")
            and hasattr(self.window, "pnd_top_h")
            and hasattr(self.window, "pnd_btm_h")
        ):
            self.window.pnd_main_v.set_position(
                self.window.pnd_main_v.get_allocated_height() // 2
            )
            self.window.pnd_top_h.set_position(
                self.window.pnd_top_h.get_allocated_width() // 2
            )
            self.window.pnd_btm_h.set_position(
                self.window.pnd_btm_h.get_allocated_width() // 2
            )
            # if hasattr(self.window, "show_notification"):
            #     self.window.show_notification("centered all panes")
