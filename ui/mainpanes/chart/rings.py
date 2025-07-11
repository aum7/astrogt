# ui/mainpanes/chart/rings.py
# ui/fonts/victor/victormonolightastro.ttf
# ruff: noqa: E402
import cairo
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from math import pi, cos, sin, radians
from ui.fonts.glyphs import get_glyph, SIGNS
from sweph.constants import TERMS
from ui.mainpanes.chart.astroobject import AstroObject


class RingBase:
    # base class to handle common attributes
    def __init__(self, radius, cx, cy, chart_settings=None):
        self.radius = radius
        self.cx = cx
        self.cy = cy
        self.chart_settings = chart_settings or {}

    def draw(self, cr):
        """subclass must override this method"""
        raise NotImplementedError

    # ascendant & midheaven
    def draw_triangle(self, cr, size):
        # triangle shape: ascendant/descendant marker
        cr.move_to(0, size)
        cr.line_to(size, -size / 2)
        cr.line_to(-size, -size / 2)
        cr.close_path()
        cr.fill()

    def draw_diamond(self, cr, size):
        # diamond shape: midheaven/nadir marker
        cr.move_to(0, -size)
        cr.line_to(size, 0)
        cr.line_to(0, size)
        cr.line_to(-size, 0)
        cr.close_path()
        cr.fill()

    def draw_marker(self, cr, cx, cy, angle, size, color, shape_func):
        # generic marker-drawing helper
        cr.save()
        cr.set_source_rgba(*color)
        cr.translate(cx, cy)
        cr.rotate(angle + pi / 2)
        shape_func(cr, size)
        cr.restore()

    def set_custom_font(self, cr, font_size=16):
        cr.select_font_face(
            "VictorMonoLightAstro",
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL,
        )
        cr.set_font_size(font_size)

    def draw_rotated_text(self, cr, text, x, y, angle, color=(1, 1, 1, 1)):
        _, _, tw, th, _, _ = cr.text_extents(text)
        cr.save()
        cr.translate(x, y)
        cr.rotate(angle + pi / 2)
        cr.move_to(-tw / 2, th / 2)
        cr.set_source_rgba(*color)
        cr.show_text(text)
        cr.new_path()
        cr.restore()


# rings in order from central to outer-most
class Info(RingBase):
    # show event 1 info in center circle
    def __init__(
        self,
        notify,
        radius,
        cx,
        cy,
        font_size,
        chart_settings,
        # radius_dict,
        event_data,
        extra_info,
    ):
        super().__init__(radius, cx, cy, chart_settings)
        self.notify = notify
        self.font_size = font_size
        self.event_data = event_data or {}
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


