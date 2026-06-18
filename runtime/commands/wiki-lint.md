---
description: Scan wiki for stale pages, broken links, overdue tasks, drift
---

Run a comprehensive wiki lint pass. Follow each step in order. After each step, append one line to `wiki/.lint-run` recording what you did and what you found (e.g. `step 3 broken-links: 2 found, 2 fixed`). Start by truncating `wiki/.lint-run`.

1. **Process update queue.** Check `wiki/.update-queue`. Read each entry, determine which wiki pages need updating, update them, clear the queue.
2. **Freshness check.** Compare `last_updated` frontmatter against git activity. Flag project pages >1 week stale relative to their repo.
3. **Broken links.** Scan all pages for markdown links. Verify targets exist. Auto-fix obvious renames.
4. **Task aggregation.** Collect all `- [ ]` items across pages. Age via git blame. Write top 10 to `wiki/tasks-open.md`.
5. **Log gap check.** Flag if most recent `log.md` entry is >3 days old.
6. **Unprocessed sources.** Flag files in `wiki/sources/` without `processed: true` frontmatter, older than 5 days.
7. **Log rotation.** If `log.md` has entries older than 30 days, archive them to `wiki/sources/log-archive-YYYY-MM.md`.
8. **Root cleanliness.** List the knowledge root contents. Flag anything not in the approved bucket list. Ask triage: do it / defer it / kill it.
9. **Auto-memory drift check.** Diff key facts between runtime auto-memory and wiki. Auto-fix obvious staleness.
10. **Plan reconciliation.** For each `wiki/plans/*.md`, compare `last_reconciled` to `last_updated` of any referenced project. Flag if plan predates its dependencies.
11. **Heartbeat.** Write current timestamp to `wiki/.lint-heartbeat`. Update the `Last updated / Last lint` heartbeat line in `INDEX.md` with the lint summary.
12. **Report.** Read `wiki/.lint-run` back verbatim, then present findings: auto-fixed (just report) and needs-attention (ask triage per item).
13. **Remote sync.** `git add -A && git commit && git push` when clean.
