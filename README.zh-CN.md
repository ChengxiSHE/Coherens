<div align="center">
  <h1>Coherens · 连接每个端侧的项目智能</h1>
  <p>面向多端、多项目工程的 Codex 原生信息协同与知识积累框架。</p>
  <p><a href="README.md">English README</a></p>
  <p>
    <a href="#skill-包">Skill 包</a> ·
    <a href="#安装">安装</a> ·
    <a href="#快速开始">快速开始</a> ·
    <a href="#支持的协同范围">协同范围</a> ·
    <a href="#架构">架构</a> ·
    <a href="#验证">验证</a> ·
    <a href="#安全与边界">安全</a>
  </p>
  <p>
    <img alt="版本 0.3.0" src="https://img.shields.io/badge/version-0.3.0-blue">
    <img alt="Skills 3" src="https://img.shields.io/badge/skills-3-2ea44f">
    <img alt="知识层 8" src="https://img.shields.io/badge/knowledge_layers-8-0f766e">
    <img alt="流程测试 12" src="https://img.shields.io/badge/workflow_tests-12-ca8a04">
    <a href="LICENSE"><img alt="MIT 许可证" src="https://img.shields.io/badge/license-MIT-brightgreen"></a>
  </p>
  <p>如果 Coherens 对你的工作有帮助，欢迎为仓库点亮 Star <a href="https://github.com/ChengxiSHE/Coherens"><img alt="在 GitHub Star Coherens" src="https://img.shields.io/badge/GitHub-Star-181717?logo=github"></a></p>
</div>

## 这个仓库是什么

Coherens 是一个 Codex 原生的项目智能框架，面向分布在多个项目、电脑、服务器、
容器、版本和 Agent 会话中的工程活动。

用户只需要在当前工作区描述工程目标。Coherens 会识别项目、端侧、版本轨道和
Git 状态，检索最小必要上下文，记录经过验证的进展，并将长期知识同步到私有
Git Vault。下一个端侧或 Agent 可以从可信的项目状态继续工作，而不必重新分析
整个仓库和历史。

代码仓库保存“发生了什么变化”，Coherens 保存“为什么变化、知识适用于哪里、
由哪个提交验证、此前失败过什么，以及下一个 Agent 需要知道什么”。

### 核心亮点

- **多端连续性：** 项目可以在 Windows、macOS、Linux、GPU 服务器和 Docker
  工作区之间延续，不再重复重建上下文。
- **多项目协同：** 每个项目保持稳定、独立的身份，同时在整个工程组合中持续
  积累知识。
- **版本可信知识：** 将工作区状态和可复用结论绑定到仓库、分支、版本轨道和
  Git 提交。
- **Agent-first 操作：** 用户只表达一个目标，由 Codex 完成安装、配置、注册、
  诊断、同步、校验、汇总和反馈。
- **精准上下文路由：** 每次会话只读取当前任务的上下文包，而不是扫描整个代码
  仓库或知识 Vault。
- **README 级首次建档：** 对已有项目进行一次完整分析，将项目目标、架构、模块、
  脚本、执行流程、命令、依赖和限制沉淀为带有代码证据的 Project Profile。
- **可治理积累：** 按所有权和持久性区分本地进度、端侧状态、环境差异、版本
  知识、操作手册、决策和公共结论。
- **Git 原生可审计：** 知识以人类可读的 Markdown 保存，并由 Git 提供来源、
  审查、回滚与协作能力。

## Skill 包

| Skill | 用途 | 入口 |
| --- | --- | --- |
| [`coherens-setup`](skills/coherens-setup) | 在电脑或服务器上发现、安装、配置、诊断或修复 Coherens 及其私有 Vault。 | [`SKILL`](skills/coherens-setup/SKILL.md) |
| [`project-knowledge`](skills/project-knowledge) | 注册项目和端侧、路由共享上下文、同步进度、生成汇总并校验 Vault。 | [`SKILL`](skills/project-knowledge/SKILL.md) |
| [`knowledge-graph-view`](skills/knowledge-graph-view) | 生成项目、版本、工作区和知识关系的独立交互式视图。 | [`SKILL`](skills/knowledge-graph-view/SKILL.md) |

Setup Skill 负责安装和机器就绪状态；Project Knowledge Skill 负责身份、路由、
同步和知识生命周期；Graph Skill 负责派生可视化。确定性本地工具负责注册表更新、
增量同步、校验、汇总和图谱生成。

## 安装