class Event(RingBase):
    # objects / planets & house cusps
    def __init__(
        self,
        radius,
        cx,
        cy,
        font_size,
        guests,
        houses,
        ascmc,
        chart_settings,
        radius_dict,
    ):
        super().__init__(radius, cx, cy, chart_settings)
        self.guests = guests
        self.houses = houses
        self.ascmc = ascmc
        self.font_size = font_size
        # radius factor for middle circle (0° latitude )
        self.event = radius_dict.get("event", "")
        self.info = radius_dict.get("info", "")
        self.mid_ring = (self.event + self.info) / 2
        # print(f"chartcircles : circleevent : guests : {[g.data for g in guests]}")
        # print(f"chartcircles : circleevent : self.houses : {self.houses}")
        # print(f"chartcircles : circleevent : ascmc : {ascmc}")
        if not self.guests or not self.houses or not self.ascmc:
            return

    def draw(self, cr):
        # main circle of event 1
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.0776, 0.0, 0.0, 1.0)  # redish for fixed
        cr.fill_preserve()
        cr.set_source_rgba(1, 1, 1, 0.7)
        cr.set_line_width(1)
        cr.stroke()
        # middle circle = lat 0°
        cr.arc(self.cx, self.cy, self.mid_ring, 0, 2 * pi)
        cr.set_source_rgba(1, 1, 1, 0.5)
        cr.set_line_width(1)
        cr.stroke()
        # houses (match inner radius with outer radius of previous circle)
        # ie 0.4 is from chartcircle.py > circle_info
        for angle in self.houses:
            angle = pi - radians(angle)
            x1 = self.cx + self.radius * 0.4 * cos(angle)
            y1 = self.cy + self.radius * 0.4 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 0.3)
            cr.stroke()

        if self.ascmc:
            radius_factor = 1.0
            ascendant = self.ascmc[0]
            midheaven = self.ascmc[1]
            marker_size = 8.2  # self.radius * 0.03
            # compute positions based on angle transformations
            asc_angle = pi - radians(ascendant)
            asc_x = self.cx + self.radius * radius_factor * cos(asc_angle)
            asc_y = self.cy + self.radius * radius_factor * sin(asc_angle)
            # draw ascendant marker (white triangle)
            self.draw_marker(
                cr,
                asc_x,
                asc_y,
                asc_angle,
                marker_size,
                (1, 1, 1, 1),
                self.draw_triangle,
            )
            dsc_angle = asc_angle + pi
            dsc_x = self.cx + self.radius * radius_factor * cos(dsc_angle)
            dsc_y = self.cy + self.radius * radius_factor * sin(dsc_angle)
            # draw descendant marker (black triangle)
            self.draw_marker(
                cr,
                dsc_x,
                dsc_y,
                dsc_angle,
                marker_size,
                (0.1, 0.1, 0.1, 1),
                self.draw_triangle,
            )
            mc_angle = pi - radians(midheaven)
            mc_x = self.cx + self.radius * radius_factor * cos(mc_angle)
            mc_y = self.cy + self.radius * radius_factor * sin(mc_angle)
            # draw midheaven marker (white diamond)
            self.draw_marker(
                cr,
                mc_x,
                mc_y,
                mc_angle,
                marker_size,
                (1, 1, 1, 1),
                self.draw_diamond,
            )
            ic_angle = mc_angle + pi
            ic_x = self.cx + self.radius * radius_factor * cos(ic_angle)
            ic_y = self.cy + self.radius * radius_factor * sin(ic_angle)
            # draw nadir marker (black diamond)
            self.draw_marker(
                cr,
                ic_x,
                ic_y,
                ic_angle,
                marker_size,
                (0.1, 0.1, 0.1, 1),
                self.draw_diamond,
            )
        # guests with adjusted radius based on latitude
        for guest in self.guests:
            lat = guest.data.get("lat", 0)
            name = guest.data.get("name", "").lower()
            # sun always 0 lat
            if name == "su":
                # factor = self.mid_ring
                radius = self.mid_ring
            # pluto has max lat range of them all
            elif name == "pl":
                max_val = 18.0
                ratio = lat / max_val
                if lat >= 0:
                    radius = self.mid_ring + (self.event - self.mid_ring) * ratio

                else:
                    radius = self.mid_ring + (self.info - self.mid_ring) * (-ratio)
            # other planets
            else:
                max_val = 8.0
                ratio = lat / max_val
                if lat >= 0:
                    radius = self.mid_ring + (self.event - self.mid_ring) * ratio
                else:
                    radius = self.mid_ring + (self.info - self.mid_ring) * (-ratio)
            # compute object drawing radius
            # obj_radius = self.radius * factor
            guest.draw(cr, self.cx, self.cy, radius, self.font_size, source="event")
            # if 'enable glyphs' > draw glyphs
            use_mean_node = self.chart_settings.get("mean node", False)
            if self.chart_settings.get("enable glyphs", True):
                glyph = get_glyph(name, use_mean_node)
                if glyph:
                    angle = pi - radians(guest.data.get("lon", 0))
                    x = self.cx + radius * cos(angle)
                    y = self.cy + radius * sin(angle)
                    cr.save()
                    # rotate chart so ascendant is horizon
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


