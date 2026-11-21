# The World in One Day — 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/knownmyface/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/knownmyface/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image that sums up Friday 20 November 2026's world news, built as a
newspaper front page: **60 stories, 7 regions, 13 places pinned on the map**.

The masthead names the day — FRIDAY 20 NOVEMBER 2026 — above three drawn
lead illustrations (Russian missiles hitting three Kyiv bridges; Cyclone
Akvan making landfall in Odisha; the AI sell-off sinking Asia's markets),
a navy band for the fourth lead (COP31 reaching its final day with no
deal), a "Day by the Clock" timeline strip in UTC, a labelled world map
with 13 numbered pins, and a full numbered index of all 60 stories. A
DATE CHECK box names what was left out on purpose — Thursday's news
(the Myanmar ruling, the Shenzhen declaration, Anthropic's IPO debut,
GTA VI's launch) — and what had not happened yet at press time. Every
illustration is drawn in code; every story carries a source, and the one
unverified claim is flagged [CLAIM].

## How it is built

`render.py` draws the front page with PIL into `entry.png` (1024x1024,
under 1 MiB, byte-identical on every run). `main.ts` validates that file
against the competition limits and copies it byte-for-byte into
`MAKEFUN_OUTPUT_DIR/entry.png`. Node standard library only for the
entrypoint; no network at run time.

```sh
python3 render.py            # rebuild entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Stories (60)

Leads: Russian missiles hit three Kyiv bridges (110+ missiles, ~400
drones, 3 killed in Kyiv, 8 overall); Cyclone Akvan makes landfall near
Gopalpur (300,000+ evacuated); AI sell-off sinks Asia's markets (Taiex
-6.2%, KOSPI -5.2%, Nikkei -5.1%, ~$4tn wiped). Fourth lead: COP31
reaches its last day with no deal (draft drops fossil fuels and the
$120bn adaptation fund). Also: the UK-EU "reset" deal (100,000 youth
visas a year), a Russian cruise missile lands in Poland, the Iraqi army
enters Jurf al-Sakhar, Italy's general strike, Japan's inflation at
2.3%, Seoul moves to impeach its top judge, Kenya drills its first oil
well, Bukele launches a third-term campaign, Phillips hits 118 against
India — and 47 more, all in the index on the page.

## Numbers (6)

3 bridges hit in Kyiv · 300,000+ evacuated before Akvan · -6.2% Taiwan's
Taiex, Friday · 100,000 youth visas a year, UK-EU · 2.3% Japan CPI,
October · $4tn wiped from stocks, gold, crypto.

## Sources

Reuters / AP / AFP / BBC / PTI / Al Jazeera / IMD / Anadolu / Xinhua /
SBS / allAfrica / ICC / ATP / Formula1.com / ESA. Every story was
checked against reporting dated 20 November 2026.
