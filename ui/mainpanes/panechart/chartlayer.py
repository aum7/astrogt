# ui/mainpanes/panechart/chartlayer.py
import cairo
from math import pi, cos, sin


class CircleLayer:
    """layer where circles as charts live happy & prosperous life"""

    def __init__(self, layer="info", chart=None, guests=None):
        self.layer = layer
        self.chart = chart
        # astrological objects as guests of cosmos
        self.guests = guests or []
        self.info_data = None
        self.radius = 0

    def add_guest(self, objects):
        self.guests.extend(objects)

    def draw(self, cr, width, height):
        """will draw small circles as objects / planets marker & zodiac signs"""
        cx, cy = width / 2, height / 2
        base = min(width, height) * 0.5
        if self.layer == "info":
            radius = base * 0.5
            cr.arc(cx, cy, radius, 0, 2 * pi)
            cr.set_source_rgba(0.9, 0.9, 0.9, 0.8)
            cr.fill_preserve()
            cr.set_source_rgba(0.3, 0.3, 0.4, 1)
            cr.stroke()
            # if hasattr(self, "info_data"):
            if self.info_data:
                info = self.info_data
                text = f"{info.get('name', '')}\n{info.get('country', '')}\n{info.get('city', '')}\n{info.get('location', '')}\n{info.get('datetime')}"
                cr.set_source_rgba(0, 0, 0, 1)
                cr.select_font_face("Sans", 0, 0)
                cr.set_font_size(12)
                xbearing, ybearing, tw, th, xadvance, yadvance = cr.text_extents(text)
                cr.move_to(cx - tw / 2, cy - th / 2)
                cr.show_text(text)
            return
        elif self.layer == "sign":
            # outer radius for astro signs
            outer_radius = base * 0.95
            # outer circle boundary
            cr.arc(cx, cy, outer_radius, 0, 2 * pi)
            cr.set_source_rgba(0.5, 0.5, 0.5, 0.3)
            cr.stroke()
            cr.select_font_face(
                "VictorMonoLightAstro",
                cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL,
            )
            cr.set_font_size(18)
            cr.set_source_rgba(1, 1, 1, 1)
            # sign segment lines : 30° & offset 15°
            segment_angle = 2 * pi / 12
            offset = segment_angle / 2
            for j in range(12):
                angle = j * segment_angle + pi  # start at left
                start_r = outer_radius * 0.9
                end_r = outer_radius
                x1 = cx + start_r * cos(angle)
                y1 = cy + start_r * sin(angle)
                x2 = cx + end_r * cos(angle)
                y2 = cy + end_r * sin(angle)
                cr.move_to(x1, y1)
                cr.line_to(x2, y2)
                cr.set_source_rgba(1, 1, 1, 1)
                cr.stroke()
            # zodiac signs list
            signs = [
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
            # draw glyph with offset & rotation
            for i, glyph in enumerate(signs):
                # compute angle for glyph
                angle = pi + i * segment_angle + offset
                # text position at outer edge
                x = cx + outer_radius * cos(angle)
                y = cy + outer_radius * sin(angle)
                # get text dimensions for centering
                xbearing, ybearing, tw, th, xandvance, yadvance = cr.text_extents(glyph)
                # save context before rotating
                cr.save()
                cr.translate(x, y)
                # rotate glyph
                cr.rotate(angle + pi / 2)
                # center glyph
                cr.move_to(-tw / 2, th / 2)
                cr.show_text(glyph)
                cr.restore()
            return
        # draw circle for other layers
        self.radius = base * 0.8
        cr.arc(cx, cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.7, 0.7, 0.8, 0.4)
        cr.fill_preserve()
        cr.set_source_rgba(0.3, 0.3, 0.4, 1)
        cr.stroke()
        # draw guests
        for obj in self.guests:
            obj.draw(cr, cx, cy, self.radius)
