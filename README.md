# The World Today — 18 November 2026

Entry for make.fun bounty **news-image-20261118**: one image summing up
the world's news of Wednesday 18 November 2026.

## What it is

A newspaper front page ("THE WORLD TODAY"), drawn programmatically with
PIL — no AI image generation, so every headline is crisp and legible.
25 verified stories across five continents: the Gulf war widening, the
Trump–Xi–Putin summit eve in Shenzhen, the Kerch Bridge strike, Peltola
flipping Alaska, Ebola in Congo, Cyclone Xavier, Nvidia's earnings beat,
Dhoni's IPL retirement, and more. Every story was verified against a
source on the day; see `research-notes.md` for the list and sources.

## Files

- `entry.png` — the front page (1024×1024, PNG)
- `render.py` — the renderer that draws `entry.png` from the story list
- `research-notes.md` — the 25 verified stories and their sources
- `main.ts` — the entry program: copies `entry.png` to the output dir

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

The program runs with no network and writes identical bytes on every run.
