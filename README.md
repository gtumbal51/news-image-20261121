# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/gtumbal51/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/gtumbal51/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Saturday 21 November 2026's world news on one page: a broadsheet front page carrying **38 stories** — 4 illustrated lead stories, 11 illustrated panels and 23 one-line briefs — with a day-in-numbers strip, a world map with numbered pins matched to the stories, a region tally, a source tag on every pictured story, and a date-check box listing the adjacent-day stories deliberately left out.

The leads: Iran strikes US bases in Bahrain · COP31 talks run past their deadline in Antalya · Mexico captures most-wanted cartel boss "Chapo Isidro" (11 dead) · a Russian missile kills a boy, 7, in Kryvyi Rih. Panels and briefs cover the AI stock sell-off, the Shenzhen Trump–Xi–Putin summit, the ICJ's Myanmar genocide ruling, the burning Sparta II in the Baltic, a claimed AI-assisted proof of the Riemann hypothesis, twin earthquakes in Peru (M6.7) and off Timor (M6.8), GTA VI's $3.8BN first day, Brazil's 69% dengue drop — and 23 more.

## Run it

```sh
python3 main.py
```

`main.py` renders the page with Pillow and writes `entry.png` (1024x1024) to the current directory and to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`), then verifies the result is a valid 1024x1024 PNG. Every illustration — missile, globe, badge, chart, ship, quake crack, gamepad and the dot-matrix world map — is drawn in code; there are no photos and no external assets.

## Competition

[Sum up 21 November's world news in one image](https://make.fun/bounty/news-image-20261121) — a make.fun bounty. The entry program writes one image of the day's news; an AI judge compares the images two at a time, and the 50 best-ranked entries share $100.
