---
name: knowledge-graph-view
description: Generate or refresh a self-contained interactive HTML graph from the Markdown project knowledge repository. Use only when the user explicitly asks to visualize, browse, inspect, or check the knowledge graph; do not use it for selecting authoritative context during ordinary project work.
---

# Knowledge Graph View

Use `scripts/knowledge_graph.py` from this skill directory. Pass the absolute
knowledge repository path with `--knowledge-root`.

The script derives:

- document nodes from YAML frontmatter
- project, version, and workspace nodes from `registry.yaml`
- edges from relative Markdown links and scope metadata
- a self-contained `generated/knowledge-graph.html`

Generate the graph, report node and edge counts, and open it only when the user
asks to view it. The output is derived and may be deleted or regenerated at any
time. Never treat graph layout, node proximity, or timestamps as authority for
context selection; `PROJECT_MAP.md`, `registry.yaml`, project `index.md`, scope
metadata, and Git commits remain authoritative.

When generation exposes missing nodes or edges, run the project knowledge
validator before editing source documents. Fix only relationships supported by
the underlying Markdown and evidence.

