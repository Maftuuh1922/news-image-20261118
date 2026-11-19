#!/usr/bin/env python3
"""Draw the v2 front page for make.fun news-image-20261118.

A newspaper front page, 1024x1024, drawn with PIL from the verified
stories in research-notes.md. No network, no AI image generation, so
every headline stays sharp at any size.

Layout lessons from the v1 review, applied here:
  * masthead shrunk ~20% so the news grid gets the space;
  * lead headline balanced across two even lines;
  * body copy bigger and darker (no pale-grey summaries);
  * one featured story per column, set larger with extra air;
  * thin separators dropped inside the grid — whitespace groups
    the stories, strong rules only between big sections.

Run: python3 render.py   -> writes entry.png next to this file.
"""
from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 40
CONTENT_W = PAGE_W - 2 * MARGIN

INK = (20, 20, 20)
BODY = (45, 45, 45)
FAINT = (96, 96, 96)
RED = (164, 24, 44)
PAPER = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def lines_for(draw, text, fnt, max_w):
    """Greedy wrap: split text into lines no wider than max_w."""
    out, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def balanced_pair(draw, text, fnt, max_w):
    """Split a headline into two lines of near-equal visual weight.

    Tries every word boundary and keeps the split whose wider line
    is narrowest, breaking ties toward the more even pair.
    """
    words = text.split()
    best = None
    for cut in range(1, len(words)):
        first = " ".join(words[:cut])
        second = " ".join(words[cut:])
        w1 = draw.textlength(first, font=fnt)
        w2 = draw.textlength(second, font=fnt)
        if w1 > max_w or w2 > max_w:
            continue
        score = (max(w1, w2), abs(w1 - w2))
        if best is None or score < best[0]:
            best = (score, [first, second])
    if best is None:
        return lines_for(draw, text, fnt, max_w)
    return best[1]


