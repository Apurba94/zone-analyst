# Putting the website on Hostinger

Everything the site needs is inside the `website` folder. It is plain HTML, CSS
and JavaScript: no database, no PHP, nothing to install on the server.

Hostinger's menus change from time to time. The labels below match Hostinger's
own help pages as of September 2026; if one has moved, the linked help page
will have the current wording.

## Put it on a subdomain

If your domain already serves a site from its main `public_html` folder — your
course platform, for instance — **don't upload into that folder.** The
`index.html` here would replace that site's home page. Give this site its own
subdomain, such as `zone.yourdomain.com`, and the two never touch.

## 1. Create the subdomain

Hostinger recommends adding a subdomain as its own website
([help page](https://www.hostinger.com/support/1583405-how-to-create-and-delete-subdomains-in-hostinger/)):

1. hPanel → **Websites** → **Add website**.
2. Enter the subdomain, e.g. `zone.yourdomain.com`, and finish the steps. Pick
   the option to upload your own files rather than a site builder or WordPress.

Alternatively, inside your main website's dashboard: **Domains → Subdomains**,
enter `zone`, keep the default directory, **Create**. That puts the files in a
subfolder of the main site (for example `public_html/zone`) — fine too, since
subdomains still have their own address.

## 2. Pack the files

1. Open the `website` folder on your computer.
2. Select **everything inside it** (Ctrl+A) — not the folder itself.
   Make sure `.htaccess` is selected; it's the server settings file.
3. Right-click → **Send to** → **Compressed (zipped) folder**. Name it `site.zip`.

Zipping the contents rather than the folder matters: otherwise the site ends up
at `zone.yourdomain.com/website/` instead of the address itself.

## 3. Upload and extract

1. hPanel → **Websites** → the subdomain's **Dashboard** → **File Manager**.
   It opens in that site's folder.
2. If the folder already has a placeholder `default.php` or `index.php`, delete
   it — it would compete with `index.html`.
3. **Upload** `site.zip` into the folder.
4. Right-click `site.zip` → **Extract**
   ([help page](https://www.hostinger.com/support/1583613-how-to-extract-archives-using-the-file-manager-in-hostinger/)).
   Choose the **current folder** as the destination, tick **Overwrite existing
   files**, then **Extract**.
5. Delete `site.zip`.

Check the result: `index.html`, `.htaccess`, `404.html` and the `assets` and
`downloads` folders should sit directly in the site's folder.

## 4. Turn on HTTPS

1. hPanel → the subdomain's dashboard → **Security** → **SSL**. Hostinger
   issues a free certificate; a new subdomain can take a little while to get one.
2. Once it shows as active, switch on **Force HTTPS**.

HTTPS is enforced here rather than in `.htaccess` on purpose: a redirect in
that file would break the site if the certificate hadn't finished installing.

## 5. Test it

- Open `https://zone.yourdomain.com` and click through every page.
- Press **Play** on the simulator; drag a slider on combat math.
- Download the workbook from the combat page.
- Visit a made-up address such as `https://zone.yourdomain.com/nothing-here`.
  You should see the "You're outside the zone" page, styled.

## Updating the site later

Upload just the files you changed, into the same place, overwriting the old
ones. Pages are sent with no caching, so changes show immediately; the
stylesheet and scripts are cached for a day, so after changing
`assets/site.css` press Ctrl+F5 to see it straight away.

## If you use a subfolder instead of a subdomain

For an address like `yourdomain.com/zone/`, two lines must name the folder:

- `.htaccess`: `ErrorDocument 404 /zone/404.html`
- `404.html`, near the top: `<base href="/zone/">`

Everything else uses relative links and works from any folder.

## Optional: deploy from GitHub with one click

Once the project is on GitHub (see `GITHUB.md`), the repository can upload the
`website` folder for you — only that folder, never the research code or the
app. It never runs by itself.

1. **FTP details.** hPanel → **Files** → **FTP Accounts** shows the hostname
   and username, and lets you set the password. Safer still, create a new FTP
   account limited to the subdomain's folder.
2. **Find the upload folder.** In File Manager, note the path from the FTP
   account's starting folder to the folder holding `index.html` — often
   `public_html/`. It must end with `/`. If the FTP account opens directly in
   that folder, use `./`.
3. **Store them in GitHub.** Repository → **Settings** → **Secrets and
   variables** → **Actions**:
   - *Secrets*: `HOSTINGER_FTP_HOST`, `HOSTINGER_FTP_USER`, `HOSTINGER_FTP_PASSWORD`
   - *Variables*: `HOSTINGER_FTP_DIR` (the folder from step 2)
4. **Run it.** **Actions** tab → **Deploy website to Hostinger** → **Run
   workflow**. The **Dry run** box starts ticked: the first run lists what it
   would upload and changes nothing. Read the log, then run again with the box
   unticked.

The workflow connects with encrypted FTP (FTPS). I couldn't confirm from
Hostinger's documentation that FTPS is supported on every plan. If the dry run
fails with a TLS or connection error, add the variable
`HOSTINGER_FTP_PROTOCOL` with the value `ftp` and run the dry run again.
