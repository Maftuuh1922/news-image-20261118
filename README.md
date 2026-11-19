# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Maftuuh1922/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Maftuuh1922/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A newspaper front page ("THE WORLD TODAY") summing up the world's news of Wednesday 18 November 2026 — 25 verified stories across five continents: the Gulf war widening, the Trump–Xi–Putin summit eve in Shenzhen, the Kerch Bridge strike, Peltola flipping Alaska, Ebola in Congo, Cyclone Xavier, Nvidia's earnings beat, Dhoni's IPL retirement, and more. Drawn programmatically with PIL, so every headline is crisp and legible — no AI image generation. Every story was verified against a source on the day; see `research-notes.md` for the list and sources.

## Files

- `entry.png` — the front page (1024×1024, PNG, 163,835 bytes)
- `render.py` — the renderer that draws `entry.png` from the story list
- `research-notes.md` — the 25 verified stories and their sources
- `main.ts` — the entry program: copies `entry.png` to the output dir

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

The program runs with no network and writes identical bytes on every run.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