class Signs(RingBase):
    # 12 astrological signs
    def __init__(self, radius, cx, cy, font_size, stars):
        super().__init__(radius, cx, cy)
        self.font_size = font_size
        self.stars = stars
        # print(f"signs : stars : {self.stars}")

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.15, 0.15, 0.15, 1)  # todo set alpha
        cr.fill_preserve()
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        # cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(1)
        cr.stroke()
        segment_angle = 2 * pi / 12
        offset = segment_angle / 2
        # sign borders
        for j in range(12):
            angle = pi - j * segment_angle  # start at left
            x1 = self.cx + self.radius * 0.92 * cos(angle)
            y1 = self.cy + self.radius * 0.92 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 0.5)
            cr.set_line_width(1)
            cr.stroke()
        # glyphs
        self.set_custom_font(cr, self.font_size)
        for i, (sign, (glyph, element, mode)) in enumerate(SIGNS.items()):
            angle = pi - i * segment_angle - offset
            x = self.cx + self.radius * 0.96 * cos(angle)
            y = self.cy + self.radius * 0.96 * sin(angle)
            self.draw_rotated_text(cr, glyph, x, y, angle)
        self.set_custom_font(cr, self.font_size * 1.2)
        for name, (lon, _) in self.stars.items():
            angle = pi - radians(lon)
            x = self.cx + self.radius * 0.97 * cos(angle)
            y = self.cy + self.radius * 0.97 * sin(angle)
            self.draw_rotated_text(cr, "*", x, y, angle, color=(1, 0.9, 0.2, 1))


class Naksatras(RingBase):
    # draw 27 or 28 naksatras ring
    def __init__(self, radius, cx, cy, naks_num, first_nak, font_size, radius_dict):
        super().__init__(radius, cx, cy)
        self.naks_num = naks_num
        self.first_nak = first_nak
        self.font_size = font_size
        self.mid_ring = (
            radius_dict.get("naksatras", "") + radius_dict.get("signs", "")
        ) / 2
        # print(f"midring : {self.mid_ring}")

    def draw(self, cr):
        """draw outer circle"""
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        cr.set_source_rgba(0.2, 0.2, 0.2, 1)
        cr.fill_preserve()
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        # cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(1)
        cr.stroke()
        # divide circle into segments
        cr.set_source_rgba(0.9, 0.9, 0.9, 0.7)
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
            x = self.cx + self.mid_ring * cos(angle)
            y = self.cy + self.mid_ring * sin(angle)
            cr.save()
            cr.translate(x, y)
            cr.rotate(angle + pi / 2)
            cr.move_to(-te.width / 2, te.height / 2)
            cr.show_text(label)
            cr.restore()
            cr.new_path()


