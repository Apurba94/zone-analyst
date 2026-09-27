# Building and publishing Zone Analyst

Written September 2026. Store requirements change; the two deadline facts below
were checked against Apple and Google's own pages on the day of writing, but
verify before you submit.

---

## 0. Before anything

**Revoke the Expo token you pasted into chat.** expo.dev → Account Settings →
Access Tokens → delete it. Create a fresh one only if you need CI; for the
manual flow below you never need a token at all, because `eas login` handles
authentication interactively.

You need, on your own machine:

- Node 20 or newer
- The project source (this folder)
- A Google Play Console account (one-off 25 USD) for Android
- An Apple Developer Program membership (99 USD/year) for iOS

You do **not** need a Mac. EAS builds iOS on Apple hardware in the cloud.

---

## 1. Set your app identity

Open `app.json`. Replace `com.CHANGEME.zoneanalyst` in **both** places:

```json
"ios":     { "bundleIdentifier": "com.yourname.zoneanalyst" },
"android": { "package":          "com.yourname.zoneanalyst" }
```

Use a reverse-domain string you control. **This cannot be changed after first
publication on either store** — a new identifier means a new app listing with
zero reviews and zero installs.

While you are here, set `name` to whatever should appear under the icon.

---

## 2. Add the icon and splash

Create two PNGs in `assets/`:

| File | Size | Rules |
|---|---|---|
| `icon.png` | 1024 × 1024 | No transparency, no rounded corners, no alpha channel. Apple rejects alpha outright. |
| `splash.png` | 1284 × 2778 or similar | Simple, centred; it is shown for under a second. |

Then reference them in `app.json`:

```json
"icon": "./assets/icon.png",
"splash": {
  "image": "./assets/splash.png",
  "resizeMode": "contain",
  "backgroundColor": "#0E1A22"
},
"android": {
  "adaptiveIcon": {
    "foregroundImage": "./assets/icon.png",
    "backgroundColor": "#0E1A22"
  }
}
```

**Do not put "PUBG" in the icon, the app name, or the store title.** The app is
not affiliated with KRAFTON or Tencent. Using their marks invites store
rejection under the impersonation rules *and* a trademark complaint that can
remove the listing without warning. "Zone Analyst" is deliberately neutral.

---

## 3. Install and verify locally

```bash
npm install
npx tsc --noEmit        # must be clean
npx expo start          # scan the QR with Expo Go to try it on a phone
```

If you add any package later, use `npx expo install <pkg>`, **never**
`npm install <pkg>@latest`. Expo SDK 57 pins specific native module versions
(React Native 0.86.3, react-native-svg 15.15.4, reanimated 4.5.1). Installing
newer published versions produces a Metro error —
`Cannot find module 'react-native/rn-get-polyfills'` — that looks exactly like a
bug in your code and is not one.

---

## 4. Build

```bash
npm install -g eas-cli
eas login
eas init          # links the project, writes the projectId into app.json
```

Then pick a profile from `eas.json`:

```bash
# APK you can sideload onto a phone right now, for testing
eas build -p android --profile preview

# AAB for Google Play
eas build -p android --profile production

# IPA for the App Store
eas build -p ios --profile production
```

Each build takes roughly 10–20 minutes and finishes with a download link.

**On signing keys:** when EAS asks whether it should generate a keystore, say
yes, then immediately run `eas credentials` and download a backup. If you lose
the Android keystore you can never update the app under the same listing again.
Play App Signing gives you a recovery path, but only if you enrol at first
upload — do it.

---

## 5. Requirements that will reject you

**Android — target API 36.** Since 31 August 2026, all new Play submissions and
updates must target Android 16 (API level 36). That deadline has passed. This
project pins it explicitly in `app.json` via `expo-build-properties`, because
the Expo Gradle defaults were ambiguous between 35 and 36. Do not remove that
plugin block.

**iOS — Xcode 26 and the iOS 26 SDK.** Since 28 April 2026, App Store Connect
requires builds made with Xcode 26 or later against an iOS 26 SDK. EAS's default
build image for SDK 57 already satisfies this, so you need do nothing. If a
build is ever rejected for SDK age, pin the image in `eas.json`:

```json
"production": { "ios": { "image": "latest" } }
```

---

## 6. Google Play, step by step

