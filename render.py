#!/usr/bin/env python3
"""Render v4 of The World Today — 18 November 2026, as a 1024x1024 PNG.

v4 follows the shape of the strongest dev-board pages: 52 stories, 16 of
them drawn as small flat-vector pictures, a UTC timeline, a numbers strip,
a world map with numbered pins, a numbered "also" list, and a date check.
Every story below was published or first reported on Wednesday
18 November 2026 (see research-notes.md); nothing is invented, and each
drawn story carries a proof tag: CONFIRMED where the event is established
by a primary source or several outlets, CLAIM where it rests on one
party's word.

Usage: python3 render.py [output.png]   (default: entry.png)
Deterministic: fixed strings, fixed layout, PNG with no timestamps.
"""

import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952
INK = (17, 17, 17)
PAPER = (247, 242, 231)
RED = (163, 18, 18)
GREEN = (20, 110, 60)
GREY = (70, 66, 60)
RULE = (160, 152, 138)
SEA = (214, 228, 235)
LAND = (232, 224, 200)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_text(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rule(draw, y, weight=2, x0=None, x1=None):
    draw.line([(x0 or MARGIN, y), (x1 or W - MARGIN, y)], fill=RULE, width=weight)


def para(draw, x, y, lines, fnt, fill=INK, leading=None):
    lh = leading or int(fnt.size * 1.18)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def tag_text(draw, x, y, status, src, fnt):
    """Proof tag: green CONFIRMED or red CLAIM, then the source."""
    color = GREEN if status == "CONFIRMED" else RED
    mark = "✓ " if status == "CONFIRMED" else "! "
    draw.text((x, y), mark + status, font=fnt, fill=color)
    w = draw.textlength(mark + status, font=fnt)
    draw.text((x + w + 5, y), "· " + src, font=fnt, fill=GREY)
    return y + int(fnt.size * 1.25)


# n, region, field, headline, deck, source, status, lon, lat, art
STORIES = [
    (1, "MIDDLE EAST", "Conflict",
     "Iran's drones hit a U.S. base in Kuwait",
     "Drones strike Ali Al Salem as Washington warns of strikes on Iran's "
     "leadership — and Iran vows to keep its defences up.",
     "Reuters", "CONFIRMED", 48, 29, "kuwait"),
    (2, "ASIA", "Diplomacy",
     "Xi hugs Trump at Shenzhen as Putin waits",
     "Trump lands to a rare airport hug from Xi; Putin is already in town "
     "for Thursday's trilateral. APEC opens today.",
     "The Tribune", "CONFIRMED", 114, 22.5, "shenzhen"),
    (3, "EUROPE", "Economy",
     "Russia pounds Kyiv's grid as EU proposes €45bn loan",
     "Strikes knock out power in Kyiv as von der Leyen proposes €45bn for "
     "2027 — €20bn budget, €25bn military.",
     "Reuters", "CONFIRMED", 30.5, 50.5, "kyiv"),
    (4, "GLOBAL", "Science",
     "Voyager 1 reaches one light-day from Earth",
     "Launched in 1977, the probe is now 26 billion km out — the farthest "
     "human-made object ever — still phoning home.",
     "AFP", "CONFIRMED", None, None, "voyager"),
    (5, "EUROPE", "Conflict",
     "Kerch Bridge's road deck collapses",
     "The rail deck is gone; Russia calls it a terrorist attack.",
     "Kyiv Independent", "CONFIRMED", 36.5, 45.3, "kerch"),
    (6, "EUROPE", "Politics",
     "France marches: 146,000 rally",
     "Unions strike over living costs across France.",
     "dailybaku.az", "CONFIRMED", 2.3, 48.9, "france"),
    (7, "AMERICAS", "Politics",
     "Peltola flips Alaska, Democrats win 56",
     "Democrats take a 56-seat Senate majority with Alaska.",
     "The Trent", "CONFIRMED", -150, 64, "alaska"),
    (8, "AFRICA", "Health",
     "Ebola cases pass 11,000 in DRC",
     "Children hit hardest as the outbreak grows.",
     "Horizon", "CONFIRMED", 23, -2, "ebola"),
    (9, "OCEANIA", "Weather",
     "Cyclone Xavier batters Australia at 315 km/h",
     "The storm slams the west coast at 315 km/h.",
     "Reports", "CONFIRMED", 115, -25, "xavier"),
    (10, "AMERICAS", "Technology",
     "Nvidia hits record $116bn revenue",
     "A.I. demand drives record quarterly revenue.",
     "Reports", "CONFIRMED", -122, 37.4, "nvidia"),
    (11, "MIDDLE EAST", "Conflict",
     "Houthi attacks on Israel and the Gulf",
     "Iran-backed Houthis strike at Israel and Gulf states.",
     "Horizon", "CONFIRMED", 45, 15, "houthi"),
    (12, "MIDDLE EAST", "Conflict",
     "Iran downs U.S. MQ-9 drone over Iraq",
     "Iran says it downed a U.S. MQ-9 Reaper in Iraqi airspace.",
     "Horizon", "CLAIM", 44, 33, "mq9"),
    (13, "MIDDLE EAST", "Conflict",
     "ADNOC tanker hit in the Gulf",
     "Iran launched missiles at an ADNOC oil tanker.",
     "Horizon", "CONFIRMED", 52, 26, "tanker"),
    (14, "AMERICAS", "Sport",
     "Argentina thrash Costa Rica 7–0",
     "Nico Paz, Álvarez and Mastantuono score twice each.",
     "RHC", "CONFIRMED", -64, -31, "argentina"),
    (15, "ASIA", "Diplomacy",
     "Modi wraps up Philippines visit",
     "Modi leaves Manila after the ASEAN, East Asia and Quad summits.",
     "EIN", "CONFIRMED", 121, 14.6, "modi"),
    (16, "ASIA", "Conflict",
     "Japan protests Russian jets in its airspace",
     "Tokyo scrambles jets after the first breach since 2024.",
     "AsiaPresse", "CONFIRMED", 139.7, 35.7, "jets"),
]

# n, region, field, one-line item, source
ALSO = [
    (17, "EUROPE", "Conflict", "Odesa strikes kill four, injure 13", "Euronews"),
    (18, "EUROPE", "Economy", "EU adds 145 Russian entities", "en.h.ua"),
    (19, "EUROPE", "Politics", "France rejects 'co-belligerent' tag", "The Independent"),
    (20, "EUROPE", "Economy", "Deutsche Bank leak: 15m files", "Horizon"),
    (21, "EUROPE", "Economy", "Markets slide; gold drops 2.31%", "Horizon"),
    (22, "EUROPE", "Diplomacy", "Portugal adds €50m to PURL fund", "h.ua"),
    (23, "EUROPE", "Weather", "Romania quake, 5.4 magnitude", "Reports"),
    (24, "ASIA", "Conflict", "Siberia plane crash: 19 dead", "Horizon"),
    (25, "AMERICAS", "Politics", "Jeffries nominated as House speaker", "France24"),
    (26, "AMERICAS", "Diplomacy", "Hegseth signs Venezuela deal", "DW"),
    (27, "AMERICAS", "Technology", "Waymo suspends freeway rides", "Horizon"),
    (28, "AMERICAS", "Technology", "Outages reach the NSA's network", "Horizon"),
    (29, "AMERICAS", "Politics", "Musk slams $500m GOP spend", "TIME"),
    (30, "AMERICAS", "Health", "U.S. loses measles-free status", "Horizon"),
    (31, "AMERICAS", "Politics", "Asif Merchant jailed for 27 years", "The Hindu"),
    (32, "ASIA", "Weather", "Akvan heads for India's coast", "AIR"),
    (33, "ASIA", "Science", "Vulcan failed on fuel starvation", "Florida Today"),
    (34, "ASIA", "Economy", "Pakistan solar hits 28% of power", "AsiaPresse"),
    (35, "ASIA", "Technology", "Singapore A.I. missions vs scams", "AsiaPresse"),
    (36, "ASIA", "Sport", "Alcaraz beats Tiafoe 6–2, 6–2", "Tribune India"),
    (37, "ASIA", "Sport", "Jay Shah re-elected ICC chairman", "Tribune India"),
    (38, "ASIA", "Sport", "Dhoni retires from the IPL", "filmfare"),
    (39, "ASIA", "Technology", "Japan's false 9.9 quake alert", "Straits Times"),
    (40, "MIDDLE EAST", "Conflict", "Cold kills in Gaza's tents", "Horizon"),
    (41, "MIDDLE EAST", "Politics", "Britain sanctions settlement firms", "Horizon"),
    (42, "MIDDLE EAST", "Politics", "Yemen brands Houthis terrorists", "AsiaPresse"),
    (43, "MIDDLE EAST", "Conflict", "Three tankers burn after mine hits", "Cyprus Mail"),
    (44, "GLOBAL", "Politics", "World Court to rule on Myanmar", "EIN"),
    (45, "AFRICA", "Health", "Nigeria–South Africa row", "The Trent"),
    (46, "AFRICA", "Politics", "Senegal's Faye expelled from party", "France24"),
    (47, "AFRICA", "Politics", "Nigeria to let states run police", "France24"),
    (48, "AFRICA", "Politics", "Migrant boat capsizes off Senegal", "Daily Digest"),
    (49, "AFRICA", "Politics", "South Sudan screens out 54 children", "Juba Global"),
    (50, "GLOBAL", "Science", "M1.1 solar flare erupts", "dailybaku"),
    (51, "ASIA", "Diplomacy", "Nepal PM shortens India visit", "AsiaPresse"),
    (52, "ASIA", "Politics", "UNHCR stops new registrations", "AppiSToS"),
]

# label, story number, short event text (times verified in research-notes)
TIMELINE = [
    ("OVERNIGHT", 39, "Japan blames code for a false 9.9 quake alert"),
    ("07:00 UTC", 47, "Nigeria moves to let states run their own police"),
    ("MORNING", 22, "Portugal adds €50m to Ukraine's weapons fund"),
    ("10:16 UTC", 3, "EU proposes a €45bn loan for Ukraine in 2027"),
    ("11:00 UTC", 2, "Xi greets Trump with a hug at Shenzhen airport"),
    ("19:00 UTC", 17, "Russian strikes on Odesa kill four"),
    ("21:00 UTC", 46, "Senegal's Faye expelled from the ruling party"),
    ("LATE", 29, "Musk calls $500m of GOP spending a mistake"),
]

NUMBERS = [
    ("315 km/h", "Cyclone Xavier's peak gusts"),
    ("11,000+", "Ebola cases in DRC"),
    ("146,000", "marchers across France"),
    ("$116bn", "Nvidia's quarterly revenue"),
]

DATE_CHECK = (
    "DATE CHECK — Left out: Indonesia's asset-forfeiture bill and the Berlin "
    "Ukraine talks (both 19 Nov) · Earthshot Prize (17 Nov) · Fiji drought "
    "declaration (announced 19 Nov local time)"
)
SOURCES_LINE = (
    "SOURCES — Reuters · AFP · The Tribune · Kyiv Independent · RHC · EIN · "
    "AsiaPresse · Horizon · France24 · DW · TIME · The Hindu · Florida Today · "
    "Tribune India · Cyprus Mail · Straits Times · Daily Digest · The Trent"
)

# ---------------- flat-vector scene painters ----------------
# Each draws a small, simple picture in the given box. No external images.

def _sky(d, box, top, bottom):
    d.rectangle(box, fill=top)
    d.rectangle([box[0], box[1] + (box[3] - box[1]) // 2, box[2], box[3]], fill=bottom)


def _stars(d, box, seed=7, n=14):
    import random
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.randint(box[0] + 2, box[2] - 2)
        y = rnd.randint(box[1] + 2, box[1] + (box[3] - box[1]) // 2)
        d.ellipse([x, y, x + 1, y + 1], fill=(255, 255, 255))


def _burst(d, cx, cy, r, color=(255, 176, 32)):
    for ang, rr in [(0, 1.0), (45, 0.75), (90, 1.0), (135, 0.7), (180, 0.95),
                    (225, 0.7), (270, 1.0), (315, 0.75)]:
        import math
        x2 = cx + rr * r * math.cos(math.radians(ang))
        y2 = cy + rr * r * math.sin(math.radians(ang))
        d.line([(cx, cy), (x2, y2)], fill=color, width=3)
    d.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], fill=color)


def _drone(d, cx, cy, s, body=(40, 40, 40)):
    d.ellipse([cx - 3 * s, cy - s // 2, cx + 3 * s, cy + s // 2], fill=body)
    d.polygon([(cx - 7 * s, cy), (cx - 3 * s, cy - s), (cx - 3 * s, cy + s)],
              fill=body)
    d.polygon([(cx + 3 * s, cy - s), (cx + 7 * s, cy), (cx + 3 * s, cy + s)],
              fill=body)
    d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=(200, 200, 200))


def draw_art(d, box, key):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if key == "kuwait":  # night base, drone, burst
        _sky(d, box, (12, 18, 40), (30, 42, 66))
        _stars(d, box, seed=1)
        d.rectangle([x0, y1 - 12, x1, y1], fill=(60, 60, 60))
        for i in range(5):
            d.rectangle([x0 + 8 + i * 24, y1 - 14, x0 + 16 + i * 24, y1 - 12],
                        fill=(240, 220, 120))
        _drone(d, cx - 18, cy - 8, 4)
        _burst(d, cx + 26, cy + 12, 12)
    elif key == "shenzhen":  # red carpet, two flags, skyline
        _sky(d, box, (24, 68, 120), (70, 120, 170))
        for i, bx in enumerate(range(x0 + 4, x1 - 10, 14)):
            d.rectangle([bx, y1 - 26 - (i % 3) * 8, bx + 10, y1 - 12],
                        fill=(40, 50, 70))
        d.polygon([(x0, y1 - 12), (x1, y1 - 12), (x1, y1), (x0, y1)],
                  fill=(150, 20, 20))
        d.rectangle([x0 + 8, y0 + 6, x0 + 10, y0 + 34], fill=(220, 220, 220))
        d.rectangle([x0 + 10, y0 + 6, x0 + 30, y0 + 18], fill=(200, 30, 30))
        d.rectangle([x1 - 10, y0 + 6, x1 - 8, y0 + 34], fill=(220, 220, 220))
        d.rectangle([x1 - 30, y0 + 6, x1 - 10, y0 + 18], fill=(250, 250, 250))
        for i in range(4):
            d.rectangle([x1 - 28 + i * 5, y0 + 8 + (i // 2) * 5, x1 - 26 + i * 5,
                         y0 + 10 + (i // 2) * 5], fill=(30, 60, 160))
        d.ellipse([cx - 16, y1 - 30, cx - 8, y1 - 22], fill=(240, 200, 160))
        d.rectangle([cx - 16, y1 - 22, cx - 8, y1 - 12], fill=(30, 30, 30))
        d.ellipse([cx + 8, y1 - 30, cx + 16, y1 - 22], fill=(240, 200, 160))
        d.rectangle([cx + 8, y1 - 22, cx + 16, y1 - 12], fill=(90, 30, 30))
    elif key == "kyiv":  # night skyline, burst, EU stars band
        _sky(d, box, (10, 16, 36), (28, 40, 70))
        _stars(d, box, seed=3)
        for i, bx in enumerate(range(x0 + 4, x1 - 8, 16)):
            bh = 22 + (i * 7) % 18
            d.rectangle([bx, y1 - 12 - bh, bx + 12, y1 - 12], fill=(16, 20, 34))
        _burst(d, cx + 20, y0 + 22, 11)
        d.rectangle([x0, y1 - 12, x1, y1], fill=(20, 50, 140))
        import math
        for k in range(8):
            a = math.radians(k * 45)
            sx = cx + 16 * math.cos(a)
            sy = y1 - 6 + 4 * math.sin(a)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 220, 60))
    elif key == "voyager":  # deep space, gold probe
        d.rectangle(box, fill=(5, 5, 14))
        _stars(d, box, seed=5, n=22)
        d.ellipse([x0 + 8, y0 + 8, x0 + 14, y0 + 14], fill=(255, 240, 180))
        d.ellipse([x1 - 18, y1 - 16, x1 - 14, y1 - 12], fill=(90, 140, 220))
        d.line([(cx - 34, cy + 18), (cx + 6, cy - 6)], fill=(200, 170, 80), width=2)
        d.polygon([(cx + 6, cy - 16), (cx + 22, cy - 2), (cx + 6, cy + 10)],
                  fill=(220, 200, 140))
        d.rectangle([cx - 6, cy - 8, cx + 8, cy + 6], fill=(200, 160, 60))
        d.rectangle([cx - 30, cy - 2, cx - 6, cy + 2], fill=(160, 120, 40))
    elif key == "kerch":  # sea, broken bridge
        _sky(d, box, (120, 170, 200), (180, 205, 225))
        d.rectangle([x0, y1 - 22, x1, y1], fill=(40, 90, 130))
        d.polygon([(x0 + 6, y0 + 30), (cx - 6, y0 + 30), (cx - 6, y0 + 36),
                   (x0 + 6, y0 + 36)], fill=(90, 90, 90))
        d.polygon([(cx + 10, y0 + 44), (x1 - 6, y0 + 30), (x1 - 6, y0 + 36),
                   (cx + 10, y0 + 50)], fill=(90, 90, 90))
        d.line([(cx - 6, y0 + 36), (cx + 10, y0 + 44)], fill=(90, 90, 90), width=3)
        d.rectangle([cx - 2, y0 + 10, cx + 2, y0 + 36], fill=(70, 70, 70))
        d.ellipse([cx - 4, y0 + 30, cx + 12, y0 + 44], fill=(200, 200, 200))
    elif key == "france":  # crowd, banners, tricolore
        _sky(d, box, (200, 220, 235), (235, 235, 235))
        d.rectangle([x0, y0, x0 + 5, y1], fill=(0, 85, 164))
        d.rectangle([x0 + 5, y0, x0 + 10, y1], fill=(255, 255, 255))
        d.rectangle([x0 + 10, y0, x0 + 15, y1], fill=(239, 65, 53))
        import random
        rnd = random.Random(11)
        for _ in range(26):
            hx = rnd.randint(x0 + 20, x1 - 6)
            hy = rnd.randint(y0 + 30, y1 - 8)
            d.ellipse([hx, hy, hx + 5, hy + 5], fill=(40, 40, 40))
        d.rectangle([x0 + 24, y0 + 8, x0 + 26, y0 + 34], fill=(120, 80, 40))
        d.rectangle([x0 + 26, y0 + 8, x0 + 56, y0 + 18], fill=(163, 18, 18))
        d.rectangle([cx, y0 + 12, cx + 2, y0 + 38], fill=(120, 80, 40))
        d.rectangle([cx + 2, y0 + 12, cx + 30, y0 + 22], fill=(20, 80, 160))
    elif key == "alaska":  # star, dome, 56
        _sky(d, box, (30, 60, 100), (90, 130, 180))
        d.polygon([(cx, y0 + 6), (cx + 4, y0 + 16), (cx + 14, y0 + 16),
                   (cx + 6, y0 + 22), (cx + 10, y0 + 32), (cx, y0 + 26),
                   (cx - 10, y0 + 32), (cx - 6, y0 + 22), (cx - 14, y0 + 16),
                   (cx - 4, y0 + 16)], fill=(255, 220, 60))
        d.rectangle([x0 + 10, y1 - 22, x1 - 10, y1 - 12], fill=(240, 240, 240))
        d.pieslice([cx - 14, y1 - 38, cx + 14, y1 - 12], 180, 360,
                   fill=(240, 240, 240))
        d.rectangle([cx - 2, y1 - 44, cx + 2, y1 - 38], fill=(240, 240, 240))
    elif key == "ebola":  # map blob, red dots, cross
        d.rectangle(box, fill=(240, 235, 220))
        d.polygon([(cx - 20, y0 + 8), (cx + 4, y0 + 4), (cx + 16, y0 + 16),
                   (cx + 10, y0 + 36), (cx - 2, y0 + 52), (cx - 12, y0 + 40),
                   (cx - 22, y0 + 24)], fill=(200, 180, 140))
        for px, py in [(cx - 6, y0 + 18), (cx + 4, y0 + 26), (cx - 2, y0 + 34),
                       (cx + 8, y0 + 14)]:
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(180, 20, 20))
        d.rectangle([x1 - 20, y0 + 6, x1 - 16, y0 + 18], fill=(180, 20, 20))
        d.rectangle([x1 - 24, y0 + 10, x1 - 12, y0 + 14], fill=(180, 20, 20))
    elif key == "xavier":  # spiral over ocean
        d.rectangle(box, fill=(180, 210, 225))
        d.rectangle([x0, y1 - 14, x1, y1], fill=(120, 150, 110))
        import math
        for k in range(4):
            r0 = 6 + k * 7
            d.arc([cx - r0, cy - r0, cx + r0, cy + r0], 20 + k * 40,
                  200 + k * 40, fill=(255, 255, 255), width=3)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(60, 90, 120))
    elif key == "nvidia":  # green chip
        d.rectangle(box, fill=(30, 40, 30))
        for i in range(5):
            d.line([(x0 + 8, y0 + 10 + i * 10), (x0 + 22, y0 + 10 + i * 10)],
                   fill=(120, 200, 120), width=1)
            d.line([(x1 - 22, y0 + 10 + i * 10), (x1 - 8, y0 + 10 + i * 10)],
                   fill=(120, 200, 120), width=1)
        d.rectangle([cx - 20, cy - 16, cx + 20, cy + 16], fill=(40, 140, 60))
        d.rectangle([cx - 12, cy - 8, cx + 12, cy + 8], fill=(20, 100, 40))
        d.text((cx - 8, cy - 6), "AI", font=font(SANS_B, 11), fill=(255, 255, 255))
    elif key == "houthi":  # desert, missile trails
        _sky(d, box, (220, 180, 120), (235, 210, 160))
        d.rectangle([x0, y1 - 16, x1, y1], fill=(200, 170, 110))
        d.polygon([(x0, y1 - 16), (cx - 20, y0 + 34), (cx + 10, y1 - 16)],
                  fill=(170, 140, 90))
        for sx in (x0 + 14, cx - 4, x1 - 30):
            d.arc([sx, y0 + 4, sx + 34, y0 + 34], 200, 340,
                  fill=(255, 255, 255), width=2)
            _burst(d, sx + 30, y0 + 8, 5)
    elif key == "mq9":  # grey drone over desert
        _sky(d, box, (150, 190, 220), (220, 200, 170))
        d.polygon([(x0, y1 - 10), (cx - 30, y0 + 44), (cx + 20, y1 - 10)],
                  fill=(150, 130, 100))
        _drone(d, cx, cy - 6, 6, body=(80, 80, 80))
        d.line([(cx - 42, cy - 6), (cx - 30, cy + 14)], fill=(80, 80, 80), width=2)
    elif key == "tanker":  # ship, flame, waves
        _sky(d, box, (200, 120, 60), (230, 170, 100))
        d.rectangle([x0, y1 - 20, x1, y1], fill=(30, 70, 110))
        d.polygon([(x0 + 10, y1 - 20), (x1 - 10, y1 - 20), (x1 - 22, y1 - 8),
                   (x0 + 22, y1 - 8)], fill=(40, 40, 40))
        d.rectangle([cx - 12, y1 - 34, cx + 12, y1 - 20], fill=(120, 120, 120))
        _burst(d, cx + 26, y1 - 30, 10)
        for wx in range(x0 + 6, x1 - 6, 18):
            d.arc([wx, y1 - 8, wx + 12, y1 - 2], 0, 180, fill=(255, 255, 255),
                  width=1)
    elif key == "argentina":  # pitch, ball, 7-0
        d.rectangle(box, fill=(60, 160, 90))
        d.line([(x0, cy), (x1, cy)], fill=(255, 255, 255), width=2)
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=(255, 255, 255),
                  width=2)
        d.ellipse([x0 + 8, y0 + 8, x0 + 22, y0 + 22], fill=(255, 255, 255))
        d.text((x1 - 52, y0 + 6), "7–0", font=font(SANS_B, 20),
               fill=(255, 255, 255))
    elif key == "modi":  # two flags, podium
        _sky(d, box, (140, 190, 230), (220, 230, 240))
        d.rectangle([x0 + 10, y0 + 8, x0 + 12, y0 + 40], fill=(120, 90, 40))
        d.rectangle([x0 + 12, y0 + 8, x0 + 42, y0 + 18], fill=(255, 153, 51))
        d.rectangle([x0 + 12, y0 + 18, x0 + 42, y0 + 28], fill=(255, 255, 255))
        d.rectangle([x0 + 12, y0 + 28, x0 + 42, y0 + 38], fill=(19, 136, 8))
        d.rectangle([x1 - 12, y0 + 8, x1 - 10, y0 + 40], fill=(120, 90, 40))
        d.rectangle([x1 - 42, y0 + 8, x1 - 12, y0 + 16], fill=(180, 40, 40))
        d.rectangle([x1 - 42, y0 + 16, x1 - 12, y0 + 24], fill=(255, 255, 255))
        d.rectangle([x1 - 42, y0 + 24, x1 - 12, y0 + 32], fill=(40, 80, 160))
        d.rectangle([cx - 18, y1 - 18, cx + 18, y1 - 10], fill=(90, 60, 30))
        d.rectangle([cx - 12, y1 - 28, cx + 12, y1 - 18], fill=(120, 80, 40))
    elif key == "jets":  # sky, two jets, rising sun
        _sky(d, box, (90, 140, 200), (200, 220, 240))
        d.ellipse([x1 - 26, y0 + 6, x1 - 6, y0 + 26], fill=(200, 30, 30))
        for jx, jy in [(cx - 24, cy - 10), (cx + 8, cy + 4)]:
            d.polygon([(jx, jy), (jx + 26, jy + 4), (jx, jy + 8)],
                      fill=(70, 70, 70))
            d.polygon([(jx + 8, jy), (jx + 14, jy - 6), (jx + 18, jy)],
                      fill=(70, 70, 70))
        d.line([(x0 + 6, cy + 14), (x1 - 6, cy + 14)], fill=(255, 255, 255),
               width=1)
    else:
        d.rectangle(box, fill=(220, 220, 220))

# ---------------- world map ----------------
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-70, 45), (-75, 35), (-80, 25), (-90, 21), (-97, 16), (-105, 20),
     (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-40, -20), (-48, -28),
     (-58, -35), (-65, -40), (-70, -50), (-73, -40), (-75, -20), (-80, -5)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (40, 0), (35, -18), (30, -30), (20, -35),
     (15, -30), (10, -15), (8, 4), (-8, 5), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (32, 68), (40, 68),
     (45, 60), (40, 55), (35, 50), (30, 46), (28, 44), (23, 40), (19, 42),
     (15, 44), (12, 44), (8, 44), (3, 42), (-2, 37), (-9, 37)],
    [(32, 68), (45, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (160, 66), (162, 60), (158, 52), (150, 45), (140, 40),
     (135, 35), (130, 33), (127, 35), (122, 30), (120, 25), (115, 20),
     (108, 10), (105, 5), (100, 8), (95, 15), (92, 20), (88, 22), (80, 15),
     (77, 8), (75, 12), (70, 20), (65, 25), (60, 25), (55, 26), (50, 29),
     (48, 30), (45, 32), (42, 36), (40, 42), (35, 45), (32, 50), (30, 55),
     (32, 62)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -11), (137, -12), (135, -15), (132, -11),
     (130, -13), (126, -14), (122, -17), (118, -20)],
]

