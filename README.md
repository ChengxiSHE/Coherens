<div align="center">
  <h1>Coherens | Project Intelligence Across Every Endpoint</h1>
  <p>Codex-native coordination and knowledge accumulation for multi-endpoint, multi-project engineering.</p>
  <p><a href="README.zh-CN.md">Chinese README</a></p>
  <p>
    <a href="#skill-packages">Skill packages</a> &middot;
    <a href="#installation">Installation</a> &middot;
    <a href="#quick-start">Quick start</a> &middot;
    <a href="#supported-collaboration-scope">Collaboration scope</a> &middot;
    <a href="#architecture">Architecture</a> &middot;
    <a href="#validation">Validation</a> &middot;
    <a href="#security-and-scope">Security</a>
  </p>
  <p>
    <img alt="version 0.3.0" src="https://img.shields.io/badge/version-0.3.0-blue">
    <img alt="skills 3" src="https://img.shields.io/badge/skills-3-2ea44f">
    <img alt="knowledge layers 8" src="https://img.shields.io/badge/knowledge_layers-8-0f766e">
    <img alt="workflow tests 12" src="https://img.shields.io/badge/workflow_tests-12-ca8a04">
    <a href="LICENSE"><img alt="license MIT" src="https://img.shields.io/badge/license-MIT-brightgreen"></a>
  </p>
  <p>If Coherens helps your work, please consider giving the repository a Star <a href="https://github.com/ChengxiSHE/Coherens"><img alt="Star Coherens on GitHub" src="https://img.shields.io/badge/GitHub-Star-181717?logo=github"></a></p>
</div>

## What This Repository Is

Coherens is a Codex-native project intelligence framework for engineering work
distributed across multiple projects, computers, servers, containers, versions,
and agent sessions.

A user states an engineering goal in the current workspace. Coherens identifies
the project, endpoint, version track, and Git state; retrieves the smallest
relevant context; records verified progress; and synchronizes durable knowledge
to a private Git-backed Vault. The next endpoint or agent can continue from an
authoritative project state instead of reconstructing the repository and its
history from scratch.

Code repositories preserve what changed. Coherens preserves why it changed,
where the knowledge applies, which commit verified it, what failed before, and
what the next agent needs to know.

### Highlights

- **Multi-endpoint continuity:** continue one project across Windows, macOS,
  Linux, GPU servers, and Docker workspaces without rebuilding context.
- **Multi-project coordination:** maintain stable, independent project identities
  while accumulating knowledge across an engineering portfolio.
- **Version-grounded knowledge:** bind every workspace state and reusable
  conclusion to repositories, branches, version tracks, and Git commits.
- **Agent-first operation:** let Codex install, configure, register, diagnose,
  synchronize, validate, summarize, and report from a single user intent.
- **Precision context routing:** read a task-specific context pack instead of
  scanning an entire codebase or knowledge Vault for every session.
- **README-quality first sync:** analyze an existing project once and preserve
  its purpose, architecture, modules, scripts, execution flow, commands,
  dependencies, and constraints in an evidence-bound Project Profile.
- **Governed accumulation:** separate local progress, endpoint state,
  environment differences, version knowledge, runbooks, decisions, and common
  conclusions by ownership and durability.
- **Git-native auditability:** keep knowledge human-readable in Markdown and use
  Git for provenance, review, rollback, and collaboration.

## Skill Packages

| Package | Use it for | Start here |
| --- | --- | --- |
| [`coherens-setup`](skills/coherens-setup) | Discover, install, configure, diagnose, or repair Coherens and its private Vault on a computer or server. | [`SKILL`](skills/coherens-setup/SKILL.md) |
| [`project-knowledge`](skills/project-knowledge) | Register projects and endpoints, route shared context, synchronize progress, build summaries, and validate the Vault. | [`SKILL`](skills/project-knowledge/SKILL.md) |
| [`knowledge-graph-view`](skills/knowledge-graph-view) | Generate a self-contained interactive view of projects, versions, workspaces, and knowledge relationships. | [`SKILL`](skills/knowledge-graph-view/SKILL.md) |

The setup Skill owns installation and machine readiness. The project-knowledge
Skill owns identity, routing, synchronization, and knowledge lifecycle. The graph
Skill owns derived visualization. Deterministic local tools perform registry
updates, incremental sync, validation, summaries, and graph generation.

