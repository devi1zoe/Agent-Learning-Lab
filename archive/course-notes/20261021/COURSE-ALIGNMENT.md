# 与 Agent-Learning-Hub 逐项对齐

核对于2026-10-20，上游固定提交 `dddf777dde6788228136862f270203424a28efbc`。[原文](references/agent-learning-hub/README.md)及MIT许可证随参考快照保存。

**覆盖不等于全部能力成功。** 下列50项均有实质设计教学与作者示范，9项阶段作品均有文件；真实模型、程序测试和阅读研究分别标明。研究报告质量、Skill收益及部分模型任务尚未达标，不给失败项补勾；学习者掌握程度另需亲自解释和修改实验。

## Stage 0 · Understand What An Agent Is

教材：[01-what-is-an-agent](00-foundations/01-what-is-an-agent.ipynb)；[04-reading-anthropic](00-foundations/04-reading-anthropic.md)；[05-reading-openai](00-foundations/05-reading-openai.md)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S0.1 | 区分 chatbot、workflow、agent、multi-agent。 | 同一资料研究目标的四种控制方式，定位谁决定下一步，并分析各自失败点。 |
| S0.2 | 理解 agent 的基本循环：observe -> think -> act -> observe。 | 以目标/状态→模型动作→执行→观察回写的数据流解释循环；不把内部思维当可审计trace。 |
| S0.3 | 明白什么时候不该用 agent：任务可预测、流程稳定、普通脚本能解决时，agent 反而增加不确定性。 | 固定两篇材料摘要保留workflow基线，说明动态取证不值得的条件与调用代价。 |
| S0.4 | 读完 [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)。 | 完成官方原文核对、短导读与独立设计分析，区分workflow模式与自主循环。 |
| S0.5 | 读完 [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)。 | 完成指定官方指南阅读导读，讨论模型/工具/指令、单Agent到协调系统、护栏与人类介入。 |

**S0.O 原产出：** 写一页短笔记，回答「我的场景为什么需要 agent，而不是普通 workflow？」

本地作品：[一页场景笔记](evidence/20261020/stage0-scenario.md)。

## Stage 1 · Build A Minimal Agent Loop

教材：[01-minimal-loop](01-agent-loop/01-minimal-loop.ipynb)；[02-live-model](01-agent-loop/02-live-model.ipynb)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S1.1 | 会用一个 LLM API 完成普通对话。 | [普通真实API记录](evidence/20261020/stage1-api.json)保存实际请求、生成文本、token与时延。 |
| S1.2 | 会让模型输出结构化 JSON。 | 同一API文件保存JSON模式实际响应；正文区分可解析、schema合法与事实正确。 |
| S1.3 | 会定义一个工具函数，例如 search、calculator、read_file。 | [98行Agent](experiments/minimal_agent.py)定义read_file/search_documents及窄参数集合，读的是课程资料而非任意服务器目录。 |
| S1.4 | 会解析模型的 tool call / function call。 | 主课逐字段拆tool_calls/function/name/arguments；[有门轨迹](evidence/20261020/stage1-evidence-gate.json)含真实read_file请求。 |
| S1.5 | 会执行工具，并把工具结果喂回模型。 | 有门轨迹保留真实工具结果与下一轮输入；与0工具的两次失败比较，显示反馈如何改变结果。 |
| S1.6 | 会给 agent loop 加最大步数、超时和错误处理。 | 实现最大轮次、HTTP超时、工具异常、重复调用与证据门；区分请求间预算检查和硬中断。 |

**S1.O 原产出：** 一个 50-150 行的最小 agent，可以选择工具、执行工具、返回最终答案。

本地作品：[98行Agent](experiments/minimal_agent.py)与[真实轨迹](evidence/20261020/stage1-evidence-gate.json)，取证成功但引用仍有缺口。

## Stage 2 · Learn Tool Use, RAG, And Memory

