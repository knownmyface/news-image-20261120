#!/usr/bin/env python3
"""Render the 20 November 2026 front page: THE WORLD IN ONE DAY.

Draws a 1024x1024 newspaper front page from the day's verified stories.
Every illustration is drawn in code with PIL (no photos, no network):
a night bridge over the Dnipro, a cyclone spiral over the Bay of Bengal,
a falling market chart, and a stylised world map with numbered pins.
60 stories, 7 regions, 7 devices: hero leads, numbers band, clock
timeline, pin map, full index, DATE CHECK box, CLAIM/FORECAST flags.
Deterministic: same bytes on every run.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (17, 17, 17)
NAVY = (18, 40, 74)
RED = (160, 30, 34)
GREY = (96, 92, 84)
BAND = (232, 228, 213)
RULE = (120, 114, 100)
SEA = (198, 214, 222)
LAND = (222, 208, 178)
NIGHT = (13, 22, 48)
GOLD = (214, 164, 60)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fnt(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    """Greedy word wrap returning lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(d, xy, s, font, fill=INK, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def lines(d, x, y, strs, font, leading, fill=INK):
    for s in strs:
        d.text((x, y), s, font=font, fill=fill)
        y += leading
    return y


def band(d, x0, y0, x1, y1, fill, top=None, bottom=None):
    d.rectangle([x0, y0, x1, y1], fill=fill)
    if top:
        d.line([x0, y0, x1, y0], fill=top, width=2)
    if bottom:
        d.line([x0, y1, x1, y1], fill=bottom, width=2)


# ------------------------------------------------------------------ data
# 60 stories, each verified against reporting dated Friday 20 Nov 2026.
# (loc, region, story) — region drives the strip counts; the index prints
# "NN. LOC: story" on one line, truncated with an ellipsis if it runs long.
INDEX = [
    ("KYIV", "Europe", "Russian missiles hit three Dnipro bridges (Reuters)"),
    ("ODISHA", "Asia", "Cyclone Akvan makes landfall near Gopalpur (IMD)"),
    ("TAIPEI", "Asia", "AI sell-off sinks Asia's markets; Taiex -6.2% (Reuters)"),
    ("ANTALYA", "Europe", "COP31 reaches its last day with no deal (AFP)"),
    ("BRUSSELS", "Europe", "UK and EU seal a 'reset' deal (Reuters)"),
    ("POLAND", "Europe", "Russian cruise missile lands in east Poland (Reuters)"),
    ("IRAQ", "Middle East", "Iraqi army enters a militia stronghold (Reuters)"),
    ("ROME", "Europe", "General strike over Italy's budget (CGIL)"),
    ("TOKYO", "Asia", "Japan's inflation quickens to 2.3% (Reuters)"),
    ("SEOUL", "Asia", "Ruling party to impeach top judge (SBS)"),
    ("TURKANA", "Africa", "Kenya starts drilling its first oil well (allAfrica)"),
    ("SAN SALVADOR", "Americas", "Bukele launches third-term campaign (AP)"),
    ("WELLINGTON", "Oceania", "Phillips hits 118 against India (ICC)"),
    ("LVIV", "Europe", "Railway station strike kills two (BBC)"),
    ("KHARKIV", "Europe", "Drone hits a hospital; four hurt (Ukrinform)"),
    ("KRYVYI RIH", "Europe", "Drone attack cuts power to hospitals"),
    ("DNIPRO", "Europe", "Five injured in drone attack (Kyiv Independent)"),
    ("SMOLENSK", "Europe", "Ukraine drones hit Dorogobuzh chemical plant"),
    ("MOSCOW", "Europe", "Russia declares Estonia's border closure (Reuters)"),
    ("BERLIN", "Europe", "School pupils strike against military service"),
    ("LONDON", "Europe", "General says UK runs cyber attacks abroad (Sky)"),
    ("BEIJING", "Asia", "China holds its loan rates for an 18th month (Xinhua)"),
    ("TOKYO", "Asia", "SoftBank shares fall more than 14% in a day (Al Jazeera)"),
    ("SEOUL", "Asia", "KOSPI ends the week 7.9% lower (Anadolu)"),
    ("SEOUL", "Asia", "Sell-off triggers KOSPI trading curb (Korea Times)"),
    ("SEOUL", "Asia", "Court upholds Kakao founder's acquittal (SBS)"),
    ("TAIPEI", "Asia", "Short-sell curbs take effect; bombers tracked (Reuters)"),
    ("HONG KONG", "Asia", "Hang Seng about 20% off January peak (AP)"),
    ("SYDNEY", "Oceania", "Australian shares fall 1.8% in sell-off (Reuters)"),
    ("SYDNEY", "Oceania", "Retailer General Pants enters administration (ABC)"),
    ("GANJAM", "Asia", "209 mm of rain as Akvan crosses Odisha (PTI)"),
    ("NEW DELHI", "Asia", "Pakistan minister to lead SCO dialogue (The Hindu)"),
    ("HORMUZ", "Middle East", "Tanker catches fire after projectile strike (UKMTO)"),
    ("HORMUZ", "Middle East", "IRGC claims two tankers hit mines [CLAIM]"),
    ("RIYADH", "Middle East", "Coalition intercepts Houthi missiles, drones"),
    ("HODEIDAH", "Middle East", "Coalition strikes Houthi targets; port warned"),
    ("LEBANON", "Middle East", "Israeli air strikes hit south and east (Anadolu)"),
    ("YEMEN", "Middle East", "Gunfire on a cargo ship off the coast (UKMTO)"),
    ("WASHINGTON", "Americas", "Pentagon puts Iran war cost at $48.3bn (Reuters)"),
    ("NEW YORK", "Americas", "Nasdaq futures fall 1.6% before the bell (24/7)"),
    ("NEW YORK", "Americas", "Mamdani plans to close Rikers by 2032"),
    ("WASHINGTON", "Americas", "Democrats query law firm's free work (Al Jazeera)"),
    ("FLORIDA", "Americas", "St Johns River hits record 18.3 ft; schools shut (AP)"),
    ("IOWA", "Americas", "Army sets noon detonation of 68 explosive barrels (AP)"),
    ("LAS VEGAS", "Americas", "Russell fastest in wet F1 practice (Formula1.com)"),
    ("MERCURY", "Global", "BepiColombo reaches Mercury after 6bn-mile trip (ESA)"),
    ("BARCELONA", "Europe", "Cancer pill shrinks tumours 60.7% (Reuters)"),
    ("TURIN", "Europe", "ATP Finals group stage ends; semis Saturday (ATP)"),
    ("TURIN", "Europe", "ATP backs plan to lift player pay past $350m (Anadolu)"),
    ("BRAZIL", "Americas", "Lula meets chief Raoni; land recognised (Al Jazeera)"),
    ("BOUGAINVILLE", "Oceania", "Rio Tinto pledges $370m for Panguna legacy (Reuters)"),
    ("CANBERRA", "Oceania", "CBO warns AUKUS sales could shrink US fleet (Reuters)"),
    ("KAMPALA", "Africa", "Police told to enforce Ebola ban on rallies (allAfrica)"),
    ("DAKAR", "Africa", "Migrant boat capsizes off Yenne; four dead (Al Jazeera)"),
    ("BLANTYRE", "Africa", "Malawi fuel crisis: night-long petrol queues (Al Jazeera)"),
    ("DAR ES SALAAM", "Africa", "Tanzania joins Africa's top five gold holders (Reuters)"),
    ("ABUJA", "Africa", "Court bars new evidence against Tinubu (Channels TV)"),
    ("ANTALYA", "Europe", "France calls fossil-fuel gap a 'black mark' (AFP)"),
    ("ANTALYA", "Europe", "EU official calls climate draft unacceptable (RTE)"),
    ("VATICAN", "Europe", "25-metre Christmas tree lifted into place (AP)"),
]

NUMBERS = [
    ("3", "bridges hit in Kyiv"),
    ("300,000+", "evacuated before Akvan"),
    ("-6.2%", "Taiwan's Taiex, Friday"),
    ("100,000", "youth visas a year, UK-EU"),
    ("2.3%", "Japan CPI, October"),
    ("$4tn", "wiped from stocks, gold, crypto"),
]

# (UTC time, what happened) — every time is sourced, see ANALYSIS.md
CLOCK = [
    ("01:07", "Coalition intercepts Houthi drones over Saudi Arabia"),
    ("02:30", "Cyclone Akvan makes landfall near Gopalpur"),
    ("06:00", "Tokyo closes: Nikkei -5.1% at 56,437"),
    ("07:20", "Brent $92.57 a barrel, up 59 cents"),
    ("10:39", "Coalition warns Hodeidah port to evacuate"),
    ("13:31", "Coalition strikes Houthi targets in Yemen"),
]

# lon, lat, legend label — pins on the world map (1-13 = featured stories)
PINS = [
    (30.5, 50.5, "Kyiv bridges"),
    (84.9, 19.3, "Akvan landfall"),
    (121.6, 25.0, "Taipei sell-off"),
    (30.7, 36.9, "COP31, Antalya"),
    (4.4, 50.8, "UK-EU deal"),
    (23.0, 51.0, "Missile in Poland"),
    (44.3, 32.8, "Iraq: Jurf al-Sakhar"),
    (12.5, 41.9, "Rome strike"),
    (139.7, 35.7, "Tokyo CPI"),
    (127.0, 37.5, "Seoul impeach"),
    (36.0, 3.5, "Kenya oil well"),
    (-89.2, 13.7, "Bukele third term"),
    (174.8, -41.3, "Phillips 118"),
]

# coarse continent outlines (lon, lat) for the stylised world map
CONTINENTS = [
    [(-168, 66), (-150, 70), (-130, 71), (-110, 72), (-95, 80), (-85, 76),
     (-75, 72), (-65, 62), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 26), (-85, 20), (-90, 15), (-95, 18), (-105, 22), (-115, 30),
     (-125, 40), (-125, 49), (-135, 58), (-150, 60), (-162, 58)],
    [(-80, 10), (-77, 5), (-70, 0), (-60, -3), (-50, -5), (-40, -10),
     (-35, -18), (-42, -25), (-50, -30), (-58, -38), (-66, -48), (-70, -52),
     (-72, -42), (-73, -32), (-78, -20), (-80, -8), (-81, 0)],
    [(-10, 36), (-8, 43), (-2, 48), (2, 51), (5, 58), (10, 57), (14, 56),
     (18, 56), (21, 60), (25, 65), (30, 70), (35, 68), (40, 62), (38, 55),
     (32, 47), (28, 44), (24, 40), (19, 42), (14, 38), (8, 39), (0, 38),
     (-6, 36)],
    [(-17, 15), (-12, 27), (-6, 33), (2, 37), (10, 37), (18, 33), (26, 32),
     (32, 31), (35, 28), (39, 20), (43, 12), (48, 11), (51, 10), (45, 2),
     (40, -6), (36, -14), (32, -22), (28, -30), (22, -35), (18, -34),
     (14, -28), (12, -18), (9, -2), (8, 4), (0, 6), (-8, 5), (-14, 11)],
    [(40, 68), (55, 69), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 66), (178, 65), (170, 60), (162, 56), (155, 50),
     (142, 45), (135, 38), (128, 33), (122, 28), (115, 22), (108, 15),
     (103, 8), (98, 12), (92, 18), (88, 22), (82, 16), (77, 10), (72, 20),
     (66, 25), (60, 25), (54, 27), (50, 30), (46, 34), (42, 38), (38, 44),
     (36, 50), (40, 58)],
    [(113, -22), (114, -30), (116, -35), (122, -34), (128, -32), (134, -33),
     (138, -35), (142, -38), (147, -39), (150, -37), (153, -30), (150, -24),
     (146, -19), (142, -11), (137, -12), (132, -12), (127, -14), (122, -17),
     (117, -20)],
]


