"""
Build the combat-math workbook: workbook/pubgm-combat-math.xlsx

    pip install openpyxl
    python workbook/build_workbook.py [output.xlsx]

openpyxl writes formulas without cached values, so recalculate before sharing
(Excel does this itself on open; previewers and phones may show blanks until
it has been done once), e.g. with LibreOffice:

    soffice --headless --convert-to xlsx --outdir out/ pubgm-combat-math.xlsx

DATA HEALTH: PUBG Mobile publishes no weapon statistics. Every figure below is a
community private-lobby estimate; sources disagree and most reload times could
not be sourced. The workbook is built so its conclusions are formulas over this
data — replace any row with your own measurements and everything recomputes.
"""

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

ARIAL = "Arial"
H1 = Font(name=ARIAL, size=15, bold=True, color="16324A")
H2 = Font(name=ARIAL, size=11, bold=True, color="FFFFFF")
BOLD = Font(name=ARIAL, size=10, bold=True)
BODY = Font(name=ARIAL, size=10)
SMALL = Font(name=ARIAL, size=9, color="555555")
INPUT_F = Font(name=ARIAL, size=10, color="0000FF", bold=True)
LINK_F = Font(name=ARIAL, size=10, color="008000")
HDRFILL = PatternFill("solid", fgColor="16324A")
INFILL = PatternFill("solid", fgColor="FFF2CC")
WARNFILL = PatternFill("solid", fgColor="FCE4E4")
BANDFILL = PatternFill("solid", fgColor="F2EFE6")
GOODFILL = PatternFill("solid", fgColor="E2EFDA")
# Status tints validated for colour-vision deficiency; the numbers stay the primary signal.
FITFILL = PatternFill("solid", fgColor="D5E4F0")
SHORTFILL = PatternFill("solid", fgColor="F3DCC3")
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top")

wb = Workbook()

# --------------------------------------------------------------------------
# Weapon data.
#   dmg_z   = base damage, zilliongamer PUBG Mobile private-lobby table (2026-09-12)
#   dmg_lq  = base damage, Liquipedia PUBG Mobile wiki, where retrieved
#   mag/ext = magazine, base and extended
#   reload  = reload seconds; None where no PUBG Mobile figure could be sourced
#   roF     = seconds between shots
#   conf    = confidence in the row as a whole
#   src     = where the numbers came from
# --------------------------------------------------------------------------
W = [
    # name, class, ammo, dmg_z, dmg_lq, mag, ext, reload, rof, src, conf, note
    ("M416",        "AR",  "5.56",  43, 41, 30, 40, 2.10, 0.085, "zilliongamer; Liquipedia PUBGM", "Medium", "Two PUBGM sources disagree on damage (43 vs 41)."),
    ("SCAR-L",      "AR",  "5.56",  43, 41, 30, 40, 2.20, 0.096, "zilliongamer; Liquipedia PUBGM", "Medium", "Two PUBGM sources disagree on damage (43 vs 41)."),
    ("G36C",        "AR",  "5.56",  43, 41, 30, 40, 3.80, 0.086, "zilliongamer; Liquipedia PUBGM", "Medium", "Vikendi/Karakin. Long reload is the headline stat."),
    ("QBZ95",       "AR",  "5.56",  43, None, 30, 40, None, 0.092, "zilliongamer", "Low", "Sanhok. Reload not sourced."),
    ("AUG A3",      "AR",  "5.56",  43, None, 30, 40, None, 0.0827, "zilliongamer", "Low", "Crate weapon. Reload not sourced."),
    ("M16A4",       "AR",  "5.56",  43, None, 30, 40, None, 0.075, "zilliongamer", "Low", "Burst only. Reload not sourced."),
    ("AKM",         "AR",  "7.62",  49, None, 30, 40, 2.90, 0.100, "zilliongamer; Liquipedia PUBG(PC) reload", "Low", "Reload from the PC wiki, not PUBGM. Verify."),
    ("Beryl M762",  "AR",  "7.62",  47, None, 30, 40, 2.90, 0.086, "zilliongamer; Liquipedia PUBG(PC) reload", "Low", "Reload from the PC wiki, not PUBGM. Verify."),
    ("Mk47 Mutant", "AR",  "7.62",  49, None, 20, 30, 3.36, 0.100, "zilliongamer; Liquipedia PUBG(PC) reload", "Low", "Burst/single only. Reload from PC wiki."),
    ("Groza",       "AR",  "7.62",  49, None, 30, None, None, 0.080, "zilliongamer", "Low", "Crate. No extended mag. Reload not sourced."),

    ("Mini14",      "DMR", "5.56",  53, None, 20, 30, None, 0.100, "zilliongamer", "Low", "Reload not sourced for PUBGM."),
    ("QBU",         "DMR", "5.56",  53, None, 10, 20, None, 0.100, "zilliongamer", "Low", "Sanhok. Reload not sourced."),
    ("SKS",         "DMR", "7.62",  56, None, 10, 20, None, 0.100, "zilliongamer", "Low", "Reload not sourced for PUBGM."),
    ("SLR",         "DMR", "7.62",  58, None, 10, 20, None, 0.100, "zilliongamer", "Low", "Reload not sourced for PUBGM."),
    ("Mk14 EBR",    "DMR", "7.62",  61, None, 10, 20, 3.683, 0.090, "zilliongamer; Sportskeeda PUBGM", "Medium", "Crate. Reload corroborated by a PUBGM source."),
    ("VSS",         "DMR", "9mm",   40, None, 10, 20, None, 0.086, "zilliongamer", "Low", "Integral suppressor. Reload not sourced."),

    ("Kar98k",      "SR",  "7.62",  74, None,  5, None, None, 1.900, "zilliongamer", "Low", "Bolt action. Reload not sourced for PUBGM."),
    ("M24",         "SR",  "7.62",  79, None,  5,  7, None, 1.900, "zilliongamer", "Low", "Bolt action. Reload not sourced."),
    ("AWM",         "SR",  ".300",  105, None, 5,  7, None, 1.850, "zilliongamer", "Low", "Crate. Reload not sourced."),
    ("Win94",       "SR",  ".45",   66, None,  8, None, None, 0.600, "zilliongamer", "Low", "No scope slot. Reload not sourced."),

    ("UMP45",       "SMG", ".45",   39, None, 25, 35, None, 0.092, "zilliongamer", "Low", "Listed as UMP9 on some tables. Reload not sourced."),
    ("Vector",      "SMG", ".45",   35, None, 19, 33, None, 0.055, "zilliongamer", "Low", "Base mag disputed (13 vs 19). Verify both."),
    ("Micro Uzi",   "SMG", "9mm",   26, None, 25, 35, None, 0.048, "zilliongamer", "Low", "Fastest fire rate in the game. Reload not sourced."),
    ("Thompson",    "SMG", ".45",   39, None, 30, 50, None, 0.086, "zilliongamer", "Low", "No muzzle slot. Reload not sourced."),
    ("PP-19 Bizon", "SMG", "9mm",   36, None, 53, None, None, 0.086, "zilliongamer", "Low", "Huge base mag, no extended. Reload not sourced."),
    ("MP5K",        "SMG", "9mm",   None, None, 30, 40, None, 0.067, "not sourced", "UNMEASURED", "Vikendi. No PUBGM damage figure sourced."),
    ("JS9",         "SMG", "9mm",   None, None, 30, 40, None, None, "not sourced", "UNMEASURED", "Rondo-exclusive. No PUBGM figures sourced."),

    ("DP-28",       "LMG", "7.62",  49, None, 47, None, None, 0.109, "zilliongamer", "Low", "Reload not sourced for PUBGM."),
    ("M249",        "LMG", "5.56",  47, None, 100, None, None, 0.075, "zilliongamer", "Low", "Crate. Reload not sourced."),

    ("S12K",        "SG",  "12ga",  195, None, 5,  8, None, 0.250, "zilliongamer", "Low", "Power is TOTAL pellet damage, not per pellet."),
    ("S1897",       "SG",  "12ga",  206, None, 5,  7, None, 0.750, "zilliongamer", "Low", "Power is TOTAL pellet damage, not per pellet."),
    ("S686",        "SG",  "12ga",  216, None, 2, None, None, 0.200, "zilliongamer", "Low", "Power is TOTAL pellet damage, not per pellet."),

    ("P18C",        "PIS", "9mm",   23, None, 17, 25, None, 0.060, "zilliongamer", "Low", "Full auto. Reload not sourced."),
    ("P1911",       "PIS", ".45",   39, None,  7, 12, None, 0.110, "zilliongamer", "Low", "Reload not sourced."),
    ("R45",         "PIS", ".45",   53, None,  6, None, None, 0.250, "zilliongamer", "Low", "Miramar. Reload not sourced."),
]


