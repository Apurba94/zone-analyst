# Running it on your computer (Windows)

## The website

**Option 1 — double-click. Nothing to install.**
Open the `website` folder and double-click `index.html`. Every page works this
way: the simulator, the probability chart, combat math with its sliders and
hover explanations, the playbook, the research report, the CSV export and the
workbook download. The two web fonts need an internet connection; offline, a
standard serif and sans-serif stand in and nothing else changes.

**Option 2 — a local server, the closest match to Hostinger.**
Double-click `start-website.bat` in the project folder. If Python is installed
it starts a server and opens `http://localhost:8000` in your browser; close the
black window to stop it. If Python isn't installed, it opens the site straight
from disk instead, so it always does something useful.

To install Python: [python.org/downloads](https://www.python.org/downloads/),
run the installer, and tick **Add python.exe to PATH** on the first screen.

The server only listens on your own computer (`127.0.0.1`), so nobody else on
your network can reach it.

**Option 3 — VS Code, if you're editing pages.**
Install the **Live Server** extension, open the project folder in VS Code,
right-click `website/index.html` and choose **Open with Live Server**. The page
reloads by itself every time you save a change.

## The research toolkit

Needs Python 3.11 or newer. In a terminal opened in the `research` folder:

```bat
py -m pip install -r requirements.txt
py -m pytest tests -q                 :: expect 21 passed
py examples\demo_end_to_end.py        :: expect 10/10 pipeline checks passed
py -m bluezone.power                  :: regenerates the power table (about a minute)
```

`research/README.md` shows how to run the model on your own annotated matches.

## The workbook

Open `workbook\pubgm-combat-math.xlsx` in Excel. To rebuild it from its
generator after editing weapon data:

```bat
py -m pip install openpyxl
py workbook\build_workbook.py
```

Excel recalculates every formula when it opens the rebuilt file. Copy the new
file into `website\downloads\` too, so the site offers the same version.

## Editing the website

| To change | Edit | Then run |
|---|---|---|
| Navigation or footer on every page | `scripts/site_chrome.py` | `py scripts\site_chrome.py` |
| The research page | `research/docs/REPORT.md` | `py -m pip install markdown`, then `py scripts\build_research_page.py`, then `py scripts\site_chrome.py` |
| Combat math numbers or logic | `mobile-app/src/combat.ts` (shared with the app) | `npx esbuild mobile-app/src/combat.ts --bundle --format=iife --global-name=ZoneCombat --target=es2019 --outfile=website/assets/combat-model.js` (needs [Node.js](https://nodejs.org)) |
| Anything | — | `py scripts\check_site.py` before uploading |

`check_site.py` fails on any broken link, missing anchor, missing asset or
unexpected external host. The GitHub checks and the Hostinger deploy both run
it, so a broken page never reaches the server.

## The mobile app

See `mobile-app/PUBLISHING.md`. Building it needs Node.js and an Expo account;
the website does not depend on it.
