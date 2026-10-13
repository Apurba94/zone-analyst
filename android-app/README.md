# Zone Analyst for Android (web version)

The website packaged as an APK with [Capacitor](https://capacitorjs.com) 8. The
pages run in Android's WebView from files inside the APK, so the app works
offline; only the two web fonts need a connection, and without one a standard
serif and sans-serif stand in.

This is not the same as `../mobile-app/`. That one is a native Expo rewrite
meant for the app stores. This one is the website itself, for installing from
the APK file.

## Install

On the phone, download `Zone-Analyst.apk` from the
[latest release](https://github.com/Apurba94/zone-analyst/releases/latest)
and open it. Android asks once to allow installs from your browser. Android 7.0
or newer.

## Build it

**In the cloud (no Android tools needed).** GitHub builds it on every tag that
starts with `v`, and on demand from **Actions → Desktop and Android apps → Run
workflow**; the APK is under **Artifacts** on the run's page.

**On your computer.** Needs Node.js 22+, JDK 21 and the Android SDK
([Android Studio](https://developer.android.com/studio) installs both):

```bat
npm install
npm run sync                 :: copies ..\website into www\ and into the Android project
cd android
gradlew assembleRelease      :: android\app\build\outputs\apk\release\app-release.apk
```

or `npm run open` to build and run it from Android Studio. Run `npm run sync`
again after every change to the website.

## Signing

Every version must be signed with the same key, or phones that have the app
can't update it. The release key is read from the environment, never from the
repository:

| Variable | Value |
|---|---|
| `ZA_KEYSTORE_FILE` | path to `zone-analyst-release.p12` |
| `ZA_KEYSTORE_PASSWORD` | its password (the key uses the same one) |
| `ZA_KEY_ALIAS` | `zoneanalyst` |

Without them the release APK is signed with the debug key: it installs, but it
can't update a copy signed with the release key.

Where the key lives:

- `android-app/signing/` on the computer that created it, with the password in
  `KEEP-THIS-SAFE.txt`. Git ignores this folder. **Back it up somewhere
  private**; it is the only readable copy.
- GitHub repository secrets `ANDROID_KEYSTORE_BASE64` (the file, base64) and
  `ANDROID_KEYSTORE_PASSWORD`, which the workflow uses. GitHub never shows
  secrets back.

## What changes on the way in

`scripts/copy-web.mjs` copies the site unchanged except for one link: Android's
WebView can't save a file a page offers for download, so the workbook button
points at `https://zoneanalyst.vercel.app/downloads/…` and the phone's browser
downloads it. The script stops with an error if that link ever moves.

## Icons and version

- `assets/*.png` come from `scripts/make_app_icons.py`; `npm run icons` turns
  them into the launcher icons and splash screens under `android/app/src/main/res`.
- Each release: raise `versionCode` by one and set `versionName` in
  `android/app/build.gradle`, and match `"version"` in `package.json`.