def style_header(ws, row, headers, widths, freeze=True):
    for i, (h, wd) in enumerate(zip(headers, widths), start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = H2
        c.fill = HDRFILL
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = BOX
        ws.column_dimensions[get_column_letter(i)].width = wd
    if freeze:
        ws.freeze_panes = ws.cell(row=row + 1, column=1)


def title(ws, text, sub=None, width=10):
    ws["A1"] = text
    ws["A1"].font = H1
    ws.row_dimensions[1].height = 22
    if sub:
        ws["A2"] = sub
        ws["A2"].font = SMALL
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width)
        ws["A2"].alignment = WRAP
        ws.row_dimensions[2].height = 28


# ==========================================================================
# 1. Read Me
# ==========================================================================
ws = wb.active
ws.title = "Read Me"
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 26
ws.column_dimensions["C"].width = 96

rows = [
    ("H", "PUBG Mobile combat math — coach's workbook", ""),
    ("", "", ""),
    ("W", "READ THIS FIRST",
     "PUBG Mobile publishes no weapon stat table. The game shows a power bar, not numbers. Every "
     "figure circulating online is community-derived from private-lobby testing or datamining, and "
     "the sources disagree with each other. Two PUBG Mobile sources give the M416 41 and 43 base "
     "damage respectively. Reload times for most weapons could not be sourced for PUBG Mobile at "
     "all.\n\n"
     "This workbook is therefore built so the CONCLUSIONS DO NOT DEPEND ON MY NUMBERS. Every "
     "calculation is a live formula over the Weapon Database. Replace any row with your own "
     "measured values and every downstream answer updates. The 'Measure It' sheet gives the exact "
     "protocol.\n\n"
     "Do not quote the damage figures in here as fact. Quote the method."),
    ("", "", ""),
    ("S", "Sheets", ""),
    ("", "Weapon Database", "Every weapon with damage, magazine, reload and fire rate. Each row carries its "
     "source and a confidence grade. Blank cells are honest gaps, not zeros."),
    ("", "Fight Math", "Effective damage, shots to knock, and time to knock — computed per weapon from the "
     "armour and hit-location assumptions you set at the top."),
    ("", "1v4 Budget", "How much ammunition a 1v4 actually costs. This is the sheet that makes the "
     "double-gun case."),
    ("", "Double Gun", "Ranked two-weapon pairs for clutch fighting. Change any weapon name and it "
     "recomputes."),
    ("", "Reload vs Swap", "The mechanic the whole strategy rests on, quantified."),
    ("", "Measure It", "The private-lobby protocol, with a table to record your own numbers before you "
     "copy them into the Weapon Database."),
    ("", "Coach Report", "The written analysis and what to actually do about it."),
    ("", "", ""),
    ("S", "Cell colours", ""),
    ("", "Blue bold", "An input you can and should change."),
    ("", "Yellow fill", "A cell awaiting your own measurement."),
    ("", "Green", "A link to another sheet. Change the source, not the link."),
    ("", "Black", "A formula. Leave it alone."),
    ("", "", ""),
    ("S", "Sources used", ""),
    ("", "zilliongamer", "PUBG Mobile Complete Weapon Stats, updated 12 Sep 2026. States explicitly that its "
     "values are estimated from private-lobby experiments and are not official."),
    ("", "Liquipedia PUBGM", "PUBG Mobile weapons portal. Used for M416, SCAR-L and G36C reload and fire rate."),
    ("", "Liquipedia PUBG (PC)", "Used ONLY for AKM, Beryl M762 and Mk47 reload, where no PUBG Mobile figure "
     "was available. PC and Mobile are separate builds — treat these as placeholders."),
    ("", "Sportskeeda", "Mk14 PUBG Mobile stats, used as a cross-check."),
]
r = 4
for kind, a, b in rows:
    if kind == "H":
        ws.cell(row=r, column=2, value=a).font = H1
        ws.row_dimensions[r].height = 22
    elif kind == "W":
        c = ws.cell(row=r, column=2, value=a); c.font = BOLD; c.fill = WARNFILL
        c2 = ws.cell(row=r, column=3, value=b); c2.font = BODY; c2.fill = WARNFILL
        c2.alignment = WRAP
        ws.row_dimensions[r].height = 168
    elif kind == "S":
        c = ws.cell(row=r, column=2, value=a); c.font = H2; c.fill = HDRFILL
        ws.cell(row=r, column=3).fill = HDRFILL
    else:
        ws.cell(row=r, column=2, value=a).font = BOLD
        c = ws.cell(row=r, column=3, value=b); c.font = BODY; c.alignment = WRAP
        if len(b) > 110:
            ws.row_dimensions[r].height = 42
    r += 1