class Harmonic(RingBase):
    # draw harmonic (aka division) ring
    def __init__(self, notify, radius, cx, cy, division, radius_dict, font_size=14):
        super().__init__(radius, cx, cy)
        self.notify = notify
        self.division = division
        self.font_size = font_size
        # print(f"harmonic : radlist : {radius_dict}")
        keys = list(radius_dict.keys())
        index = ""
        try:
            index = keys.index("harmonic")
        except ValueError:
            raise ValueError("missing 'harmonic' key in radiusdict")
        if index < len(keys) - 1:
            next_key = keys[index + 1]
            next_val = radius_dict[next_key]
        else:
            # fallback
            next_val = radius_dict["harmonic"]
        if radius_dict:
            self.mid_ring = (radius_dict["harmonic"] + next_val) / 2

    def draw(self, cr):
        # draw circle
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        # background color : dark
        cr.set_source_rgba(0.1, 0.1, 0.1, 1)
        cr.fill_preserve()
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        cr.set_line_width(1)
        cr.stroke()
        # (egyptian) terms (aka bounds) if division 1
        if self.division == 1:
            terms_sorted = sorted(TERMS.items())
            terms_num = len(terms_sorted)
            self.set_custom_font(cr, self.font_size)
            for i, (deg, ruler) in enumerate(terms_sorted):
                # start angle
                angle = pi - (deg * pi / 180)
                x = self.cx + self.radius * cos(angle)
                y = self.cy + self.radius * sin(angle)
                cr.move_to(self.cx, self.cy)
                cr.line_to(x, y)
                cr.set_source_rgba(1, 1, 1, 0.5)
                cr.stroke()
                # glyphs : next border for mid term position
                if i == terms_num - 1:
                    next_deg = 360
                else:
                    next_deg = terms_sorted[(i + 1) % terms_num][0]
                angle_next = pi - (next_deg * pi / 180)
                # handle wrap-around
                mid_angle = (angle + angle_next) / 2
                # position glyph at ring middle
                glyph_fix = 1.008
                xg = self.cx + self.mid_ring * glyph_fix * cos(mid_angle)
                yg = self.cy + self.mid_ring * glyph_fix * sin(mid_angle)
                glyph = get_glyph(ruler, False)
                self.draw_rotated_text(cr, glyph, xg, yg, mid_angle)
        else:
            # draw divisions for selected harmonic
            total_divisions = 12 * self.division
            seg_angle = 2 * pi / total_divisions
            # draw lines
            for i in range(total_divisions):
                angle = pi - (i * seg_angle)
                x = self.cx + self.radius * cos(angle)
                y = self.cy + self.radius * sin(angle)
                cr.move_to(self.cx, self.cy)
                cr.line_to(x, y)
                cr.stroke()
            # labels
            self.set_custom_font(cr, self.font_size)
            for i in range(total_divisions):
                angle = pi - ((i + 0.5) * seg_angle)
                sign = (i + 1) % 12
                label = str(12 if sign == 0 else sign)
                # te = cr.text_extents(label)
                x = self.cx + self.radius * 0.97 * cos(angle)
                y = self.cy + self.radius * 0.97 * sin(angle)
                self.draw_rotated_text(cr, label, x, y, angle)


# event 2 circles (inside-to-outside) : progress, returns, transits
class P1Progress(RingBase):
    # p1 progression
    def __init__(self, radius, cx, cy, font_size, chart_settings, p1_pos, radius_dict):
        super().__init__(radius, cx, cy, chart_settings)
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        self.font_size = font_size
        self.p1_pos = p1_pos
        # get ring radius
        keys = list(radius_dict.keys())
        index = ""
        try:
            index = keys.index("p1 progress")
        except ValueError:
            raise ValueError("missing 'p1 progress' key in radiusdict")
        if index < len(keys) - 1:
            next_key = keys[index + 1]
            next_val = radius_dict[next_key]
        else:
            # fallback
            next_val = radius_dict["p1 progress"]
        if radius_dict:
            self.mid_ring = (radius_dict["p1 progress"] + next_val) / 2
            self.ring = radius_dict.get("p1 progress", "/")
            self.before_ring = next_val
            # msg += (
            #     f"p1 midring : {self.mid_ring} | radius : {self.ring} | radinext : {next_val}"
            # )
        self.guests = []
        try:
            if self.p1_pos:
                # create astroobject instance for drawing
                self.guests = [
                    self.create_astro_obj(obj)
                    for obj in self.p1_pos
                    if isinstance(obj, dict)
                ]
        except Exception as e:
            self.notify.error(
                f"no p1 positions\n\terror :\n\t{e}",
                source="rings",
                route=["terminal", "user"],
            )

    def create_astro_obj(self, obj):
        p1_obj_data = obj.copy()
        return AstroObject(p1_obj_data)

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        # blueish
        cr.set_source_rgba(0.0471, 0.1059, 0.1843, 1.0)
        cr.fill_preserve()
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        # cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(1)
        cr.stroke()
        segment_angle = 2 * pi / 12
        # sign borders
        for j in range(12):
            angle = pi - j * segment_angle  # start at left
            x1 = self.cx + self.radius * 0.9 * cos(angle)
            y1 = self.cy + self.radius * 0.9 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            # fade sign segments
            cr.set_source_rgba(1, 1, 1, 0.5)
            cr.set_line_width(1)
            cr.stroke()
        for guest in self.guests:
            angle = pi - radians(guest.data.get("lon"))
            x = self.cx + self.mid_ring * cos(angle)
            y = self.cy + self.mid_ring * sin(angle)
            marker_size = 9.2
            # draw triangle for ascendant
            if guest.data.get("name") == "asc":
                self.draw_marker(
                    cr,
                    x,
                    y,
                    angle,
                    marker_size,
                    (0, 0.309, 0.721, 1),
                    self.draw_triangle,
                )
            # draw diamond for midheaven
            elif guest.data.get("name") == "mc":
                self.draw_marker(
                    cr,
                    x,
                    y,
                    angle,
                    marker_size,
                    (0, 0.309, 0.721, 1),
                    # (1, 1, 1, 1),
                    self.draw_diamond,
                )
            else:
                guest.draw(
                    cr, self.cx, self.cy, self.mid_ring, obj_scale=12.0, source="p1"
                )


