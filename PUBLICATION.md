# Publication status and next commands

Public publication was **not completed by the agent**. The workspace is not a Git repository, so there is no existing local history, branch or remote to preserve. `git init -b main` failed because the sandbox denies writing this project's `.git` path. GitHub CLI (`gh`) is absent and shell DNS access to github.com fails. The connected GitHub tools expose profile/file/commit operations but no repository creation operation. No repository URL, successful push or public commit ID is claimed.

The public file set is the original Python scripts, app/backend, tests, requirements, documentation, `.gitignore`, fictional TXT resumes and synthetic development CSV/JSON. No dataset binaries, user uploads, personal documents, environment directories, local verification/session logs or model weights should be added. A credential-pattern scan of the source/docs/evaluation files found no matches; that is not a guarantee for subsequently added files.

## Complete publication in normal macOS Terminal

Run from this project directory, outside the agent sandbox. Do not stop the working Streamlit process.

```sh
brew install gh
gh auth login --web --git-protocol https
gh auth status
```

Confirm this is the GitHub account you intend to publish under. Never paste credentials into chat. If Homebrew is unavailable, install GitHub CLI using its official installer instructions: https://cli.github.com/ .

Before initializing, run `git status`, `git branch --show-current` and `git remote -v`. The audited workspace had no `.git`; if that changes, inspect the existing repository/history rather than overwriting it. Only for the still-uninitialized project:

```sh
git init -b main
git add .gitignore README.md TEAM_DEMO.md PUBLICATION.md DEMO_GUIDE.md requirements.txt app.py launch_demo.py evaluate_demo.py rank_dataset.py match_resume.py inspect_data.py audit_data.py preprocess_data.py verify_processed.py talentrag tests demo_resumes data/README.md results/development.csv results/development.json
git diff --cached --stat
git diff --cached --name-only
git status --short
```

Review staged paths/content. No raw/processed dataset binary, secret, environment, upload or log should appear. If Git requests author configuration, set your own Git identity locally; no author identity is invented here.

```sh
git commit -m "Prepare TalentRAG interim demonstration and team handoff"
```

Inspect whether the repository name is available under the authenticated account:

```sh
gh repo view talentrag --json nameWithOwner,isPrivate,url,description
```

If it reports **not found** and authentication is working, create and push:

```sh
gh repo create talentrag --public --source=. --remote=origin --push
```

If `talentrag` exists and is unrelated, inspect `gh repo view talentrag-demo --json nameWithOwner,isPrivate,url,description` and use the alternative name only if free:

```sh
gh repo create talentrag-demo --public --source=. --remote=origin --push
```

If an existing repository has conflicting contents or private visibility, do not force-push, delete it or change visibility automatically. Inspect/report that conflict first. If a suitable public repository already exists, review its history and integrate normally; these new-empty-repository commands must not overwrite unrelated history.

Finally confirm both visibility and pushed commit:

```sh
gh repo view --json url,isPrivate
git rev-parse HEAD
git ls-remote origin refs/heads/main
git status --short
```

Only report success when `isPrivate` is false and remote main's SHA equals local HEAD. Share that real URL with teammates, who can use the README's Windows instructions and data-download guide.
