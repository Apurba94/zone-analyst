# Data collection protocol

Read §7 and §8 of REPORT.md first. They determine how much of this is worth
doing and which phases are worth annotating.

## Legal scope

Permitted sources only: publicly broadcast tournament VODs, your own gameplay
recordings, your own custom rooms, and public screenshots. Nothing that touches
game memory, network traffic, the client binary, or anti-cheat. If a tournament
organiser restricts analytical use of their footage, that governs.

## Priority order

1. **Radius schedule** (~5 matches per map). Cheapest, highest leverage, and
   reusable forever. Every downstream probability depends on it.
2. **Ten transitions** for the structural tests. Two matches. Settles
   containment, angle-radius coupling and the half-plane reading at high power.
3. **Your own error characterisation** on your own footage, before trusting any
   containment tolerance.
4. **~200 transitions, phases 1-4 only**, one map, for radial and phase structure.
5. Custom rooms for late phases and the player-distribution question.

Do not start at step 4.

## Per-observation checklist

Record one row per circle in `data/raw/circles.csv`
(`python -c "from bluezone.schema import write_template as w; w('data/raw/circles.csv')"`).

- `match_id` stable and unique: tournament, day, match number.
- `phase` 1-based, and never guessed. A skipped phase looks like a double-size
  jump and corrupts every displacement statistic. `schema.validate` catches gaps
  in numbering but cannot catch a phase you mislabelled consistently.
- `x, y, r` normalised to the playable map square, not to the video frame.
- `source` a URL or filename plus a timestamp precise enough to re-find the
  frame. An observation you cannot re-check is one you cannot correct.
- `fit_quality` honest. `poor` rows are excluded by default rather than
  quietly weighted down.

## Frame selection

Prefer full-screen map views over minimap views: the circle is larger,
unclipped, and drawn on a known rectangle. `cv.find_map_frames` triages a video
for candidates; it is a shortlist for a human, not a detector.

Establish the pixel rectangle of the playable map area once per broadcast
layout, from landmarks, and reuse it. Re-derive it whenever the overlay changes,
including mid-tournament — a graphics package update silently shifts every
coordinate you record afterwards.

## Two-annotator agreement

For the first 20 transitions, have two people annotate independently and compare.
The spread between them is your real error, and it is usually larger than the
fitter's synthetic error. Use it, not the synthetic figure, to set
`containment_test(tol=...)`.

## What not to do

- Do not annotate the blue zone boundary mid-shrink as if it were the target
  circle. Only the settled white circle defines phase geometry.
- Do not mix public matches with esports rooms in one dataset. They may use
  different parameters; that is an open question, not an assumption.
- Do not fill missing phases by interpolation. Drop the match.
- Do not annotate from clips that have been re-encoded, cropped or zoomed by a
  third party, unless you can recover the original framing.