> [!TIP]
> 只向 Codex 提出一次配置请求，Codex 会自行完成可发现的步骤。如果尚无 Vault，
> 它会提示你创建一个空的 Private Git 仓库并返回克隆链接；Coherens 不代替用户
> 创建仓库。

在具备 Git 和网络访问的任意 Codex 环境中输入：

```text
请从 https://github.com/ChengxiSHE/Coherens.git 配置 Coherens。
如果我还没有连接 Vault，请提示我创建一个空的 Private Coherens-Vault，
并等待我返回克隆链接。请验证该仓库确实为 Private，然后完成连接、注册当前环境、
运行 doctor，并分别报告机器、Vault、项目和同步就绪状态。
```

`coherens-setup` Skill 固定保存官方仓库地址，验证插件身份，检查 Git、Python、
Codex 插件能力、网络和 Git 认证，然后验证并连接用户提供的 Private Vault，
并为当前电脑或容器注册稳定身份。

安装完成后，轻量级 `SessionStart` Hook 只检查本地就绪标记，不读取或拉取
Vault。新的或发生变化的生命周期 Hook 首次运行前需要通过一次 Codex 信任审查。

<details>
<summary><strong>本地开发安装</strong></summary>

要求 Python 3.10 或更高版本、PyYAML 6.x 和 Git。

```bash
git clone https://github.com/ChengxiSHE/Coherens.git
cd Coherens
python -m pip install -r requirements.txt
python tools/install_plugin.py
```

安装器会验证插件身份，将完整插件安装到个人 Codex marketplace 并启用。如果新的
Skills 或 SessionStart Hook 没有立即显示，请重新启动 Codex。
`tools/install_skills.py` 仍用于仅安装 Skills 的开发或其他 Agent 集成场景。

</details>

## 快速开始

> [!NOTE]
> 从真正的工程目标开始。Coherens 会检查机器和项目状态，在相关情况下补齐接入
> 流程，并且只在任务需要时读取共享上下文。

```text
在 GPU 服务器上继续当前项目。
```

其他自然语言示例：

```text
根据当前私有版本准备开源发布。
同步今天所有活跃项目的进展。
读取复现上一次成功 Docker 训练所需的上下文。
生成项目知识图谱。
```

仍然可以显式调用 Skill，但日常使用不需要这样做。

项目第一次同步时，Coherens 会执行一次完整的仓库建档并填写
`PROJECT_PROFILE.md`。它相当于一份长期维护的技术 README，说明项目目标、架构、
目录、模块、关键脚本、输入输出、运行方式、依赖与限制，并绑定到当前干净的 Git
提交。后续同步只处理新增进展和状态变化，除非项目架构发生实质变化。

在 0.3 之前接入的项目会被视为旧版项目，必须补齐稳定 origin、真实代码提交和
Project Profile，并让既有同步记录通过新的就绪与隐私检查后，才能继续正常同步。

## 支持的协同范围

### 端侧

| 端侧 | 跟踪角色 |
| --- | --- |
| Windows 工作站 | 开发、测试、打包或项目操作。 |
| macOS 工作站 | 开发、集成、发布或项目操作。 |
| Linux 工作站或服务器 | 开发、自动化、部署或远程执行。 |
| Docker 工作区 | 隔离构建、训练、推理、测试或部署状态。 |
| GPU 服务器 | 结合环境专属操作手册执行版本绑定的训练与推理。 |

每个物理或逻辑端侧都拥有稳定的 `workspace_id`。需要在容器重建后延续身份时，
必须为 Coherens 配置目录提供持久化存储。

### 身份模型

| 身份 | 用途 |
| --- | --- |
| `project_id` | 同一项目所有检出目录和端侧共享的稳定身份。 |
| `workspace_id` | 一个物理或逻辑执行端侧的稳定身份。 |
| `version_track` | 分支、发布、实验、私有、生产或开源版本的知识边界。 |
| `environment` | 操作系统、硬件、容器、运行时和依赖范围。 |
| Git 提交 | 支撑同步结论的具体代码状态。 |

项目接入前必须具有稳定的 origin 远端。Coherens 不会仅凭时间戳判断哪个端侧最
可信，而是联合解析项目、工作区、版本轨道、分支和提交。脏工作区或未跟踪源码
可以记录为 `unanchored`，但不得称为已验证状态。

### 知识模型

