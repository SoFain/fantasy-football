# Fantasy Football GitHub Workflow Rules

## Core Rule

Never commit directly to `master`.

All work must happen on a feature branch, then go through a GitHub Pull Request.

Your computer or IDE should treat "send my updates to GitHub" as:

1. Commit changes on a non-master branch.
2. Push that branch to GitHub.
3. Open a Pull Request into `master`.

It should not treat "send my updates to GitHub" as pushing directly to `master`.

## IDE Agent Instructions

If an IDE agent, coding assistant, or GitHub helper is doing the Git work, give it this instruction:

```text
Do not push directly to master. Create or use a feature branch named partner/<short-feature-name>, commit only the intended files, push that branch to origin, and open a Pull Request targeting master. Leave unrelated local files alone. Do not deploy.
```

If the IDE asks whether to "publish branch", "sync changes", or "push commits", confirm only when the current branch is a feature branch like:

```text
partner/fraud-watch-chart
partner/sleeper-team-ui
partner/script-mode-polish
```

Do not confirm if the current branch is:

```text
master
main
```

## Before Starting Work

1. Switch to `master`.
2. Pull latest code.
3. Create a new branch.

Commands:

```bash
git checkout master
git pull --ff-only origin master
git checkout -b partner/short-feature-name
```

Good branch names:

```bash
partner/fraud-watch-chart
partner/sleeper-team-ui
partner/script-mode-polish
```

Bad branch names:

```bash
new-stuff
test
fix
master
```

## While Working

Make focused changes. Do not mix unrelated work in one branch.

Good:

- One branch for Fraud Watch chart cleanup
- One branch for Sleeper viewer-team UI
- One branch for prompt wording

Bad:

- Changing UI, ingestion, prompts, deploy docs, and BigQuery SQL all in one branch

## Before Committing

Run a quick status check:

```bash
git status
```

Review what changed:

```bash
git diff
```

Never commit secrets:

- No API keys
- No service account JSON files
- No `.env`
- No passwords
- No Gemini keys
- No Google Cloud credentials

## Commit Rules

Commit small, logical chunks.

```bash
git add app.py
git commit -m "Improve Fraud Watch chart layout"
```

Use clear commit messages:

- `Add Segments tab chart shell`
- `Fix Sleeper team selector labels`
- `Improve Pigskin script mode prompt`

Avoid vague messages:

- `updates`
- `stuff`
- `final`
- `fix again`

## Push Rules

Push only your feature branch:

```bash
git push -u origin partner/short-feature-name
```

Never force push unless we explicitly agree.

Avoid:

```bash
git push --force
git push origin master
```

## Open A PR From The Command Line

If GitHub CLI is installed and logged in, use:

```bash
gh pr create --base master --head partner/short-feature-name
```

Use a clear title and body:

```bash
gh pr create --base master --head partner/short-feature-name --title "Improve Sleeper team UI" --body "Updates the Sleeper viewer-team form and console layout. Tested locally."
```

If GitHub CLI is not installed, open GitHub in the browser after pushing. GitHub should show a button like:

```text
Compare & pull request
```

Click it, set base to `master`, and submit the Pull Request.

## Pull Request Rules

After pushing, open a Pull Request on GitHub.

Base branch:

```text
master
```

Compare branch:

```text
partner/short-feature-name
```

PR title should say what changed.

PR body should include:

```md
## What changed

- Short bullet list

## Validation

- What was tested, or say "Not tested"

## Risk

- Any known risk or uncertainty
```

## Updating Your Branch

If `master` changed while you were working:

```bash
git checkout master
git pull --ff-only origin master
git checkout partner/short-feature-name
git merge master
```

If there are conflicts, stop and inspect them carefully. Do not blindly choose "ours" or "theirs".

## Conflict Rules

When resolving conflicts:

- Read the whole conflict block.
- Keep both changes when both are valid.
- Ask before deleting someone else's work.
- Do not resolve by guessing.

Conflict markers look like:

```text
HEAD marker
your version
separator marker
their version
end marker
```

Remove the markers after resolving.

## Deployment Rule

Do not deploy to Cloud Run unless we explicitly agree.

Deployment changes can affect the live dashboard, BigQuery access, Gemini keys, and search limits.

## BigQuery Rule

Be careful touching:

- `src/materialize.py`
- `src/pipeline.py`
- ingestion scripts
- BigQuery table names
- Cloud Run env vars

These can break the warehouse or live app.

## Final Rule

When in doubt:

1. Stop.
2. Push your branch.
3. Open a PR.
4. Ask for review.

Do not try to fix a confusing Git state by running destructive commands.

Avoid:

```bash
git reset --hard
git checkout -- .
git clean -fd
```

unless we explicitly agree.

## Quick Copy/Paste Workflow

Use this when starting a normal change:

```bash
git checkout master
git pull --ff-only origin master
git checkout -b partner/short-feature-name
```

Use this when finished:

```bash
git status
git diff
git add path/to/file1 path/to/file2
git commit -m "Describe the focused change"
git push -u origin partner/short-feature-name
gh pr create --base master --head partner/short-feature-name
```

Replace `partner/short-feature-name` with the real branch name.

If `gh pr create` fails, do not push to `master`. Open the PR manually in the GitHub website.