class P3Progress(RingBase):
    # p3 progression
    def __init__(self, radius, cx, cy, font_size, p3_pos, radius_dict):
        super().__init__(radius, cx, cy)
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        self.font_size = font_size
        self.p3_pos = p3_pos
        # print(f"rings : p3pos : {self.p3_pos}")
        # get ring radius
        keys = list(radius_dict.keys())
        index = ""
        try:
            index = keys.index("p3 progress")
        except ValueError:
            raise ValueError("missing 'p3 progress' key in radiusdict")
        if index < len(keys) - 1:
            next_key = keys[index + 1]
            next_val = radius_dict[next_key]
        else:
            # fallback
            next_val = radius_dict["p3 progress"]
        if radius_dict:
            self.mid_ring = (radius_dict["p3 progress"] + next_val) / 2
            self.ring = radius_dict.get("p3 progress", "/")
            self.before_ring = next_val
            # msg += (
            #     f"p3 midring : {self.mid_ring} | radius : {self.ring} | radinext : {next_val}"
            # )
        self.guests = []
        try:
            if self.p3_pos:
                # create astroobject instance for drawing
                self.guests = [
                    self.create_astro_obj(obj)
                    for obj in self.p3_pos
                    if isinstance(obj, dict)
                ]
        except Exception as e:
            self.notify.error(
                f"no p3 positions\n\terror :\n\t{e}",
                source="rings",
                route=["terminal", "user"],
            )

    def create_astro_obj(self, obj):
        p3_obj_data = obj.copy()
        return AstroObject(p3_obj_data)

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        # blueish
        cr.set_source_rgba(0.0353, 0.0863, 0.1490, 1)
        # cr.set_source_rgba(0.0471, 0.1059, 0.1843, 1.0)
        cr.fill_preserve()
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.5)
        # cr.set_source_rgba(1, 1, 1, 1)
        cr.set_line_width(1)
        cr.stroke()
        segment_angle = 2 * pi / 12
        # sign borders
        for j in range(12):
            angle = pi - j * segment_angle  # start at left
            x1 = self.cx + self.radius * 0.9 * cos(angle)
            y1 = self.cy + self.radius * 0.9 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            # fade sign segments
            cr.set_source_rgba(1, 1, 1, 0.5)
            cr.set_line_width(1)
            cr.stroke()
        for guest in self.guests:
            angle = pi - radians(guest.data.get("lon"))
            x = self.cx + self.mid_ring * cos(angle)
            y = self.cy + self.mid_ring * sin(angle)
            marker_size = 9.2
            # draw triangle for ascendant
            if guest.data.get("name") == "asc":
                self.draw_marker(
                    cr,
                    x,
                    y,
                    angle,
                    marker_size,
                    (0, 0.159, 0.521, 1),
                    self.draw_triangle,
                )
            # draw diamond for midheaven
            elif guest.data.get("name") == "mc":
                self.draw_marker(
                    cr,
                    x,
                    y,
                    angle,
                    marker_size,
                    (0, 0.159, 0.521, 1),
                    self.draw_diamond,
                )
            else:
                guest.draw(
                    cr, self.cx, self.cy, self.mid_ring, obj_scale=12.0, source="p3"
                )


