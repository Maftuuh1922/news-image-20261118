#!/usr/bin/env python3
"""Render the front page for news-image-20261118.

Draws a newspaper front page (1024x1024) with PIL from the verified
stories in research-notes.md. No network, no AI image generation:
every glyph is rendered from system fonts, so the text stays crisp.
Run: python3 render.py  -> writes entry.png beside this file.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
INK = (17, 17, 17)
RED = (166, 25, 46)
GREY = (110, 110, 110)
PAPER = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MX = 36                      # side margin
CW = W - 2 * MX              # content width


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(draw, xy, text, fnt, fill, tracking=2):
    """Draw text with extra space between characters (for kickers)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def rule(draw, y, x0=MX, x1=W - MX, width=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vrule(draw, x, y0, y1, width=1, fill=INK):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


LEAD = {
    "kicker": "THE GULF  —  WAR WIDENS",
    "headline": "Gulf war widens as Iran drones hit U.S. base in Kuwait",
    "dek": ("Tehran says its drones struck Patriot systems at Ali Al Salem "
            "air base; Bahrain repels a third attack in a week, a day after "
            "U.S. jets hit a missile site on Qeshm Island."),
}

SECOND = [
    {
        "kicker": "SUMMIT EVE  —  SHENZHEN",
        "headline": "Xi hosts Putin as Trump heads for first trilateral talks",
        "dek": ("APEC opens in Shenzhen; Xi urges AI co-operation and free "
                "trade. Trump stops in Manila for Quad talks first."),
    },
    {
        "kicker": "UKRAINE  —  KERCH BRIDGE",
        "headline": "Ukraine strike drops bridge road span into the strait",
        "dek": ("Two killed; road traffic closed, rail resumes after a "
                "seven-stage operation planned over weeks, Zelensky says."),
    },
]

COLUMNS = [
    ("MIDDLE EAST", [
        ("Houthi attacks on Saudi intercepted",
         "Coalition says it struck 60 Houthi targets"),
        ("Iran downs U.S. MQ-9 near Hormuz",
         "Drone shot down near the strait, Tehran says"),
        ("ADNOC tanker hit; one missing, 11 hurt",
         "Vessel struck as Gulf shipping comes under fire"),
        ("Cold kills displaced in Gaza tents",
         "Winter bites in camps with little shelter"),
        ("Britain sanctions West Bank builders",
         "Australia lists Weiss, Amana, Nachala"),
        ("World Court to rule on Myanmar case",
         "ICJ genocide ruling due Thursday"),
    ]),
    ("EUROPE & AMERICAS", [
        ("Peltola flips Alaska Senate seat",
         "Democrats take 56 seats after historic upset"),
        ("146,000 march in France as unions strike",
         "Protests over living costs sweep the country"),
        ("EU adds 145 Russian entities to sanctions",
         "Brussels proposes a further €45bn for Kyiv"),
        ("U.S. outages hit Microsoft and Chase",
         "Air traffic control hit; no sign of malign actor"),
        ("Waymo pulls robotaxis off U.S. freeways",
         "California calls them an “imminent hazard”"),
        ("France rejects “co-belligerent” claim",
         "Paris: no troops fighting in Ukraine"),
    ]),
    ("ASIA-PACIFIC & AFRICA", [
        ("Ebola in Congo passes 11,000 cases",
         "5,400 dead; three in four young children die"),
        ("U.S. loses measles-free status",
         "5,400 cases and 10 deaths after 26 years"),
        ("Cyclone Xavier, Cat. 5, hits Cooks",
         "Gusts to 315 km/h; Pukapuka warned"),
        ("Cyclone Akvan nears Andhra coast",
         "Landfall expected on Friday, India warns"),
        ("Nvidia beats forecasts; futures rally",
         "Revenue about $116bn; Dow fell 849 the day before"),
        ("Dhoni retires from IPL after 19 seasons",
         "Chennai legend to mentor the Super Kings"),
    ]),
]

IN_BRIEF = ("IN BRIEF  —  Romania quake 5.3  ·  Russian crash kills 19  ·  "
            "Fiji drought disaster  ·  Nigeria–S. Africa row eases")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top info bar -------------------------------------------------
    f_info = font(SANS, 13)
    d.text((MX, 14), "VOL. I  ·  NO. 322", font=f_info, fill=GREY)
    right = "ONE DAY  ·  ONE PAGE"
    d.text((W - MX - d.textlength(right, font=f_info), 14), right,
           font=f_info, fill=GREY)
    rule(d, 36)

    # ---- masthead ------------------------------------------------------
    f_mast = font(SERIF_B, 92)
    mast = "THE WORLD TODAY"
    d.text(((W - d.textlength(mast, font=f_mast)) / 2, 44), mast,
           font=f_mast, fill=INK)
    rule(d, 142, width=4)
    rule(d, 148, width=2, fill=RED)

    # ---- date line ------------------------------------------------------
    f_date = font(SANS_B, 30)
    date = "WEDNESDAY, 18 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 158), date,
           font=f_date, fill=RED)
    f_tag = font(SANS, 15)
    tag = "25 STORIES  ·  FIVE CONTINENTS  ·  THE DAY IN WORLD NEWS"
    d.text(((W - d.textlength(tag, font=f_tag)) / 2, 196), tag,
           font=f_tag, fill=GREY)
    rule(d, 220)

    # ---- lead story ------------------------------------------------------
    y = 232
    f_kick = font(SANS_B, 19)
    draw_tracked(d, (MX, y), LEAD["kicker"], f_kick, RED, tracking=2)
    y += 30
    f_head = font(SERIF_B, 54)
    for line in wrap(d, LEAD["headline"], f_head, CW):
        d.text((MX, y), line, font=f_head, fill=INK)
        y += 60
    y += 4
    f_dek = font(SERIF, 20)
    for line in wrap(d, LEAD["dek"], f_dek, CW):
        d.text((MX, y), line, font=f_dek, fill=INK)
        y += 26
    rule(d, y + 8)
    y += 16

    # ---- second row: two stories ----------------------------------------
    col_w = (CW - 24) // 2
    x1 = MX + col_w + 24
    y2_top = y
    y2_end = y2_top
    for i, s in enumerate(SECOND):
        x = MX if i == 0 else x1
        yy = y2_top
        draw_tracked(d, (x, yy), s["kicker"], font(SANS_B, 15), RED)
        yy += 24
        f_h2 = font(SERIF_B, 27)
        for line in wrap(d, s["headline"], f_h2, col_w):
            d.text((x, yy), line, font=f_h2, fill=INK)
            yy += 31
        yy += 3
        f_d2 = font(SANS, 14)
        for line in wrap(d, s["dek"], f_d2, col_w):
            d.text((x, yy), line, font=f_d2, fill=INK)
            yy += 19
        y2_end = max(y2_end, yy)
    vrule(d, MX + col_w + 12, y2_top + 2, y2_end - 4)
    y = y2_end + 8
    rule(d, y)
    y += 12

    # ---- grid: three columns, six stories each ---------------------------
    grid_top = y
    col_w = (CW - 2 * 20) // 3
    xs = [MX, MX + col_w + 20, MX + 2 * (col_w + 20)]
    f_lab = font(SANS_B, 15)
    f_h3 = font(SERIF_B, 17)
    f_d3 = font(SANS, 12)
    grid_end = grid_top
    for ci, (label, items) in enumerate(COLUMNS):
        x = xs[ci]
        yy = grid_top
        draw_tracked(d, (x, yy), label, f_lab, RED, tracking=1)
        yy += 22
        rule(d, yy, x0=x, x1=x + col_w, width=1)
        yy += 8
        for h, dek in items:
            for line in wrap(d, h, f_h3, col_w):
                d.text((x, yy), line, font=f_h3, fill=INK)
                yy += 20
            for line in wrap(d, dek, f_d3, col_w):
                d.text((x, yy), line, font=f_d3, fill=GREY)
                yy += 16
            yy += 7
            rule(d, yy, x0=x, x1=x + col_w, width=1, fill=(210, 210, 210))
            yy += 7
        grid_end = max(grid_end, yy)
    for x in (xs[1] - 10, xs[2] - 10):
        vrule(d, x, grid_top, grid_end - 4)
    y = grid_end + 10
    rule(d, y)
    y += 10

    # ---- in brief strip ---------------------------------------------------
    f_ib = font(SANS, 13)
    f_ib_b = font(SANS_B, 13)
    d.text((MX, y), "IN BRIEF", font=f_ib_b, fill=RED)
    brief = IN_BRIEF.split("—", 1)[1].strip()
    for line in wrap(d, brief, f_ib, CW - 110):
        d.text((MX + 96, y), line, font=f_ib, fill=INK)
        y += 19
    y += 4
    rule(d, y, width=2)
    y += 8

    # ---- footer ------------------------------------------------------------
    f_ft = font(SANS, 12)
    foot = ("Compiled from Reuters, BBC, Al Jazeera, AFP, AP and others  ·  "
            "All events of Wednesday 18 November 2026")
    d.text(((W - d.textlength(foot, font=f_ft)) / 2, y), foot,
           font=f_ft, fill=GREY)

    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