# ------------------------------------------------------------ illustrations
def draw_kyiv(d, x, y, w, h):
    """Night over the Dnipro: skyline, a bridge, missile trails, fires."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    # stars
    for sx, sy, r in [(0.12, 0.14, 1), (0.30, 0.08, 1), (0.52, 0.18, 1),
                      (0.68, 0.10, 2), (0.85, 0.20, 1), (0.42, 0.06, 1),
                      (0.95, 0.08, 1), (0.22, 0.26, 1)]:
        d.ellipse([x + sx * w - r, y + sy * h - r, x + sx * w + r,
                   y + sy * h + r], fill=(230, 230, 240))
    # missile trails: dotted orange arcs falling left to right
    for t0, t1 in [(0.06, 0.30), (0.38, 0.62), (0.70, 0.94)]:
        for k in range(9):
            t = t0 + (t1 - t0) * k / 8
            px = x + t * w
            py = y + h * (0.10 + 0.34 * ((t - t0) / (t1 - t0)) ** 2)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 170, 60))
    # skyline: dark towers with a few lit windows
    base = y + h * 0.72
    for bx, bw, bh in [(0.02, 0.10, 0.30), (0.14, 0.08, 0.42), (0.24, 0.12, 0.34),
                       (0.62, 0.09, 0.38), (0.73, 0.11, 0.30), (0.86, 0.10, 0.44)]:
        d.rectangle([x + bx * w, base - bh * h, x + (bx + bw) * w, base],
                    fill=(8, 12, 30))
        for wy in range(3):
            for wx in range(2):
                if (int(bx * 100) + wy + wx) % 3 == 0:
                    d.rectangle([x + (bx + 0.015 + wx * 0.04) * w,
                                 base - bh * h + (0.05 + wy * 0.09) * h,
                                 x + (bx + 0.035 + wx * 0.04) * w,
                                 base - bh * h + (0.07 + wy * 0.09) * h],
                                fill=(255, 200, 90))
    # river
    d.rectangle([x, base, x + w, y + h], fill=(16, 34, 66))
    # the bridge: deck + arch + cables, centre-left
    bx0, bx1 = x + 0.30 * w, x + 0.72 * w
    by = base - 0.10 * h
    d.line([bx0, by, bx1, by], fill=(200, 200, 210), width=4)
    d.arc([bx0, by - 0.16 * h, bx1, by + 0.16 * h], 180, 360,
          fill=(200, 200, 210), width=3)
    for k in range(1, 7):
        cx = bx0 + (bx1 - bx0) * k / 7
        d.line([cx, by, cx, by - 0.13 * h], fill=(160, 160, 175), width=1)
    for k in range(4):
        px = bx0 + 0.10 * w + k * 0.03 * w
        d.rectangle([px, by - 0.06 * h, px + 0.012 * w, by],
                    fill=(200, 200, 210))
    # fires on the bridge deck: orange glows
    for fx in (0.38, 0.58):
        cx, cy = x + fx * w, by - 2
        for r, col in [(14, (255, 120, 20)), (8, (255, 190, 60)),
                       (4, (255, 240, 160))]:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # smoke
    for sx, sy, r in [(0.40, 0.30, 9), (0.44, 0.24, 12), (0.60, 0.28, 10)]:
        d.ellipse([x + sx * w - r, y + sy * h - r, x + sx * w + r,
                   y + sy * h + r], fill=(90, 95, 110))


def draw_akvan(d, x, y, w, h):
    """Bay of Bengal: tan coast on the left, cyclone spiral, red eye."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 90, 140))
    # coast of India: a tan wedge down the left edge
    d.polygon([(x, y + 0.05 * h), (x + 0.30 * w, y + 0.22 * h),
               (x + 0.24 * w, y + 0.55 * h), (x + 0.34 * w, y + 0.85 * h),
               (x, y + h)], fill=(214, 196, 158))
    d.polygon([(x, y + 0.05 * h), (x + 0.30 * w, y + 0.22 * h),
               (x + 0.24 * w, y + 0.55 * h), (x + 0.34 * w, y + 0.85 * h),
               (x, y + h)], outline=(160, 140, 100))
    text(d, (x + 8, y + 0.62 * h), "BAY OF", fnt(SANS_B, 10), fill=(240, 235, 220))
    text(d, (x + 8, y + 0.62 * h + 12), "BENGAL", fnt(SANS_B, 10),
         fill=(240, 235, 220))
    # cyclone spiral: concentric arcs around the eye
    cx, cy = x + 0.62 * w, y + 0.48 * h
    for r in (52, 40, 28, 17):
        d.arc([cx - r, cy - r * 0.82, cx + r, cy + r * 0.82], 20, 300,
              fill=(245, 245, 250), width=4)
        d.arc([cx - r, cy - r * 0.82, cx + r, cy + r * 0.82], 200, 340,
              fill=(200, 215, 230), width=3)
    d.ellipse([cx - 8, cy - 7, cx + 8, cy + 7], fill=RED)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255))
    # wind barbs: short slashes around the spiral
    for k in range(8):
        ang = 0.4 + k * 0.78
        import math
        r = 62
        px = cx + r * math.cos(ang)
        py = cy + r * 0.82 * math.sin(ang)
        d.line([px, py, px + 10 * math.cos(ang + 0.6),
                py + 8 * math.sin(ang + 0.6)], fill=(245, 245, 250), width=2)
    # Gopalpur marker
    gx, gy = x + 0.30 * w, y + 0.30 * h
    d.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=RED,
              outline=(255, 255, 255), width=2)
    d.line([gx + 5, gy, cx - 30, cy - 18], fill=(255, 255, 255), width=1)


