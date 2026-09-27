# Zone Analyst

Competitive blue-zone and fight analytics for PUBG Mobile: a website, a Python
research toolkit, a combat-math workbook and an Expo mobile app, all built on
the same models.

The zone models test a candidate algorithm described in a published Tencent
patent. The weapon numbers are community estimates, graded by confidence.
Neither is a measurement of the live game, and every page says so.

## What's inside

| Folder | What it is | Start here |
|---|---|---|
| `website/` | Static site: zone simulator, probability chart, combat math, playbook, research report. No build step, no server code. | Double-click `website/index.html` |
| `research/` | Python toolkit: generative zone models, statistical test battery, Monte Carlo forecasting, CV circle fitting | `research/README.md` |
| `workbook/` | Excel combat-math workbook and the script that generates it | `workbook/pubgm-combat-math.xlsx` |
| `mobile-app/` | Expo SDK 57 app with the same four tools, for Android and iOS | `mobile-app/PUBLISHING.md` |
| `scripts/` | Site maintenance: shared navigation, research-page generator, site checker | `docs/RUN_LOCALLY.md` |
| `docs/` | How to run it locally, put it on Hostinger, and publish on GitHub | below |

## Quick start (Windows)

- **See the website:** double-click `website/index.html`, or `start-website.bat`
  for a local server at `http://localhost:8000`.
- **Run the research tests:** in `research/`, `py -m pip install -r requirements.txt`
  then `py -m pytest tests -q`.
- **Guides:** [run locally](docs/RUN_LOCALLY.md) ·
  [deploy to Hostinger](docs/DEPLOY_HOSTINGER.md) ·
  [publish on GitHub](docs/GITHUB.md) ·
  [build the app](mobile-app/PUBLISHING.md)

## Three findings

1. **Above a 0.5 shrink ratio, the centre is free.** A disc of radius
   2r′ − r around the current centre cannot be caught outside the next zone.
   That follows from containment alone and needs no match data.
2. **Late circles can't be read from broadcast video.** Circle-fitting error
   carried through the key statistic grows from ±0.012 at phase 1 to ±0.79 at
   phase 8, on a 0–1 scale.
3. **One magazine rarely covers a 1v4.** Four of eighteen accuracy-and-armour
   cases fit an extended M416 magazine, none of them against Level 3 armour.

The research report (`research/docs/REPORT.md`, also the site's Research page)
gives the method and evidence behind each.

## What has been verified

| Part | Check | Result |
|---|---|---|
| Research toolkit | Unit tests | 21 pass |
| | End-to-end pipeline on synthetic tournaments | 10 of 10 checks |
| | Verdict false-alarm rate on uniform data | 4.0% (target 5%) |
| Website | 7 pages × desktop/phone × light/dark, rendered in Chromium | no script errors, no sideways scrolling |
| | Links, anchors and assets (`scripts/check_site.py`) | clean |
| | Simulator verdict on 2,000 uniform batches / 4 non-uniform rules | 4.8% false alarms / 100% detection |
| | Browser combat model vs spreadsheet | identical on every compared figure |
| | Browser vs Python verdicts, 200 browser-generated tournaments | 199 agree; the one split is a false alarm on uniform data, within both verdicts' 5% rate |
| Workbook | LibreOffice recalculation | 630 formulas, 0 errors |
| Mobile app | Full TypeScript check and Android bundle export (Expo SDK 57) | clean; 2.9 MB bundle |

GitHub runs the research tests and the site checker on every push.

## Honest status

- **No tournament matches have been annotated yet.** Every zone result is a
  property of the instrument, tested on synthetic data generated from known
  rules. Pointing it at real footage is the next step, and
  `research/docs/PROTOCOL.md` says how.
- **PUBG Mobile publishes no weapon statistics.** Sources disagree (two put the
  M416 at 41 and 43 base damage) and most reload times could not be sourced.
  Everything computes from inputs you can replace with your own measurements.

## Disclaimer

Independent analysis toolkit. Not affiliated with, endorsed by, or connected to
KRAFTON, Tencent or PUBG Mobile. Game names are used only to describe what is
analysed.

© 2026 Janin A Apurba. No licence has been chosen yet, so all rights are
reserved; `docs/GITHUB.md` explains how to add one.