## Installation

> [!TIP]
> Give Codex one setup request. Codex performs the discoverable steps. When no
> Vault exists, it asks you to create one empty Private Git repository and send
> back its clone URL; Coherens never creates the repository on your behalf.

Use this prompt in any Codex environment with Git and network access:

```text
Configure Coherens from https://github.com/ChengxiSHE/Coherens.git.
If I have not connected a Vault, tell me to create an empty Private
Coherens-Vault and wait for its clone URL. Verify the supplied repository is
Private, connect it, register this environment, run doctor, and report machine,
Vault, project, and sync readiness separately.
```

The `coherens-setup` Skill pins the canonical repository URL, validates the
plugin identity, checks Git, Python, Codex plugin support, network access, and
Git authentication, then verifies and connects the user-provided private Vault
and registers a stable machine or container identity.

A lightweight `SessionStart` hook checks local readiness markers after
installation. It does not read or pull the Vault. New or changed lifecycle hooks
require a one-time Codex trust review before they run.

<details>
<summary><strong>Local development installation</strong></summary>

Requirements are Python 3.10+, PyYAML 6.x, and Git.

```bash
git clone https://github.com/ChengxiSHE/Coherens.git
cd Coherens
python -m pip install -r requirements.txt
python tools/install_plugin.py
```

The installer validates the plugin identity, installs the complete package into
the personal Codex marketplace, and enables it. Restart Codex if the new Skills
or SessionStart hook do not appear immediately. `tools/install_skills.py`
remains available for Skill-only development or non-plugin agent integration.

</details>

## Quick Start

> [!NOTE]
> Start with the engineering outcome. Coherens checks machine and project state,
> performs missing onboarding when relevant, and loads shared context only when
> the task requires it.

```text
Continue this project on the GPU server.
```

Other natural-language examples:

```text
Prepare the open-source release from the current private version.
Synchronize today's progress for every active project.
Load the context needed to reproduce the last successful Docker training run.
Generate the project knowledge graph.
```

Explicit Skill invocation remains available, but it is not required for normal
use.

For a project's first synchronization, Coherens performs one repository-wide
onboarding analysis and completes `PROJECT_PROFILE.md`. The profile explains the
project like a durable technical README and is bound to the current clean Git
commit. Later synchronizations upload only new progress and state changes unless
the architecture has materially changed.

Projects connected before 0.3 are treated as legacy until their stable origin,
tracked code, Project Profile, and older synchronized records pass the new
readiness and privacy checks.

## Supported Collaboration Scope

### Endpoints

| Endpoint | Tracked role |
| --- | --- |
| Windows workstation | Development, testing, packaging, or project operations. |
| macOS workstation | Development, integration, release, or project operations. |
| Linux workstation or server | Development, automation, deployment, or remote execution. |
| Docker workspace | Isolated build, training, inference, testing, or deployment state. |
| GPU server | Version-bound training and inference execution with environment-specific runbooks. |

Each physical or logical endpoint receives a stable `workspace_id`. Containers
that must survive recreation need a persistent Coherens configuration location.

### Identity model

| Identity | Purpose |
| --- | --- |
| `project_id` | Stable identity shared by every checkout and endpoint of one project. |
| `workspace_id` | Stable identity for one physical or logical execution endpoint. |
| `version_track` | Branch, release, experiment, private, production, or open-source knowledge boundary. |
| `environment` | Operating-system, hardware, container, runtime, and dependency scope. |
| Git commit | Concrete code state that supports a synchronized claim. |

Coherens requires a stable project origin before onboarding and never decides
that one endpoint is authoritative from timestamps alone. It resolves project,
workspace, version track, branch, and commit together. Dirty or untracked code
may be recorded as `unanchored`, but it is never labeled as verified.

### Knowledge model

| Layer | Purpose |
| --- | --- |
| `PROGRESS.md` | Lightweight, local, append-only work evidence. |
| `workspaces/` | Current state of each registered machine, server, or container. |
| `environments/` | Operating-system, hardware, container, and runtime differences. |
| `versions/` | Branch, release, experiment, private, production, and open-source knowledge. |
| `runbooks/` | Repeatable procedures with prerequisites and verification. |
| `decisions/` | Durable choices, rationale, alternatives, and effective commits. |
| `common/` | Conclusions verified across the endpoints and versions where they apply. |
| `context-packs/` | Small task-specific routes to the exact knowledge an agent needs. |

