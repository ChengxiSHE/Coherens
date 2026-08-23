# Coherens

Coherens keeps one project's engineering knowledge coherent across Windows,
macOS, servers, Docker workspaces, Git versions, Codex, and other coding agents.
Markdown and Git remain the source of truth; VS Code is enough for reading and
editing, and the browser graph is a generated view.

## Repository model

Use two repositories:

1. **Public `Coherens` repository:** plugin, Skills, scripts, schemas, tests, and
   example data. Its canonical source is
   `https://github.com/ChengxiSHE/Knowledge.git`.
2. **Private `Coherens-Vault` repository:** real project knowledge, workspace
   states, version notes, decisions, runbooks, and progress evidence.

Do not separate public and private data with branches. Repository permissions are
the security boundary.

## Agent-first operation

Coherens is packaged as a Codex plugin. Its `project-knowledge` Skill allows
implicit invocation, so users speak in terms of intent rather than commands:

- `配置 Coherens`
- `把当前项目接入 Coherens`
- `把当前项目的进度同步到知识库`
- `读取 Docker 训练任务需要的共享上下文`
- `汇总今天所有已同步项目的进展`
- `生成项目知识图谱`

The Agent inspects the current Git repository, infers safe defaults, invokes the
deterministic tools, validates the result, and reports project ID, workspace ID,
version track, code commit, Vault commit, and push status.

Users do not need to download Coherens first, create a Vault first, choose a
folder, or remember setup steps. Once Coherens is published in a plugin
directory, an arbitrary Codex can discover and install it from the request
`配置 Coherens`. During local development, the Agent can bootstrap it from the
canonical GitHub repository above instead. The dedicated `coherens-setup` Skill
contains this exact URL so Codex never has to guess which repository is official.

## One-time machine setup

On the first request, the Agent checks Git and GitHub authentication, discovers
an existing `Coherens-Vault`, or creates it as a private repository when GitHub
CLI access is available. It asks for a URL or login only when it cannot safely
infer the account. The Agent then runs `setup`, which clones or locates the Vault
and stores only local machine configuration at:

- macOS/Linux: `~/.config/coherens/config.yaml`
- Windows: `%APPDATA%\Coherens\config.yaml`

An empty private Git repository is initialized automatically. Git credentials
and author identity must already be available; Coherens never stores or bypasses
credentials.

After installation, a lightweight session-start hook checks only local setup
markers. It does not read or pull the Vault. When machine configuration or
project registration is missing, it reminds Codex to perform and explain the
next step. Codex hooks require one trust confirmation when first enabled.

## What onboarding creates

In the code repository:

```text
AGENTS.md                  committed progress rule
.kb/project.yaml           committed stable project identity
.kb/workspace.local.yaml   ignored local machine identity
PROGRESS.md                ignored local progress journal
.kb/sync-state.json        ignored incremental upload cursor
```

In the private Vault, Coherens registers the project and workspace, updates
`PROJECT_MAP.md`, and creates the project's common, environment, workspace,
version, runbook, decision, log, and context-pack routes.

## Daily behavior

Ordinary coding reads no cloud knowledge. `AGENTS.md` only requires a compact
local `PROGRESS.md` update for non-trivial work. Cloud access happens when the
user explicitly asks to connect, read shared context, synchronize, summarize,
validate, or visualize.

Publishing is fail-closed: Coherens refuses a dirty or diverged Vault, uses a
fast-forward-only pull, stages only the active project's knowledge paths,
validates Markdown metadata and links, commits, and pushes. It never resolves a
merge conflict by guessing.

## Install from a checkout

Requirements are Python 3.10+, PyYAML 6.x, and Git. Install the dependency and
the bundled Skills:

```text
python -m pip install -r requirements.txt
python tools/install_skills.py
```

Restart Codex if the Skills do not appear immediately. The repository also
contains `.codex-plugin/plugin.json` for plugin distribution.

## Source-of-truth routing

1. `PROJECT_MAP.md` is the human-readable project map.
2. `registry.yaml` stores stable project, workspace, and version identities.
3. `projects/<project-id>/index.md` routes a task to a small context pack.
4. Git commits bind knowledge claims to concrete code revisions.

## Verification

```text
python skills/project-knowledge/scripts/project_knowledge.py validate --knowledge-root .
python skills/knowledge-graph-view/scripts/knowledge_graph.py --knowledge-root .
python -m unittest discover -s tests -v
```

Never commit passwords, tokens, private keys, raw conversation archives, or full
terminal dumps. A daily summary cannot include work that remains unsynchronized
on an offline machine.