ALSO_COORDS = {
    17: (30.7, 46.5), 18: (4.35, 50.85), 19: (2.3, 48.9), 20: (8.7, 50.1),
    21: (2.3, 48.9), 22: (-9.1, 38.7), 23: (26.1, 44.4), 24: (100, 60),
    25: (-77, 38.9), 26: (-66.9, 10.5), 27: (-122, 37), 28: (-77, 38.9),
    29: (-77, 38.9), 30: (-98, 39), 31: (-74, 40.7), 32: (80, 13),
    33: (-80.5, 28.4), 34: (73, 33.7), 35: (103.8, 1.35), 36: (7.7, 45.1),
    37: (55.3, 25.2), 38: (80.3, 13.1), 39: (139.7, 35.7), 40: (34.5, 31.5),
    41: (-0.1, 51.5), 42: (44.2, 15.4), 43: (52, 26), 44: (4.3, 52.1),
    45: (7.5, 9.1), 46: (-17.4, 14.7), 47: (7.5, 9.1), 48: (-17.4, 14.7),
    49: (31.6, 4.85), 51: (85.3, 27.7), 52: (101.7, 3.1),
}


def draw_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=SEA)
    def px(lon, lat):
        x = x0 + (lon + 170) / 360.0 * (x1 - x0)
        y = y0 + (75 - lat) / 130.0 * (y1 - y0)
        return (x, y)
    for poly in CONTINENTS:
        d.polygon([px(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(180, 170, 150))
    for n, region, field, text, src in ALSO:
        if n in ALSO_COORDS:
            lon, lat = ALSO_COORDS[n]
            x, y = px(lon, lat)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=INK)
    # nudge crowded pins apart so the numbers never stack
    NUDGE = {1: (0, -9), 2: (-9, -7), 3: (-8, -8), 5: (7, 9), 11: (0, 9),
             12: (-11, -3), 13: (11, 7), 15: (9, 9), 16: (8, -8)}
    for s in STORIES[:16]:
        n, region, field, head, deck, src, status, lon, lat, art = s
        if lon is None:
            continue
        x, y = px(lon, lat)
        dx, dy = NUDGE.get(n, (0, 0))
        x, y = x + dx, y + dy
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=RED, outline=(255, 255, 255))
        f = font(SANS_B, 9)
        tw = d.textlength(str(n), font=f)
        d.text((x - tw / 2, y - 6), str(n), font=f, fill=(255, 255, 255))


