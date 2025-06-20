# ui/mainpanes/datagraph.py
# ruff: noqa: E402
import os
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("GTK4Agg")
from matplotlib.backends.backend_gtk4agg import (
    FigureCanvasGTK4Agg as FigureCanvas,
)
import matplotlib.pyplot as plt
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D


class DataGraph(Gtk.Box):
    """load data & plot it as chart"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = Gtk.Application.get_default()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        # create figure & axes
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.append(self.canvas)
        # load & plot data
        self.full_df = None
        self.plot_range = [None, None]  # start, end
        self.last_mouse_x = None  # mouse position zoom
        self.data_load()
        self.plot_last_n(200)
        # cursor line
        self.info_cursor = self.ax.axvline(
            0,
            color="white",
            lw=0.7,
            ls="--",
            alpha=0.8,
        )
        self.cursor_text = self.ax.text(
            0.01,
            0.99,
            "",
            color="white",
            fontsize=10,
            transform=self.ax.transAxes,
            va="top",
            ha="left",
            zorder=10,
            bbox=dict(
                facecolor="#181818",
                edgecolor="white",
                alpha=0.8,
                pad=2,
            ),
        )
        # mouse events
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)

    def data_load(self):
        """load & plot data"""
        # construct file path
        data_folder = self.app.files.get("data")
        filepath = os.path.join(data_folder, "gold/gold_1h_utc.csv")
        # load csv
        df = pd.read_csv(
            filepath, parse_dates=["datetime_utc"], index_col="datetime_utc"
        )
        self.full_df = df

    def plot_last_n(self, n):
        df = self.full_df
        if df is None or len(df) == 0:
            return
        if len(df) > n:
            start = len(df) - n
        else:
            start = 0
        end = len(df)
        self.plot_range = [start, end]
        self.plot_data(start, end)

    def plot_data(self, start, end):
        df_ = self.full_df
        if df_ is None or len(df_) == 0:
            return
        if start is None or end is None:
            return
        df = df_.iloc[start:end]
        self.df = df
        # clear previous axes drawing
        self.ax.clear()
        # restore cursor line
        self.info_cursor = self.ax.axvline(
            self.last_mouse_x if self.last_mouse_x else 0,
            color="white",
            lw=0.7,
            ls="--",
            alpha=0.8,
        )
        self.cursor_text = self.ax.text(
            0.01,
            0.99,
            "",
            color="white",
            fontsize=10,
            transform=self.ax.transAxes,
            va="top",
            ha="left",
            zorder=10,
            bbox=dict(facecolor="#181818", edgecolor="white", alpha=0.8, pad=2),
        )
        self.canvas.draw()
        # dark background
        self.figure.patch.set_facecolor("#181818")
        self.ax.set_facecolor("#181818")
        # remove spines, ticks, labels
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.ax.tick_params(
            axis="both",
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )
        # minimal margins
        self.ax.set_position((0, 0, 1, 1))
        self.ax.margins(5)
        self.figure.subplots_adjust(
            left=0,
            right=1,
            top=1,
            bottom=0,
        )
        # plot candles manually for full color control
        ohlc = df[["open", "high", "low", "close"]].values
        x = np.arange(len(ohlc))
        bars_shown = (self.plot_range[1] or 0) - (self.plot_range[0] or 0)
        width = max(0.7, 0.8 * (len(ohlc) / bars_shown)) if bars_shown > 0 else 0.7
        self.candles = []
        for i in range(len(ohlc)):
            op, hi, lo, cl = ohlc[i]
            color = "dodgerblue" if cl >= op else "red"
            # body
            rect = Rectangle(
                (x[i] - width / 2, min(op, cl)),
                width,
                abs(cl - op) if cl != op else 0.8,
                facecolor=color,
                edgecolor=color,
                zorder=2,
            )
            # wick
            wick = Line2D(
                [x[i], x[i]],
                [lo, hi],
                color=color,
                linewidth=1,
                zorder=1,
            )
            self.ax.add_line(wick)
            self.candles.append((rect, wick, op, hi, lo, cl))
        self.ax.set_xlim(-1, len(ohlc))
        lows = df["low"].min() if not df.empty else 0
        highs = df["high"].max() if not df.empty else 1
        # fill canvas vertically
        self.ax.set_ylim(lows - (highs - lows) * 0.03, highs + (highs - lows) * 0.03)
        self.canvas.draw()

    def on_mouse_move(self, event):
        """show bar info on mouse-over"""
        if not event.inaxes:
            self.info_cursor.set_visible(False)
            self.cursor_text.set_visible(False)
            self.canvas.draw_idle()
            return
        self.info_cursor.set_visible(True)
        self.cursor_text.set_visible(True)
        # store last mouse x for zoom
        self.last_mouse_x = event.xdata
        self.info_cursor.set_xdata([event.xdata, event.xdata])
        ix = int(round(event.xdata))
        info = ""
        if 0 <= ix < len(self.candles):
            dt_str = self.df.index[ix].strftime("%Y-%m-%d %H:%M")
            op, hi, lo, cl = self.candles[ix][2:]
            info = f"{dt_str}\no={op:.2f}\nh={hi:.2f}\nl={lo:.2f}\nc={cl:.2f}"
        self.cursor_text.set_text(info)
        self.canvas.draw_idle()

    def on_scroll(self, event):
        """zoom on mouse-over & mouse-scroll"""
        # print(f"datagraph : event : {event}")
        cur_start, cur_end = self.plot_range
        if cur_start is None or cur_end is None or cur_end <= cur_start:
            return
        n = cur_end - cur_start
        if self.full_df is not None:
            df_len = len(self.full_df)
        zoom_amount = int(max(10, n * 0.2))
        if event.button == "up":  # zoom out - more bars
            new_n = min(df_len, n + zoom_amount)
            # print("datagraph : button : up")
        elif event.button == "down":  # zoom in - less bars
            new_n = max(20, n - zoom_amount)
            # print("datagraph : button : up")
        else:
            return
        # determine zoom center
        if self.last_mouse_x is not None:
            center_x = int(self.last_mouse_x)
        else:
            center_x = n // 2
        # center_x is index in current window, map to global index
        if cur_start:
            global_center = cur_start + center_x
        new_start = max(0, global_center - new_n // 2)
        new_end = min(df_len, new_start + new_n)
        # adjust start if at right edge
        if new_end <= new_start:
            return
        self.plot_range = [new_start, new_end]
        self.plot_data(new_start, new_end)
