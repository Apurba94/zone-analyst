# Publishing the project on GitHub

The project folder is already a Git repository with its first commit, so its
history and authorship come with it. Publishing it only has to connect that
repository to your GitHub account.

## Option A — GitHub Desktop (no command line)

1. Install [GitHub Desktop](https://desktop.github.com/) and sign in with your
   GitHub account.
2. Unzip `zone-analyst.zip` somewhere you'll keep it, such as
   `Documents\zone-analyst` — not Downloads, since you'll keep working in it.
3. GitHub Desktop → **File** → **Add local repository** → choose the
   `zone-analyst` folder → **Add repository**. It recognises the existing
   commit.
4. Click **Publish repository**. Keep the name `zone-analyst` or change it,
   choose whether to tick **Keep this code private**, then **Publish repository**.

It's now at `github.com/<your-username>/zone-analyst`, and the **Actions** tab
will show the checks running for the first time.

**Making changes later:** edit files as usual. GitHub Desktop lists what
changed; type a one-line summary, click **Commit to main**, then **Push origin**.

## Option B — the command line

Create an empty repository on [github.com/new](https://github.com/new) — no
README, licence or .gitignore, since the project has its own — then, in a
terminal in the project folder:

```bat
git remote add origin https://github.com/<your-username>/zone-analyst.git
git push -u origin main
```

## Option C — let Claude push it

Connect GitHub to Claude in claude.ai **Settings → Connectors**, create an
empty repository as in option B, and tell Claude its name.

## Before you make it public

- **Nothing secret is in it.** No passwords, tokens or keys; the repository was
  scanned for them before the first commit. Hostinger FTP details belong in
  GitHub's encrypted **Secrets**, never in a file.
- **Your name is in it on purpose**: the copyright line in the site footer and
  the README. Change it in `scripts/site_chrome.py` if you'd prefer otherwise.
- **Choose a licence if you want others to reuse the work.** A public
  repository without one can be read, but nobody has permission to copy or
  reuse it. To add one: **Add file → Create new file**, name it `LICENSE`, and
  GitHub offers templates. MIT is the common choice for letting people reuse
  code with credit; leaving it out keeps all rights reserved.