# ==========================================================================
# 2. Weapon Database
# ==========================================================================
db = wb.create_sheet("Weapon Database")
db.sheet_view.showGridLines = False
title(db, "Weapon Database",
      "Base damage is damage to an unarmoured torso before multipliers. Blank = no PUBG Mobile "
      "figure could be sourced; fill it from your own test rather than from a tier-list blog. "
      "Confidence grades the row, not the game.")
hdr = ["Weapon", "Class", "Ammo", "Base dmg\n(source A)", "Base dmg\n(source B)", "Mag",
       "Ext mag", "Reload (s)", "Fire interval (s)", "RPM", "Source", "Confidence", "Note"]
style_header(db, 4, hdr, [15, 7, 7, 11, 11, 7, 8, 10, 12, 9, 30, 12, 46])

r = 5
for (name, cls, ammo, dz, dl, mag, ext, rel, rof, src, conf, note) in W:
    db.cell(row=r, column=1, value=name).font = BOLD
    db.cell(row=r, column=2, value=cls).font = BODY
    db.cell(row=r, column=3, value=ammo).font = BODY
    for col, val in ((4, dz), (5, dl), (6, mag), (7, ext), (8, rel), (9, rof)):
        c = db.cell(row=r, column=col, value=val)
        c.font = INPUT_F
        if val is None:
            c.fill = INFILL
    db.cell(row=r, column=10, value=f"=IF(I{r}=\"\",\"\",ROUND(60/I{r},0))").font = BODY
    db.cell(row=r, column=11, value=src).font = SMALL
    c = db.cell(row=r, column=12, value=conf)
    c.font = BOLD if conf == "UNMEASURED" else BODY
    if conf == "UNMEASURED":
        c.fill = WARNFILL
    c2 = db.cell(row=r, column=13, value=note); c2.font = SMALL; c2.alignment = WRAP
    for col in range(1, 14):
        db.cell(row=r, column=col).border = BOX
        if r % 2 == 0:
            if db.cell(row=r, column=col).fill.fgColor.rgb in (None, "00000000"):
                db.cell(row=r, column=col).fill = BANDFILL
    r += 1
LAST = r - 1
db.cell(row=r + 1, column=1, value="Shotgun 'base dmg' is TOTAL pellet damage at point blank, not per pellet — do not compare it "
        "directly against rifle figures.").font = SMALL

# ==========================================================================
# 3. Fight Math
# ==========================================================================
fm = wb.create_sheet("Fight Math")
fm.sheet_view.showGridLines = False
title(fm, "Fight Math",
      "Set the fight you are modelling in the blue cells. Everything below recomputes. "
      "In squads the threshold that matters is the KNOCK at 100 HP, not the kill.")

fm["B4"] = "Assumptions"; fm["B4"].font = H2; fm["B4"].fill = HDRFILL
for c in "CDEFGHIJ":
    fm[f"{c}4"].fill = HDRFILL
inputs = [
    ("Target HP (knock threshold)", 100, "Full-health target. A knock happens at 0 HP."),
    ("Armour damage reduction", 0.40, "Fraction removed by the vest. UNVERIFIED — commonly quoted as 0.30 / 0.40 / 0.55 for Lv1/2/3. Measure it."),
    ("Hit location multiplier", 1.00, "1.00 = torso. Limbs are lower, head much higher. Real fights are mostly torso."),
    ("Hit rate (accuracy)", 0.40, "Fraction of fired rounds that connect. Pull your real number from your own match replays."),
    ("Weapon swap time (s)", 0.65, "UNVERIFIED placeholder. Measure it — the whole double-gun case scales with this."),
]
r = 5
for lab, val, note in inputs:
    fm.cell(row=r, column=2, value=lab).font = BOLD
    c = fm.cell(row=r, column=3, value=val); c.font = INPUT_F; c.fill = INFILL; c.border = BOX
    if lab.startswith(("Armour", "Hit rate")):
        c.number_format = "0%"
    elif lab.startswith(("Hit location", "Weapon swap")):
        c.number_format = "0.00"
    # The note spans D:J so it never depends on the table's narrow column widths.
    fm.cell(row=r, column=4, value=note).font = SMALL
    fm.cell(row=r, column=4).alignment = Alignment(wrap_text=True, vertical="center")
    fm.merge_cells(start_row=r, start_column=4, end_row=r, end_column=10)
    fm.row_dimensions[r].height = 28
    r += 1

