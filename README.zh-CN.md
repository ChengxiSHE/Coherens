# Coherens

[English README](README.md)

**面向多端、多项目 Agentic Engineering 的项目智能协同底座。**

> 每一个项目，每一个端侧，共享同一个连贯的智能层。

代码仓库保存“发生了什么变化”，Coherens 保存“项目从变化中学到了什么”：
为什么做出某项决策、它适用于哪个环境、由哪个版本验证、此前经历过哪些失败，
以及下一个 Agent 继续工作时真正需要知道什么。

Coherens 将工作站、服务器、容器、分支、版本和编程 Agent 中分散的项目信息，
统一为持久、可治理的知识体系，让每一次分散执行最终汇聚为持续增值的项目智能。

## 现代工程缺失的关键一层

今天的工程活动早已不再局限于一台电脑、一个仓库。一个项目可能在 Windows
完成前期开发，在 macOS 进行集成，再进入 GPU 容器完成训练与推理；个人和
团队同时推进多个项目，而 Codex 等 Agent 在每个新环境中拥有的上下文并不
相同。

Git 可以移动代码，却无法携带项目完整的操作记忆；聊天记录可以保存对话，
却无法形成具有版本边界和可信来源的项目知识；传统文档可以积累页面，却不会
持续协调端侧状态、项目身份、版本语义和 Agent 交接。

Coherens 正是这层长期缺失的项目智能基础设施。

## Coherens 带来的核心价值

| 核心能力 | 产品价值 |
| --- | --- |
| 多端连续性 | 项目可以在 Windows、macOS、Linux、服务器和 Docker 之间延续，不再重复重建理解。 |
| 多项目智能 | 每个项目保持独立身份，同时在整个工程组合中持续积累可复用知识。 |
| 版本可信语义 | 将知识绑定到仓库、分支、版本轨道、工作区和经过验证的 Git 提交。 |
| Agent 自主运营 | 用户只表达目标，由 Codex 完成发现、配置、注册、同步、校验和反馈。 |
| 精准上下文路由 | 只读取当前任务所需的最小上下文包，而不是每次扫描整个项目或 Vault。 |
| 可治理知识积累 | 明确区分原始进度、端侧状态、环境差异、版本知识、操作手册和长期决策。 |
| 可审计协同 | 以 Markdown 和 Git 实现可读变更、确定性校验、来源追踪、回滚与协作。 |

## 为高摩擦工程场景而生

- 在 Windows 和 macOS 之间迁移开发，不丢失决策，也不重新分析整个项目。
- 将代码传递到 Docker 或 GPU 服务器时，同时获得正确版本、环境约束、操作
  手册和历史失败记录。
- 同时维护私有、实验、生产和开源版本，不混淆各自的前提与边界。
- 并行推进多个项目，并根据已同步证据生成项目级每日汇总。
- 在不同编程 Agent 之间交接工作，不依赖彼此不兼容的对话记忆。
- 保存源代码本身无法表达的设计理由、实践经验和操作知识。

## 真正的 Agent-first

Coherens 不是一套需要用户学习和记忆的流程。用户只表达目标，Agent 负责发现
并运营整个过程。

第一次配置只需要一句话：

```text
请从 https://github.com/ChengxiSHE/Coherens.git 配置 Coherens，并完成全部检查。
```

专用的 `coherens-setup` Skill 固定保存官方仓库地址，并要求 Codex 自动完成：

1. 检查 Git、Python、Codex 插件能力、网络连接和 GitHub 身份认证。
2. 安装并验证官方 Coherens 插件。
3. 查找或创建私有 `Coherens-Vault` 仓库。
4. 为当前电脑、服务器或容器注册稳定身份。
5. 使用 `doctor` 诊断环境并解决所有可自动处理的问题。
6. 判断当前 Git 项目是否需要接入。
7. 汇报已完成工作，只在身份认证、权限确认或真正存在歧义时请求用户操作。

安装完成后，用户继续描述真正的工程目标即可：

```text
在 GPU 服务器上继续当前项目。
根据当前私有版本准备开源发布。
同步今天所有活跃项目的进展。
生成项目知识图谱。
```

轻量级 `SessionStart` Hook 只检查本地就绪标记，不拉取或读取 Vault。当发现
缺少设备配置或项目注册时，它会向 Codex 提供必要的流程信息，让 Codex 在
相关任务中主动完成处理。

## 持续复利的知识体系

Coherens 根据所有权和持久性划分信息，使 Vault 在长期增长后仍然保持准确：

| 知识层 | 用途 |
| --- | --- |
| `PROGRESS.md` | 轻量、本地、追加式工作证据。 |
| `workspaces/` | 每台已注册电脑、服务器或容器的当前状态。 |
| `environments/` | 操作系统、硬件、容器与运行时差异。 |
| `versions/` | 分支、发布、实验、私有和开源版本知识。 |
| `runbooks/` | 带有前置条件和验证步骤的可重复操作流程。 |
| `decisions/` | 长期决策、理由、替代方案和生效提交。 |
| `common/` | 在相关端侧和版本中得到验证的公共结论。 |
| `context-packs/` | 面向具体任务、只包含必要知识的精简路由。 |

`PROJECT_MAP.md` 是供人阅读的多项目地图，`registry.yaml` 提供稳定的机器
路由，每个 `projects/<project-id>/index.md` 负责面向任务的上下文选择，
Git 提交则把知识结论锚定到具体代码状态。

## 信任与控制

Coherens 从设计上建立明确边界：

- 公开产品仓库和私有知识 Vault 使用两个独立 Git 仓库，永远不使用分支作为
  隐私边界。
- Markdown 保持人类可读，Git 保持完整来源记录。
- 普通编码不会自动读取或同步云端知识。
- 密码、令牌、私钥、原始对话归档和完整终端输出不得进入 Vault。
- Vault 存在未提交修改或分支分叉时，同步将停止。
- 只允许快进拉取、限定生成文件范围，并在提交和推送前执行校验。
- 不猜测解决合并冲突、凭据问题、受保护分支或模糊的项目身份。

## 仓库模型

Coherens 使用两个仓库：

1. **公开产品仓库：** 插件、Skills、Hooks、确定性工具、数据结构、测试和示例。
   `https://github.com/ChengxiSHE/Coherens.git`
2. **私有智能 Vault：** 真实项目知识、端侧状态、版本记录、决策、操作手册和
   进度证据。默认名称：`<github-owner>/Coherens-Vault`

## 本地开发

要求 Python 3.10 或更高版本、PyYAML 6.x 和 Git。

```text
python -m pip install -r requirements.txt
python tools/install_skills.py
```

仓库包含用于插件分发的 `.codex-plugin/plugin.json`。本地安装 Skills 后如果
没有立即显示，请重新启动 Codex。插件生命周期 Hook 首次运行前需要进行一次
Codex 信任确认。

## 校验

```text
python skills/project-knowledge/scripts/project_knowledge.py validate --knowledge-root .
python skills/knowledge-graph-view/scripts/knowledge_graph.py --knowledge-root .
python -m unittest discover -s tests -v
```

Coherens 让每个项目拥有持久记忆，让每个端侧共享同一幅运行图景，让每个 Agent
都能获得推动工作继续前进的准确上下文，而不再从头开始。
