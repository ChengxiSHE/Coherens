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

Use ordinary relative Markdown links for relationships. The graph generator
derives edges from those links; the link text becomes the relationship label.