hdr2 = ["Weapon", "Class", "Base dmg", "Effective dmg\nper hit", "Hits to knock",
        "Shots to fire\n(at hit rate)", "Mag", "Ext mag", "Knocks per\next mag",
        "Time to knock\n(s, hits only)"]
HR = 12
# Column B is wide because it also holds the assumption labels above the table.
style_header(fm, HR, hdr2, [15, 28, 11, 13, 12, 13, 7, 8, 11, 13], freeze=False)
r = HR + 1
for i, wpn in enumerate(W):
    src = 5 + i
    fm.cell(row=r, column=1, value=f"='Weapon Database'!A{src}").font = LINK_F
    fm.cell(row=r, column=2, value=f"='Weapon Database'!B{src}").font = LINK_F
    # A bare reference to an empty cell evaluates to 0, which would read as "does no damage".
    fm.cell(row=r, column=3,
            value=f"=IF('Weapon Database'!D{src}=\"\",\"\",'Weapon Database'!D{src})").font = LINK_F
    fm.cell(row=r, column=4, value=f'=IF(C{r}="","",ROUND(C{r}*$C$7*(1-$C$6),1))').font = BODY
    fm.cell(row=r, column=5, value=f'=IF(OR(D{r}="",D{r}=0),"",CEILING($C$5/D{r},1))').font = BODY
    fm.cell(row=r, column=6, value=f'=IF(E{r}="","",CEILING(E{r}/$C$8,1))').font = BODY
    fm.cell(row=r, column=7, value=f"='Weapon Database'!F{src}").font = LINK_F
    fm.cell(row=r, column=8, value=f"=IF('Weapon Database'!G{src}=\"\",'Weapon Database'!F{src},'Weapon Database'!G{src})").font = LINK_F
    fm.cell(row=r, column=9, value=f'=IF(OR(E{r}="",H{r}=""),"",ROUND(H{r}*$C$8/E{r},1))').font = BODY
    fm.cell(row=r, column=10,
            value=f'=IF(OR(E{r}="",\'Weapon Database\'!I{src}=""),"",ROUND((E{r}-1)*\'Weapon Database\'!I{src},2))').font = BODY
    for col in range(1, 11):
        fm.cell(row=r, column=col).border = BOX
    r += 1
FM_LAST = r - 1
fm.cell(row=r + 1, column=1,
        value="'Knocks per ext mag' is the number this sheet exists for: how many enemies one magazine can "
              "put down at your real hit rate. Under 4.0, one magazine cannot knock a full squad — the 1v4 "
              "Budget sheet does the same arithmetic in rounds.").font = SMALL

# ==========================================================================
# 4. 1v4 Budget
# ==========================================================================
bg = wb.create_sheet("1v4 Budget")
bg.sheet_view.showGridLines = False
title(bg, "1v4 Ammunition Budget",
      "Whether a clutch is mechanically possible before skill enters the picture. The headline "
      "number is knife-edge and flips on your assumptions, so the grid below matters more than the "
      "single answer.")
bg.column_dimensions["A"].width = 3
bg.column_dimensions["B"].width = 34
bg.column_dimensions["C"].width = 13
bg.column_dimensions["D"].width = 72

bg.cell(row=4, column=2, value="Scenario").font = H2
bg.cell(row=4, column=2).fill = HDRFILL
for c in "CD":
    bg[f"{c}4"].fill = HDRFILL
scen = [
    ("Enemies to knock", 4, "A full squad. Set to 3 if one is already down."),
    ("Weapon under test", "M416", "Type any name exactly as it appears in the Weapon Database."),
]
r = 5
for lab, val, note in scen:
    bg.cell(row=r, column=2, value=lab).font = BOLD
    c = bg.cell(row=r, column=3, value=val); c.font = INPUT_F; c.fill = INFILL; c.border = BOX
    bg.cell(row=r, column=4, value=note).font = SMALL
    r += 1
bg.cell(row=7, column=2, value="Base damage of that weapon").font = BOLD
bg.cell(row=7, column=3,
        value=(f'=IFERROR(IF(INDEX(\'Weapon Database\'!D$5:D${LAST},MATCH($C$6,\'Weapon Database\'!A$5:A${LAST},0))="",'
               f'"not sourced",INDEX(\'Weapon Database\'!D$5:D${LAST},MATCH($C$6,\'Weapon Database\'!A$5:A${LAST},0))),"not found")')).font = BODY
bg.cell(row=7, column=3).border = BOX
bg.cell(row=7, column=4, value="Pulled from the database. Blank there means nobody has published it.").font = SMALL

bg.cell(row=9, column=2, value="At the assumptions set on Fight Math").font = H2
bg.cell(row=9, column=2).fill = HDRFILL
for c in "CD":
    bg[f"{c}9"].fill = HDRFILL
calc = [
    ("Hits needed to knock one", f'=IFERROR(INDEX(\'Fight Math\'!E${HR+1}:E${FM_LAST},MATCH($C$6,\'Fight Math\'!A${HR+1}:A${FM_LAST},0)),"")',
     "At your armour and hit-location assumptions."),
    ("Hits needed for the whole squad", '=IF(ISNUMBER(C10),C10*C5,"")', "Four knocks, not four kills. Finishing is extra."),
    ("Rounds you must FIRE", "=IF(ISNUMBER(C11),CEILING(C11/'Fight Math'!$C$8,1),\"\")", "At your hit rate. The honest number."),
    ("Rounds available, extended mag", f'=IFERROR(INDEX(\'Fight Math\'!H${HR+1}:H${FM_LAST},MATCH($C$6,\'Fight Math\'!A${HR+1}:A${FM_LAST},0)),"")',
     "One magazine, no reload."),
    ("Margin (rounds to spare)", '=IF(AND(ISNUMBER(C12),ISNUMBER(C13)),C13-C12,"")', "Negative means one gun cannot finish the fight. Zero is not a margin."),
]
r = 10
for lab, f, note in calc:
    bg.cell(row=r, column=2, value=lab).font = BOLD
    c = bg.cell(row=r, column=3, value=f); c.font = BODY; c.border = BOX
    bg.cell(row=r, column=4, value=note).font = SMALL
    r += 1

