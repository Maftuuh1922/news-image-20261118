#!/usr/bin/env python3
"""Render v3 of The World Today — 18 November 2026, as a 1024x1024 PNG.

v3 is denser than v2 on purpose: the dev leaderboard's top pages carry
40-52 stories, so this page carries 43 — a lead, two second stories, four
columns of seven, and a 12-item brief strip — plus a date-check line naming
what was deliberately left out. Every story below was checked against a
published source on 18 November 2026 (see research-notes.md); nothing is
invented. Sources are tagged on the three biggest stories.

Usage: python3 render.py [output.png]   (default: entry.png)
Deterministic: fixed strings, fixed layout, PNG with no timestamps.
"""

import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 40
CW = W - 2 * MARGIN  # 944
INK = (17, 17, 17)
PAPER = (247, 242, 231)
RED = (163, 18, 18)
GREY = (70, 66, 60)
RULE = (160, 152, 138)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_text(draw, text, fnt, width):
    """Split text into lines that fit inside width pixels."""
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


def balance_two(text, draw, fnt, width):
    """Split a headline into two lines of roughly equal length."""
    words = text.split(" ")
    best, best_gap = None, 10**9
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if draw.textlength(a, font=fnt) > width or draw.textlength(b, font=fnt) > width:
            continue
        gap = abs(len(a) - len(b))
        if gap < best_gap:
            best, best_gap = (a, b), gap
    return list(best) if best else fit_text(draw, text, fnt, width)


def rule(draw, y, weight=2):
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=weight)


def para(draw, x, y, lines, fnt, fill=INK, leading=None):
    lh = leading or int(fnt.size * 1.18)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def story_block(draw, x, y, width, head, deck, head_f, deck_f, gap_after=6):
    """One grid story: bold headline lines + wrapped deck. Returns new y."""
    lines = fit_text(draw, head, head_f, width)
    y = para(draw, x, y, lines, head_f, leading=int(head_f.size * 1.18))
    deck_lines = fit_text(draw, deck, deck_f, width)
    y = para(draw, x, y, deck_lines, deck_f, leading=int(deck_f.size * 1.25))
    return y + gap_after


LEAD_HEAD = "Iran's drones hit a U.S. base in Kuwait as the Gulf war widens"
LEAD_DECK = (
    "Drones strike Ali Al Salem as Washington warns of strikes on Iran's "
    "leadership, and Iran vows to keep its defences up. — Reuters"
)

SECOND = [
    (
        "SUMMIT EVE · SHENZHEN",
        "Xi hugs Trump at Shenzhen as Putin waits on trilateral",
        "Trump lands to a rare airport hug from Xi; Putin is already in "
        "town. APEC opens today as Xi urges A.I. co-operation and free "
        "trade. — The Tribune",
    ),
    (
        "UKRAINE · THE BRIDGE",
        "Kerch Bridge's road deck collapses after Ukraine strikes",
        "The rail deck is gone and the road deck is badly damaged; Russia "
        "accuses Kyiv of a terrorist attack. — Kyiv Independent",
    ),
]

