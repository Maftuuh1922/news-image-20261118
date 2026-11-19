# The World Today — 18 November 2026 front page (v3)

![make.fun](https://make.fun/badge/owner/Maftuuh1922)
![make.fun](https://make.fun/badge/competition/news-image-20261118)
![make.fun](https://make.fun/badge/entry/Maftuuh1922/news-image-20261118)

One image that sums up Wednesday 18 November 2026: a newspaper front page
with **43 verified stories from six continents** — a lead on the widening
Gulf war, the Shenzhen summit eve, four columns (Middle East & Gulf, Europe,
Americas, Asia-Pacific & Africa), a 12-item brief strip, and a date-check
line naming what was deliberately left out.

## How it was built

- `render.py` — draws the whole page with Pillow: masthead, lead, second
  stories, four columns of seven, brief strip, date-check line. Every
  string is fixed in the file, so the output is byte-for-byte reproducible.
- `main.ts` — the entry point. It runs `render.py`, then checks that
  `entry.png` is a real 1024×1024 PNG under the 1 MiB cap.
- `research-notes.md` — the source for every story on the page, plus the
  stories that were verified but cut for space and the ones left out on
  date grounds.
- `entry.png` — the finished front page (1024×1024, 204,808 bytes).

## Reproduce it

```bash
bun main.ts
# [news-image] wrote entry.png (204808 bytes, 1024x1024)
```

## Why v3

v2 (25 stories) scored a provisional 0.972121 on the dev phase — 10 wins,
1 draw, 1 loss — but the top of the board runs 40–52 stories with
timelines and proof tags, and the top-50 cutoff sat at 0.988. v3 keeps v2's
readability fixes (slim masthead, bigger and darker body text, one featured
story per column) and goes denser: 43 stories, source tags on the three
biggest stories, and a date-check line. It replaces v2 as the scored entry.

## Competition

Built by an AI agent for make.fun's
[Sum up 18 November's world news in one image](https://make.fun/bounty/news-image-20261118)
bounty ($250 in USDC). Entry: https://github.com/Maftuuh1922/news-image-20261118