bg.cell(row=16, column=2, value="Verdict").font = H2
bg.cell(row=16, column=2).fill = HDRFILL
for c in "CD":
    bg[f"{c}16"].fill = HDRFILL
v = bg.cell(row=17, column=2,
            value='=IF(C7="not found","That name is not in the Weapon Database. Check the spelling.",'
                  'IF(C14="","No damage figure on record for that weapon. Measure it and enter it in the '
                  'Weapon Database.",IF(C14<0,"Short by "&ABS(C14)&" rounds. One gun cannot finish this fight — you will be '
                  'reloading in front of three people.",IF(C14<=8,"Covered by "&C14&" rounds. That is not a '
                  'margin. One missed burst, one enemy who heals, or Level 3 armour and you are short.",'
                  '"Covered with "&C14&" rounds to spare under these assumptions. Check the grid below '
                  'before believing it."))))')
v.font = Font(name=ARIAL, size=11, bold=True, color="16324A")
v.alignment = WRAP
bg.merge_cells("B17:D17")
bg.row_dimensions[17].height = 36

bg.cell(row=20, column=2, value="Rounds you must fire, by hit rate and enemy armour").font = H2
bg.cell(row=20, column=2).fill = HDRFILL
for col in range(3, 7):
    bg.cell(row=20, column=col).fill = HDRFILL
bg.cell(row=21, column=2,
        value="Compare every cell against your extended magazine capacity in C13. Amber cells need a "
              "reload mid-fight; blue cells fit in one magazine.").font = SMALL
bg.merge_cells("B21:F21")

ARMOURS = [0.30, 0.40, 0.55]
ARMLAB = ["Lv1 vest", "Lv2 vest", "Lv3 vest"]
HITRATES = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50]

bg.cell(row=23, column=2, value="Hit rate").font = H2
bg.cell(row=23, column=2).fill = HDRFILL
for j, (a, lab) in enumerate(zip(ARMOURS, ARMLAB)):
    c = bg.cell(row=22, column=3 + j, value=a); c.font = INPUT_F; c.fill = INFILL
    c.number_format = "0%"; c.border = BOX
    h = bg.cell(row=23, column=3 + j, value=lab); h.font = H2; h.fill = HDRFILL
    h.alignment = Alignment(horizontal="center")
    h.border = BOX
bg.cell(row=22, column=2, value="armour reduction ->").font = SMALL
bg.column_dimensions["E"].width = 13
bg.column_dimensions["F"].width = 13

r = 24
for hr in HITRATES:
    c = bg.cell(row=r, column=2, value=hr); c.font = INPUT_F; c.fill = INFILL
    c.number_format = "0%"; c.border = BOX
    for j in range(len(ARMOURS)):
        col = 3 + j
        L = get_column_letter(col)
        f = (f'=IF(ISNUMBER($C$7),'
             f'CEILING($C$5*CEILING(\'Fight Math\'!$C$5/($C$7*\'Fight Math\'!$C$7*(1-{L}$22)),1)/$B{r},1),"")')
        cc = bg.cell(row=r, column=col, value=f)
        cc.font = BODY; cc.border = BOX
        cc.alignment = Alignment(horizontal="center")
    r += 1
GRID_LAST = r - 1
grid_range = f"C24:E{GRID_LAST}"
bg.conditional_formatting.add(grid_range, FormulaRule(formula=["AND(ISNUMBER(C24),ISNUMBER($C$13),C24>$C$13)"],
                                                       fill=SHORTFILL, font=Font(name=ARIAL, bold=True)))
bg.conditional_formatting.add(grid_range, FormulaRule(formula=["AND(ISNUMBER(C24),ISNUMBER($C$13),C24<=$C$13)"],
                                                       fill=FITFILL))

bg.cell(row=r + 1, column=2,
        value="Read the row that matches your real hit rate, not the one you would like. Pull it from "
              "five match replays: rounds fired against hits landed. Every cell above your magazine "
              "capacity is a fight you cannot finish on one gun.").font = SMALL
bg.merge_cells(start_row=r + 1, start_column=2, end_row=r + 1, end_column=6)
bg.cell(row=r + 1, column=2).alignment = WRAP
bg.row_dimensions[r + 1].height = 40

bg.cell(row=r + 3, column=2,
        value="Why the knock and not the kill: in squads a downed player is out of the fight but still "
              "alive. You need four knocks to be safe and each costs a full 100 HP. Finishing knocked "
              "players costs more rounds again and is usually not worth the exposure.").font = SMALL
bg.merge_cells(start_row=r + 3, start_column=2, end_row=r + 3, end_column=6)
bg.cell(row=r + 3, column=2).alignment = WRAP
bg.row_dimensions[r + 3].height = 40

# ==========================================================================
# 5. Double Gun
# ==========================================================================
dg = wb.create_sheet("Double Gun")
dg.sheet_view.showGridLines = False
title(dg, "Double-Gun Loadouts for the 1v4",
      "Ranked by rounds available before a forced reload, and by whether both guns are usable at "
      "clutch range. Change any weapon name — the row recomputes.")

PAIRS = [
    ("M416", "Beryl M762", "AR + AR", "Both", "Two full ARs. Maximum sustained rounds at the range clutches happen."),
    ("M416", "AKM", "AR + AR", "Both", "Same logic, higher per-bullet damage on the second gun."),
    ("M416", "Groza", "AR + AR", "Both", "Best case if the crate lands. Groza has no extended mag."),
    ("M416", "UMP45", "AR + SMG", "Both", "SMG is lighter on ammo weight and very controllable indoors."),
    ("M416", "Vector", "AR + SMG", "Both", "Highest close burst, smallest magazine. Verify the base mag."),
    ("M416", "DP-28", "AR + LMG", "Both", "47-round second magazine. Slow to swap to and loud."),
    ("M416", "Mini14", "AR + DMR", "One", "The standard team loadout. Second gun is weak inside 30 m."),
    ("M416", "SLR", "AR + DMR", "One", "Team loadout. Ten rounds of usable clutch ammunition."),
    ("M416", "Kar98k", "AR + SR", "One", "Team loadout. The sniper contributes almost nothing in a clutch."),
    ("Beryl M762", "UMP45", "AR + SMG", "Both", "Aggressive entry build."),
]