教材：[01-rag-and-memory](02-tools-rag-memory/01-rag-and-memory.ipynb)；[02-research-agent](02-tools-rag-memory/02-research-agent.ipynb)；[03-web-research](02-tools-rag-memory/03-web-research.ipynb)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S2.1 | 会做检索增强生成：chunk、embed、retrieve、answer with citations。 | [真实MiniLM复跑](evidence/20261020/stage2-rag-fixed-snapshot/result.json)有chunk、384维embedding、检索与带编号答案；语义支持另审。 |
| S2.2 | 会把搜索、数据库、文件、浏览器、代码执行接成工具。 | [联网研究](evidence/20261020/stage2-web-research/result.json)有搜索/正文读取；RAG记录含文件/SQLite/受限代码的程序直调；浏览器实测单列，未伪称全由模型选择。 |
| S2.3 | 会区分短期上下文、会话记忆、长期记忆。 | 正文按生命周期区分messages/会话磁盘/显式长期记忆，展示写入、召回、删除与来源权限；默认程序回归覆盖。 |
| S2.4 | 会处理工具失败、空结果、重复调用、幻觉引用。 | 处理空检索/重复工具/错误与伪来源，结合20题真实失败说明协议正确和拒答策略仍有差距。 |
| S2.5 | 会让 agent 在回答里给出来源或证据。 | 本地RAG答案绑定来源；联网报告含实际链接但语义空泛，明确自动引用门无法验证完整回答质量。 |

**S2.O 原产出：** 一个资料研究助手，输入主题后自动搜索、筛选、总结并输出引用链接。

本地作品：[联网报告](evidence/20261020/stage2-web-research/report.md)与[RAG答案](evidence/20261020/stage2-rag-fixed-snapshot/result.json)，报告语义质量未充分达标。

## Stage 3 · Study One Modern Agent Harness

教材：[01-harness](03-agent-harness/01-harness.ipynb)；[02-upstream-comparison](03-agent-harness/02-upstream-comparison.ipynb)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S3.1 | 读懂一个 agent harness 的目录结构。 | [固定源码目录](references/learn-claude-code/source.json)与逐文件导读定位所选learn-claude-code版本。 |
| S3.2 | 找出它的 agent loop、tool registry、permission gate、session store、context compaction。 | 逐层标注s02已有safe_path/命令限制及其缺少的持久会话/compaction/交互权限门；后续源码与本地Harness分别归属。 |
| S3.3 | 跑通它的最小示例，并加一个你自己的工具。 | [原上游loop实跑](evidence/20261020/stage3-upstream/comparison.json)加入count_words，真实模型生成工具请求，程序返回4。 |
| S3.4 | 观察一次完整 trace，解释每一步为什么发生。 | 原件保留原始模型请求、两轮循环、工具执行与1调用预算失败；正文逐步解释。 |
| S3.5 | 把同一个任务分别用「裸 agent loop」和「harness」实现，对比差异。 | 原上游与裸loop同题同模型同工具均两调用答对；对照控制点和适配差异，不凭简单题证明生产能力。 |

**S3.O 原产出：** 一个可调试的 agent harness demo，包含 README、运行步骤、示例输入输出和失败记录。

本地作品：[固定上游及裸loop对照](evidence/20261020/stage3-upstream/comparison.json)，附源码、运行与失败记录。

## Stage 4 · Multi-Agent Is Coordination, Not Magic

教材：[01-coordination](04-multi-agent/01-coordination.ipynb)；[02-live-coordination](04-multi-agent/02-live-coordination.ipynb)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S4.1 | 理解 planner / executor / reviewer / critic / router 等常见角色。 | 正文给planner/executor/reviewer/critic/router不同输入、输出、权限和职责；区分角色命名与独立决策。 |
| S4.2 | 学会用 supervisor 或 graph 管理多 agent，而不是让 agent 随便聊天。 | 实现有界writer→reviewer→revise协调图；[真实对照](evidence/20261020/stage4-coordination/result.json)是固定监督拓扑，非任意群聊。 |
| S4.3 | 会定义每个 agent 的职责边界、输入输出 schema、停止条件。 | 证据数组、稿件、review对象与task_id契约经过schema检查；真实writer/reviewer输入分别保留。 |
| S4.4 | 会处理循环、争论、任务漂移、上下文膨胀。 | 循环审阅、任务漂移、无效review与300字符上下文边界使用固定故障回归，明确非模型独立生成攻击。 |
| S4.5 | 会判断什么时候单 agent 更好。 | 同题单角色1调用、协调2调用均答对；本次没有修订收益，分析隔离/审阅成本。 |