| 知识层 | 用途 |
| --- | --- |
| `PROGRESS.md` | 轻量、本地、追加式工作证据。 |
| `workspaces/` | 每台已注册电脑、服务器或容器的当前状态。 |
| `environments/` | 操作系统、硬件、容器与运行时差异。 |
| `versions/` | 分支、发布、实验、私有、生产和开源版本知识。 |
| `runbooks/` | 带有前置条件和验证步骤的可重复操作流程。 |
| `decisions/` | 长期决策、理由、替代方案和生效提交。 |
| `common/` | 在适用端侧和版本中得到验证的公共结论。 |
| `context-packs/` | 面向具体任务、只包含必要知识的精简路由。 |

每个项目还必须包含 `PROJECT_PROFILE.md`。首次同步前，Agent 必须分析并说明已有
项目的目标、架构、模块和脚本职责、接口、执行流程、命令、依赖、限制及查阅证据。

`PROJECT_MAP.md` 是供人阅读的多项目入口，`registry.yaml` 是机器注册表，
每个 `projects/<project-id>/index.md` 将任务路由到有限上下文，Git 提交则把
知识锚定到具体代码状态。

## 架构

Coherens 工作流由三层组成：

- **Agent 接口层：** 三个 Codex Skills 和一个轻量会话 Hook，将自然语言意图
  转换为配置、路由、同步、校验和可视化工作流。
- **确定性控制层：** 本地 Python 工具管理身份、同步游标、项目脚手架、工作区
  状态、每日汇总、校验、Git 发布和图谱生成。
- **Git 项目智能模型：** 私有 Vault 以可审查的 Markdown 和 YAML 保存项目地图、
  注册信息、端侧状态、版本知识、证据、操作手册、决策和上下文包。

普通编码只更新本地 `PROGRESS.md`。只有用户请求跨端工作、共享上下文、同步、
汇总、校验或可视化时，才会读取或发布共享知识。

## 仓库结构

```text
Coherens/
|-- .codex-plugin/        # 插件身份和分发元数据
|-- skills/               # Setup、项目知识和图谱 Skills
|-- hooks/                # 轻量 Codex 生命周期就绪检查
|-- tools/                # 本地安装工具
|-- templates/            # 安装到已接入代码项目的文件
|-- schema/               # 知识文档元数据契约
|-- projects/             # 示例 Vault 项目和知识层
|-- tests/                # 端到端流程和打包测试
|-- PROJECT_MAP.md        # 供人阅读的多项目地图
|-- registry.yaml         # 稳定、机器可读的身份注册表
`-- README.md             # 英文文档
```

公开仓库只包含产品代码、模板、测试和可再分发示例。真实项目知识必须保存在独立
私有 `Coherens-Vault` 仓库中，不得提交到这里。

## 验证

运行确定性验证套件：

```bash
python -m unittest discover -s tests -v
python skills/project-knowledge/scripts/project_knowledge.py validate --knowledge-root .
python skills/knowledge-graph-view/scripts/knowledge_graph.py --knowledge-root .
```

12 项流程测试覆盖完整插件安装、用户确认的 Private Vault 初始化、就绪状态拆分、
官方仓库地址锁定、隐式会话路由、稳定项目身份、首次同步 Profile、增量同步、
未锚定代码状态、重复发布、每日汇总、Markdown 校验、双语 README 完整性和
图谱生成。
校验还会拒绝包含本地用户主目录路径的同步 Markdown，以及在 `unanchored` 状态下
错误声明 `verified_commit` 的文档。

验证只能证明仓库包含的确定性流程和测试样例，不代表每一条由 Agent 编写的知识
结论都天然正确。长期结论仍然需要证据、明确适用范围和与项目风险相匹配的审查。

## 安全与边界

- **仓库边界：** 公开产品仓库和私有知识 Vault 是两个独立 Git 仓库，分支永远
  不是隐私边界。
- **凭据边界：** 密码、令牌、私钥、`.env` 文件、原始聊天归档和完整终端输出
  不得进入 Vault。
- **读取边界：** 普通编码不会自动读取或拉取共享知识，上下文检索由任务触发且
  范围受限。
- **写入边界：** 本地进度只在显式请求时同步，经过审查后才能提升为长期知识。
- **路径边界：** 本地项目绝对路径只保存在当前设备，不写入同步进度记录。
- **Git 安全：** Vault 存在未提交修改或分支分叉时停止同步，只允许快进拉取、
  限定暂存路径、提交前校验，并且不猜测解决冲突或受保护分支问题。
- **Agent 范围：** Coherens 当前以 Codex 插件形式打包。Markdown、YAML 和
  确定性工具具备可移植性，但其他编程 Agent 仍需要各自的集成层才能获得等价的
  生命周期行为。

Coherens 使用 [MIT License](LICENSE) 发布。