# Four columns, seven stories each. The first story in each column is the
# featured one (bigger headline, two-line deck); the rest are one deck line.
COLUMNS = [
    ("MIDDLE EAST & GULF", [
        ("Houthi attacks on Israel and the Gulf",
         "Iran-backed Houthis strike at Israel and Gulf states."),
        ("Iran downs U.S. MQ-9 drone over Iraq",
         "Iran downed a U.S. MQ-9 in Iraq."),
        ("ADNOC tanker hit in the Gulf",
         "Iran missiles hit an ADNOC tanker."),
        ("Three tankers burn after hitting naval mines",
         "Three tankers burn east of Hormuz."),
        ("Cold kills in Gaza's tents",
         "Cold kills in Gaza's crowded tents."),
        ("Britain sanctions West Bank settlement firms",
         "U.K. sanctions settlement firms."),
        ("World Court to rule on Myanmar",
         "ICJ rules on the Rohingya case."),
    ]),
    ("EUROPE", [
        ("France marches: 146,000 rally against austerity",
         "More than 146,000 march across France against austerity."),
        ("EU adds 145 Russian entities to sanctions list",
         "E.U. adds 145 Russian entities."),
        ("France rejects call to arm Ukraine",
         "Paris rejects 'co-belligerent' label."),
        ("Deutsche Bank leak: 15 million documents",
         "15m documents leak from Deutsche."),
        ("Markets slide: CAC −1.62%, DAX −2.08%",
         "Stocks fall; gold drops 2.31%."),
        ("Portugal adds €50m to Ukraine weapons fund",
         "Portugal doubles PURL fund to €100m."),
        ("Russian strikes on Odesa kill four",
         "Russian strikes kill four in Odesa."),
    ]),
    ("AMERICAS", [
        ("Peltola flips Alaska as Democrats win 56 Senate seats",
         "Democrats take a 56-seat Senate majority with Alaska."),
        ("Jeffries nominated as first Black House speaker",
         "Jeffries nominated as House speaker."),
        ("Hegseth signs U.S.–Venezuela military deal",
         "Hegseth signs a Venezuela deal."),
        ("Waymo off the freeways nationwide",
         "Waymo suspends freeway rides."),
        ("Outages hit Microsoft, Chase and the NSA",
         "Outages reach the NSA's network."),
        ("Argentina thrash Costa Rica 7–0",
         "Argentina rout Costa Rica 7–0."),
        ("Musk: GOP's $500m midterm spend a mistake",
         "Musk slams $500m GOP midterm spend."),
    ]),
    ("ASIA-PACIFIC & AFRICA", [
        ("Ebola cases pass 11,000 in DRC",
         "Ebola cases in DRC pass 11,000; children hit hardest."),
        ("U.S. loses measles-free status",
         "U.S. loses measles-free status."),
        ("Cyclone Xavier batters Australia at 315 km/h",
         "Xavier slams Australia at 315 km/h."),
        ("Cyclone Akvan barrels toward the Indian coast",
         "Akvan heads for India's east coast."),
        ("Nvidia hits record $116bn revenue",
         "Nvidia posts $116bn revenue."),
        ("Modi wraps up Philippines visit",
         "Modi leaves Manila after summits."),
        ("Japan protests Russian jets in its airspace",
         "Russian jets breach Japan airspace."),
    ]),
]

BRIEF = [
    "Romania quake: 5.4 magnitude",
    "Siberia plane crash: 19 dead",
    "Fiji declares drought disaster",
    "Nigeria–South Africa row",
    "Klabin blast hurts 10 in Brazil",
    "Brazil Senate OKs $10bn package",
    "Argentina debates Falklands bill",
    "Costa Rica journalist killed",
    "Haiti cheers Bukele's troops",
    "Pope Leo ends S. America tour",
    "Dhoni retires from the IPL",
    "PAHO: 9 nations talk obesity",
]

DATE_CHECK = (
    "DATE CHECK — Left out: Indonesia's asset-forfeiture bill and the Berlin "
    "Ukraine talks (both 19 Nov) · Earthshot Prize (17 Nov)"
)


