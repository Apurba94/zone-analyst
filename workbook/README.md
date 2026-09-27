# Combat-math workbook

`pubgm-combat-math.xlsx` is the 1v4 ammunition model as a spreadsheet: weapon
database, fight math, the 1v4 budget with its armour sensitivity grid, ranked
double-gun loadouts, reload-versus-swap, a measurement protocol, and a coach's
report. Blue bold cells are inputs; change them and everything recomputes.

`build_workbook.py` generates it:

```bat
py -m pip install openpyxl
py workbook\build_workbook.py            :: writes workbook\pubgm-combat-math.xlsx
```

Excel recalculates on open. The shipped copy has also been recalculated with
LibreOffice (630 formulas, 0 errors), so phone and web previewers show values
rather than blanks. After rebuilding, copy the file to `website/downloads/` so
the site serves the same version.

The website's combat page runs the same model in the browser, compiled from
`mobile-app/src/combat.ts`; the two were checked to agree on every compared
figure.
