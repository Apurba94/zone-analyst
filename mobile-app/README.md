# Zone Analyst

An Expo / React Native app carrying the four tools built in this project:

- **Zone simulator** — animated shrinking zone, draggable team with HP, escape
  calculator, and a live test battery over accumulated matches.
- **Probability chart** — next-centre density and the survival field.
- **Combat math** — weapon database, 1v4 ammunition budget with the armour
  sensitivity grid, ranked double-gun loadouts.
- **Playbook** — anti-rush defence, the 1v4 clutch, 2026 map pool analysis.

All screens are native React Native with `react-native-svg`. Nothing is a
WebView wrapper, which matters: Apple rejects repackaged websites under
App Store Review Guideline 4.2 (Minimum Functionality).

## Verified state

Both platforms bundle clean on Expo SDK 57:

```
npx tsc --noEmit            # passes
npx expo export --platform android   # 2.9 MB Hermes bundle
npx expo export --platform ios       # 2.6 MB Hermes bundle
```

`targetSdkVersion` is pinned to **36** via `expo-build-properties`. Google Play
has required API 36 for all new apps and updates since 31 August 2026, and the
Expo Gradle defaults were ambiguous between 35 and 36, so it is set explicitly.

## Version pinning

Use `npx expo install <pkg>`, never `npm install <pkg>@latest`. Expo SDK 57 pins
specific native module versions (RN 0.86.3, react-native-svg 15.15.4,
reanimated 4.5.1, and so on). Installing latest-published versions produces a
Metro resolution failure that looks like a code bug and is not one.

## Build

```bash
npm install
npm install -g eas-cli
eas login
eas init                       # links the project, writes the project ID
eas build -p android --profile preview      # APK for sideloading
eas build -p android --profile production   # AAB for Play
eas build -p ios     --profile production   # IPA for App Store
```

## Before you ship

1. `app.json` → replace `com.CHANGEME.zoneanalyst` in **both** `ios.bundleIdentifier`
   and `android.package` with your real reverse-domain id. It cannot be changed
   after first publication.
2. Add `assets/icon.png` (1024×1024, no transparency, no rounded corners) and
   `assets/splash.png`, then reference them in `app.json`.
3. Keep the disclaimer on the home screen. The app is not affiliated with
   KRAFTON, Tencent or PUBG Mobile, and using those marks in the store listing
   title or icon invites both store rejection and a trademark complaint.

## Data honesty

The zone models come from a published Tencent patent describing a candidate
centre-selection routine — an embodiment, not shipped code. The weapon numbers
are community private-lobby estimates; PUBG Mobile publishes no stat table, the
sources contradict each other, and most reload times could not be sourced at
all. Rows carry their own confidence grade and the UI surfaces it.
