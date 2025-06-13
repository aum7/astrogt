# ui/mainpanes/panechart/chartcircles.py
import cairo
from math import pi, cos, sin, radians
# background colors
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

    def draw(self, cr):
        """subclass must override this method"""
        raise NotImplementedError

    def set_custom_font(self, cr, font_size=16):
        cr.select_font_face(
            "VictorMonoLightAstro",
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL,
        )
        cr.set_font_size(font_size)

    def draw_rotated_text(self, cr, text, x, y, angle):
        _, _, tw, th, _, _ = cr.text_extents(text)
        cr.save()
        cr.translate(x, y)
        cr.rotate(angle + pi / 2)
        cr.move_to(-tw / 2, th / 2)
        cr.set_source_rgba(1, 1, 1, 1)
        cr.show_text(text)
        cr.new_path()
        cr.restore()


class CircleInfo(CircleBase):
    """show event 1 info in center circle"""

    def __init__(self, radius, cx, cy, event_data, chart_settings, extra_info):
        super().__init__(radius, cx, cy)
        self.font_size = 18
        self.event_data = event_data or {}
        self.chart_settings = chart_settings or {}
        self.extra_info = extra_info
        if not self.event_data:
            return
        # print(f"chartcircles : circleinfo : e1 data : {self.event_data}")
        # print(f"chartcircles : circleinfo : chartsettings : {self.chart_settings}")
        # print(f"chartcircles : circleinfo : house system : {self.house_system}")

    def draw(self, cr):
        """circle with info text"""
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.15, 0.15, 0.15, 1)
        cr.fill_preserve()
        # circle border
        cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(1)
        cr.stroke()
        cr.set_source_rgba(1, 1, 1, 1)
        self.set_custom_font(cr, self.font_size)
        # event 1 default chart info string (format)
        fmt_basic = self.chart_settings.get(
            "chart info string",
            "{name}\n{date}\n{wday} {time_short}\n{city} @ {country}\n{lat}\n{lon}",
        )
        # print(f"chartcircles : circleinfo : ... string : {fmt_basic}")
        fmt_extra = self.chart_settings.get(
            "chart info string extra",
            "{hsys} | {zod}\n{aynm}",
            # "chart info string extra", "{hsys} | {zod}\n{aynm} | {ayvl}"
        )
        # print(f"chartcircles : circleinfo : ... string extra : {fmt_extra}")
        try:
            info_text = (
                fmt_basic.format(**self.event_data)
                + "\n"  # + f"{self.house_system}"
                + fmt_extra.format(**self.extra_info)
            )
            print(f"chartcircles : circleinfo : infotext : {info_text}")
        except Exception as e:
            # fallback to default info string
            info_text = f"{self.event_data.get('name', '')}"
            print(f"chartcircles : circleinfo : exception reached\n\terror :\n\t{e}")
        lines = info_text.split("\n")
        line_spacing = self.font_size * 1.2
        total_height = (len(lines) - 1) * self.font_size
        # calculate start y to roughly center text block
        y = self.cy - total_height / 2
        for line in lines:
            _, _, tw, _, _, _ = cr.text_extents(line)
            x = self.cx - tw / 2
            cr.move_to(x, y)
            cr.show_text(line)
            cr.new_path()  # clear drawn path
            y += line_spacing


