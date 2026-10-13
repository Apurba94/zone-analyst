# Zone Analyst

Competitive blue-zone and fight analytics for PUBG Mobile: a website, a Windows
app, an Android app, a Python research toolkit, a combat-math workbook and an
Expo mobile app, all built on the same models.

**Use it online: [zoneanalyst.vercel.app](https://zoneanalyst.vercel.app)** ·
**Download:** [Windows installer](https://github.com/Apurba94/zone-analyst/releases/latest/download/Zone-Analyst-Setup.exe) ·
[Windows portable](https://github.com/Apurba94/zone-analyst/releases/latest/download/Zone-Analyst-Portable.exe) ·
[Android APK](https://github.com/Apurba94/zone-analyst/releases/latest/download/Zone-Analyst.apk) ·
[all releases](https://github.com/Apurba94/zone-analyst/releases)

The zone models test a candidate algorithm described in a published Tencent
patent. The weapon numbers are community estimates, graded by confidence.
Neither is a measurement of the live game, and every page says so.

## What's inside

| Folder | What it is | Start here |
|---|---|---|
| `website/` | Static site: zone simulator, probability chart, combat math, playbook, research report. No build step, no server code. Live on Vercel. | Double-click `website/index.html` |
| `desktop-app/` | The website as a Windows program (Electron): installer and portable `.exe`, works offline | `desktop-app/README.md` |
| `android-app/` | The website as an Android app (Capacitor): `.apk`, works offline | `android-app/README.md` |
| `research/` | Python toolkit: generative zone models, statistical test battery, Monte Carlo forecasting, CV circle fitting | `research/README.md` |
| `workbook/` | Excel combat-math workbook and the script that generates it | `workbook/pubgm-combat-math.xlsx` |
| `mobile-app/` | Native Expo SDK 57 rewrite of four tools, for the Android and iOS stores | `mobile-app/PUBLISHING.md` |
| `scripts/` | Site maintenance: shared navigation, research-page generator, site checker, app icons | `docs/RUN_LOCALLY.md` |
| `docs/` | How to run it locally, deploy it to Vercel or Hostinger, and publish on GitHub | below |

## Quick start (Windows)

- **Use it online:** [zoneanalyst.vercel.app](https://zoneanalyst.vercel.app).
- **Install it:** `Zone-Analyst-Setup.exe` for Windows or `Zone-Analyst.apk`
  for Android, from the [latest release](https://github.com/Apurba94/zone-analyst/releases/latest).
- **See the website from the source:** double-click `website/index.html`, or
  `start-website.bat` for a local server at `http://localhost:8000`.
- **Run the research tests:** in `research/`, `py -m pip install -r requirements.txt`
  then `py -m pytest tests -q`.
- **Guides:** [run locally](docs/RUN_LOCALLY.md) ·
  [Vercel](docs/DEPLOY_VERCEL.md) ·
  [deploy to Hostinger](docs/DEPLOY_HOSTINGER.md) ·
  [publish on GitHub](docs/GITHUB.md) ·
  [Windows app](desktop-app/README.md) ·
  [Android app](android-app/README.md) ·
  [build the Expo app](mobile-app/PUBLISHING.md)

## Releasing the apps

The Windows and Android apps bundle `website/` when they are built, so a site
change reaches them with the next release:

1. Set the new version in `desktop-app/package.json`, `android-app/package.json`
   and `android-app/android/app/build.gradle` (`versionName`, and raise
   `versionCode` by one).
2. Commit and push, then tag it: `git tag v1.0.1` and `git push origin v1.0.1`.
3. GitHub Actions (**Desktop and Android apps**) builds the installer, the
   portable `.exe` and the signed `.apk`, and publishes them as a release. The
   download buttons on the website always point at the latest one.

The website itself redeploys on Vercel with every push to `main`.

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
| | Live on Vercel: every page, the workbook download, the 404 page | served; the deploy runs the site checker first |
| Windows app | Built installer and portable `.exe`, launched, all 6 pages driven over DevTools | every page renders, no script errors |
| Android app | Release APK built in GitHub Actions; signature checked with `apksigner` | builds clean; signed with the release key (v2 signature verified); Android 7+ (min SDK 24), target SDK 36. Not yet tried on a physical phone |
| Mobile app | Full TypeScript check and Android bundle export (Expo SDK 57) | clean; 2.9 MB bundle |

GitHub runs the research tests and the site checker on every push, and builds
both apps for every release tag.

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

## Follow Janin on YouTube

If this project helped you, please follow and subscribe:

- **Study with Janin**: [youtube.com/@studywithjanin](https://www.youtube.com/@studywithjanin)
- **Pomodoro Study with Janin**: [youtube.com/@pomodorostudywithjanin3326](https://www.youtube.com/@pomodorostudywithjanin3326)
