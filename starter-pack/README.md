# Agentic Engineering Starter Pack

A ready-to-use harness for embedding AI agents into your Software Development Lifecycle using Claude Code. Copy these files into your repo and customize them for your project.

## What's Included

```
starter-pack/
├── README.md                          # This file
├── CLAUDE.md.template                 # Project context template — the agent's entry point
├── Design/
│   └── golden-principles.md           # Non-negotiable architectural rules (20 principles)
├── .claude/
│   ├── settings.json.template         # PostToolUse hooks: compile-on-edit, lint-on-edit, PR workflow
│   ├── settings.local.json            # Per-user defaults (MCP server toggles)
│   ├── agents/
│   │   ├── architect.md               # System/detailed design, exec-plan creation
│   │   ├── implementer.md             # Code generation following designs
│   │   ├── reviewer.md                # Code review, convention compliance
│   │   └── tester.md                  # Test-first, coverage validation
│   ├── skills/
│   │   ├── system-design/             # The Method: decomposition, structure, composition (6 files)
│   │   ├── detailed-design/           # Interface quality: signatures, DTOs, errors (6 files)
│   │   ├── detailed-design-v2/        # IDesign contract factoring, BFF, call chains (7 files)
│   │   └── jira-integration/          # Jira REST API: fetch, search, transition, comment (1 file)
│   ├── hooks/
│   │   ├── post-mr-create.sh          # Triggers reviewer after MR/PR creation
│   │   ├── post-push-mr-check.sh      # Checks for unresolved feedback after push
│   │   └── fetch-mr-feedback.sh       # Parses MR comments into severity-classified JSON
│   └── rules/
│       ├── exec-plans.md              # IDesign + tiered architecture enforcement for plans
│       ├── typescript.md.example      # Example coding rules for TypeScript
│       └── python.md.example          # Example coding rules for Python
├── .mcp.json.template                 # Palantir MCP configuration
└── .devcontainer/
    └── setup.sh.template              # ONA environment bootstrap
```

## Quick Start (30 minutes)

### Step 1: Copy files into your repo (5 min)

```bash
# From your repo root
cp -r path/to/starter-pack/.claude .claude
cp path/to/starter-pack/CLAUDE.md.template CLAUDE.md
cp path/to/starter-pack/.mcp.json.template .mcp.json
cp path/to/starter-pack/.devcontainer/setup.sh.template .devcontainer/setup.sh
```

### Step 2: Customize with Claude prompts (15 min)

Open a Claude Code session in your repo and run these prompts:

**1. Generate your CLAUDE.md** — reads your codebase and produces project-specific content:
> "Read the codebase structure, build files, and existing documentation. Generate a CLAUDE.md with: project description, build/test commands, project structure, conventions, quick navigation table. Keep it under 200 lines."

**2. Generate path-scoped rules** — creates coding conventions from your existing code:
> "Analyze the source code. For each language/framework area, create a `.claude/rules/{area}.md` with: stack details, directory structure, import rules, naming conventions, do/don't lists. Base on actual code patterns."

**3. Generate agent definitions** — tailors agents to your project:
> "Create agent definitions in `.claude/agents/` for architect, implementer, reviewer, and tester. Reference our build/test commands and coding standards."

### Step 3: Configure hooks and MCP (10 min)

- Edit `.claude/settings.json.template` — swap the TypeScript compiler/linter commands for your stack
- Edit `.mcp.json.template` — point to your Jira and Foundry instances
- Add tokens as ONA/environment secrets

## What You Get

- **Compile-on-edit** — type errors caught the moment an agent writes code
- **Lint-on-edit** — coding standards enforced mechanically
- **PR-driven review loop** — agents create PRs, review each other's diffs, auto-fix Critical findings, loop until clean
- **Architect with design skills** — structured decomposition using The Method (IDesign)
- **Exec-plan rules** — every implementation plan must demonstrate tiered architecture compliance
- **Jira integration skill** — agents fetch issues, search with JQL, transition status, and add comments via Jira REST API using the `jira-integration` skill
- **Foundry access** — agents explore ontology, datasets, and documentation via MCP

## Customization Guide