def draw_market(d, x, y, w, h):
    """Falling market: dark board, red down-trend, faint grid."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 16, 20))
    for gy in range(1, 4):
        d.line([x, y + gy * h / 4, x + w, y + gy * h / 4],
               fill=(45, 45, 55), width=1)
    # bars: a week of closes, falling
    closes = [0.92, 0.88, 0.90, 0.82, 0.74, 0.66, 0.52, 0.38]
    bw = w / (len(closes) + 1)
    for i, c in enumerate(closes):
        bx = x + bw * (i + 0.5)
        top = y + h * (1 - c) * 0.85
        d.rectangle([bx - bw * 0.28, top, bx + bw * 0.28, y + h * 0.92],
                    fill=(120, 30, 34) if i < len(closes) - 1 else (160, 30, 34))
    # the trend line over the bars
    pts = []
    for i, c in enumerate(closes):
        pts.append((x + bw * (i + 0.5), y + h * (1 - c) * 0.85))
    d.line(pts, fill=(255, 70, 60), width=3, joint="curve")
    # last point: a red dot
    d.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5],
              fill=(255, 70, 60), outline=(255, 255, 255), width=2)


def draw_map(d, x, y, w, h):
    """Stylised world map (equirectangular) with numbered red pins."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # graticule
    for gx in range(1, 12):
        d.line([x + gx * w / 12, y, x + gx * w / 12, y + h],
               fill=(214, 226, 232), width=1)
    for gy in range(1, 6):
        d.line([x, y + gy * h / 6, x + w, y + gy * h / 6],
               fill=(214, 226, 232), width=1)
    for poly in CONTINENTS:
        pts = []
        for lon, lat in poly:
            px = x + (lon + 180) / 360 * w
            py = y + (90 - lat) / 180 * h
            pts.append((px, py))
        d.polygon(pts, fill=LAND, outline=(170, 152, 115))
    # Badge offsets (dx, dy) for the crowded European pins: the numbered
    # badge is drawn away from the true spot, joined by a thin leader line,
    # so neighbouring badges never overlap. Other pins sit on their spot.
    offsets = {1: (0, 0), 4: (4, 18), 5: (-18, -16), 6: (2, -20),
               7: (18, 2), 8: (-16, 14), 13: (-24, -8)}
    for n, (lon, lat, _lab) in enumerate(PINS, 1):
        px = x + (lon + 180) / 360 * w
        py = y + (90 - lat) / 180 * h
        ox, oy = offsets.get(n, (0, 0))
        bx = min(max(px + ox, x + 9), x + w - 9)
        by = min(max(py + oy, y + 9), y + h - 9)
        if ox or oy:
            d.line([px, py, bx, by], fill=(90, 90, 90), width=1)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
                  outline=(255, 255, 255), width=2)
        text(d, (bx, by - 6), str(n), fnt(SANS_B, 9),
             fill=(255, 255, 255), anchor="ma")