1. **play.google.com/console** → *Create app*. Set name, default language, App
   or Game (choose **App** — it is a tool, not a game), Free/Paid.
2. Work through the **Dashboard** checklist. Play will not let you publish
   until every item is green.
3. **App content** — this is where most first submissions stall:
   - *Privacy policy*: a URL is mandatory even if you collect nothing. Host a
     one-page policy stating that the app collects and transmits no personal
     data. GitHub Pages is fine.
   - *Data safety*: declare no collection and no sharing. This app stores
     nothing off-device.
   - *Ads*: no.
   - *Content rating*: complete the IARC questionnaire. Answer honestly; the
     app has no violence, so it will rate very low.
   - *Target audience*: select 18+ or 13+. Do **not** include under-13 unless
     you want Families Policy review, which is a much longer process.
   - *Government apps*, *Financial features*, *Health*: all no.
4. **Store listing** — short description (80 chars), full description (4000),
   at least **2 phone screenshots** (16:9 or 9:16, min 320 px), a 512 × 512
   icon, and a 1024 × 500 feature graphic. Take the screenshots from the
   simulator and combat-math screens; they are the most visually distinctive.
5. **Testing first.** Go to *Testing → Internal testing*, create a release,
   upload the AAB, add your own email as a tester. Install from the opt-in link
   and confirm the app actually runs on a real device. Do this before
   production — it is faster and catches signing problems early.
6. **Production** → *Create new release* → upload the AAB → release notes →
   *Send for review*.
7. Review takes anywhere from a few hours to about seven days for a new
   developer account. First-time personal accounts may additionally need
   **20 testers running a closed test for 14 days** before production access
   unlocks; check whether your account is subject to this, because it changes
   your timeline from days to weeks.

You can also automate the upload with `eas submit -p android`, but for the first
release do it by hand so you see every consent screen.

---

## 7. App Store, step by step

1. **developer.apple.com** → enrol in the Apple Developer Program. Individual
   enrolment is usually approved in 24–48 hours; organisation enrolment needs a
   D-U-N-S number and takes longer.
2. **appstoreconnect.apple.com** → *My Apps* → **+** → *New App*. Pick iOS, the
   name, primary language, your bundle ID (it appears in the dropdown once EAS
   has registered it), and an SKU (any private string).
3. **Upload the build**: `eas submit -p ios` — or download the IPA and use
   Transporter from the Mac App Store. Processing takes 10–30 minutes before
   the build appears in App Store Connect.
4. Fill in the listing:
   - Screenshots for 6.7" and 6.5" iPhone are mandatory. Simulator screenshots
     are acceptable.
   - Description, keywords, support URL, marketing URL.
   - **Privacy policy URL** — mandatory, same as Play.
   - *App Privacy* questionnaire → declare no data collection.
   - Age rating questionnaire. Apple updated this in January 2026; answer the
     current questions rather than copying an old submission.
5. **Export compliance**: you will be asked whether the app uses encryption.
   This app makes no network calls and uses no encryption, so answer no. If you
   ever add HTTPS calls, the answer becomes "yes, exempt".
6. Submit for review. Typical turnaround is 24–48 hours.

### The rejection to actually plan for

Guideline **4.2 Minimum Functionality**. Apple rejects apps that are thin
wrappers around a website or that merely repackage content. This is exactly why
every screen here is native React Native with `react-native-svg` rather than a
WebView around the HTML versions — the interactive simulator and the
calculators are real app functionality. If you are asked to justify it in the
review notes, say plainly: the app performs Monte Carlo simulation and
statistical inference on-device, with no server and no web content.

Also worth pre-empting in the review notes: state that the app is an
independent analytical tool, is not affiliated with any game publisher, and
contains no game assets.

---

## 8. After the first release

`eas.json` sets `autoIncrement` on the production profile, so build numbers
advance by themselves. To ship an update:

1. Bump `"version"` in `app.json` (the human-facing string, e.g. `1.0.1`).
2. `eas build -p android --profile production` and/or `-p ios`.
3. `eas submit` to the relevant store.

For pure JavaScript changes — new playbook text, a tweaked formula — you can
push an over-the-air update with `eas update` and skip review entirely. Native
changes, new packages, or anything touching `app.json` plugins still require a
full build and a new review.
