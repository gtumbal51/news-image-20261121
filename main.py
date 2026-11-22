#!/usr/bin/env python3
"""news-image-20261121 — Saturday 21 November 2026 world news on one page.

Dense broadsheet front page: 38 stories — 4 illustrated leads, 11 illustrated
panels, 23 one-line briefs — plus a day-in-numbers strip, a pinned world map
with a region tally, source tags throughout and a date-check footer.
Renders 1024x1024 to entry.png and to /output/entry.png ($MAKEFUN_OUTPUT_DIR).
Stdlib + Pillow only. All copy, code and drawings are original to this entry;
story facts are from the day's wire reports, tagged per story.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MX = 28                      # page margin
CW = W - 2 * MX              # content width = 968
PAPER = (250, 247, 238)
INK = (18, 18, 18)
GREY = (88, 84, 76)
FAINT = (196, 188, 170)
RED = (178, 26, 30)
PANEL_BG = (255, 253, 246)
LEAD_BG = (244, 238, 224)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANSB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def tw(d, s, fnt):
    return d.textlength(s, font=fnt)


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = word if not cur else cur + " " + word
        if tw(d, t, fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, fnt, fill, max_w, leading, max_lines=None):
    lines = wrap(d, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def centre(d, y, text, fnt, fill):
    d.text(((W - tw(d, text, fnt)) / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- icons ----
# Each icon draws inside box (x, y, s) in ink, using red sparingly.

def i_missile(d, x, y, s):
    d.line([x + 4, y + s - 4, x + s - 14, y + 14], fill=INK, width=5)
    d.polygon([(x + s - 18, y + 4), (x + s - 4, y + 10), (x + s - 10, y + 20)],
              fill=RED)
    d.polygon([(x + 8, y + s - 16), (x + 16, y + s - 4), (x + 4, y + s - 2)], fill=INK)
    for dx, dy in ((0, 0), (7, -3), (-3, 7)):
        d.line([x + s - 8 + dx, y + 6 + dy, x + s - 2 + dx, y + dy], fill=RED, width=2)


def i_globe(d, x, y, s):
    d.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=INK, width=3)
    d.line([x + 2, y + s / 2, x + s - 2, y + s / 2], fill=INK, width=2)
    rx = s * 0.22
    d.ellipse([x + s / 2 - rx, y + 2, x + s / 2 + rx, y + s - 2], outline=INK, width=2)
    for f in (-0.48, 0.48):
        yy = y + s / 2 + f * s / 2
        hw = (s / 2) * (1 - f * f) ** 0.5
        d.line([x + s / 2 - hw, yy, x + s / 2 + hw, yy], fill=INK, width=2)


def i_badge(d, x, y, s):
    cx, cy, r = x + s / 2, y + s / 2, s * 0.46
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    pts = []
    import math
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r * 0.62 if i % 2 == 0 else r * 0.27
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=RED)


def i_burst(d, x, y, s):
    d.rectangle([x + 2, y + s - 12, x + s * 0.38, y + s - 2], fill=INK)
    d.rectangle([x + s * 0.44, y + s - 20, x + s * 0.68, y + s - 2], fill=INK)
    import math
    cx, cy = x + s * 0.66, y + s * 0.26
    for i in range(8):
        ang = i * math.pi / 4
        r1, r2 = 2, s * (0.24 if i % 2 == 0 else 0.13)
        d.line([cx + r1 * math.cos(ang), cy + r1 * math.sin(ang),
                cx + r2 * math.cos(ang), cy + r2 * math.sin(ang)], fill=RED, width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)


def i_chart(d, x, y, s):
    d.line([x + 3, y + 3, x + 3, y + s - 3], fill=INK, width=2)
    d.line([x + 3, y + s - 3, x + s - 2, y + s - 3], fill=INK, width=2)
    pts = [(x + 6, y + s * 0.25), (x + s * 0.35, y + s * 0.4),
           (x + s * 0.55, y + s * 0.32), (x + s * 0.88, y + s * 0.82)]
    d.line(pts, fill=RED, width=4)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 9, ey - 1), (ex - 2, ey - 8)], fill=RED)


def i_peaks(d, x, y, s):
    for bx, hh in ((0.02, 0.55), (0.36, 0.8), (0.68, 0.5)):
        bx0 = x + s * bx
        d.polygon([(bx0, y + s), (bx0 + s * 0.16, y + s * (1 - hh)), (bx0 + s * 0.32, y + s)],
                  outline=INK, width=3)
    d.line([x + s * 0.52, y + s * 0.2, x + s * 0.52, y + s * 0.42], fill=RED, width=3)
    d.polygon([(x + s * 0.52, y + s * 0.2), (x + s * 0.66, y + s * 0.27),
               (x + s * 0.52, y + s * 0.34)], fill=RED)


def i_scales(d, x, y, s):
    cx = x + s / 2
    d.line([cx, y + 4, cx, y + s - 6], fill=INK, width=3)
    d.line([x + 6, y + 10, x + s - 6, y + 10], fill=INK, width=3)
    for sx in (x + 6, x + s - 6):
        d.line([sx, y + 10, sx - 6, y + s * 0.5], fill=INK, width=2)
        d.line([sx, y + 10, sx + 6, y + s * 0.5], fill=INK, width=2)
        d.arc([sx - 9, y + s * 0.38, sx + 9, y + s * 0.62], 0, 180, fill=INK, width=3)
    d.line([x + s * 0.3, y + s - 4, x + s * 0.7, y + s - 4], fill=INK, width=3)


def i_ship(d, x, y, s):
    d.polygon([(x + 2, y + s * 0.55), (x + s - 2, y + s * 0.55),
               (x + s * 0.82, y + s * 0.78), (x + s * 0.16, y + s * 0.78)], fill=INK)
    d.rectangle([x + s * 0.3, y + s * 0.34, x + s * 0.62, y + s * 0.55], outline=INK, width=3)
    d.line([x + s * 0.78, y + s * 0.2, x + s * 0.78, y + s * 0.55], fill=INK, width=3)
    for i in range(3):
        wx = x + 4 + i * s * 0.3
        d.arc([wx, y + s * 0.8, wx + s * 0.24, y + s * 0.98], 180, 360, fill=RED, width=2)


def i_curve(d, x, y, s):
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((x + 3 + t * (s - 6), y + s * 0.75 - (s * 0.55) * (t ** 0.5) +
                    s * 0.12 * ((i % 3) - 1)))
    d.line(pts, fill=INK, width=3)
    d.ellipse([x + s - 10, y + 2, x + s - 2, y + 10], fill=RED)


def i_truck(d, x, y, s):
    d.rectangle([x + 2, y + s * 0.3, x + s * 0.6, y + s * 0.72], outline=INK, width=3)
    d.polygon([(x + s * 0.6, y + s * 0.45), (x + s * 0.8, y + s * 0.45),
               (x + s * 0.92, y + s * 0.6), (x + s * 0.92, y + s * 0.72),
               (x + s * 0.6, y + s * 0.72)], outline=INK, width=3)
    for wx in (x + s * 0.2, x + s * 0.76):
        d.ellipse([wx - 5, y + s * 0.7, wx + 5, y + s * 0.7 + 10], fill=RED)


def i_strikes(d, x, y, s):
    for i, off in enumerate((0.05, 0.4, 0.72)):
        x0 = x + s * off
        d.line([x0, y + 3, x0 + s * 0.16, y + s * 0.55], fill=INK, width=3)
        cx, cy = x0 + s * 0.18, y + s * 0.68
        for dx, dy in ((0, -6), (5, 3), (-5, 3)):
            d.line([cx, cy, cx + dx, cy + dy], fill=RED, width=2)


def i_planet(d, x, y, s):
    cx, cy, r = x + s / 2, y + s / 2, s * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=INK)
    d.ellipse([x + 2, cy - s * 0.13, x + s - 2, cy + s * 0.13], outline=RED, width=3)
    d.ellipse([cx + s * 0.3, cy - s * 0.42, cx + s * 0.38, cy - s * 0.34], fill=RED)


def i_quake(d, x, y, s):
    d.rectangle([x + s * 0.55, y + s * 0.18, x + s * 0.9, y + s * 0.62], outline=INK, width=3)
    d.polygon([(x + s * 0.5, y + s * 0.18), (x + s * 0.72, y + s * 0.04),
               (x + s * 0.95, y + s * 0.18)], outline=INK, width=3)
    pts = [(x + 2, y + s * 0.66), (x + s * 0.25, y + s * 0.66), (x + s * 0.33, y + s * 0.9),
           (x + s * 0.42, y + s * 0.66), (x + s * 0.62, y + s * 0.66),
           (x + s * 0.7, y + s * 0.88), (x + s * 0.78, y + s * 0.66), (x + s - 2, y + s * 0.66)]
    d.line(pts, fill=RED, width=3)


def i_game(d, x, y, s):
    d.rounded_rectangle([x + 2, y + s * 0.25, x + s - 2, y + s * 0.75], radius=10,
                        outline=INK, width=3)
    d.line([x + s * 0.18, y + s * 0.42, x + s * 0.18, y + s * 0.58], fill=INK, width=3)
    d.line([x + s * 0.11, y + s * 0.5, x + s * 0.25, y + s * 0.5], fill=INK, width=3)
    for dx, dy in ((0.72, 0.42), (0.82, 0.52)):
        d.ellipse([x + s * dx - 3, y + s * dy - 3, x + s * dx + 3, y + s * dy + 3], fill=RED)


def i_shield(d, x, y, s):
    d.polygon([(x + s * 0.5, y + 2), (x + s - 3, y + s * 0.15), (x + s - 3, y + s * 0.55),
               (x + s * 0.5, y + s - 2), (x + 3, y + s * 0.55), (x + 3, y + s * 0.15)],
              outline=INK, width=3)
    d.line([x + s * 0.5, y + s * 0.25, x + s * 0.5, y + s * 0.65], fill=RED, width=4)
    d.line([x + s * 0.32, y + s * 0.45, x + s * 0.68, y + s * 0.45], fill=RED, width=4)


ICONS = {"missile": i_missile, "globe": i_globe, "badge": i_badge, "burst": i_burst,
         "chart": i_chart, "peaks": i_peaks, "scales": i_scales, "ship": i_ship,
         "curve": i_curve, "truck": i_truck, "strikes": i_strikes, "planet": i_planet,
         "quake": i_quake, "game": i_game, "shield": i_shield}

# ----------------------------------------------------------------- data ----
# (num, kicker, headline, summary, tag, numeral, icon, region, lon, lat)
LEADS = [
    (1, "MANAMA, BAHRAIN — CONFLICT", "IRAN STRIKES US BASES IN BAHRAIN",
     "The Guards claim hits at al-Riffa and Awali; Bahrain says a civilian "
     "plant burned and no one was hurt.", "AL JAZEERA · CONFIRMED", "2",
     "missile", "ASIA", 50.6, 26.2),
    (2, "ANTALYA, TURKIYE — CLIMATE", "COP31 TALKS RUN PAST DEADLINE",
     "Nearly 200 nations remain split on fossil fuels and finance; the draft "
     "text drops fossil fuels entirely.", "BBC NEWS · CONFIRMED", "200",
     "globe", "ASIA", 30.7, 36.9),
    (3, "GUASAVE, MEXICO — JUSTICE", "MOST-WANTED CARTEL BOSS CAPTURED",
     "Special forces seize 'Chapo Isidro' Meza Flores; the gun battles that "
     "follow kill at least 11 people.", "BBC NEWS · CONFIRMED", "11",
     "badge", "N AMERICA", -108.5, 25.6),
    (4, "KRYVYI RIH, UKRAINE — WAR", "MISSILE KILLS BOY, 7, IN ZELENSKY'S HOMETOWN",
     "A ballistic strike on the city centre wounds up to 60; Russian missiles "
     "also came down in Poland.", "AL JAZEERA · OFFICIALS", "60",
     "burst", "EUROPE", 33.4, 47.9),
]

PANELS = [
    (5, "AI SELL-OFF TIPS US STOCKS INTO CORRECTION", "UPI · CONFIRMED", "10%",
     "chart", "N AMERICA", -74.0, 40.7),
    (6, "TRUMP DEFENDS PUTIN TIES AFTER SHENZHEN SUMMIT", "BBC · CONFIRMED", "3",
     "peaks", "ASIA", 114.1, 22.5),
    (7, "UN COURT: MYANMAR COMMITTED GENOCIDE", "PBS · CONFIRMED", "700K",
     "scales", "EUROPE", 4.3, 52.1),
    (8, "DRONES SET RUSSIAN CARGO SHIP ABLAZE IN BALTIC", "BBC · REPORTED", "2",
     "ship", "EUROPE", 24.0, 60.0),
    (9, "RIEMANN HYPOTHESIS 'PROVED' WITH AI HELP", "GUARDIAN · REPORTED", "167",
     "curve", "N AMERICA", -122.4, 37.8),
    (10, "STRIKE ON FOOD VEHICLE KILLS 3 IN GAZA CITY", "AL JAZEERA · REPORTED", "3",
     "truck", "ASIA", 34.3, 31.5),
    (11, "71 STRIKES IN 24H AS YEMEN FIGHTING FLARES", "MID EAST EYE · REPORTED", "71",
     "strikes", "ASIA", 42.9, 14.8),
    (12, "PROBE ORBITS MERCURY AFTER 8-YEAR JOURNEY", "UPI · CONFIRMED", "8",
     "planet", "SPACE", None, None),
    (13, "MAGNITUDE 6.7 QUAKE SHAKES CENTRAL PERU", "UPI · CONFIRMED", "6.7",
     "quake", "S AMERICA", -75.0, -9.2),
    (14, "GTA VI EARNS $3.8BN ON ITS FIRST DAY", "BBC BIZ · CONFIRMED", "$3.8B",
     "game", "N AMERICA", -118.2, 34.1),
    (15, "BRED MOSQUITOES CUT CHILD DENGUE BY 69%", "AP · CONFIRMED", "69%",
     "shield", "S AMERICA", -51.9, -14.2),
]

# (num, region, one-line brief)
BRIEFS = [
    (16, "EUROPE", "Kyiv — Russian strikes kill 3, cripple bridges and power (AP)"),
    (17, "EUROPE", "Brussels — UK and EU sign three post-Brexit agreements (Guardian)"),
    (18, "EUROPE", "Brussels — EU–Indonesia trade deal scraps 98.5% of tariffs (DW)"),
    (19, "N AMERICA", "Washington — Trump threatens tax on data centres built abroad (BBC)"),
    (20, "N AMERICA", "Washington — FBI crime database reportedly hacked again (BBC)"),
    (21, "EUROPE", "Geneva — 100 states back binding AI-weapons rules by 2028 (CBC)"),
    (22, "EUROPE", "Copenhagen — Denmark expels Russian attaché over murder plot (BBC)"),
    (23, "EUROPE", "Paris — 144 arrested at sixth Saturday of cost-of-living marches (F24)"),
    (24, "OCEANIA", "Melbourne — Teen, 17, accused of organising arsons on Signal (Guardian)"),
    (25, "N AMERICA", "Los Angeles — Palisades arson verdict: 12 dead, 6,800 buildings (BBC)"),
    (26, "N AMERICA", "Virginia — Child dies of measles; US has lost elimination status (Guardian)"),
    (27, "AFRICA", "Bayelsa — Funeral boat capsizes in Nigeria: 24 dead, 24 rescued (Sky)"),
    (28, "ASIA", "Tokyo — Saudi oil stored in Japan to triple to 24M barrels (Japan Today)"),
    (29, "S AMERICA", "Buenos Aires — Bonds hit distress; $50BN LNG project approved (BA Times)"),
    (30, "N AMERICA", "New York — Gupta gets 19 years over plot to kill Sikh leader (BBC)"),
    (31, "ASIA", "Istanbul — Turkey seizes Sozcu TV, last big independent channel (RFI)"),
    (32, "AFRICA", "Tanzania — Opposition leader Lissu convicted of sedition (BBC)"),
    (33, "AFRICA", "Kampala — Uganda curbs gatherings as Ebola spreads in Congo (Guardian)"),
    (34, "N AMERICA", "Washington — Nvidia chief Huang ousted; Trump raised it with Xi (CNBC)"),
    (35, "ASIA", "Basra — Power-station fire kills 4 and injures 35 (Reuters)"),
    (36, "AFRICA", "Ethiopia — 700,000 displaced in south; troops mass near Eritrea (F24)"),
    (37, "ASIA", "Seoul — Ruling party moves to impeach chief justice (Yonhap)"),
    (38, "N AMERICA", "Cleveland — Harden scores 51 and passes Kobe; Cavs win (Guardian)"),
]

NUMBERS = [("11", "DEAD IN SINALOA RAIDS"), ("60", "WOUNDED IN KRYVYI RIH"),
           ("$3.8BN", "GTA VI FIRST-DAY SALES"), ("69%", "DENGUE DROP, BRAZIL"),
           ("71", "STRIKES ON YEMEN IN 24H"), ("700K", "ROHINGYA FLED IN 2017")]

DATE_CHECK = ("LEFT OUT — OTHER DAYS: Anthropic's record IPO was priced Thu Nov 19 · the Crimean Bridge "
              "was hit on Nov 19 · the Shenzhen summit opened Nov 20.  NOT YET: Nepal PM Shah reaches "
              "Delhi Sun Nov 22 · Spain votes Nov 29 · Estonia shuts its Russia crossings Dec 1.")

MAP_ROWS = [
    "        ## ##  ##                ############################    ",
    "  #####  ############        #####  ########################      ",
    "        ############         ######## ####################        ",
    "       #############        #########  #################          ",
    "       ############         ##########  ############## ##         ",
    "        #########           ###########  #################        ",
    "          #####             ###########    #########              ",
    "               #####         #########      ########              ",
    "               ######         #######        ########             ",
    "               ######          #####          #######             ",
    "                #####          #####           #######            ",
    "                ####            ###            ######             ",
    "                 ##              ##             ####        #     ",
    "                 #                                          ##    ",
    "                 #                                                ",
]

# -------------------------------------------------------------- rendering ----

def num_badge(d, x, y, n, r=11):
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED)
    s = str(n)
    f = F(SANSB, 12 if len(s) < 2 else 10)
    d.text((x - tw(d, s, f) / 2, y - (7 if len(s) < 2 else 6)), s, font=f, fill=(255, 255, 255))


def draw_lead(d, x, y, w, h, st):
    n, kick, head, summ, tag, num, icon, region, lon, lat = st
    d.rectangle([x, y, x + w, y + h], fill=LEAD_BG, outline=INK, width=2)
    ih = 92
    d.rectangle([x, y, x + w, y + ih], fill=(238, 230, 208))
    ICONS[icon](d, x + 12, y + 14, 62)
    nf = F(SERIF, 40)
    nw = tw(d, num, nf)
    d.text((x + w - nw - 12, y + ih - 52), num, font=nf, fill=RED)
    num_badge(d, x + 16, y + 16, n)
    ty = y + ih + 8
    d.text((x + 10, ty), kick, font=F(SANSB, 10), fill=RED)
    ty = block(d, x + 10, ty + 15, head, F(SERIF, 19), INK, w - 20, 23, max_lines=3)
    ty = block(d, x + 10, ty + 3, summ, F(SANS, 11), (40, 38, 32), w - 20, 14.5, max_lines=3)
    d.text((x + 10, y + h - 15), tag, font=F(SANSB, 9), fill=GREY)


def draw_panel(d, x, y, w, h, st):
    n, head, tag, num, icon, region, lon, lat = st
    d.rectangle([x, y, x + w, y + h], fill=PANEL_BG, outline=FAINT, width=1)
    ICONS[icon](d, x + 8, y + 7, 26)
    nf = F(SERIF, 23)
    nw = tw(d, num, nf)
    d.text((x + w - nw - 8, y + 5), num, font=nf, fill=RED)
    num_badge(d, x + w - 16, y + h - 16, n, r=9)
    block(d, x + 8, y + 40, head, F(SANSB, 12), INK, w - 16, 15, max_lines=3)
    d.text((x + 8, y + h - 13), tag, font=F(SANSB, 8), fill=GREY)


def draw_map(d, x, y, w, h, pins):
    d.rectangle([x, y, x + w, y + h], fill=(243, 239, 228), outline=FAINT, width=1)
    d.text((x + 8, y + 4), "WHERE IT HAPPENED — NUMBERED PINS MATCH THE STORIES",
           font=F(SANSB, 10), fill=INK)
    cols = max(len(r) for r in MAP_ROWS)
    rows = len(MAP_ROWS)
    gx, gy = x + 10, y + 20
    gw, gh = w - 20, h - 26
    cell = min(gw / cols, gh / rows)
    for ri, row in enumerate(MAP_ROWS):
        for ci, ch in enumerate(row):
            if ch == "#":
                px, py = gx + ci * cell, gy + ri * cell
                d.rectangle([px, py, px + cell * 0.72, py + cell * 0.72], fill=(178, 170, 152))
    for (n, lon, lat) in pins:
        px = gx + (lon + 180) / 360 * gw
        py = gy + (74 - lat) / 126 * gh
        num_badge(d, px, py, n, r=9)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(LEADS) + len(PANELS) + len(BRIEFS)
    tally = {}
    for st in LEADS:
        tally[st[7]] = tally.get(st[7], 0) + 1
    for st in PANELS:
        tally[st[5]] = tally.get(st[5], 0) + 1
    for st in BRIEFS:
        tally[st[1]] = tally.get(st[1], 0) + 1

    # masthead
    centre(d, 12, f"THE WORLD ON ONE PAGE · {total} STORIES · SIX CONTINENTS AND SPACE",
           F(SANSB, 15), INK)
    centre(d, 34, "Saturday 21 November 2026", F(SERIF, 57), INK)
    d.rectangle([MX, 104, W - MX, 108], fill=RED)
    d.rectangle([MX, 111, W - MX, 112], fill=INK)

    # day in numbers
    ny = 118
    cw6 = CW // 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = MX + i * cw6
        if i:
            d.line([cx, ny + 4, cx, ny + 44], fill=FAINT, width=1)
        d.text((cx + 8, ny), num, font=F(SERIF, 27), fill=RED)
        block(d, cx + 8, ny + 33, lab, F(SANSB, 8.5), GREY, cw6 - 14, 10.5, max_lines=2)
    d.line([MX, ny + 52, W - MX, ny + 52], fill=INK, width=1)

    # leads
    ly = ny + 58
    lw = (CW - 3 * 8) // 4
    for i, st in enumerate(LEADS):
        draw_lead(d, MX + i * (lw + 8), ly, lw, 262, st)

    # map + tally
    my = ly + 270
    pins = [(st[0], st[8], st[9]) for st in LEADS]
    pins += [(st[0], st[6], st[7]) for st in PANELS if st[6] is not None]
    draw_map(d, MX, my, 640, 120, pins)
    tx = MX + 652
    d.rectangle([tx, my, W - MX, my + 120], fill=(243, 239, 228), outline=FAINT, width=1)
    d.text((tx + 10, my + 6), "STORIES BY REGION", font=F(SANSB, 11), fill=INK)
    order = ["N AMERICA", "EUROPE", "ASIA", "AFRICA", "S AMERICA", "OCEANIA", "SPACE"]
    yy = my + 24
    for reg in order:
        if reg in tally:
            label = "SPACE (OFF-MAP)" if reg == "SPACE" else reg
            d.text((tx + 10, yy), label, font=F(SANS, 10.5), fill=INK)
            s = str(tally[reg])
            d.text((tx + 296 - tw(d, s, F(SANSB, 11)), yy), s, font=F(SANSB, 11), fill=RED)
            yy += 12.5

    # panels: 5 + 5 + 1 row of 5 (11 panels: rows of 5 and 6? use 5/6 split 6+5)
    py = my + 128
    pw = (CW - 5 * 8) // 6
    row1, row2 = PANELS[:6], PANELS[6:]
    for i, st in enumerate(row1):
        draw_panel(d, MX + i * (pw + 8), py, pw, 98, st)
    for i, st in enumerate(row2):
        draw_panel(d, MX + i * (pw + 8), py + 106, pw, 98, st)

    # briefs
    by = py + 212
    d.text((MX, by), f"ALSO ON SATURDAY — {len(BRIEFS)} MORE STORIES IN BRIEF",
           font=F(SANSB, 12.5), fill=RED)
    d.line([MX, by + 17, W - MX, by + 17], fill=INK, width=1)
    col_w = (CW - 16) // 2
    bf = F(SANS, 10.5)
    half = (len(BRIEFS) + 1) // 2
    for ci, chunk in enumerate((BRIEFS[:half], BRIEFS[half:])):
        bx = MX + ci * (col_w + 16)
        yy = by + 23
        for (n, reg, line) in chunk:
            s = f"{n}. {line}"
            if tw(d, s, bf) > col_w:
                s = s[:]
            d.text((bx, yy), s, font=bf, fill=INK)
            yy += 13.5

    # date check
    dy = by + 23 + half * 13.5 + 6
    d.rectangle([MX, dy, W - MX, dy + 46], outline=INK, width=1)
    block(d, MX + 8, dy + 6, DATE_CHECK, F(SANS, 10), INK, CW - 16, 13, max_lines=3)
    return img


def main():
    img = build()
    img.save("entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        img.save(os.path.join(out_dir, "entry.png"))
    except OSError as exc:
        print(f"note: could not write to {out_dir}: {exc}")
    check = Image.open("entry.png")
    assert check.size == (1024, 1024), check.size
    print("entry.png OK", check.size, check.format)


if __name__ == "__main__":
    main()