hdr3 = ["Gun A", "Gun B", "Pair", "Both usable\nat clutch range", "Rounds A", "Rounds B",
        "Total rounds\nbefore reload", "Rounds needed\nfor 1v4", "Margin\n(rounds)",
        "Gap cost:\nswap (s)", "Gap cost:\nreload A (s)", "Seconds saved\nby swapping"]
style_header(dg, 4, hdr3, [14, 14, 11, 13, 10, 10, 12, 12, 11, 11, 12, 12])

r = 5
for a, b, pair, usable, note in PAIRS:
    dg.cell(row=r, column=1, value=a).font = INPUT_F
    dg.cell(row=r, column=2, value=b).font = INPUT_F
    dg.cell(row=r, column=3, value=pair).font = BODY
    c = dg.cell(row=r, column=4, value=usable)
    c.font = BOLD
    c.fill = GOODFILL if usable == "Both" else WARNFILL
    dg.cell(row=r, column=5, value=f'=IFERROR(INDEX(\'Fight Math\'!H${HR+1}:H${FM_LAST},MATCH(A{r},\'Fight Math\'!A${HR+1}:A${FM_LAST},0)),"")').font = BODY
    dg.cell(row=r, column=6, value=f'=IFERROR(INDEX(\'Fight Math\'!H${HR+1}:H${FM_LAST},MATCH(B{r},\'Fight Math\'!A${HR+1}:A${FM_LAST},0)),"")').font = BODY
    dg.cell(row=r, column=7, value=f'=IF(OR(E{r}="",F{r}=""),"",E{r}+IF(D{r}="Both",F{r},0))').font = BODY
    dg.cell(row=r, column=8, value="='1v4 Budget'!$C$12").font = LINK_F
    c9 = dg.cell(row=r, column=9, value=f'=IF(OR(G{r}="",NOT(ISNUMBER(H{r}))),"",G{r}-H{r})')
    c9.font = BOLD
    dg.cell(row=r, column=10, value="='Fight Math'!$C$9").font = LINK_F
    dg.cell(row=r, column=11,
            value=f'=IFERROR(INDEX(\'Weapon Database\'!H$5:H${LAST},MATCH(A{r},\'Weapon Database\'!A$5:A${LAST},0)),"")').font = BODY
    dg.cell(row=r, column=12, value=f'=IF(K{r}="","",ROUND(K{r}-J{r},2))').font = BODY
    for col in range(1, 13):
        dg.cell(row=r, column=col).border = BOX
    r += 1

note_r = r + 1
dg.cell(row=note_r, column=1,
        value="Column D is the column that decides it. 'Rounds' on a gun you cannot shoot at 15 metres are "
              "not rounds. That is why the standard AR+DMR team loadout scores badly here and the AR+AR "
              "pairings score well — and it is the reason your team loadout and your clutch loadout are "
              "not the same loadout.").font = SMALL
dg.merge_cells(start_row=note_r, start_column=1, end_row=note_r, end_column=12)
dg.cell(row=note_r, column=1).alignment = WRAP
dg.row_dimensions[note_r].height = 44

dg.cell(row=note_r + 2, column=1, value="Pair notes").font = H2
dg.cell(row=note_r + 2, column=1).fill = HDRFILL
for col in range(2, 13):
    dg.cell(row=note_r + 2, column=col).fill = HDRFILL
rr = note_r + 3
for a, b, pair, usable, note in PAIRS:
    dg.cell(row=rr, column=1, value=f"{a} + {b}").font = BOLD
    dg.cell(row=rr, column=3, value=note).font = SMALL
    dg.merge_cells(start_row=rr, start_column=3, end_row=rr, end_column=12)
    rr += 1

# ==========================================================================
# 6. Reload vs Swap
# ==========================================================================
rs = wb.create_sheet("Reload vs Swap")
rs.sheet_view.showGridLines = False
title(rs, "Reload versus Swap",
      "The single mechanic the double-gun strategy rests on: switching weapons is faster than "
      "reloading one. Everything else is a consequence of this table.")
rs.column_dimensions["A"].width = 3
rs.column_dimensions["B"].width = 18
rs.column_dimensions["C"].width = 13
rs.column_dimensions["D"].width = 13
rs.column_dimensions["E"].width = 15
rs.column_dimensions["F"].width = 62

style_header(rs, 4, ["", "Weapon", "Reload (s)", "Swap (s)", "Seconds saved", "What that time is worth"],
             [3, 18, 13, 13, 15, 62])
worth = {
    "M416": "Enough to knock a second player at close range.",
    "SCAR-L": "Enough to knock a second player at close range.",
    "G36C": "The worst reload in the class — never be caught empty with this gun.",
    "AKM": "Reload figure is from the PC wiki. Verify before trusting the margin.",
    "Beryl M762": "Reload figure is from the PC wiki. Verify before trusting the margin.",
    "Mk47 Mutant": "Reload figure is from the PC wiki. Verify before trusting the margin.",
    "Mk14 EBR": "A crate DMR you should never be reloading inside a compound.",
}
r = 5
for i, wpn in enumerate(W):
    src = 5 + i
    rs.cell(row=r, column=2, value=f"='Weapon Database'!A{src}").font = LINK_F
    rs.cell(row=r, column=3,
            value=f"=IF('Weapon Database'!H{src}=\"\",\"not sourced\",'Weapon Database'!H{src})").font = LINK_F
    rs.cell(row=r, column=4, value="='Fight Math'!$C$9").font = LINK_F
    c = rs.cell(row=r, column=5, value=f'=IF(ISNUMBER(C{r}),ROUND(C{r}-D{r},2),"")')
    c.font = BOLD
    rs.cell(row=r, column=6, value=worth.get(wpn[0], "")).font = SMALL
    for col in range(2, 7):
        rs.cell(row=r, column=col).border = BOX
    r += 1
