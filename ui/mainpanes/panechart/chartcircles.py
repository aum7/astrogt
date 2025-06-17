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

    def __init__(self, radius, cx, cy):
        self.radius = radius
        self.cx = cx
        self.cy = cy

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


# circles in order from central to outer-most
class CircleInfo(CircleBase):
    """show event 1 info in center circle"""

    def __init__(self, notify, radius, cx, cy, chart_settings, event_data, extra_info):
        super().__init__(radius, cx, cy)
        self.notify = notify
        self.font_size = 18
        self.event_data = event_data or {}
        self.chart_settings = chart_settings or {}
        self.extra_info = extra_info
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
        # avoid terminal error if no data
        if not self.event_data:
            return
        self.set_custom_font(cr, self.font_size)
        # event 1 default chart info string (format)
        fmt_basic = self.chart_settings.get(
            "chart info string",
            "{name}\n{date}\n{wday} {time_short}\n{city} @ {country}\n{lat}\n{lon}",
        )
        fmt_extra = self.chart_settings.get(
            "chart info string extra",
            "{hsys} | {zod}\n{aynm}",
            # "chart info string extra", "{hsys} | {zod}\n{aynm} | {ayvl}"
        )
        # convert raw newline into actual newline
        fmt_basic = fmt_basic.replace(r"\n", "\n")
        fmt_extra = fmt_extra.replace(r"\n", "\n")
        try:
            info_text = (
                fmt_basic.format(**self.event_data)
                + "\n"
                + fmt_extra.format(**self.extra_info)
            )
            self.notify.debug(
                f"circleinfo : infotext : {info_text}",
                source="chartcircles",
                route=["none"],
            )
        except Exception as e:
            # fallback to default info string
            info_text = f"{self.event_data.get('name', '')}"
            self.notify.error(
                f"circleinfo : error :\n\t{e}",
                source="chartcircles",
                route=["terminal"],
            )
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

    def __init__(self, radius, cx, cy, guests, houses, ascmc, chart_settings):
        super().__init__(radius, cx, cy)
        self.guests = guests
        self.houses = houses
        self.ascmc = ascmc
        self.chart_settings = chart_settings
        # radius factor for middle circle (0° latitude )
        self.middle_factor = 0.82
        # inner circle factor (min latitude value)
        self.inner_factor = 2 * self.middle_factor - 1.0
        # print(f"chartcircles : circleevent : guests : {[g.data for g in guests]}")
        # print(f"chartcircles : circleevent : self.houses : {self.houses}")
        # print(f"chartcircles : circleevent : ascmc : {ascmc}")
        # unicode glyphs from victormonolightastro.ttf font
        self.glyphs = {
            "su": "\u0180",
            "mo": "\u0181",
            "me": "\u0182",
            "ve": "\u0183",
            "ma": "\u0184",
            "ju": "\u0185",
            "sa": "\u0186",
            "ur": "\u0187",
            "ne": "\u0188",
            "pl": "\u0189",
            "ra": "\u018e"
            if not self.chart_settings.get("mean node", False)
            else "\u018c",  # rahu true else mean
        }
        self.glyphs_extra = {
            "fr1": "\u018b",  # fortuna
            "fr2": "\u01e2",  # fortuna alter
            "syz": "\u01d8",  # syzygy / prenatal lunation : jin-jang
            "syn": "\u01ec",  # syzygy : conjunction : new moon
            "syf": "\u01ed",  # syzygy : opposition : full moon
        }
        if not self.guests or not self.houses or not self.ascmc:
            return

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
        def draw_triangle(cr, size):
            # triangle shape: ascendant/descendant marker
            cr.move_to(0, size)
            cr.line_to(size, -size / 2)
            cr.line_to(-size, -size / 2)
            cr.close_path()
            cr.fill()

        def draw_diamond(cr, size):
            # diamond shape: midheaven/nadir marker
            cr.move_to(0, -size)
            cr.line_to(size, 0)
            cr.line_to(0, size)
            cr.line_to(-size, 0)
            cr.close_path()
            cr.fill()

        def draw_marker(cr, cx, cy, angle, size, color, shape_func):
            # generic marker-drawing helper
            cr.save()
            cr.set_source_rgba(*color)
            cr.translate(cx, cy)
            cr.rotate(angle + pi / 2)
            shape_func(cr, size)
            cr.restore()

        if self.ascmc:
            radius_factor = 1.0
            ascendant = self.ascmc[0]
            midheaven = self.ascmc[1]
            marker_size = self.radius * 0.03
            # compute positions based on angle transformations
            asc_angle = pi - radians(ascendant)
            asc_x = self.cx + self.radius * radius_factor * cos(asc_angle)
            asc_y = self.cy + self.radius * radius_factor * sin(asc_angle)
            # draw ascendant marker (white triangle)
            draw_marker(
                cr, asc_x, asc_y, asc_angle, marker_size, (1, 1, 1, 1), draw_triangle
            )
            dsc_angle = asc_angle + pi
            dsc_x = self.cx + self.radius * radius_factor * cos(dsc_angle)
            dsc_y = self.cy + self.radius * radius_factor * sin(dsc_angle)
            # draw descendant marker (black triangle)
            draw_marker(
                cr, dsc_x, dsc_y, dsc_angle, marker_size, (0, 0, 0, 1), draw_triangle
            )
            mc_angle = pi - radians(midheaven)
            mc_x = self.cx + self.radius * radius_factor * cos(mc_angle)
            mc_y = self.cy + self.radius * radius_factor * sin(mc_angle)
            # draw midheaven marker (white diamond)
            draw_marker(
                cr, mc_x, mc_y, mc_angle, marker_size, (1, 1, 1, 1), draw_diamond
            )
            ic_angle = mc_angle + pi
            ic_x = self.cx + self.radius * radius_factor * cos(ic_angle)
            ic_y = self.cy + self.radius * radius_factor * sin(ic_angle)
            # draw nadir marker (black diamond)
            draw_marker(
                cr, ic_x, ic_y, ic_angle, marker_size, (0, 0, 0, 1), draw_diamond
            )
        # if self.ascmc:
        #     radius_factor = 1.0
        #     ascendant = self.ascmc[0]
        #     midheaven = self.ascmc[1]
        #     marker_size = self.radius * 0.03
        #     # ascendant
        #     asc_angle = pi - radians(ascendant)
        #     asc_x = self.cx + self.radius * radius_factor * cos(asc_angle)
        #     asc_y = self.cy + self.radius * radius_factor * sin(asc_angle)
        #     # marker for ascendant : triangle
        #     cr.save()
        #     cr.set_source_rgba(1, 1, 1, 1)
        #     cr.translate(asc_x, asc_y)
        #     cr.rotate(asc_angle + pi / 2)
        #     cr.move_to(0, marker_size)
        #     cr.line_to(marker_size, -marker_size / 2)
        #     cr.line_to(-marker_size, -marker_size / 2)
        #     cr.close_path()
        #     cr.fill()
        #     cr.restore()
        #     # descendant
        #     dsc_angle = asc_angle + pi
        #     dsc_x = self.cx + self.radius * radius_factor * cos(dsc_angle)
        #     dsc_y = self.cy + self.radius * radius_factor * sin(dsc_angle)
        #     # marker for descendant : triangle black
        #     cr.save()
        #     cr.set_source_rgba(0, 0, 0, 1)
        #     cr.translate(dsc_x, dsc_y)
        #     cr.rotate(dsc_angle + pi / 2)
        #     cr.move_to(0, marker_size)
        #     cr.line_to(marker_size, -marker_size / 2)
        #     cr.line_to(-marker_size, -marker_size / 2)
        #     cr.close_path()
        #     cr.fill()
        #     cr.restore()
        #     # midheaven (zenith)
        #     mc_angle = pi - radians(midheaven)
        #     mc_x = self.cx + self.radius * radius_factor * cos(mc_angle)
        #     mc_y = self.cy + self.radius * radius_factor * sin(mc_angle)
        #     # marker for midheaven : rotated square (diamond)
        #     cr.save()
        #     cr.set_source_rgba(1, 1, 1, 1)
        #     cr.translate(mc_x, mc_y)
        #     cr.rotate(mc_angle + pi / 2)
        #     cr.move_to(0, -marker_size)
        #     cr.line_to(marker_size, 0)
        #     cr.line_to(0, marker_size)
        #     cr.line_to(-marker_size, 0)
        #     cr.close_path()
        #     cr.fill()
        #     cr.restore()
        #     # nadir
        #     ic_angle = mc_angle + pi
        #     ic_x = self.cx + self.radius * radius_factor * cos(ic_angle)
        #     ic_y = self.cy + self.radius * radius_factor * sin(ic_angle)
        #     # marker for nadir : rotated square black
        #     cr.save()
        #     cr.set_source_rgba(0, 0, 0, 1)
        #     cr.translate(ic_x, ic_y)
        #     cr.rotate(ic_angle + pi / 2)
        #     cr.move_to(0, -marker_size)
        #     cr.line_to(marker_size, 0)
        #     cr.line_to(0, marker_size)
        #     cr.line_to(-marker_size, 0)
        #     cr.close_path()
        #     cr.fill()
        #     cr.restore()
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
            # if 'enable glyphs' > draw glyphs
            if self.chart_settings.get("enable glyphs", True):
                glyph = self.glyphs.get(name, "")
                # glyph_radius = self.radius
                if glyph:
                    angle = pi - radians(guest.data.get("lon", 0))
                    x = self.cx + obj_radius * cos(angle)
                    y = self.cy + obj_radius * sin(angle)
                    # x = self.cx + glyph_radius * cos(angle)
                    # y = self.cy + glyph_radius * sin(angle)
                    cr.save()
                    if self.chart_settings.get("fixed asc", False) and self.ascmc:
                        cr.translate(x, y)
                        cr.rotate(-radians(self.ascmc[0]))
                        te = cr.text_extents(glyph)
                        tx = -(te.width / 2 + te.x_bearing)
                        ty = -(te.height / 2 + te.y_bearing)
                        cr.set_source_rgba(0, 0, 0, 1)
                        cr.move_to(tx, ty)
                        cr.show_text(glyph)
                        cr.new_path()
                    else:
                        te = cr.text_extents(glyph)
                        tx = x - (te.width / 2 + te.x_bearing)
                        ty = y - (te.height / 2 + te.y_bearing)
                        cr.set_source_rgba(0, 0, 0, 1)
                        # cr.set_source_rgba(1, 1, 1, 1)
                        cr.move_to(tx, ty)
                        cr.show_text(glyph)
                        cr.new_path()
                    cr.restore()


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


