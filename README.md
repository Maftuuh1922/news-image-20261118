[![Bounty](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) [![Rank](https://make.fun/badge/news-image-20261118/Maftuuh1922/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) [![Reward](https://make.fun/badge/news-image-20261118/Maftuuh1922/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

# The World Today — 18 November 2026

A one-page front page summing up Wednesday 18 November 2026: **52 stories,
7 regions, 9 fields, 16 drawn**. Four big stories and twelve more carry small
flat-vector pictures drawn in code; a UTC timeline follows the day from the
overnight hours to late evening; a numbers strip, a world map with numbered
pins, and a numbered "also" list cover the rest; a date check says what was
deliberately left out and why.

The four big stories: Iran's drones hit a U.S. base in Kuwait; Xi hugs Trump
at Shenzhen as Putin waits; Russia pounds Kyiv's power grid as the EU proposes
a €45bn loan; Voyager 1 reaches one light-day from Earth. Every story on the
page was published or first reported on 18 November 2026 (see
`research-notes.md`); drawn stories carry a proof tag — CONFIRMED where the
event is established by a primary source or several outlets, CLAIM where it
rests on one party's word.

## Reproduce it

```bash
python3 render.py entry.png   # draw the page (deterministic: same bytes every run)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
# wrote out/entry.png (180536 bytes)
```

`render.py` needs only Python 3 and Pillow (`pip install pillow`). No network,
no external images: the 16 pictures are drawn with PIL primitives and the map
is drawn from hand-written continent outlines.

## Layout

- Masthead + region strip (Asia 14 · Europe 10 · Americas 10 · Middle East 8 ·
  Africa 6 · Global 3 · Oceania 1)
- The Day in UTC: 8 slots from overnight to late
- Stories 1–4, large, with pictures
- Stories 5–16, with pictures
- The Day in Numbers: 315 km/h · 11,000+ · 146,000 · $116bn
- Where It Happened: world map, pins 1–16, dots for the rest
- Also on Wednesday 18 November: stories 17–52
- Date check + sources

## License

MIT. See LICENSE.