class SolarReturn(RingBase):
    # solar return
    def __init__(self, radius, cx, cy, font_size, sol_ret_data, radius_dict):
        super().__init__(radius, cx, cy)
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        self.font_size = font_size
        self.sol_ret_data = sol_ret_data
        # print(f"rings : solretdata : {self.sol_ret_data}")
        self.cusps = []
        # get ring radius
        keys = list(radius_dict.keys())
        index = ""
        try:
            index = keys.index("solar return")
        except ValueError:
            raise ValueError("missing 'solar return' key in radiusdict")
        if index < len(keys) - 1:
            next_key = keys[index + 1]
            next_val = radius_dict[next_key]
        else:
            # fallback
            next_val = radius_dict["solar return"]
        if radius_dict:
            self.mid_ring = (radius_dict["solar return"] + next_val) / 2
            self.ring = radius_dict.get("solar return", "/")
            self.before_ring = next_val
            # msg += (
            #     f"p1 midr : {self.mid_ring} | rad : {self.ring} | rdnext : {next_val}"
            # )
        # houses drawn 1st
        self.cusps = next(x for x in self.sol_ret_data if not isinstance(x, dict))
        # print(f"srrings : cusps :\n\t{self.cusps}")
        self.guests = []
        try:
            if self.sol_ret_data:
                # create astroobject instance for drawing
                self.guests = [
                    self.create_astro_obj(obj)
                    for obj in self.sol_ret_data
                    if isinstance(obj, dict)
                ]
        except Exception as e:
            self.notify.error(
                f"no solar return positions\n\terror :\n\t{e}",
                source="rings",
                route=["terminal", "user"],
            )

    def create_astro_obj(self, obj):
        sol_ret_obj_data = obj.copy()
        # p1_obj_data["lon"] = p1_obj_data.get("zpp", 0)
        return AstroObject(sol_ret_obj_data)

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        # blueish
        cr.set_source_rgba(0.1686, 0.1569, 0.0392, 1)
        cr.fill_preserve()
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        # cr.set_source_rgba(1, 1, 1, 0.7)
        cr.set_line_width(1)
        cr.stroke()
        # houses of e2 solar return
        for angle in self.cusps:
            angle = pi - radians(angle)
            x1 = self.cx + self.radius * 0.35 * cos(angle)
            y1 = self.cy + self.radius * 0.35 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_line_width(2)
            cr.set_source_rgba(1, 1, 0.6, 0.7)
            cr.stroke()
        segment_angle = 2 * pi / 12
        # sign borders
        for j in range(12):
            angle = pi - j * segment_angle  # start at left
            x1 = self.cx + self.radius * 0.9 * cos(angle)
            y1 = self.cy + self.radius * 0.9 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 0.7)
            cr.set_line_width(1)
            cr.stroke()
        for guest in self.guests:
            angle = pi - radians(guest.data.get("lon"))
            x = self.cx + self.mid_ring * cos(angle)
            y = self.cy + self.mid_ring * sin(angle)
            marker_size = 9.2
            # print(f"markersize : {marker_size}")
            # draw triangle for ascendant
            if guest.data.get("name") == "asc":
                self.draw_marker(
                    cr,
                    x,
                    y,
                    angle,
                    marker_size,
                    (0.6686, 0.6569, 0.5392, 1),
                    self.draw_triangle,
                )
            # draw diamond for midheaven
            elif guest.data.get("name") == "mc":
                self.draw_marker(
                    cr,
                    x,
                    y,
                    angle,
                    marker_size,
                    (0.6686, 0.6569, 0.5392, 1),
                    self.draw_diamond,
                )
            else:
                guest.draw(
                    cr,
                    self.cx,
                    self.cy,
                    self.mid_ring,
                    obj_scale=12.0,
                    source="solarreturn",
                )


