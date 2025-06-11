# ui/mainpanes/panechart/chartcircles.py
# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import cairo  # type: ignore
from math import pi, cos, sin
# colors
# redish    1,0.7,0.7
# greenish  0.8,1,0.83
# yellowish 0.2,0.2,0
# blueish   0.7,0.75,1


class CircleBase:
    """base class to handle common attributes"""

    def __init__(self, radius, cx, cy, rotation=0):
        self.radius = radius
        self.cx = cx
        self.cy = cy
        self.rotation = rotation  # in radians

    def set_custom_font(self, cr, font_size=16):
        cr.select_font_face(
            "VictorMonoLightAstro",
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL,
        )
        cr.set_font_size(font_size)

    def draw(self, cr):
        """subclass must override this method"""
        raise NotImplementedError


class CircleInfo(CircleBase):
    """show event 1 info in center circle"""

    def __init__(self, radius, cx, cy, event_data):
        super().__init__(radius, cx, cy)
        # self.event_data = event_data
        self.event_data = {"name": "mi mua", "datetime": "1975-02-08 14:10:00"}
        self.font_size = 18

    def draw(self, cr):
        """ircle with info text"""
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.15, 0.15, 0.15, 0)  # todo set alpha
        cr.fill_preserve()
        # circle border
        cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(0)  # thinnest possible
        cr.stroke()
        # event 1 info text
        info_text = (
            f"{self.event_data.get('name', '')}\n{self.event_data.get('datetime', '')}"
        )
        self.set_custom_font(cr, self.font_size)
        _, _, tw, th, _, _ = cr.text_extents(info_text)
        cr.move_to(self.cx - tw / 2, self.cy - th / 2)
        cr.set_source_rgba(1, 1, 1, 1)
        cr.show_text(info_text)


class CircleEvent(CircleBase):
    """objects / planets & house cusps"""

    def __init__(self, radius, cx, cy, guests, houses):
        super().__init__(radius, cx, cy)
        self.guests = guests
        self.houses = houses

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(1, 0.7, 0.7, 1)  # redish for fixed
        cr.stroke()
        # guests
        for guest in self.guests:
            guest.draw(cr, self.cx, self.cy, self.radius)
        # houses
        for angle in self.houses:
            x1 = self.cx + self.radius * 0.9 * cos(angle)
            y1 = self.cy + self.radius * 0.0 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.stroke()


class CircleSigns(CircleBase):
    """12 astrological signs"""

    def __init__(self, radius, cx, cy):
        super().__init__(radius, cx, cy)
        self.font_size = 18
        self.signs = [
            "\u0192",  # 01 aries
            "\u019d",  # 12 pisces
            "\u019c",  # 11
            "\u019b",  # 10
            "\u019a",  # 09
            "\u0199",  # 08
            "\u0198",  # 07
            "\u0197",  # 06
            "\u0196",  # 05
            "\u0195",  # 04
            "\u0194",  # 03
            "\u0193",  # 02
        ]

    def draw(self, cr):
        segment_angle = 2 * pi / 12
        offset = segment_angle / 2
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.5, 0.5, 0.5, 0)  # todo set alpha
        cr.set_line_width(0)
        cr.stroke()
        # sign borders
        for j in range(12):
            angle = j * segment_angle + pi  # start at left
            x1 = self.cx + self.radius * 0.9 * cos(angle)
            y1 = self.cy + self.radius * 0.0 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.set_line_width(0)
            cr.stroke()
        # glyphs
        self.set_custom_font(cr, self.font_size)
        for i, glyph in enumerate(self.signs):
            angle = (i * segment_angle) + offset
            x = self.cx + self.radius * cos(angle)
            y = self.cy + self.radius * sin(angle)
            _, _, tw, th, _, _ = cr.text_extents(glyph)
            cr.save()
            cr.translate(x, y)
            cr.rotate(angle + pi / 2)
            cr.move_to(-tw / 2, th / 2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.show_text(glyph)
            cr.restore()


# additional optional circles : varga, naksatras
# then event 2 circles