# ------------------------------------------------------------------- layout
REGIONS = ["Europe", "Asia", "Middle East", "Africa", "Americas",
           "Oceania", "Global"]
RCOLOURS = {"Europe": NAVY, "Asia": RED, "Middle East": (146, 96, 30),
            "Africa": (32, 110, 60), "Americas": (96, 56, 140),
            "Oceania": (16, 110, 118), "Global": GREY}


def region_counts():
    counts = {r: 0 for r in REGIONS}
    for _loc, reg, _s in INDEX:
        counts[reg] += 1
    return counts


def build():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    mx, rx = 28, W - 28

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 8], fill=NAVY)
    text(d, (W // 2, 20), "THE WORLD IN ONE DAY", fnt(SERIF_B, 50), anchor="ma")
    d.line([mx, 88, rx, 88], fill=INK, width=3)
    d.line([mx, 92, rx, 92], fill=INK, width=1)
    text(d, (mx, 100), "FRIDAY 20 NOVEMBER 2026", fnt(SERIF_B, 21))
    text(d, (rx, 102), "60 STORIES  ·  7 REGIONS  ·  ONE DAY",
         fnt(SANS_B, 12), fill=NAVY, anchor="ra")

    # ---- numbers band --------------------------------------------------
    by0, by1 = 126, 180
    band(d, mx, by0, rx, by1, BAND, top=NAVY, bottom=NAVY)
    cell_w = (rx - mx) / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = mx + cell_w * i
        if i:
            d.line([cx, by0 + 8, cx, by1 - 8], fill=RULE, width=1)
        text(d, (cx + cell_w / 2, by0 + 6), num, fnt(SERIF_B, 24),
             fill=NAVY, anchor="ma")
        for j, ln in enumerate(wrap(d, lab, fnt(SANS, 9), cell_w - 14)):
            text(d, (cx + cell_w / 2, by0 + 34 + j * 11), ln,
                 fnt(SANS, 9), fill=INK, anchor="ma")

    # ---- region strip --------------------------------------------------
    counts = region_counts()
    sy0, sy1 = 184, 200
    total_w = rx - mx
    widths = {r: max(60, round(counts[r] / len(INDEX) * total_w))
              for r in REGIONS}
    over = sum(widths.values()) - total_w
    widths["Europe"] -= over
    cx = mx
    for r in REGIONS:
        wseg = widths[r]
        d.rectangle([cx, sy0, cx + wseg, sy1], fill=RCOLOURS[r])
        label = f"{r} {counts[r]}"
        text(d, (cx + wseg / 2, sy0 + 3), label, fnt(SANS_B, 9),
             fill=(255, 255, 255), anchor="ma")
        cx += wseg

    # ---- three lead cards ----------------------------------------------
    col_w = (rx - mx - 24) // 3
    ly, lh = 206, 176
    leads = [
        ("KYIV", "3 bridges hit", draw_kyiv,
         "1  KYIV, UKRAINE · WAR",
         "Russian missiles hit three Kyiv bridges",
         "An overnight barrage of about 110 missiles and 400 drones killed "
         "at least eight people across Ukraine and cut power and water in "
         "the capital. (Reuters, BBC)"),
        ("CYCLONE AKVAN", "Landfall · 8 am", draw_akvan,
         "2  ODISHA, INDIA · CYCLONE",
         "Cyclone Akvan comes ashore in eastern India",
         "The storm crossed the coast near Gopalpur from about 8 am after "
         "more than 300,000 people were moved to shelters. No deaths were "
         "reported. (IMD, PTI)"),
        ("AI SELL-OFF", "Asia, Friday's close", draw_market,
         "3  TAIPEI · SEOUL · TOKYO · MARKETS",
         "AI sell-off sinks Asia's stock markets",
         "Taiwan's index fell 6.2% to end its worst week since 1991. Seoul "
         "lost 5.2% and Tokyo 5.1% as chipmakers led the slide. "
         "(Reuters, AP)"),
    ]
    for i, (tag, tag2, drawfn, kicker, head, deck) in enumerate(leads):
        lx = mx + i * (col_w + 12)
        # illustration panel, drawn in code
        panel = Image.new("RGB", (col_w, lh), PAPER)
        pd = ImageDraw.Draw(panel)
        drawfn(pd, 0, 0, col_w, lh)
        page.paste(panel, (lx, ly))
        d.rectangle([lx, ly, lx + col_w, ly + lh], outline=INK, width=1)
        # red tag top-left, white fact bottom-left
        tw = d.textlength(tag, font=fnt(SANS_B, 11)) + 12
        d.rectangle([lx, ly, lx + tw, ly + 20], fill=RED)
        text(d, (lx + 6, ly + 3), tag, fnt(SANS_B, 11), fill=(255, 255, 255))
        t2w = d.textlength(tag2, font=fnt(SANS_B, 10)) + 12
        d.rectangle([lx, ly + lh - 19, lx + t2w, ly + lh], fill=(255, 255, 255))
        text(d, (lx + 6, ly + lh - 16), tag2, fnt(SANS_B, 10), fill=INK)
        # kicker, headline, deck
        ty = ly + lh + 8
        text(d, (lx, ty), kicker, fnt(SANS_B, 9), fill=RED)
        ty += 13
        for ln in wrap(d, head, fnt(SERIF_B, 18), col_w):
            text(d, (lx, ty), ln, fnt(SERIF_B, 18))
            ty += 21
        ty += 2
        for ln in wrap(d, deck, fnt(SANS, 10.5), col_w):
            text(d, (lx, ty), ln, fnt(SANS, 10.5))
            ty += 13

    # ---- COP31 band ----------------------------------------------------
    iy0, iy1 = 496, 548
    band(d, mx, iy0, rx, iy1, NAVY)
    # globe pictogram: circle + meridians
    px, py = mx + 14, iy0 + 10
    d.ellipse([px, py, px + 32, py + 32], outline=(247, 242, 231), width=2)
    d.ellipse([px + 8, py, px + 24, py + 32], outline=(247, 242, 231), width=1)
    d.line([px, py + 16, px + 32, py + 16], fill=(247, 242, 231), width=1)
    d.line([px + 16, py, px + 16, py + 32], fill=(247, 242, 231), width=1)
    # thermometer pictogram
    tx = mx + 56
    d.rectangle([tx, iy0 + 8, tx + 6, iy0 + 34], outline=(247, 242, 231), width=2)
    d.ellipse([tx - 3, iy0 + 32, tx + 9, iy0 + 44], fill=RED)
    tx2 = mx + 78
    text(d, (tx2, iy0 + 7), "COP31: NO DEAL ON THE FINAL DAY",
         fnt(SERIF_B, 19), fill=(247, 242, 231))
    text(d, (tx2, iy0 + 32),
         "Draft drops fossil fuels and the $120bn adaptation fund  ·  talks run "
         "into the weekend  ·  third draft due Saturday [FORECAST]",
         fnt(SANS, 11), fill=(210, 205, 190))

    # ---- clock strip ---------------------------------------------------
    cy0 = 556
    text(d, (mx, cy0), "DAY BY THE CLOCK — ALL TIMES UTC",
         fnt(SANS_B, 11), fill=NAVY)
    d.line([mx, cy0 + 24, rx, cy0 + 24], fill=NAVY, width=2)
    slot = (rx - mx) / 6
    for i, (t, what) in enumerate(CLOCK):
        cx = mx + slot * i + slot / 2
        d.ellipse([cx - 5, cy0 + 19, cx + 5, cy0 + 29], fill=RED)
        text(d, (cx, cy0 + 33), t, fnt(SANS_B, 11), fill=RED, anchor="ma")
        for j, ln in enumerate(wrap(d, what, fnt(SANS, 8.5), slot - 10)):
            text(d, (cx, cy0 + 47 + j * 10), ln, fnt(SANS, 8.5), anchor="ma")

    # ---- map + index ---------------------------------------------------
    my0 = 632
    map_w, map_h = 540, 216
    text(d, (mx, my0), "WHERE IT HAPPENED", fnt(SERIF_B, 15))
    text(d, (mx + map_w, my0 + 2), "13 pins, numbered to the index →",
         fnt(SANS, 10), fill=GREY, anchor="ra")
    draw_map(d, mx, my0 + 22, map_w, map_h)
    d.rectangle([mx, my0 + 22, mx + map_w, my0 + 22 + map_h], outline=INK, width=1)
    # pin legend, two columns under the map
    leg_y = my0 + 22 + map_h + 8
    for i, (_lon, _lat, lab) in enumerate(PINS):
        col = i // 7
        row = i % 7
        lx = mx + col * 275
        ly2 = leg_y + row * 10
        text(d, (lx, ly2), f"{i + 1}. {lab}", fnt(SANS, 9))

    # index panel: all 60 stories, two columns
    ix = mx + map_w + 20
    iw = rx - ix
    text(d, (ix, my0), "THE DAY IN FULL — 60 STORIES", fnt(SERIF_B, 13))
    d.line([ix, my0 + 18, rx, my0 + 18], fill=INK, width=2)
    col_w2 = (iw - 12) / 2
    f_idx = fnt(SANS, 7.5)
    row_h = 10.0
    for i, (loc, _reg, story) in enumerate(INDEX):
        col = i // 30
        row = i % 30
        x = ix + col * (col_w2 + 12)
        y = my0 + 22 + row * row_h
        text(d, (x, y), f"{i + 1:>2}.", f_idx, fill=RED)
        head = f"{loc}: {story}"
        while d.textlength(head, font=f_idx) > col_w2 - 22 and len(head) > 4:
            head = head[:-4] + "…"
        text(d, (x + 20, y), head, f_idx)

    # ---- DATE CHECK ----------------------------------------------------
    dy0, dy1 = 962, 992
    d.rectangle([mx, dy0, rx, dy1], outline=RED, width=2)
    dc = ("DATE CHECK — Left out as Thursday 19 November's news: the Myanmar "
          "ruling, the Shenzhen declaration, Anthropic's IPO debut, GTA VI's "
          "launch, the $190.4m Van Gogh sale, Voyager 1's one-light-day mark. "
          "Not yet shown: BepiColombo's Mercury orbit insertion (Saturday) "
          "and any final COP31 text.")
    dclines = wrap(d, dc, fnt(SANS, 8.5), rx - mx - 16)
    for j, ln in enumerate(dclines[:3]):
        text(d, (mx + 8, dy0 + 3 + j * 10), ln, fnt(SANS, 8.5), fill=RED)

    # ---- footer --------------------------------------------------------
    fy = 998
    d.line([mx, fy, rx, fy], fill=INK, width=2)
    text(d, (mx, fy + 5),
         "All 60 stories checked against reporting dated 20 November 2026 — "
         "sources: Reuters / AP / AFP / BBC / PTI / Al Jazeera",
         fnt(SANS_B, 10), fill=NAVY)
    text(d, (mx, fy + 19),
         "All illustrations drawn in code for this page.  THE WORLD IN ONE DAY  ·  "
         "make.fun news-image-20261120  ·  $250 bounty",
         fnt(SANS, 9), fill=GREY)
    text(d, (rx, fy + 19), "20 NOV 2026", fnt(SANS_B, 9), fill=GREY, anchor="ra")

    page.save(OUT, "PNG", optimize=True)
    return OUT


if __name__ == "__main__":
    path = build()
    size = os.path.getsize(path)
    print(f"wrote {path} ({size} bytes)")