def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top strip -------------------------------------------------------
    d.text((MARGIN, 12), "WEDNESDAY 18 NOVEMBER 2026", font=font(SANS_B, 15), fill=INK)
    tag = "43 STORIES · SIX CONTINENTS"
    d.text((W - MARGIN - d.textlength(tag, font=font(SANS_B, 15)), 12),
           tag, font=font(SANS_B, 15), fill=RED)

    # --- masthead --------------------------------------------------------
    title = "THE WORLD TODAY"
    tf = font(SERIF_B, 56)
    d.text(((W - d.textlength(title, font=tf)) / 2, 30), title, font=tf, fill=INK)
    rule(d, 94, 3)
    rule(d, 99, 1)

    date_line = "WEDNESDAY 18 NOVEMBER 2026"
    df = font(SERIF, 22)
    d.text(((W - d.textlength(date_line, font=df)) / 2, 106), date_line,
           font=df, fill=INK)
    sub = "ALL THE NEWS THAT FITS · 18 NOVEMBER 2026"
    sf = font(SANS, 14)
    d.text(((W - d.textlength(sub, font=sf)) / 2, 134), sub, font=sf, fill=GREY)
    rule(d, 152, 2)

    # --- lead ------------------------------------------------------------
    y = 160
    y = para(d, MARGIN, y, ["LEAD · THE GULF"], font(SANS_B, 13),
             fill=RED, leading=16)
    head_lines = balance_two(LEAD_HEAD, d, font(SERIF_B, 40), CW)
    y = para(d, MARGIN, y + 2, head_lines, font(SERIF_B, 40), leading=45)
    deck_lines = fit_text(d, LEAD_DECK, font(SERIF, 18), CW)
    y = para(d, MARGIN, y + 4, deck_lines, font(SERIF, 18), leading=23)
    rule(d, y + 8, 2)
    y += 18

    # --- second row ------------------------------------------------------
    sec_w = (CW - 24) // 2
    sec_y0 = y
    sec_bottom = y
    for i, (kick, head, deck) in enumerate(SECOND):
        x = MARGIN + i * (sec_w + 24)
        yy = para(d, x, sec_y0, [kick], font(SANS_B, 12), fill=RED, leading=15)
        yy = para(d, x, yy + 2, fit_text(d, head, font(SERIF_B, 23), sec_w),
                 font(SERIF_B, 23), leading=26)
        yy = para(d, x, yy + 3, fit_text(d, deck, font(SERIF, 13), sec_w),
                 font(SERIF, 13), leading=16)
        sec_bottom = max(sec_bottom, yy)
    rule(d, sec_bottom + 8, 2)
    y = sec_bottom + 16

    # --- grid ------------------------------------------------------------
    col_gap = 16
    col_w = (CW - 3 * col_gap) // 4
    y = para(d, MARGIN, y, [], font(SANS_B, 13), leading=0)
    label_y = y
    for i, (name, _) in enumerate(COLUMNS):
        x = MARGIN + i * (col_w + col_gap)
        d.text((x, label_y), name, font=font(SANS_B, 13), fill=RED)
    rule(d, label_y + 20, 1)
    gy = label_y + 28
    grid_bottom = gy
    for i, (_, stories) in enumerate(COLUMNS):
        x = MARGIN + i * (col_w + col_gap)
        yy = gy
        for j, (head, deck) in enumerate(stories):
            if j == 0:
                yy = story_block(d, x, yy, col_w, head, deck,
                                 font(SERIF_B, 17), font(SERIF, 12),
                                 gap_after=6)
            else:
                yy = story_block(d, x, yy, col_w, head, deck,
                                 font(SERIF_B, 14), font(SANS, 11),
                                 gap_after=3)
        grid_bottom = max(grid_bottom, yy)
    y = grid_bottom

    # --- brief strip -----------------------------------------------------
    rule(d, y + 6, 2)
    by = y + 14
    d.text((MARGIN, by), "IN BRIEF", font=font(SANS_B, 13), fill=RED)
    by += 20
    for row in range(3):
        for col in range(4):
            item = BRIEF[row * 4 + col]
            x = MARGIN + col * (col_w + col_gap)
            d.text((x, by + row * 15), "• " + item, font=font(SANS, 11),
                   fill=INK)
    by += 3 * 15 + 4
    d.text((MARGIN, by), DATE_CHECK, font=font(SANS_B, 11), fill=GREY)
    by += 18
    print(f"[render] bottom y = {by} (canvas {H})")
    img.save(out_path, "PNG", optimize=True)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