class CircleNaksatras(CircleBase):
    """draw 27 or 28 naksatras ring"""

    def __init__(self, radius, cx, cy, naks_num, first_nak, font_size):
        super().__init__(radius, cx, cy)
        self.naks_num = naks_num
        self.first_nak = first_nak
        self.font_size = font_size

    def draw(self, cr):
        """draw outer circle"""
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.2, 0.2, 0.2, 0.3)
        cr.stroke_preserve()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(1)
        cr.stroke()
        # divide circle into segments
        seg_angle = 2 * pi / self.naks_num
        for i in range(self.naks_num):
            angle = pi - (i * seg_angle)
            x = self.cx + self.radius * cos(angle)
            y = self.cy + self.radius * sin(angle)
            cr.move_to(self.cx, self.cy)
            cr.line_to(x, y)
            cr.stroke()
        # labels
        self.set_custom_font(cr, self.font_size)
        for i in range(self.naks_num):
            angle = pi - ((i + 0.5) * seg_angle)
            label = str((self.first_nak + i - 1) % self.naks_num + 1)
            te = cr.text_extents(label)
            x = self.cx + (self.radius * 0.85) * cos(angle) - te.width / 2
            y = self.cy + (self.radius * 0.85) * sin(angle) + te.height / 2
            cr.move_to(x, y)
            cr.show_text(label)
            cr.new_path()


class CircleHarmonics(CircleBase):
    """draw harmonics / divisions ring"""

    def __init__(self, notify, radius, cx, cy, divisions, font_size=14):
        super().__init__(radius, cx, cy)
        self.notify = notify
        self.divisions = divisions
        self.font_size = font_size

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.3, 0.3, 0.5, 0.3)
        cr.stroke_preserve()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.stroke()
        # draw divisions for selected harmonic
        for d in self.divisions:
            if d == 0:
                self.notify.info(
                    "division 0 : nothing to draw; skipping ...",
                    source="astrochart",
                    route=["terminal"],
                )
                continue
            seg_angle = 2 * pi / d
            # draw lines
            for i in range(d):
                angle = pi - (i * seg_angle)
                x = self.cx + self.radius * cos(angle)
                y = self.cy + self.radius * sin(angle)
                cr.move_to(self.cx, self.cy)
                cr.line_to(x, y)
                cr.stroke()
            # labels


# additional optional circles : varga, naksatras
# then event 2 circles