class LunarReturn(RingBase):
    # lunar return
    def __init__(self, radius, cx, cy, font_size, lun_ret_data, radius_dict):
        super().__init__(radius, cx, cy)
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        self.font_size = font_size
        self.lun_ret_data = lun_ret_data
        self.cusps = []
        # get ring radius
        keys = list(radius_dict.keys())
        index = ""
        try:
            index = keys.index("lunar return")
        except ValueError:
            raise ValueError("missing 'lunar return' key in radiusdict")
        if index < len(keys) - 1:
            next_key = keys[index + 1]
            next_val = radius_dict[next_key]
        else:
            # fallback
            next_val = radius_dict["lunar return"]
        if radius_dict:
            self.mid_ring = (radius_dict["lunar return"] + next_val) / 2
            self.ring = radius_dict.get("lunar return", "/")
            self.before_ring = next_val
            # msg += (
            #     f"p1 midring : {self.mid_ring} | radius : {self.ring} | radinext : {next_val}"
            # )
        # houses drawn 1st
        self.cusps = next(x for x in self.lun_ret_data if not isinstance(x, dict))
        # print(f"srrings : cusps :\n\t{self.cusps}")
        self.guests = []
        try:
            if self.lun_ret_data:
                # create astroobject instance for drawing
                self.guests = [
                    self.create_astro_obj(obj)
                    for obj in self.lun_ret_data
                    if isinstance(obj, dict)
                ]
        except Exception as e:
            self.notify.error(
                f"no lunar return positions\n\terror :\n\t{e}",
                source="rings",
                route=["terminal", "user"],
            )

    def create_astro_obj(self, obj):
        sol_ret_obj_data = obj.copy()
        # p1_obj_data["lon"] = p1_obj_data.get("zpp", 0)
        return AstroObject(sol_ret_obj_data)

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        # blueish
        cr.set_source_rgba(0.1386, 0.1269, 0.0092, 1)
        cr.fill_preserve()
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        # cr.set_source_rgba(1, 1, 1, 0.7)
        cr.set_line_width(1)
        cr.stroke()
        # houses of e2 lunar return
        for angle in self.cusps:
            angle = pi - radians(angle)
            x1 = self.cx + self.radius * 0.35 * cos(angle)
            y1 = self.cy + self.radius * 0.35 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 0.6, 1)
            cr.stroke()
        segment_angle = 2 * pi / 12
        # sign borders
        for j in range(12):
            angle = pi - j * segment_angle  # start at left
            x1 = self.cx + self.radius * 0.9 * cos(angle)
            y1 = self.cy + self.radius * 0.9 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 0.7)
            cr.set_line_width(1)
            cr.stroke()
        for guest in self.guests:
            angle = pi - radians(guest.data.get("lon"))
            x = self.cx + self.mid_ring * cos(angle)
            y = self.cy + self.mid_ring * sin(angle)
            marker_size = 9.2
            # print(f"markersize : {marker_size}")
            # draw triangle for ascendant
            if guest.data.get("name") == "asc":
                self.draw_marker(
                    cr,
                    x,
                    y,
                    angle,
                    marker_size,
                    (0.549, 0.568, 0, 1),
                    self.draw_triangle,
                )
            # draw diamond for midheaven
            elif guest.data.get("name") == "mc":
                self.draw_marker(
                    cr,
                    x,
                    y,
                    angle,
                    marker_size,
                    (0.549, 0.568, 0, 1),
                    self.draw_diamond,
                )
            else:
                guest.draw(
                    cr,
                    self.cx,
                    self.cy,
                    self.mid_ring,
                    obj_scale=12.0,
                    source="lunarreturn",
                )


