# ESS Service Desk – Open Ticket Analysis

An interactive HTML dashboard (`index.html`) built from the open tickets (statusCategory ≠ Done) in the Jira Service Management project **ESS** (ederm.atlassian.net). It opens in any browser and needs no internet connection.

Pages (left sidebar):

- **Dashboard:** headline numbers, ticket mix, tickets opened (weekly/monthly), top pain points, automation summary, product-area boxes and backlog age
- **Pain points:** the six biggest customer problems, ordered by impact
- **Automation:** 11 product features that would remove manual agent work, with a "what-if" you can switch on and off
- **Similar tickets:** 51 groups of related tickets plus hand-checked duplicate pairs
- **Noise:** server alerts, vendor notices and reply-all duplicates, plus rules to keep them out of the queue
- **All tickets:** a searchable, sortable list with links to Jira

Filters at the top (date range, organization, product area) update every page. Clicking any chart element opens the matching tickets, and there's a light/dark switch.

Data snapshot: **2026-11-04 · 710 open tickets**

## Privacy

`index.html` is the **redacted** version for this repo. Ticket descriptions and reporter names are removed, and any summary containing an MRN, DOB or patient name is replaced with "Patient-specific ticket (details redacted)".

The full version with descriptions is in `local-only/`. That folder is git-ignored so it never gets committed. Don't commit it or publish it.

If you turn on GitHub Pages, keep the repo **private** and check who can see the Pages site. On most GitHub plans, a Pages site is public even when the repo is private.

## Publishing to GitHub

Repo: https://github.com/practice-engine/jira-dashboard-ederm

**With GitHub Desktop:** File → Add local repository → pick this folder. If it isn't a repo yet, choose "create a repository" first. Commit, set the remote to the repo above, then Push.

**With the command line** (run in this folder):

```bash
git init
git add .
git commit -m "ESS open-ticket analysis dashboard (2026-11-04 snapshot)"
git branch -M main
git remote add origin https://github.com/practice-engine/jira-dashboard-ederm.git
git pull origin main --allow-unrelated-histories   # only if the repo already has commits (e.g. a README)
git push -u origin main
```

**To view it as a web page (optional):** in the repo go to Settings → Pages → Deploy from branch → `main` / root. Read the Privacy note above first.

## Refreshing the data

The `scripts/` folder has the pipeline that generated the dashboard:

1. `consolidate.py`: flattens the Jira search results into `tickets.json`
2. `classify.py`: assigns product area, ticket kind, noise flag and automation opportunity (keyword rules plus manual overrides)
3. `cluster.py`: builds the similar-ticket groups and text-similarity pairs
4. `build.py`: fills `template.html` with the data and the eDerm logos (`logo.b64`, `logow.b64`). Add `--public --out index.html` for the redacted build.
5. `opp.json`: descriptions of each automation opportunity (today's process, what to build, effort, who benefits)

The scripts were run in a temporary workspace, so the file paths at the top of each script (`/tmp/w/…`) need updating before you reuse them. The ticket data came from the Jira JQL `project = ESS AND statusCategory != Done`.

Classification is a strong first pass, not ground truth. Check groups before bulk-linking or closing tickets in Jira.