| File | What to change |
|------|---------------|
| `CLAUDE.md` | Replace all `[REPLACE]` markers with your project specifics |
| `Design/golden-principles.md` | Fill in `[REPLACE]` sections with domain invariants, entity statuses, frontend/cross-language rules |
| `.claude/rules/*.example` | Rename to `.md`, replace with your conventions (or auto-generate with Prompt 2) |
| `.claude/rules/exec-plans.md` | Adjust layer names and responsibilities for your architecture |
| `.claude/agents/*.md` | Update build/test commands and coding standards references |
| `.claude/settings.json.template` | Swap compiler/linter commands; rename to `settings.json` |
| `.mcp.json.template` | Update Foundry/Jira URLs; rename to `.mcp.json` |
| `.devcontainer/setup.sh.template` | Add/remove tools for your stack; rename to `setup.sh` |

## What Ships As-Is (no customization needed)

- **Golden principles** — 20 architectural rules covering layers, engine purity, TDD, documentation, with `[REPLACE]` markers for domain-specific invariants.
- **Design skills** (`system-design`, `detailed-design`, `detailed-design-v2`) — encode The Method (Juval Lowy's IDesign). Project-agnostic methodology.
- **Jira integration skill** (`jira-integration`) — curl-based Jira REST API patterns for on-prem instances. Bearer PAT auth, get/search/transition/comment operations. Triggers automatically on Jira issue keys.
- **PR workflow hooks** — support both GitHub (`gh`) and GitLab (`glab`). Auto-detect VCS type.
- **Statusline** — shows user, branch, model, and context usage percentage.

## VCS CLI Setup (GitHub / GitLab)

The PR workflow hooks require an authenticated `gh` (GitHub) or `glab` (GitLab) CLI. Without it, the Ralph Wiggum Loop cannot create PRs, post review comments, or approve merges.

### Installation

`.devcontainer/setup.sh.template` includes both CLIs. By default `gh` is enabled and `glab` is commented out. Uncomment the CLI for your platform and remove the other.

For GitLab, also set your host:
```bash
glab config set host YOUR_GITLAB_HOST
```

### Token Setup

Create a Personal Access Token and add it as an ONA secret (type: **Environment Variable**):

| Platform | Token source | Required scope | ONA secret name |
|----------|-------------|---------------|-----------------|
| **GitHub** | Settings > Developer settings > Personal access tokens (classic) | `repo` | `GITHUB_TOKEN` |
| **GitLab** | User Settings > Access Tokens | `api` | `GITLAB_TOKEN` |

Restart your FlexDev environment after adding the secret.

### Authentication

- **GitHub:** `gh` picks up `GITHUB_TOKEN` automatically — no login command needed.
- **GitLab:** Run `glab auth login --hostname YOUR_GITLAB_HOST --token "$GITLAB_TOKEN"` after environment start. Add this to your `setup.sh` to persist across rebuilds.

### Verify

```bash
# GitHub
gh auth status && gh pr list

# GitLab
glab auth status && glab mr list
```

If the CLI is not authenticated, the hooks will silently skip and the PR workflow will not function.

## Architecture: The Ralph Wiggum Loop

The PR-driven review workflow automates the review-fix-re-review cycle:

1. Implementer works in isolated worktree, self-reviews, opens MR/PR
2. `post-mr-create.sh` hook fires → instructs orchestrator to invoke reviewer
3. Reviewer posts severity-tagged findings as MR comments (prefixed `[Agent Review]`)
4. Critical findings → implementer auto-fixes → pushes → `post-push-mr-check.sh` fires
5. Hook re-invokes reviewer → loop until zero Critical findings
6. Warning findings presented to user for decision
7. Human comments have final authority
8. Zero Critical → reviewer approves → human final approval

## MCP Integrations

| Server | Access | Tools |
|--------|--------|-------|
| **Palantir MCP** | Full read-write | 44 read + 25 write tools (ontology, datasets, builds, PRs) |

Palantir MCP consumes ~50k tokens when active. Keep disabled by default (configured in `settings.local.json`), enable per-session when needed.

Jira integration uses the `jira-integration` skill (curl-based REST API with Bearer PAT auth) instead of an MCP server. See the main README for [setup instructions](../README.md#setting-up-jira-integration).

## Support

- **Agentic Engineering Office Hours** — bring questions, share patterns
- **Knowledge Base** — `agentic-engineering-kb.md` for best practices
- **Feedback** — open a merge request with improvements to this starter pack
