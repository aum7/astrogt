# ruff: noqa: E402
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pathlib import Path
import os
import logging
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib  # type: ignore


class NotifyLevel(Enum):
    """notification levels for the application"""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class NotifyMessage:
    """notification message object, implemented via adw.toastoverlay"""

    def __init__(
        self,
        message: str,
        level=NotifyLevel.INFO,
        source: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        timeout: Optional[int] = None,
        do_log: Optional[bool] = True,
    ):
        self.level = level if isinstance(level, NotifyLevel) else NotifyLevel.INFO
        self.message = message
        self.source = source or "sys"
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.timeout = timeout
        self.do_log = do_log

    def __str__(self):
        return f"{self.source} : {self.message}"

    def full_str(self):
        """detailed string representation"""
        return (
            f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} utc "
            f"[{self.level.value.upper()}] {self.source} : {self.message}"
        )


class NotifyLogger:
    """write notifications to log file"""

    def __init__(self, log_file=None):
        self.logger = logging.getLogger("notifications")
        self.logger.setLevel(logging.DEBUG)
        # default log file in home directory
        if log_file is None:
            log_dir = Path.home() / ".astrogt" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = str(log_dir / "notifications.log")
        # setup file handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

        self.log_file = log_file

    def log(self, msg: NotifyMessage):
        """log notification message"""
        log_level = {
            NotifyLevel.INFO: logging.INFO,
            NotifyLevel.SUCCESS: logging.INFO,
            NotifyLevel.WARNING: logging.WARNING,
            NotifyLevel.ERROR: logging.ERROR,
            NotifyLevel.DEBUG: logging.DEBUG,
        }

        self.logger.log(log_level[msg.level], msg.full_str())


class NotifyManager:
    """notification manager with level-specific toasts"""

    def __init__(self, log_file=None):
        self.toast_overlay = None
        # setup logger
        self.logger = NotifyLogger(log_file)
        self._DEFAULT_TIMEOUTS = {
            NotifyLevel.INFO: 3,
            NotifyLevel.SUCCESS: 3,
            NotifyLevel.WARNING: 4,
            NotifyLevel.ERROR: 5,
            NotifyLevel.DEBUG: 5,
        }
        self.convenience_methods()

    # dynamic convenience methods
    def convenience_methods(self):
        for level in NotifyLevel:
            setattr(self, level.name.lower(), self._make_notify(level))

    def _make_notify(self, level: NotifyLevel):
        def notify_method(
            message: str,
            source: Optional[str] = None,
            timeout: Optional[int] = None,
            do_log: Optional[bool] = True,
        ) -> bool:
            return self.notify(message, level, source, timeout, do_log)

        return notify_method

    def notify(
        self,
        message: str,
        level: NotifyLevel = NotifyLevel.INFO,
        source: Optional[str] = None,
        timeout: Optional[int] = None,
        do_log: Optional[bool] = True,
    ) -> bool:
        """show notification with specified level and optional custom icon"""
        if isinstance(level, str):
            level = NotifyLevel(level.lower())
        if not self.toast_overlay:
            print(f"[{level.value}] {message}")
            return False

        msg = NotifyMessage(message, level, source, timeout=timeout)
        # log to file
        if do_log:
            self.logger.log(msg)
            print(msg.full_str())

        GLib.idle_add(self._show_toast, msg)
        return True

    def _show_toast(self, msg: NotifyMessage) -> None:
        """show toast notification with level-specific icon"""
        try:
            if self.toast_overlay:
                # custom layout box
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                box.set_margin_start(3)
                box.set_margin_end(5)
                # icon based on level
                icon = Gtk.Image()
                icon.set_pixel_size(24)
                # try to load custom icon
                icon_name = f"notify-{msg.level.value}"
                icon_path = os.path.join(
                    os.path.dirname(__file__),
                    "imgs",
                    "icons",
                    "notify",
                    f"{icon_name}.svg",
                )

                if os.path.exists(icon_path):
                    icon.set_from_file(icon_path)
                else:
                    # fallback to system icons
                    fallback_icons = {
                        NotifyLevel.INFO: "dialog-information",
                        NotifyLevel.SUCCESS: "checkbox-checked",
                        NotifyLevel.WARNING: "dialog-warning",
                        NotifyLevel.ERROR: "dialog-error",
                        NotifyLevel.DEBUG: "preferences-system",
                    }
                    icon.set_from_icon_name(fallback_icons[msg.level])

                box.append(icon)
                # label with message
                label = Gtk.Label(label=str(msg))
                # label.add_css_class("heading")
                box.append(label)
                # create toast
                toast = Adw.Toast.new("")
                toast.set_custom_title(box)
                # use custom timeout if provided, else use default
                if msg.timeout is not None:
                    toast.set_timeout(msg.timeout)
                else:
                    toast.set_timeout(self._DEFAULT_TIMEOUTS[msg.level])

                self.toast_overlay.add_toast(toast)

        except Exception as e:
            print(f"error in toast notification: {str(e)}")
            print(f"message was: {msg.full_str()}")

    # convenience methods
    # def info(
    #     self,
    #     message: str,
    #     source: Optional[str] = None,
    #     timeout: Optional[int] = None,
    #     do_log: Optional[bool] = True,
    # ) -> bool:
    #     """show info notification"""
    #     return self.notify(message, NotifyLevel.INFO, source, timeout)

    # def success(
    #     self,
    #     message: str,
    #     source: Optional[str] = None,
    #     timeout: Optional[int] = None,
    #     do_log: Optional[bool] = True,
    # ) -> bool:
    #     """show success notification"""
    #     return self.notify(message, NotifyLevel.SUCCESS, source, timeout)

    # def warning(
    #     self,
    #     message: str,
    #     source: Optional[str] = None,
    #     timeout: Optional[int] = None,
    #     do_log: Optional[bool] = True,
    # ) -> bool:
    #     """show warning notification"""
    #     return self.notify(message, NotifyLevel.WARNING, source, timeout)

    # def error(
    #     self,
    #     message: str,
    #     source: Optional[str] = None,
    #     timeout: Optional[int] = None,
    #     do_log: Optional[bool] = True,
    # ) -> bool:
    #     """show error notification"""
    #     return self.notify(message, NotifyLevel.ERROR, source, timeout)

    # def debug(
    #     self,
    #     message: str,
    #     source: Optional[str] = None,
    #     timeout: Optional[int] = None,
    #     do_log: Optional[bool] = True,
    # ) -> bool:
    #     """show debug notification"""
    #     return self.notify(message, NotifyLevel.DEBUG, source, timeout)