**S4.O 原产出：** 一个小型多 agent 系统，例如 research -> write -> review -> revise。

本地作品：[多角色系统记录](evidence/20261020/stage4-coordination/result.json)，单Agent基线与终止压力测试。

## Stage 5 · Learn Skills, Protocols, And Capability Packaging

教材：[01-skills-and-protocols](05-skills-protocols/01-skills-and-protocols.ipynb)；[02-skill-comparison](05-skills-protocols/02-skill-comparison.ipynb)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S5.1 | 理解 Skill 和 Tool 的区别：tool 是可调用接口，skill 是可复用流程知识。 | 用同一取证任务区分可调用接口与可复用决策知识；工具可用性不因Skill文本扩大。 |
| S5.2 | 理解 Skill 和 Prompt 的区别：prompt 通常是一次性指令，skill 是可发现、可版本化、可分发的能力包。 | 对比一次性指令与有元数据/版本/模板/验证的能力包，分析发现成本与输入token代价。 |
| S5.3 | 理解 Skill 和 MCP 的区别：MCP 接入外部工具/数据源，skill 告诉 agent 如何完成一类任务。 | 分开MCP连接、Tool执行、Skill步骤知识和宿主权限；不声称协议自动提供规划或安全。 |
| S5.4 | 阅读 Claude Code Skills 的文件结构和触发机制。 | 对照Claude官方发现/触发/渐进加载/作用域文档；正文列产品特性与本地教学宿主区别。 |
| S5.5 | 阅读 OpenClaw Skills 的加载、作用域和安全边界。 | 对照OpenClaw官方加载/作用域/来源边界；不宣称在真实OpenClaw宿主安装。 |
| S5.6 | 写一个最小 `SKILL.md`，包含 name、description、何时使用、步骤、验收标准。 | [独立SKILL.md](05-skills-protocols/assets/research-report/SKILL.md)具精确触发、步骤、证据规则与验收边界。 |
| S5.7 | 给 skill 加一个脚本或模板文件，并说明 agent 什么时候才需要加载它。 | 模板、证据契约、确定性检查器按需加载；能力包复制到独立目录仍能运行6项smoke。 |
| S5.8 | 给 skill 写一个 smoke test，验证它是否真的提升任务成功率。 | [六题有无Skill](evidence/20261020/stage5-skill/results.json)保存原请求和固定评分：任务均0/6；没有观察到成功率提升，未修改评分凑通过。 |

**S5.O 原产出：** 一个可复用 skill，例如 code-review、research-report、migration-helper、pdf-extraction 或 release-note-writer。

本地作品：[独立research-report包](05-skills-protocols/assets/research-report/SKILL.md)和[成对实验](evidence/20261020/stage5-skill/summary.json)，本次未证明收益。

## Stage 6 · Browser And Computer-Use Agents

教材：[01-browser-basics](06-browser-agent/01-browser-basics.ipynb)；[02-public-page-agent](06-browser-agent/02-public-page-agent.ipynb)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S6.1 | 理解 browser agent 和普通 API tool 的区别。 | 正文区分HTTP文本、DOM可见内容、截图和动作空间；解释页面状态及观察遗漏。 |
| S6.2 | 会用 Playwright 或 browser-use 做网页观察和点击。 | 默认23本回归中执行本地真实Chromium读取/定位/点击；实际公开页模型选择read_page另保存。 |
| S6.3 | 会给浏览器操作加安全限制：不登录敏感账号、不越权、不绕过平台规则。 | 公开案例限定HTTPS GET主机与固定页面，不登录、不提交；正文解释宿主授权不来自页面提示。 |
| S6.4 | 会处理页面变化、弹窗、加载失败、元素定位失败。 | 受控页面覆盖失效定位/等待/恢复，区分程序恢复与模型重规划；真实公开页未据此宣称复杂恢复。 |
| S6.5 | 会记录截图、DOM、动作日志，方便复盘。 | [真实课程网页轨迹](evidence/20261020/stage6-course-page/result.json)有DOM、截图、动作、模型请求、摘要和原文quote。 |