# ---------------- page build ----------------

def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(STORIES) + len(ALSO)
    regions = {}
    fields = set()
    for s in STORIES:
        regions[s[1]] = regions.get(s[1], 0) + 1
        fields.add(s[2])
    for a in ALSO:
        regions[a[1]] = regions.get(a[1], 0) + 1
        fields.add(a[2])
    assert total == 52, total
    assert len(regions) == 7, regions
    assert len(fields) == 9, fields

    y = 10
    # top strip
    d.text((MARGIN, y), "THE WORLD TODAY", font=font(SANS_B, 11), fill=INK)
    strip = f"{total} STORIES · {len(regions)} REGIONS · {len(fields)} FIELDS · 16 DRAWN"
    tw = d.textlength(strip, font=font(SANS_B, 11))
    d.text((W - MARGIN - tw, y), strip, font=font(SANS_B, 11), fill=INK)
    y += 18
    rule(d, y, 2)
    y += 8
    # masthead
    title = "WEDNESDAY 18 NOVEMBER 2026"
    tf = font(SERIF_B, 52)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, y), title, font=tf, fill=INK)
    y += 62
    sub = "Everything on this page happened, or was first reported, on Wednesday 18 November 2026."
    sf = font(SERIF, 15)
    tw = d.textlength(sub, font=sf)
    d.text(((W - tw) / 2, y), sub, font=sf, fill=GREY)
    y += 24
    # region strip
    order = sorted(regions.items(), key=lambda kv: -kv[1])
    rtext = "  ·  ".join(f"{k} {v}" for k, v in order)
    rf = font(SANS_B, 11)
    tw = d.textlength(rtext, font=rf)
    d.text(((W - tw) / 2, y), rtext, font=rf, fill=RED)
    y += 18
    rule(d, y, 1)
    y += 6
    # timeline
    d.text((MARGIN, y), "THE DAY IN UTC", font=font(SANS_B, 11), fill=INK)
    y += 16
    slot_w = CW / 8
    tf2 = font(SANS_B, 10)
    bf = font(SANS, 10.5)
    for i, (label, n, text) in enumerate(TIMELINE):
        sx = MARGIN + i * slot_w
        d.text((sx + 2, y), label, font=tf2, fill=RED)
        lines = fit_text(d, text, bf, slot_w - 8)
        para(d, sx + 2, y + 13, lines[:3], bf, leading=12)
        if i:
            d.line([(sx, y - 2), (sx, y + 44)], fill=RULE, width=1)
    y += 48
    rule(d, y, 2)
    y += 8
    # big four: 2x2 grid
    cell_w = (CW - 16) // 2
    cell_h = 96
    for r in range(2):
        for c in range(2):
            s = STORIES[r * 2 + c]
            n, region, field, head, deck, src, status, lon, lat, art = s
            x = MARGIN + c * (cell_w + 16)
            img_box = (x, y, x + 148, y + 90)
            d.rectangle([img_box[0] - 1, img_box[1] - 1, img_box[2] + 1,
                         img_box[3] + 1], outline=INK, width=1)
            draw_art(d, img_box, art)
            tx = x + 158
            twd = cell_w - 158
            hf = font(SERIF_B, 16)
            lines = fit_text(d, f"{n}. {head}", hf, twd)
            yy = para(d, tx, y + 1, lines[:2], hf, leading=19)
            df = font(SANS, 11)
            lines = fit_text(d, deck, df, twd)
            yy = para(d, tx, yy + 2, lines[:2], df, leading=13)
            tag_text(d, tx, yy + 3, status, src, font(SANS_B, 9))
        y += cell_h + 8
    rule(d, y, 1)
    y += 6
    # medium twelve: 2 rows x 6
    mcell_w = (CW - 5 * 10) // 6
    mrow_h = 104
    for r in range(2):
        for c in range(6):
            s = STORIES[4 + r * 6 + c]
            n, region, field, head, deck, src, status, lon, lat, art = s
            x = MARGIN + c * (mcell_w + 10)
            img_box = (x, y, x + mcell_w, y + 48)
            d.rectangle([img_box[0] - 1, img_box[1] - 1, img_box[2] + 1,
                         img_box[3] + 1], outline=INK, width=1)
            draw_art(d, img_box, art)
            hf = font(SANS_B, 11)
            lines = fit_text(d, f"{n}. {head}", hf, mcell_w)
            yy = para(d, x, y + 54, lines[:3], hf, leading=13)
            tag_text(d, x, yy + 2, status, src, font(SANS_B, 8))
        y += mrow_h + 4
    rule(d, y, 1)
    y += 6
    # numbers strip
    d.text((MARGIN, y), "THE DAY IN NUMBERS", font=font(SANS_B, 11), fill=INK)
    y += 16
    col_w = CW / 4
    for i, (val, cap) in enumerate(NUMBERS):
        nx = MARGIN + i * col_w
        vf = font(SERIF_B, 30)
        d.text((nx, y), val, font=vf, fill=RED)
        cf = font(SANS, 10.5)
        d.text((nx, y + 36), cap, font=cf, fill=GREY)
        if i:
            d.line([(nx - 8, y), (nx - 8, y + 48)], fill=RULE, width=1)
    y += 50
    rule(d, y, 1)
    y += 6
    # map
    d.text((MARGIN, y), "WHERE IT HAPPENED", font=font(SANS_B, 11), fill=INK)
    y += 16
    map_h = 66
    draw_map(d, (MARGIN, y, W - MARGIN, y + map_h))
    y += map_h + 4
    lf = font(SANS, 9.5)
    leg = ("Red numbers = drawn stories 1–16  ·  dots = also on the page  ·  "
           "4 Voyager 1 is 26 billion km out, so it has no pin")
    d.text((MARGIN, y), leg, font=lf, fill=GREY)
    y += 15
    rule(d, y, 1)
    y += 6
    # also list: 4 columns x 9 rows
    d.text((MARGIN, y), "ALSO ON WEDNESDAY 18 NOVEMBER",
           font=font(SANS_B, 11), fill=INK)
    y += 16
    col_w2 = CW / 4
    af = font(SANS, 10.5)
    for i, a in enumerate(ALSO):
        n, region, field, text, src = a
        col = i // 9
        row = i % 9
        ax = MARGIN + col * col_w2
        ay = y + row * 13
        item = f"{n}. {text}"
        if d.textlength(item, font=af) > col_w2 - 6:
            while d.textlength(item + "…", font=af) > col_w2 - 6 and len(item) > 4:
                item = item[:-1]
            item += "…"
        d.text((ax, ay), item, font=af, fill=INK)
    y += 9 * 13 + 6
    rule(d, y, 1)
    y += 6
    # date check + sources
    df2 = font(SANS, 9.5)
    lines = fit_text(d, DATE_CHECK, df2, CW)
    y = para(d, MARGIN, y, lines, df2, fill=GREY, leading=12)
    lines = fit_text(d, SOURCES_LINE, df2, CW)
    y = para(d, MARGIN, y + 2, lines, df2, fill=GREY, leading=12)
    print(f"bottom y={y} (limit {H - 6}); regions={dict(sorted(regions.items(), key=lambda kv: -kv[1]))}; fields={len(fields)}")
    assert y <= H - 4, f"overflow: bottom y={y}"
    img.save(out_path, "PNG")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