class CircleEvent(CircleBase):
    """objects / planets & house cusps"""

    def __init__(self, radius, cx, cy, guests, houses, ascmc):
        super().__init__(radius, cx, cy)
        self.guests = guests
        self.houses = houses
        self.ascmc = ascmc
        # radius factor for middle circle (0° latitude )
        self.middle_factor = 0.82
        # inner circle factor (min latitude value)
        self.inner_factor = 2 * self.middle_factor - 1.0
        if not self.guests or not self.houses or not self.ascmc:
            return
        # print(f"chartcircles : circleevent : guests : {[g.data for g in guests]}")
        # print(f"chartcircles : circleevent : self.houses : {self.houses}")
        # print(f"chartcircles : circleevent : ascmc : {ascmc}")

    def draw(self, cr):
        # main circle of event 1
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.2, 0.0, 0.0, 0.3)  # redish for fixed
        # cr.set_source_rgba(0.18, 0.15, 0.15, 1)  # redish for fixed
        cr.fill_preserve()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(1)
        cr.stroke()
        # middle circle = lat 0°
        cr.arc(self.cx, self.cy, self.radius * self.middle_factor, 0, 2 * pi)
        cr.set_source_rgba(1, 1, 1, 0.5)
        cr.set_line_width(1)
        cr.stroke()
        # houses
        for angle in self.houses:
            angle = pi - radians(angle)
            x1 = self.cx + self.radius * 0.5 * cos(angle)
            y1 = self.cy + self.radius * 0.5 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 0.3)
            cr.stroke()
        # ascendant & midheaven
        if self.ascmc:
            radius_factor = 1.0
            ascendant = self.ascmc[0]
            midheaven = self.ascmc[1]
            marker_size = self.radius * 0.03
            # ascendant
            asc_angle = pi - radians(ascendant)
            asc_x = self.cx + self.radius * radius_factor * cos(asc_angle)
            asc_y = self.cy + self.radius * radius_factor * sin(asc_angle)
            # marker for ascendant : triangle
            cr.save()
            cr.set_source_rgba(1, 1, 1, 1)
            cr.translate(asc_x, asc_y)
            cr.rotate(asc_angle + pi / 2)
            cr.move_to(0, marker_size)
            cr.line_to(marker_size, -marker_size / 2)
            cr.line_to(-marker_size, -marker_size / 2)
            cr.close_path()
            cr.fill()
            cr.restore()
            # descendant
            dsc_angle = asc_angle + pi
            dsc_x = self.cx + self.radius * radius_factor * cos(dsc_angle)
            dsc_y = self.cy + self.radius * radius_factor * sin(dsc_angle)
            # marker for descendant : triangle black
            cr.save()
            cr.set_source_rgba(0, 0, 0, 1)
            cr.translate(dsc_x, dsc_y)
            cr.rotate(dsc_angle + pi / 2)
            cr.move_to(0, marker_size)
            cr.line_to(marker_size, -marker_size / 2)
            cr.line_to(-marker_size, -marker_size / 2)
            cr.close_path()
            cr.fill()
            cr.restore()
            # midheaven (zenith)
            mc_angle = pi - radians(midheaven)
            mc_x = self.cx + self.radius * radius_factor * cos(mc_angle)
            mc_y = self.cy + self.radius * radius_factor * sin(mc_angle)
            # marker for midheaven : rotated square (diamond)
            cr.save()
            cr.set_source_rgba(1, 1, 1, 1)
            cr.translate(mc_x, mc_y)
            cr.rotate(mc_angle + pi / 2)
            cr.move_to(0, -marker_size)
            cr.line_to(marker_size, 0)
            cr.line_to(0, marker_size)
            cr.line_to(-marker_size, 0)
            cr.close_path()
            cr.fill()
            cr.restore()
            # nadir
            ic_angle = mc_angle + pi
            ic_x = self.cx + self.radius * radius_factor * cos(ic_angle)
            ic_y = self.cy + self.radius * radius_factor * sin(ic_angle)
            # marker for nadir : rotated square black
            cr.save()
            cr.set_source_rgba(0, 0, 0, 1)
            cr.translate(ic_x, ic_y)
            cr.rotate(ic_angle + pi / 2)
            cr.move_to(0, -marker_size)
            cr.line_to(marker_size, 0)
            cr.line_to(0, marker_size)
            cr.line_to(-marker_size, 0)
            cr.close_path()
            cr.fill()
            cr.restore()
        # guests with adjusted radius based on latitude
        for guest in self.guests:
            lat = guest.data.get("lat", 0)
            name = guest.data.get("name", "").lower()
            # sun always 0 lat
            if name == "su":
                factor = self.middle_factor
            # pluto has max lat range of them all
            elif name == "pl":
                max_val = 18.0
                if lat >= 0:
                    factor = self.middle_factor + (lat / max_val) * (
                        1.0 - self.middle_factor
                    )
                else:
                    factor = self.middle_factor + (lat / max_val) * (
                        self.middle_factor - self.inner_factor
                    )
            # other planets
            else:
                max_val = 8.0
                if lat >= 0:
                    factor = self.middle_factor + (lat / max_val) * (
                        1.0 - self.middle_factor
                    )
                else:
                    factor = self.middle_factor + (lat / max_val) * (
                        self.middle_factor - self.inner_factor
                    )
            # compute object drawing radius
            obj_radius = self.radius * factor
            guest.draw(cr, self.cx, self.cy, obj_radius)


class CircleSigns(CircleBase):
    """12 astrological signs"""

    def __init__(self, radius, cx, cy):
        super().__init__(radius, cx, cy)
        self.font_size = 18
        self.signs = [
            "\u0192",  # 01 aries
            "\u0193",  # 02
            "\u0194",  # 03
            "\u0195",  # 04
            "\u0196",  # 05
            "\u0197",  # 06
            "\u0198",  # 07
            "\u0199",  # 08
            "\u019a",  # 09
            "\u019b",  # 10
            "\u019c",  # 11
            "\u019d",  # 12 pisces
        ]

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.5, 0.5, 0.5, 0)  # todo set alpha
        cr.fill_preserve()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(1)
        cr.stroke()
        segment_angle = 2 * pi / 12
        offset = segment_angle / 2
        # sign borders
        for j in range(12):
            angle = pi - j * segment_angle  # start at left
            x1 = self.cx + self.radius * 0.84 * cos(angle)
            y1 = self.cy + self.radius * 0.84 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.set_line_width(1)
            cr.stroke()
        # glyphs
        self.set_custom_font(cr, self.font_size)
        for i, glyph in enumerate(self.signs):
            angle = pi - i * segment_angle - offset
            x = self.cx + self.radius * 0.92 * cos(angle)
            y = self.cy + self.radius * 0.92 * sin(angle)
            self.draw_rotated_text(cr, glyph, x, y, angle)


# additional optional circles : varga, naksatras
# then event 2 circles
