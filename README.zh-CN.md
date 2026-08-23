# Coherens

[English README](README.md)

Coherens 用于让同一个项目的工程知识在 Windows、macOS、服务器、Docker
工作区、Git 版本、Codex 和其他编程 Agent 之间保持连贯。Markdown 和 Git
是事实来源；使用 VS Code 即可阅读和编辑，浏览器知识图谱只是生成视图。

## 仓库模型

使用两个仓库：

1. **公开的 `Coherens` 仓库：** 保存插件、Skills、脚本、数据结构、测试和
   示例数据。唯一官方来源是
   `https://github.com/ChengxiSHE/Coherens.git`。
2. **私有的 `Coherens-Vault` 仓库：** 保存真实项目知识、工作区状态、版本
   说明、决策、操作手册和进度证据。

不要使用不同分支区分公开与私有内容。仓库权限才是安全边界。

## Agent-first 操作方式

Coherens 被封装为 Codex 插件。`project-knowledge` Skill 支持隐式调用，因此
用户只需要描述目标，不需要记忆命令：

- `配置 Coherens。`
- `把当前项目接入 Coherens。`
- `把当前项目的进度同步到知识库。`
- `读取 Docker 训练任务需要的共享上下文。`
- `汇总今天所有已同步项目的进展。`
- `生成项目知识图谱。`

Agent 会检查当前 Git 仓库、推断安全的默认值、调用确定性工具、校验结果，
并报告项目 ID、工作区 ID、版本轨道、代码提交、Vault 提交和推送状态。

用户不需要提前下载 Coherens、创建 Vault、选择目录或记忆安装步骤。Coherens
发布到插件目录后，任意 Codex 都可以根据 `配置 Coherens` 发现并安装它。
在本地开发阶段，Agent 也可以从上面的官方 GitHub 仓库完成引导。
专用的 `coherens-setup` Skill 固定保存该地址，因此 Codex 不需要猜测哪个
仓库才是官方来源。

## 一次性设备配置

收到第一次配置请求后，Agent 会检查 Git 和 GitHub 登录状态，查找现有的
`Coherens-Vault`；如果 GitHub CLI 可用但 Vault 不存在，则自动创建私有
仓库。只有账号无法安全推断或尚未登录时，才会请求用户确认。

随后 Agent 会运行 `setup`，克隆或定位 Vault，并将纯本地设备配置保存在：

- macOS/Linux：`~/.config/coherens/config.yaml`
- Windows：`%APPDATA%\Coherens\config.yaml`

空的私有 Git 仓库会被自动初始化。Git 凭据和提交者身份需要能够正常使用；
Coherens 不会存储或绕过凭据。

安装后，轻量级会话启动 Hook 只检查本地配置标记，不读取或拉取 Vault。
如果缺少设备配置或项目注册，它会提醒 Codex 自动完成并解释下一步。
Codex Hook 首次启用时需要进行一次信任确认。

## 项目接入后生成的文件

代码仓库中：

```text
AGENTS.md                  需要提交的进度记录规则
.kb/project.yaml           需要提交的稳定项目身份
.kb/workspace.local.yaml   忽略的本地设备身份
PROGRESS.md                忽略的本地进度日志
.kb/sync-state.json        忽略的增量同步游标
```

私有 Vault 中，Coherens 会注册项目和工作区、更新 `PROJECT_MAP.md`，并创建
项目的公共知识、环境、工作区、版本、操作手册、决策、日志和上下文包目录。

## 日常行为

普通编码不会读取云端知识。`AGENTS.md` 只要求 Codex 在完成非简单任务后更新
精简的本地 `PROGRESS.md`。只有用户提出接入、读取共享上下文、同步、汇总、
校验或可视化目标时，才会访问云端。

发布采用失败即停止策略：如果 Vault 存在未提交修改或分支分叉，Coherens
会停止；否则使用仅快进拉取，只暂存当前项目的知识路径，校验 Markdown
元数据和链接，然后提交并推送。它不会猜测如何解决合并冲突。

## 从本地检出安装

要求 Python 3.10 或更高版本、PyYAML 6.x 和 Git。安装依赖及随附 Skills：

```text
python -m pip install -r requirements.txt
python tools/install_skills.py
```

如果 Skills 没有立即出现，请重新启动 Codex。仓库还提供
`.codex-plugin/plugin.json`，用于插件分发。

## 事实来源与路由

1. `PROJECT_MAP.md` 是供人阅读的项目地图。
2. `registry.yaml` 保存稳定的项目、工作区和版本身份。
3. `projects/<project-id>/index.md` 将任务路由到精简上下文包。
4. Git 提交把知识结论绑定到具体代码版本。

## 校验

```text
python skills/project-knowledge/scripts/project_knowledge.py validate --knowledge-root .
python skills/knowledge-graph-view/scripts/knowledge_graph.py --knowledge-root .
python -m unittest discover -s tests -v
```

不要提交密码、令牌、私钥、原始对话归档或完整终端输出。某台离线设备上尚未
同步的工作无法出现在当日汇总中。