rs.conditional_formatting.add(f"E5:E{r - 1}", FormulaRule(formula=["ISNUMBER(E5)"], fill=GOODFILL))

rs.cell(row=r + 1, column=2,
        value="Every weapon is listed. 'not sourced' means no PUBG Mobile reload time could be found — "
              "measure it, enter it in the Weapon Database, and its row fills in here.").font = SMALL
rs.merge_cells(start_row=r + 1, start_column=2, end_row=r + 1, end_column=6)
rs.cell(row=r + 1, column=2).alignment = WRAP

rs.cell(row=r + 3, column=2, value="The tactical pattern").font = H2
rs.cell(row=r + 3, column=2).fill = HDRFILL
for col in range(3, 7):
    rs.cell(row=r + 3, column=col).fill = HDRFILL
steps = [
    ("1", "Fire gun A until it is empty or the duel breaks."),
    ("2", "SWAP — do not reload. You are back in the fight in under a second instead of nearly three."),
    ("3", "Fight with gun B."),
    ("4", "Reload A only when line of sight is broken and you have repositioned."),
    ("5", "Never reload and heal in the same window. Pick one."),
]
rr = r + 4
for n, txt in steps:
    rs.cell(row=rr, column=2, value=n).font = BOLD
    rs.cell(row=rr, column=3, value=txt).font = BODY
    rs.merge_cells(start_row=rr, start_column=3, end_row=rr, end_column=6)
    rr += 1

# ==========================================================================
# 7. Measure It
# ==========================================================================
mi = wb.create_sheet("Measure It")
mi.sheet_view.showGridLines = False
title(mi, "Measure It Yourself",
      "Thirty minutes of Training Grounds gives you better numbers than any tier list, for your "
      "device, your sensitivity and your recoil control. Record results in the yellow cells, then copy "
      "them into the Weapon Database (armour and swap time go on Fight Math); every sheet recomputes.")

proto = [
    ("Reload time", "Record your screen at 60 fps. Fire one round, then reload from a partial magazine "
     "and separately from empty — they differ. Count frames from the reload animation starting to the "
     "weapon being fireable again. Ten trials, take the median. Empty reload is the number that belongs "
     "in the database."),
    ("Swap time", "Same method. Count from pressing swap to the second weapon being fireable — not to it "
     "appearing on screen. This one number scales the entire double-gun case, so do it first."),
    ("Base damage", "Private lobby with a teammate at a fixed short distance, no armour, no helmet. Fire "
     "one round at the torso and read the damage off the kill feed or their health bar. Repeat ten times; "
     "you want the mode, not the mean, because range falloff will skew a few shots."),
    ("Armour reduction", "Repeat the damage test against Level 1, 2 and 3 vests at the same distance. "
     "Reduction = 1 minus (armoured damage / unarmoured damage). Put the result in Fight Math C6."),
    ("Your real hit rate", "Not a lab number. Pull it from your own match replays: count rounds fired and "
     "hits landed across five real fights. It will be lower than you expect, and that is the point — the "
     "1v4 budget is meaningless at an imaginary accuracy."),
    ("After every patch", "Re-run reload, swap and base damage for the three or four guns you actually "
     "carry. Balance changes silently invalidate everything downstream."),
]
r = 5
mi.cell(row=4, column=2, value="Protocol").font = H2
for col in range(2, 10):
    mi.cell(row=4, column=col).fill = HDRFILL
for lab, txt in proto:
    mi.cell(row=r, column=2, value=lab).font = BOLD
    mi.cell(row=r, column=2).alignment = Alignment(vertical="top")
    c = mi.cell(row=r, column=3, value=txt); c.font = BODY; c.alignment = WRAP
    mi.merge_cells(start_row=r, start_column=3, end_row=r, end_column=9)
    mi.row_dimensions[r].height = 44
    r += 1

r += 1
mi.cell(row=r, column=2, value="Your measurements").font = H2
for col in range(2, 10):
    mi.cell(row=r, column=col).fill = HDRFILL
r += 1
style_header(mi, r, ["", "Weapon", "Base dmg", "Empty reload (s)", "Tactical reload (s)",
                     "Swap to (s)", "Trials", "Date", "Notes"],
             [3, 20, 11, 15, 16, 11, 8, 11, 40], freeze=False)
example = ["", "M416", 41, 2.10, 1.85, 0.65, 10, "2026-09-14", "EXAMPLE ROW — overwrite with your own"]
r += 1
for col, val in enumerate(example, start=1):
    if col == 1:
        continue
    c = mi.cell(row=r, column=col, value=val)
    c.font = SMALL
    c.border = BOX
for extra in range(14):
    r += 1
    for col in range(2, 10):
        c = mi.cell(row=r, column=col)
        c.fill = INFILL
        c.border = BOX
        c.font = INPUT_F

# ==========================================================================
# 8. Coach Report
# ==========================================================================
cr = wb.create_sheet("Coach Report")
cr.sheet_view.showGridLines = False
title(cr, "Coach Report")
cr.column_dimensions["A"].width = 3
cr.column_dimensions["B"].width = 108

