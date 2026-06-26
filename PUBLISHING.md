# Publishing this repo (maintainer only)

This file is for the person publishing the template (the author). End users never need it — they just click **Use this template**. Keep it separate from the build flow so consumers do not run these commands by mistake.

Publish private-first, eyeball it, then flip public and turn on the template button. Every step is reversible. macOS/Linux terminal, run from inside the repo.

(If you forked this template, use your own GitHub username and repo name in the commands below.)

### 0. Confirm the right GitHub account

```bash
gh auth status
```

The line `Active account: true` must sit under your personal account (`entropyeq`), not a work account. If it is on the wrong one:

```bash
gh auth switch --user entropyeq
```

### 1. Go to the repo

```bash
cd path/to/karpathy-plus
```

### 2. Create it PRIVATE and push (one command)

```bash
gh repo create karpathy-plus --private --source=. --remote=origin --push
```

Creates `entropyeq/karpathy-plus` as private, links it as `origin`, uploads `main`. Nobody can see it yet.
Undo: `gh repo delete entropyeq/karpathy-plus --yes` (your local files stay untouched).

### 3. Look it over in the browser (still private)

```bash
gh repo view entropyeq/karpathy-plus --web
```

Confirm the files look right before anyone can see them.

### 4. Flip it PUBLIC (only after step 3 looks good)

```bash
gh repo edit entropyeq/karpathy-plus --visibility public --accept-visibility-change-consequences
```

The `--accept-visibility-change-consequences` flag is REQUIRED by current gh or the command errors out.
Undo: same command with `--visibility private`.

### 5. Turn on "Use this template"

```bash
gh repo edit entropyeq/karpathy-plus --template
```

The flag is `--template` (NOT `--enable-template`). This shows the green "Use this template" button the README depends on; without it, the downstream instructions do not work.
Undo: `gh repo edit entropyeq/karpathy-plus --template=false`

### Verify

```bash
gh repo view entropyeq/karpathy-plus --json visibility,isTemplate
```

Expect `"visibility":"PUBLIC"` and `"isTemplate":true`.

---

**Before flipping public:** skim `git log` and the tracked files. Anything committed becomes permanently public, history included. Never fill `personal/bio.md` or `runtime/CLAUDE.md` with real personal data in the copy you publish — they ship as blank templates on purpose.