def spaced(draw, xy, text, fnt, fill, gap=2):
    """Draw a kicker with a little air between its letters."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + gap
    return x


def hline(draw, y, x0=MARGIN, x1=PAGE_W - MARGIN, width=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(draw, x, y0, y1, width=1, fill=INK):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


LEAD = {
    "kicker": "THE GULF — WAR WIDENS",
    "headline": "Gulf war widens as Iran drones hit U.S. base in Kuwait",
    "dek": ("Tehran says its drones struck Patriot systems at Ali Al Salem "
            "air base; Bahrain repels a third attack in a week, a day after "
            "U.S. jets hit a missile site on Qeshm Island."),
}

SECOND = [
    {
        "kicker": "SUMMIT EVE — SHENZHEN",
        "headline": "Xi hosts Putin as Trump heads for first trilateral talks",
        "dek": ("APEC opens in Shenzhen; Xi urges AI co-operation and free "
                "trade. Trump stops in Manila for Quad talks first."),
    },
    {
        "kicker": "UKRAINE — KERCH BRIDGE",
        "headline": "Ukraine strike drops bridge road span into the strait",
        "dek": ("Two killed; road traffic closed, rail resumes after a "
                "seven-stage operation planned over weeks, Zelensky says."),
    },
]

# (headline, dek) per column. The first item of each column is the
# featured story and is set larger. All 25 stories are the verified
# ones from research-notes.md — same facts as v1, tighter wording.
GRID = [
    ("MIDDLE EAST", [
        ("Houthi attacks on Saudi intercepted",
         "Coalition struck 60 Houthi targets; a cruise missile aimed at Riyadh was destroyed"),
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
         "Democrats take 56 seats after a historic upset"),
        ("146,000 march in France as unions strike",
         "Protests over living costs sweep the country"),
        ("EU adds 145 Russian entities to sanctions",
         "Brussels proposes a further €45bn for Kyiv"),
        ("U.S. outages hit Microsoft and Chase",
         "Air traffic control hit; no sign of a malign actor"),
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

BRIEF = ("Romania quake 5.3  ·  Russian crash kills 19  ·  "
         "Fiji drought disaster  ·  Nigeria–S. Africa row eases")

# Numbers already stated in the stories above, pulled out for the
# reader who only scans: every figure is verified in research-notes.md.
NUMBERS = [
    ("315 km/h", "Cyclone Xavier gusts in the Cook Islands"),
    ("11,000+", "Ebola cases in DR Congo"),
    ("146,000", "marchers in France over living costs"),
    ("$116bn", "Nvidia quarterly revenue"),
]


def draw_top(draw):
    """Top info bar, masthead, date line. Returns the y below them."""
    f_info = load(SANS, 12)
    draw.text((MARGIN, 14), "VOL. I  ·  NO. 322", font=f_info, fill=FAINT)
    right = "ONE DAY  ·  ONE PAGE"
    draw.text((PAGE_W - MARGIN - draw.textlength(right, font=f_info), 14),
              right, font=f_info, fill=FAINT)
    hline(draw, 34)

    f_mast = load(SERIF_BOLD, 70)
    mast = "THE WORLD TODAY"
    draw.text(((PAGE_W - draw.textlength(mast, font=f_mast)) / 2, 40),
              mast, font=f_mast, fill=INK)
    hline(draw, 118, width=3)
    hline(draw, 123, width=2, fill=RED)

    f_date = load(SANS_BOLD, 24)
    date = "WEDNESDAY, 18 NOVEMBER 2026"
    draw.text(((PAGE_W - draw.textlength(date, font=f_date)) / 2, 130),
              date, font=f_date, fill=RED)
    f_tag = load(SANS, 13)
    tag = "25 STORIES  ·  FIVE CONTINENTS  ·  FROM REUTERS, BBC, AL JAZEERA, AFP, AP"
    draw.text(((PAGE_W - draw.textlength(tag, font=f_tag)) / 2, 160),
              tag, font=f_tag, fill=FAINT)
    hline(draw, 184)
    return 194


def draw_lead(draw, y):
    """Lead story: kicker, balanced two-line headline, dek."""
    spaced(draw, (MARGIN, y), LEAD["kicker"], load(SANS_BOLD, 17), RED)
    y += 28
    f_head = load(SERIF_BOLD, 44)
    for line in balanced_pair(draw, LEAD["headline"], f_head, CONTENT_W):
        draw.text((MARGIN, y), line, font=f_head, fill=INK)
        y += 50
    y += 6
    f_dek = load(SERIF, 19)
    for line in lines_for(draw, LEAD["dek"], f_dek, CONTENT_W):
        draw.text((MARGIN, y), line, font=f_dek, fill=BODY)
        y += 25
    hline(draw, y + 10)
    return y + 22


def draw_second(draw, y):
    """Two stories side by side under the lead."""
    col_w = (CONTENT_W - 24) // 2
    x_right = MARGIN + col_w + 24
    top = y
    bottom = top
    for i, story in enumerate(SECOND):
        x = MARGIN if i == 0 else x_right
        yy = top
        spaced(draw, (x, yy), story["kicker"], load(SANS_BOLD, 14), RED)
        yy += 22
        f_h = load(SERIF_BOLD, 24)
        for line in lines_for(draw, story["headline"], f_h, col_w):
            draw.text((x, yy), line, font=f_h, fill=INK)
            yy += 28
        yy += 4
        f_d = load(SANS, 14)
        for line in lines_for(draw, story["dek"], f_d, col_w):
            draw.text((x, yy), line, font=f_d, fill=BODY)
            yy += 18
        bottom = max(bottom, yy)
    vline(draw, MARGIN + col_w + 12, top + 2, bottom - 4)
    hline(draw, bottom + 10)
    return bottom + 22


def draw_grid(draw, y):
    """Three columns; first story per column is featured (larger)."""
    col_w = (CONTENT_W - 2 * 22) // 3
    xs = [MARGIN, MARGIN + col_w + 22, MARGIN + 2 * (col_w + 22)]
    top = y
    end = top
    f_lab = load(SANS_BOLD, 15)
    f_feat_h = load(SERIF_BOLD, 19)
    f_feat_d = load(SANS, 13)
    f_h = load(SERIF_BOLD, 16)
    f_d = load(SANS, 13)
    for ci, (label, items) in enumerate(GRID):
        x = xs[ci]
        yy = top
        spaced(draw, (x, yy), label, f_lab, RED, gap=1)
        yy += 22
        hline(draw, yy, x0=x, x1=x + col_w, width=1)
        yy += 10
        for si, (head, dek) in enumerate(items):
            if si == 0:
                for line in lines_for(draw, head, f_feat_h, col_w):
                    draw.text((x, yy), line, font=f_feat_h, fill=INK)
                    yy += 23
                for line in lines_for(draw, dek, f_feat_d, col_w):
                    draw.text((x, yy), line, font=f_feat_d, fill=BODY)
                    yy += 17
                yy += 12
            else:
                for line in lines_for(draw, head, f_h, col_w):
                    draw.text((x, yy), line, font=f_h, fill=INK)
                    yy += 20
                for line in lines_for(draw, dek, f_d, col_w):
                    draw.text((x, yy), line, font=f_d, fill=BODY)
                    yy += 17
                yy += 9
        end = max(end, yy)
    for x in (xs[1] - 11, xs[2] - 11):
        vline(draw, x, top, end - 4)
    return end


def draw_brief(draw, y):
    """One-line IN BRIEF strip and the closing rule."""
    hline(draw, y)
    y += 10
    f_b = load(SANS_BOLD, 12)
    draw.text((MARGIN, y), "IN BRIEF", font=f_b, fill=RED)
    f_t = load(SANS, 12)
    draw.text((MARGIN + 92, y), BRIEF, font=f_t, fill=BODY)
    y += 18
    hline(draw, y, width=2)
    return y


def draw_numbers(draw, y):
    """THE DAY IN NUMBERS: four verified figures, big and scannable."""
    y += 12
    spaced(draw, (MARGIN, y), "THE DAY IN NUMBERS", load(SANS_BOLD, 14), RED)
    y += 24
    col_w = (CONTENT_W - 3 * 20) // 4
    xs = [MARGIN + i * (col_w + 20) for i in range(4)]
    f_num = load(SERIF_BOLD, 25)
    f_lab = load(SANS, 12)
    bottom = y
    for i, (num, lab) in enumerate(NUMBERS):
        x = xs[i]
        draw.text((x, y), num, font=f_num, fill=RED)
        yy = y + 32
        for line in lines_for(draw, lab, f_lab, col_w):
            draw.text((x, yy), line, font=f_lab, fill=BODY)
            yy += 16
        bottom = max(bottom, yy)
    return bottom


def main():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)
    y = draw_top(draw)
    print("after top:", y)
    y = draw_lead(draw, y)
    print("after lead:", y)
    y = draw_second(draw, y)
    print("after second:", y)
    y = draw_grid(draw, y)
    print("after grid:", y)
    y = draw_brief(draw, y)
    print("after brief:", y)
    y = draw_numbers(draw, y)
    print("after numbers:", y)
    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