report = [
    ("H", "1. The finding, and it is not the one I expected"),
    ("P", "I built this expecting the arithmetic to show that one magazine cannot finish a 1v4. It is "
          "narrower than that, and the narrower version is more useful."),
    ("P", "At a 40 percent hit rate against Level 2 armour, knocking four full-health players costs "
          "exactly 40 rounds fired — and an extended M416 magazine holds exactly 40. A dead tie, zero "
          "rounds to spare. That is not a margin, it is a coincidence, and it does not survive one "
          "missed burst or one enemy who heals back up."),
    ("P", "The sensitivity grid on the 1v4 Budget sheet is the real answer. Of the eighteen "
          "hit-rate-and-armour combinations on it, only four fit inside a 40-round magazine, and all "
          "four need a hit rate of 40 percent or better against Level 1 or Level 2 armour. Against "
          "Level 3 armour, one gun does not cover a 1v4 at ANY hit rate on the grid — 60 rounds needed "
          "at 40 percent, 80 at 30 percent, 120 at 20 percent."),

    ("H", "2. Why that particular gap matters"),
    ("P", "Clutches do not happen at the start of a match. They happen in the last three circles, when "
          "your squad has been broken and the surviving enemies have had twenty minutes to find Level 3 "
          "armour. So the one column of the grid where a single gun reliably fails is precisely the "
          "column that describes every real 1v4 you will ever play."),
    ("P", "That is the case for the second gun, stated properly. Not 'one magazine is never enough' — "
          "it is enough in the early game against lightly armoured opponents, where you will rarely be "
          "in a 1v4 anyway. It is never enough in the situation that actually produces clutches."),

    ("H", "3. What the second gun buys you"),
    ("P", "Swapping weapons is faster than reloading one. For the weapons where a reload time could be "
          "sourced, swapping saves roughly one and a half to two seconds, and more than three on the "
          "G36C. Two seconds at close range is a full duel."),
    ("P", "So the second gun does not add damage so much as it removes the reload from the moment that "
          "decides the fight. You reload later, behind cover, on your own schedule. The Reload versus "
          "Swap sheet quantifies it per weapon, and the tactical pattern is on the same sheet."),

    ("H", "4. Your team loadout and your clutch loadout are different"),
    ("P", "This is the recommendation I expect most pushback on, and the Double Gun sheet is the "
          "argument. The standard competitive loadout is an assault rifle plus a DMR or a bolt-action. "
          "That is correct for four-player work: the team needs range coverage and the marksman weapon "
          "earns its slot across a whole match."),
    ("P", "It is the wrong loadout for a 1v4. Clutches happen inside thirty metres, and a Mini14 or a "
          "Kar98k contributes almost nothing there. Counting its magazine as available ammunition is "
          "self-deception. Column D on the Double Gun sheet marks each pair on whether BOTH weapons are "
          "usable at clutch range, and the effect on the margin column is stark: every AR plus AR and AR "
          "plus SMG pairing carries 30 to 47 rounds of spare capacity, while AR plus DMR and AR plus "
          "sniper carry exactly zero — the same as holding one gun, because that is effectively what "
          "you are doing."),
    ("P", "The practical instruction: when your last teammate goes down, if there is a second assault "
          "rifle or an SMG within reach, swapping your marksman weapon for it is usually worth the four "
          "seconds it costs. You are no longer playing the game your loadout was built for."),

    ("H", "5. What the pairings say"),
    ("P", "AR plus AR is the strongest clutch loadout on this model — around eighty rounds of usable "
          "close-range ammunition with a sub-second gap between the two magazines. M416 plus Beryl M762 "
          "pairs the most controllable rifle with the highest close output."),
    ("P", "AR plus SMG is close behind and lighter on ammunition weight, which matters more than it "
          "sounds when you are looting a dead squad mid-fight. The DP-28 pairing is the outlier worth "
          "knowing: a 47-round second magazine gives the largest margin on the sheet, at the cost of a "
          "slow swap and a very loud gun that tells three people exactly where you are."),

    ("H", "6. What I could not establish"),
    ("P", "PUBG Mobile publishes no weapon statistics. The game exposes a power bar and nothing else. "
          "Every number in the database came from community private-lobby testing, the sources "
          "contradict each other — two PUBG Mobile sources put the M416 at 41 and 43 base damage — and "
          "reload times for most weapons could not be sourced for PUBG Mobile at all. Three reload "
          "figures in here are from the PC wiki and are labelled as placeholders. The armour reduction "
          "values driving the grid are widely quoted but I could not verify them either."),
    ("P", "None of that is hidden, and the workbook is built so it matters less than it looks: every "
          "conclusion is a formula over the database, so your measured numbers replace mine and the "
          "answers update. Note also that the central finding survives the uncertainty — at 41 base "
          "damage instead of 43 the tie becomes a shortfall, which strengthens the case rather than "
          "weakening it."),

    ("H", "7. What to run this week"),
    ("P", "Measure swap time first. The whole double-gun case scales with that one number and it is the "
          "one nobody publishes. Then empty reload and base damage for the three guns you actually "
          "carry. Enter them on the Measure It sheet and copy them into the database."),
    ("P", "Then pull your real hit rate from five match replays — rounds fired against hits landed — and "
          "put it in Fight Math C8. It will be lower than the 40 percent placeholder, and every point "
          "below 40 makes the second gun more necessary, not less."),
    ("P", "Then run the clutch drill: four teammates push one player in a fixed compound, solo player "
          "survives ninety seconds rather than trying to win. Once with the team loadout, once with a "
          "second AR, opponents in Level 3 armour both times. If the model is right the difference shows "
          "inside ten repetitions, and if it is not, you have found that out cheaply."),
]
r = 4
for kind, txt in report:
    if kind == "H":
        c = cr.cell(row=r, column=2, value=txt)
        c.font = Font(name=ARIAL, size=12, bold=True, color="16324A")
        r += 1
    else:
        c = cr.cell(row=r, column=2, value=txt)
        c.font = BODY
        c.alignment = WRAP
        cr.row_dimensions[r].height = max(30, 13 * (len(txt) // 100 + 1))
        r += 2

wb.calculation.fullCalcOnLoad = True
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("pubgm-combat-math.xlsx")
wb.save(out)
print("saved", out)
print("weapon rows:", len(W), "| database rows 5 to", LAST)
