# The website on Vercel

**Live at [zoneanalyst.vercel.app](https://zoneanalyst.vercel.app).**
`zone-analyst-pi.vercel.app`, the name Vercel assigned first, points at the same
deployment.

The Vercel project is `zone-analyst` (team `janin-a-apurba`), connected to
[github.com/Apurba94/zone-analyst](https://github.com/Apurba94/zone-analyst):

- every push to `main` deploys to production;
- every other branch and pull request gets its own preview address.

Nothing has to be uploaded by hand.

## What Vercel does with the repository

`vercel.json` at the top of the repository sets it up:

| Setting | Value | Why |
|---|---|---|
| Build command | `python3 scripts/check_site.py` | There is nothing to build, so the deploy runs the site checker instead. A broken link or missing file fails the deploy, and production keeps serving the last good version. |
| Output directory | `website` | Served exactly as it is in the repository. |
| Headers | the same as `website/.htaccess` | `nosniff`, referrer and frame policies, no camera/microphone/location; the workbook downloads instead of opening; stylesheet, scripts and icon cached for a day. |

`.vercelignore` leaves the research toolkit, the apps and the docs out of the
upload. Unknown addresses get `website/404.html`, which Vercel picks up by
name.

## Deploy by hand

Only needed if the GitHub connection is ever removed. In the project folder:

```bat
npx vercel login
npx vercel deploy --prod
```

## Use your own domain

Vercel → project `zone-analyst` → **Settings → Domains** → **Add**, enter for
example `zone.yourdomain.com`, and add the DNS record Vercel shows at the
company that manages the domain. The certificate is issued automatically.

Then change `https://zoneanalyst.vercel.app` wherever it appears: `README.md`,
this file, `android-app/scripts/copy-web.mjs` (the workbook link inside the
Android app), and `"homepage"` in `desktop-app/package.json` and
`android-app/package.json`.

## Vercel and Hostinger

Both serve the same `website` folder, so either or both can run.
[DEPLOY_HOSTINGER.md](DEPLOY_HOSTINGER.md) still applies unchanged.