**S6.O 原产出：** 一个只操作公开网页的 browser agent，例如打开网页、提取信息、生成摘要。

本地作品：[课程GitHub公开页Agent](evidence/20261020/stage6-course-page/result.json)，保留DOM/截图/动作日志。

## Stage 7 · Evaluation, Observability, And Safety

教材：[01-contract-evaluation](07-evaluation-safety/01-contract-evaluation.ipynb)；[02-live-evaluation](07-evaluation-safety/02-live-evaluation.ipynb)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S7.1 | 为 agent 准备固定测试集，而不是只看 demo。 | [冻结20题](evidence/20261020/eval-tasks.json)覆盖正常/空结果/冲突/工具故障/注入，原期待值和评分保留。 |
| S7.2 | 记录成功率、失败原因、工具调用次数、成本、延迟。 | [eval.csv](evidence/20261020/eval.csv)逐题记录实际/期望/分类/调用/token/延迟；成本无外部API账单，硬件费用未知。 |
| S7.3 | 会看 trace，知道失败发生在 prompt、工具、检索、模型还是状态管理。 | 正文对empty-1/conflict-1/injection-2逐事件分层分析，解析/事实/引用/完成分开计分。 |
| S7.4 | 给危险工具加人工确认，例如发邮件、删文件、付款、发布内容。 | [独立交付审批](evidence/20261020/stage8-delivery/verification/delivery-result.json)六项检查绑定内容/路径/摘要，拒绝与变化不写；不真实发送/删除/支付。 |
| S7.5 | 了解 prompt injection、data exfiltration、tool abuse 等风险。 | 实际注入题与能力包注入结果揭示内容污染；无邮件工具只限制动作面，不能当全面安全率。 |
| S7.6 | 会用回归测试防止 prompt 或工具改动后能力退化。 | 保留固定任务和默认程序回归；证据门有明确版本差异，日志修复同配置复跑；没有冒充严格前后能力回归。 |

**S7.O 原产出：** 一个 agent eval 表格，至少包含 20 个任务、期望结果、实际结果、失败分类。

本地作品：[20题完整结果](evidence/20261020/eval.csv)，真实9/20通过，失败不删改。

## Stage 8 · Ship A Real Agent

教材：[01-research-assistant](08-capstone/01-research-assistant.ipynb)；[02-delivery-check](08-capstone/02-delivery-check.ipynb)。

| 编号 | 上游要求 | 当前完成内容、证据与边界 |
| --- | --- | --- |
| S8.1 | 有明确用户、明确任务、明确成功标准。 | 任务契约规定学习笔记读者、输入、证据答案与明确完成/缺证状态，阶段作品在独立目录。 |
| S8.2 | 有日志、trace、错误重试、超时、成本上限。 | 导出CLI有trace/一次重试/共享超时/请求间token预算；小模型与API调用的费用归因明确，承认软上限。 |
| S8.3 | 有权限边界和人工确认机制。 | 副作用导出按具体内容/路径/摘要审批；6个审批回归验证不扩权和防参数变化。 |
| S8.4 | 有部署方式：CLI、Web app、Slack bot、GitHub Action 或后台任务。 | [可独立运行CLI](evidence/20261020/stage8-delivery/project/README.md)在全新venv通过离线/真实模型/预算/缺失模型等6CLI检查。 |
| S8.5 | 有 README：怎么运行、怎么配置 key、怎么扩展工具、有哪些限制。 | 导出README与[交付设计](08-capstone/DELIVERY.md)说明运行、模型服务、扩工具、退出码与限制；不把本机验证当生产SLA。 |

**S8.O 原产出：** 一个别人能 clone 下来跑的 agent 项目。

本地作品：[独立项目与README](evidence/20261020/stage8-delivery/project/README.md)及[新venv验证](evidence/20261020/stage8-delivery/verification/delivery-result.json)。

