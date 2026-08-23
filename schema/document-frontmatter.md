---
type: schema
id: document-frontmatter
title: Knowledge document metadata
status: active
---

# Knowledge document metadata

Documents that participate in routing or graph generation should use this
frontmatter:

```yaml
---
type: runbook
id: docker-gpu-training
title: Docker GPU training
project: project-a
workspace_scope: [docker-gpu-01]
version_scope: [experiment-v2]
verified_commit: 8f4c21a
status: active
updated_at: 2026-08-23T21:30:00+08:00
---
```

Required fields are `type`, `id`, `title`, and `status`. Project documents also
require `project`. Valid status values are `draft`, `active`, `superseded`, and
`archived`.

`project-profile` is the mandatory README-quality description produced before a
project's first synchronization. It must be `active` and its `verified_commit`
must match the current clean project commit.

Use `verified_commit` only when the relevant code is tracked and the working
tree is clean. Workspace and progress records from a dirty or untracked state
must use `code_state: unanchored` and may record `base_commit`; they must not
claim a verified commit.

Use ordinary relative Markdown links for relationships. The graph generator
derives edges from those links; the link text becomes the relationship label.