class Transit(RingBase):
    # transits for event 2 datetime
    def __init__(self, radius, cx, cy, font_size, transit_data, radius_dict):
        super().__init__(radius, cx, cy)
        self.app = Gtk.Application.get_default()
        self.notify = self.app.notify_manager
        self.font_size = font_size
        self.transit_data = transit_data
        self.cusps = []
        # get ring radius
        keys = list(radius_dict.keys())
        index = ""
        try:
            index = keys.index("transit")
        except ValueError:
            raise ValueError("missing 'transit' key in radiusdict")
        if index < len(keys) - 1:
            next_key = keys[index + 1]
            next_val = radius_dict[next_key]
        else:
            # fallback
            next_val = radius_dict["transit"]
        if radius_dict:
            self.mid_ring = (radius_dict["transit"] + next_val) / 2
            self.ring = radius_dict.get("transit", "/")
            self.before_ring = next_val
            # msg += (
            #     f"p1 midring : {self.mid_ring} | radius : {self.ring} | radinext : {next_val}"
            # )
        # houses drawn 1st
        self.cusps = next(x for x in self.transit_data if not isinstance(x, dict))
        self.guests = []
        try:
            if self.transit_data:
                # create astroobject instance for drawing
                self.guests = [
                    self.create_astro_obj(obj)
                    for obj in self.transit_data
                    if isinstance(obj, dict)
                ]
        except Exception as e:
            self.notify.error(
                f"no transit positions\n\terror :\n\t{e}",
                source="rings",
                route=["terminal", "user"],
            )

    def create_astro_obj(self, obj):
        transit_obj_data = obj.copy()
        return AstroObject(transit_obj_data)

    def draw(self, cr):
        cr.arc(self.cx, self.cy, self.radius, 0, 2 * pi)
        # circle background : greenish
        cr.set_source_rgba(0.0078, 0.0941, 0, 1)
        cr.fill_preserve()
        # circle border
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.7)
        # cr.set_source_rgba(1, 1, 1, 0.7)
        cr.set_line_width(1)
        cr.stroke()
        # houses of e2 transit
        for angle in self.cusps:
            angle = pi - radians(angle)
            x1 = self.cx + self.radius * 0.35 * cos(angle)
            y1 = self.cy + self.radius * 0.35 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(0, 1, 0, 1)
            cr.stroke()
        segment_angle = 2 * pi / 12
        # sign borders
        for j in range(12):
            angle = pi - j * segment_angle  # start at left
            x1 = self.cx + self.radius * 0.9 * cos(angle)
            y1 = self.cy + self.radius * 0.9 * sin(angle)
            x2 = self.cx + self.radius * cos(angle)
            y2 = self.cy + self.radius * sin(angle)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.set_source_rgba(1, 1, 1, 0.5)
            cr.set_line_width(1)
            cr.stroke()
        for guest in self.guests:
            angle = pi - radians(guest.data.get("lon"))
            x = self.cx + self.mid_ring * cos(angle)
            y = self.cy + self.mid_ring * sin(angle)
            marker_size = 9.2
            # print(f"markersize : {marker_size}")
            # draw triangle for ascendant
            if guest.data.get("name") == "asc":
                self.draw_marker(
                    cr, x, y, angle, marker_size, (0, 0.9, 0.1, 1), self.draw_triangle
                )
            # draw diamond for midheaven
            elif guest.data.get("name") == "mc":
                self.draw_marker(
                    cr, x, y, angle, marker_size, (0, 0.9, 0.1, 1), self.draw_diamond
                )
            else:
                guest.draw(
                    cr,
                    self.cx,
                    self.cy,
                    self.mid_ring,
                    obj_scale=12.0,
                    source="transit",
                )