Each project also has a mandatory `PROJECT_PROFILE.md`. Before the first sync,
the agent documents the existing project's purpose, architecture, module and
script responsibilities, interfaces, execution flow, commands, dependencies,
constraints, and reviewed evidence.

`PROJECT_MAP.md` is the human-readable multi-project entry point.
`registry.yaml` is the machine registry. Each
`projects/<project-id>/index.md` routes tasks to bounded context. Git commits
anchor knowledge to concrete code states.

## Architecture

The Coherens workflow combines three layers:

- **Agent interface:** three Codex Skills and a lightweight session hook turn
  natural-language intent into setup, routing, synchronization, validation, and
  visualization workflows.
- **Deterministic control plane:** local Python tools manage identities, sync
  cursors, project scaffolding, workspace state, daily summaries, validation,
  Git publication, and graph generation.
- **Git-backed intelligence model:** a private Vault stores project maps,
  registry data, endpoint state, version knowledge, evidence, runbooks,
  decisions, and context packs as reviewable Markdown and YAML.

Ordinary coding updates only local `PROGRESS.md`. Shared knowledge is read or
published when the user requests cross-endpoint work, shared context,
synchronization, summarization, validation, or visualization.

## Repository Layout

```text
Coherens/
|-- .codex-plugin/        # Plugin identity and distribution metadata
|-- skills/               # Setup, project knowledge, and graph Skills
|-- hooks/                # Lightweight Codex lifecycle readiness check
|-- tools/                # Local installation utility
|-- templates/            # Files installed into connected code projects
|-- schema/               # Knowledge document metadata contract
|-- projects/             # Example Vault project and knowledge layers
|-- tests/                # End-to-end workflow and packaging tests
|-- PROJECT_MAP.md        # Human-readable multi-project map
|-- registry.yaml         # Stable machine-readable identity registry
`-- README.zh-CN.md       # Chinese documentation
```

The public repository contains product code, templates, tests, and
redistributable examples. Real project knowledge belongs in a separate private
`Coherens-Vault` repository and must not be committed here.

## Validation

Run the deterministic validation suite with:

```bash
python -m unittest discover -s tests -v
python skills/project-knowledge/scripts/project_knowledge.py validate --knowledge-root .
python skills/knowledge-graph-view/scripts/knowledge_graph.py --knowledge-root .
```

The 12-test workflow suite covers complete plugin installation, user-confirmed
Private Vault setup, readiness separation, canonical repository pinning,
implicit session routing, stable project identity, mandatory first-sync
profiles, incremental synchronization, unanchored code handling, repeat
publication, daily summaries, Markdown validation, bilingual README integrity,
and graph generation.
Validation also rejects synchronized Markdown that contains a local user home
path or claims a verified commit while marked `unanchored`.

Validation proves the included deterministic workflows and fixtures. It does not
claim that every agent-authored knowledge conclusion is correct. Durable
conclusions still require evidence, explicit scope, and review appropriate to
the project.

## Security and Scope

- **Repository boundary:** the public product repository and private knowledge
  Vault are separate Git repositories. Branches are never a privacy boundary.
- **Credential boundary:** passwords, tokens, private keys, `.env` files, raw
  chat archives, and full terminal dumps must not enter the Vault.
- **Read boundary:** ordinary coding does not automatically read or pull shared
  knowledge. Context retrieval is task-driven and bounded.
- **Write boundary:** local progress is synchronized explicitly and promoted to
  durable knowledge only after review.
- **Path boundary:** absolute local project paths remain local and are not added
  to synchronized progress records.
- **Git safety:** synchronization stops on dirty or diverged Vault state, uses
  fast-forward-only pulls, stages scoped paths, validates before commit, and
  never guesses through conflicts or protected branches.
- **Agent scope:** Coherens is currently packaged for Codex. Its Markdown, YAML,
  and deterministic tools are portable, but other coding agents require their
  own integration layer for equivalent lifecycle behavior.

Coherens is released under the [MIT License](LICENSE).
