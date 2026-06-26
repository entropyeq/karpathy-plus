---
description: Scan wiki for stale pages, broken links, overdue tasks, drift
---

Run a comprehensive wiki lint pass. Follow each step in order.

A slash command runs in whatever directory the session happens to be in, so do not use bare relative paths — every path below is absolute under the wiki root.

0. **Resolve the wiki root.** Set `WIKI=~/knowledge/wiki` (expand the `~` to the absolute home path) and use `$WIKI/...` throughout. After each step, append one line to `$WIKI/.lint-run` recording what you did and what you found (e.g. `step 3 broken-links: 2 found, 2 fixed`). Start by truncating `$WIKI/.lint-run`.

Which checks are mechanical vs judgment: link validity (step 3), frontmatter-date-vs-git (step 2), and root clutter (step 8) are mechanical — same answer every run, and a good candidate to extract into a script later. The rest (which pages to update, whether a flagged item actually matters) are judgment calls and stay here.

1. **Process update queue.** Check `$WIKI/.update-queue`. Read each entry, determine which wiki pages need updating, update them, clear the queue.
2. **Freshness check.** Compare `last_updated` frontmatter against git activity. Flag project pages >1 week stale relative to their repo. (Mechanical.)
3. **Broken links.** Scan all pages for markdown links. Verify targets exist. Auto-fix obvious renames. (Mechanical.)
4. **Task aggregation.** Collect all `- [ ]` items across pages. Age via git blame. Write top 10 to `$WIKI/tasks-open.md`.
5. **Log gap check.** Flag if most recent `$WIKI/log.md` entry is >3 days old.
6. **Unprocessed sources.** Skip unless your pages actually use a `processed:` frontmatter key — no shipped page does on a fresh install, so this no-ops until the convention appears. Once it does: flag files in `$WIKI/sources/` without `processed: true`, older than 5 days.
7. **Log rotation.** If `$WIKI/log.md` has entries older than 30 days, archive them to `$WIKI/sources/log-archive-YYYY-MM.md`.
8. **Root cleanliness.** List the knowledge root (`~/knowledge/`) contents. Flag anything not in the approved bucket list. Ask triage: do it / defer it / kill it. (Mechanical.)
9. **Auto-memory drift check.** Skip unless you have enabled Claude Code memory (the template does not scaffold it). If enabled: diff key facts between auto-memory and wiki, auto-fix obvious staleness.
10. **Plan reconciliation.** Skip unless your plan pages actually carry a `last_reconciled` frontmatter key — no shipped page does on a fresh install. Once they do: for each `$WIKI/plans/*.md`, compare `last_reconciled` to `last_updated` of any referenced project and flag plans that predate their dependencies.
11. **Heartbeat.** Write the current timestamp to `$WIKI/.lint-heartbeat`. Update the `Last updated / Last lint` heartbeat line in `$WIKI/INDEX.md` with the lint summary, and make sure its task pointer reads `tasks-open.md`.
12. **Report.** Read `$WIKI/.lint-run` back verbatim, then present findings: auto-fixed (just report) and needs-attention (ask triage per item).
13. **Remote sync.** `cd ~/knowledge/wiki && (git diff --quiet HEAD || (git add -A && git commit -m 'wiki-lint: auto-sync' && GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10' git push))`. BatchMode makes an SSH remote fail fast instead of hanging when no ssh-agent is loaded; an HTTPS remote with a credential helper avoids it entirely.

These steps grow as conventions actually appear. Following the repo's own rule, add a new check (or a new gated frontmatter key) only after its need has fired twice — don't pre-wire checks for keys no page uses yet.
