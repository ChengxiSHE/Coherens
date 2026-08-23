#!/usr/bin/env python3
"""Generate a self-contained interactive HTML graph from the knowledge repository."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import webbrowser
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install it with: python -m pip install PyYAML") from exc


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
EXCLUDED_PARTS = {".git", "generated", "skills", "templates", "tests", "tools", "__pycache__"}


def parse_markdown(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    return (meta if isinstance(meta, dict) else {}), text[match.end() :]


def load_registry(root: Path) -> dict[str, Any]:
    path = root / "registry.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def local_link(raw: str) -> str | None:
    target = raw.strip().split(maxsplit=1)[0].strip("<>").split("#", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:", "obsidian:")):
        return None
    return target


def build_graph(root: Path) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    path_to_id: dict[Path, str] = {}
    links: list[dict[str, str]] = []
    seen_links: set[tuple[str, str, str]] = set()

    markdown_paths = [
        path
        for path in root.rglob("*.md")
        if not EXCLUDED_PARTS.intersection(path.relative_to(root).parts)
    ]
    for path in sorted(markdown_paths):
        meta, body = parse_markdown(path)
        if not meta.get("id"):
            continue
        node_id = str(meta["id"])
        relative = path.relative_to(root)
        nodes[node_id] = {
            "id": node_id,
            "title": str(meta.get("title") or path.stem),
            "type": str(meta.get("type") or "document"),
            "status": str(meta.get("status") or "unknown"),
            "project": str(meta.get("project") or ""),
            "path": relative.as_posix(),
            "body": body.strip(),
            "meta": meta,
            "virtual": False,
        }
        path_to_id[path.resolve()] = node_id

    registry = load_registry(root)
    for project_id, project in (registry.get("projects") or {}).items():
        project_id = str(project_id)
        if project_id not in nodes:
            nodes[project_id] = {
                "id": project_id,
                "title": str(project.get("title") or project_id),
                "type": "project",
                "status": "active",
                "project": project_id,
                "path": str(project.get("knowledge_entry") or ""),
                "body": "Registered project",
                "meta": project,
                "virtual": True,
            }
        for track in project.get("version_tracks") or []:
            version_id = f"{project_id}-{track}"
            if version_id not in nodes:
                nodes[version_id] = {
                    "id": version_id,
                    "title": f"{project_id} / {track}",
                    "type": "version",
                    "status": "registered",
                    "project": project_id,
                    "path": "registry.yaml",
                    "body": "Registered version track",
                    "meta": {"version_track": track},
                    "virtual": True,
                }
            add_link(links, seen_links, project_id, version_id, "has version")
        for workspace_id, workspace in (project.get("workspaces") or {}).items():
            workspace_node_id = f"{project_id}-{workspace_id}"
            if workspace_node_id not in nodes:
                nodes[workspace_node_id] = {
                    "id": workspace_node_id,
                    "title": str(workspace_id),
                    "type": "workspace",
                    "status": str(workspace.get("status") or "registered"),
                    "project": project_id,
                    "path": "registry.yaml",
                    "body": f"Environment: {workspace.get('environment', 'unknown')}\n\nRole: {workspace.get('role', 'unknown')}",
                    "meta": workspace,
                    "virtual": True,
                }
            add_link(links, seen_links, project_id, workspace_node_id, "has workspace")

    for path in sorted(markdown_paths):
        source = path_to_id.get(path.resolve())
        if not source:
            continue
        meta, body = parse_markdown(path)
        for label, raw in LINK_RE.findall(body):
            target = local_link(raw)
            if target is None:
                continue
            resolved = (path.parent / target).resolve()
            if resolved.suffix == "" and resolved.with_suffix(".md").exists():
                resolved = resolved.with_suffix(".md")
            target_id = path_to_id.get(resolved)
            if target_id:
                add_link(links, seen_links, source, target_id, label.strip() or "links to")
        project_id = str(meta.get("project") or "")
        if project_id and project_id in nodes and source != project_id:
            add_link(links, seen_links, project_id, source, "contains")
        for workspace_id in meta.get("workspace_scope") or []:
            target_id = f"{project_id}-{workspace_id}"
            if target_id in nodes and target_id != source:
                add_link(links, seen_links, source, target_id, "applies to")
        for track in meta.get("version_scope") or []:
            target_id = f"{project_id}-{track}"
            if target_id in nodes and target_id != source:
                add_link(links, seen_links, source, target_id, "valid for")

    return {"nodes": list(nodes.values()), "links": links}


def add_link(
    links: list[dict[str, str]],
    seen: set[tuple[str, str, str]],
    source: str,
    target: str,
    label: str,
) -> None:
    key = (source, target, label)
    if source == target or key in seen:
        return
    seen.add(key)
    links.append({"source": source, "target": target, "label": label})


def safe_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")


def render_html(graph: dict[str, Any], title: str) -> str:
    graph_json = safe_json(graph)
    escaped_title = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escaped_title}</title>
<style>
:root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: 100%; height: 100%; overflow: hidden; background: #f5f7f9; color: #17202a; }}
#app {{ display: grid; grid-template-rows: 52px 1fr; height: 100%; }}
header {{ display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: #fff; border-bottom: 1px solid #d9e0e6; z-index: 3; }}
h1 {{ font-size: 15px; margin: 0 12px 0 0; white-space: nowrap; }}
input, select, button {{ height: 34px; border: 1px solid #bdc8d1; border-radius: 6px; background: #fff; color: #17202a; padding: 0 10px; font: inherit; }}
input {{ width: min(320px, 35vw); }}
button {{ cursor: pointer; }}
button:hover {{ background: #edf2f5; }}
#count {{ margin-left: auto; color: #65727d; font-size: 13px; white-space: nowrap; }}
main {{ position: relative; min-height: 0; }}
canvas {{ width: 100%; height: 100%; display: block; cursor: grab; }}
canvas.dragging {{ cursor: grabbing; }}
#detail {{ position: absolute; right: 12px; top: 12px; bottom: 12px; width: min(390px, calc(100% - 24px)); overflow: auto; background: #fff; border: 1px solid #d9e0e6; border-radius: 8px; box-shadow: 0 12px 32px rgba(23,32,42,.16); padding: 18px; display: none; }}
#detail.open {{ display: block; }}
#detail h2 {{ font-size: 19px; margin: 0 32px 6px 0; }}
#detail h3 {{ font-size: 14px; margin-top: 20px; }}
#detail p, #detail li {{ font-size: 14px; line-height: 1.55; }}
#detail code {{ background: #edf2f5; padding: 2px 4px; border-radius: 3px; }}
#detail .meta {{ color: #65727d; font-size: 12px; line-height: 1.6; overflow-wrap: anywhere; }}
#close {{ position: absolute; top: 10px; right: 10px; width: 30px; padding: 0; font-size: 18px; }}
.legend {{ position: absolute; left: 12px; bottom: 12px; display: flex; flex-wrap: wrap; max-width: min(700px, calc(100% - 24px)); gap: 6px 12px; background: rgba(255,255,255,.9); border: 1px solid #d9e0e6; border-radius: 6px; padding: 8px 10px; font-size: 12px; pointer-events: none; }}
.legend span::before {{ content: ''; display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 5px; background: var(--c); }}
@media (max-width: 680px) {{ header {{ flex-wrap: wrap; height: auto; }} #app {{ grid-template-rows: auto 1fr; }} h1 {{ width: 100%; }} input {{ flex: 1; width: auto; }} #count {{ display: none; }} }}
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>{escaped_title}</h1>
    <input id="search" type="search" placeholder="Search title, ID, project, path">
    <select id="type"><option value="">All types</option></select>
    <button id="fit" type="button">Fit</button>
    <span id="count"></span>
  </header>
  <main>
    <canvas id="graph"></canvas>
    <div class="legend" id="legend"></div>
    <aside id="detail"><button id="close" type="button" aria-label="Close">×</button><div id="detailBody"></div></aside>
  </main>
</div>
<script>
const data = {graph_json};
const colors = {{project:'#1976d2',workspace:'#2e7d32',version:'#7b1fa2',runbook:'#d35400',environment:'#00838f',decision:'#c62828','context-pack':'#455a64',collection:'#6d7a86','progress-log':'#8d6e63','daily-summary':'#ad1457',map:'#37474f',schema:'#546e7a',document:'#607d8b'}};
const canvas = document.getElementById('graph');
const ctx = canvas.getContext('2d');
const search = document.getElementById('search');
const typeSelect = document.getElementById('type');
const detail = document.getElementById('detail');
const detailBody = document.getElementById('detailBody');
const count = document.getElementById('count');
const DPR = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
let width = 0, height = 0, scale = 1, panX = 0, panY = 0, selected = null, hovered = null;
let dragNode = null, panning = false, lastX = 0, lastY = 0;
const nodes = data.nodes.map((n,i) => ({{...n, x: Math.cos(i*2.399)*180, y: Math.sin(i*2.399)*180, vx:0, vy:0, visible:true}}));
const byId = new Map(nodes.map(n => [n.id,n]));
const links = data.links.map(l => ({{...l, source:byId.get(l.source), target:byId.get(l.target)}})).filter(l => l.source && l.target);

function resize() {{ const r=canvas.getBoundingClientRect(); width=r.width; height=r.height; canvas.width=Math.round(width*DPR); canvas.height=Math.round(height*DPR); ctx.setTransform(DPR,0,0,DPR,0,0); draw(); }}
function graphToScreen(n) {{ return {{x:width/2+panX+n.x*scale,y:height/2+panY+n.y*scale}}; }}
function screenToGraph(x,y) {{ return {{x:(x-width/2-panX)/scale,y:(y-height/2-panY)/scale}}; }}
function radius(n) {{ return n.type==='project'?9:(n.type==='workspace'||n.type==='version'?7:5); }}
function applyFilter() {{
  const q=search.value.trim().toLowerCase(), t=typeSelect.value;
  nodes.forEach(n => {{ const hay=`${{n.title}} ${{n.id}} ${{n.project}} ${{n.path}}`.toLowerCase(); n.visible=(!q||hay.includes(q))&&(!t||n.type===t); }});
  const visible=nodes.filter(n=>n.visible).length; count.textContent=`${{visible}} / ${{nodes.length}} nodes · ${{links.length}} edges`; draw();
}}
function simulate() {{
  const visible=nodes.filter(n=>n.visible);
  for (let i=0;i<visible.length;i++) for (let j=i+1;j<visible.length;j++) {{ const a=visible[i],b=visible[j]; let dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy+80; const f=28/d2; a.vx+=dx*f; a.vy+=dy*f; b.vx-=dx*f; b.vy-=dy*f; }}
  links.forEach(l => {{ if(!l.source.visible||!l.target.visible)return; const dx=l.target.x-l.source.x,dy=l.target.y-l.source.y,d=Math.sqrt(dx*dx+dy*dy)||1,f=(d-90)*.0025; l.source.vx+=dx*f; l.source.vy+=dy*f; l.target.vx-=dx*f; l.target.vy-=dy*f; }});
  visible.forEach(n => {{ if(n!==dragNode){{ n.vx+=-n.x*.0015; n.vy+=-n.y*.0015; n.vx=Math.max(-3,Math.min(3,n.vx*.82)); n.vy=Math.max(-3,Math.min(3,n.vy*.82)); n.x=Math.max(-440,Math.min(440,n.x+n.vx)); n.y=Math.max(-260,Math.min(260,n.y+n.vy)); }} }});
}}
function draw() {{
  ctx.clearRect(0,0,width,height); ctx.lineWidth=1;
  links.forEach(l => {{ if(!l.source.visible||!l.target.visible)return; const a=graphToScreen(l.source),b=graphToScreen(l.target); ctx.strokeStyle='rgba(95,110,120,.25)'; ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke(); }});
  nodes.forEach(n => {{ if(!n.visible)return; const p=graphToScreen(n),r=radius(n); ctx.fillStyle=colors[n.type]||colors.document; ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill(); if(selected===n){{ctx.strokeStyle='#111';ctx.lineWidth=2;ctx.stroke();ctx.lineWidth=1;}} if(n===selected||n===hovered||n.type==='project'||search.value.trim()){{ctx.fillStyle='#25313b';ctx.font=`${{n.type==='project'?'600 ':''}}12px system-ui`;ctx.fillText(n.title,p.x+r+4,p.y+4);}} }});
}}
function loop() {{ simulate(); draw(); requestAnimationFrame(loop); }}
function hit(x,y) {{ let best=null,bestD=Infinity; nodes.forEach(n=>{{if(!n.visible)return;const p=graphToScreen(n),d=Math.hypot(x-p.x,y-p.y);if(d<radius(n)+7&&d<bestD){{best=n;bestD=d;}}}});return best; }}
function escapeHtml(s) {{ return String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[c])); }}
function renderMarkdown(s) {{ let out=escapeHtml(s); out=out.replace(/^### (.*)$/gm,'<h3>$1</h3>').replace(/^## (.*)$/gm,'<h3>$1</h3>').replace(/^# (.*)$/gm,'<h3>$1</h3>').replace(/`([^`]+)`/g,'<code>$1</code>').replace(/^[-*] (.*)$/gm,'<li>$1</li>').replace(/\\n{{2,}}/g,'</p><p>').replace(/\\n/g,'<br>'); return `<p>${{out}}</p>`; }}
function showNode(n) {{
  selected=n; const outgoing=links.filter(l=>l.source===n).map(l=>`${{escapeHtml(l.label)}} → ${{escapeHtml(l.target.title)}}`); const incoming=links.filter(l=>l.target===n).map(l=>`${{escapeHtml(l.source.title)}} → ${{escapeHtml(l.label)}}`);
  detailBody.innerHTML=`<h2>${{escapeHtml(n.title)}}</h2><div class="meta">${{escapeHtml(n.type)}} · ${{escapeHtml(n.status)}}<br>${{escapeHtml(n.path)}}<br>ID: ${{escapeHtml(n.id)}}</div>${{renderMarkdown(n.body)}}<h3>Links to</h3>${{outgoing.length?'<ul><li>'+outgoing.join('</li><li>')+'</li></ul>':'<p>None</p>'}}<h3>Cited by</h3>${{incoming.length?'<ul><li>'+incoming.join('</li><li>')+'</li></ul>':'<p>None</p>'}}`;
  detail.classList.add('open'); draw();
}}
canvas.addEventListener('pointerdown',e=>{{const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;lastX=x;lastY=y;dragNode=hit(x,y);panning=!dragNode;canvas.setPointerCapture(e.pointerId);canvas.classList.add('dragging');}});
canvas.addEventListener('pointermove',e=>{{const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;if(!canvas.hasPointerCapture(e.pointerId)){{hovered=hit(x,y);return;}}if(dragNode){{const p=screenToGraph(x,y);dragNode.x=p.x;dragNode.y=p.y;dragNode.vx=dragNode.vy=0;}}else if(panning){{panX+=x-lastX;panY+=y-lastY;}}lastX=x;lastY=y;}});
canvas.addEventListener('pointerleave',()=>{{hovered=null;}});
canvas.addEventListener('pointerup',e=>{{const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top,node=hit(x,y);if(dragNode&&node===dragNode&&Math.hypot(x-lastX,y-lastY)<5)showNode(node);dragNode=null;panning=false;canvas.classList.remove('dragging');}});
canvas.addEventListener('dblclick',e=>{{const r=canvas.getBoundingClientRect(),n=hit(e.clientX-r.left,e.clientY-r.top);if(n)showNode(n);}});
canvas.addEventListener('wheel',e=>{{e.preventDefault();const factor=e.deltaY<0?1.1:.9;scale=Math.max(.25,Math.min(3,scale*factor));}},{{passive:false}});
document.getElementById('close').onclick=()=>{{detail.classList.remove('open');selected=null;}};
document.getElementById('fit').onclick=()=>{{scale=1;panX=panY=0;}};
search.addEventListener('input',applyFilter); typeSelect.addEventListener('change',applyFilter);
const types=[...new Set(nodes.map(n=>n.type))].sort(); types.forEach(t=>{{const o=document.createElement('option');o.value=t;o.textContent=t;typeSelect.appendChild(o);}});
document.getElementById('legend').innerHTML=types.map(t=>`<span style="--c:${{colors[t]||colors.document}}">${{escapeHtml(t)}}</span>`).join('');
window.addEventListener('resize',resize); resize(); applyFilter(); loop();
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--knowledge-root", required=True)
    parser.add_argument("--output")
    parser.add_argument("--title", default="Project Knowledge Graph")
    parser.add_argument("--open", action="store_true", dest="open_browser")
    args = parser.parse_args()
    root = Path(args.knowledge_root).expanduser().resolve()
    if not (root / "registry.yaml").exists():
        print(f"ERROR: registry.yaml not found under {root}", file=sys.stderr)
        return 2
    output = Path(args.output).expanduser().resolve() if args.output else root / "generated" / "knowledge-graph.html"
    graph = build_graph(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(graph, args.title), encoding="utf-8")
    print(f"Generated {output} with {len(graph['nodes'])} nodes and {len(graph['links'])} edges")
    if args.open_browser:
        webbrowser.open(output.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
