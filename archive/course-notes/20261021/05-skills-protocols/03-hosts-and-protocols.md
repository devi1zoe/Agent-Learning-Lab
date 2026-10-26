# Stage5 · 宿主怎样把能力包接入一次任务？

先读 [设计主线](01-skills-and-protocols.ipynb)，再看 [成对效果实验](02-skill-comparison.ipynb)。本页解决一个常见误解：磁盘上有SKILL.md，不等于宿主发现、模型触发、资源加载、工具获准、任务成功这五件事都发生了。

## 从原始任务到技能生效

用户要“比较给定资料，写有依据的研究报告”。发现阶段只需要看到`research-report`名称与描述；相关时加载正文；决定输出报告后读模板；需要结构验收时调用包内脚本；最后逐项检查claim与来源是否匹配。

其中任何一环都可能失败：描述过宽导致无关任务误触发，正文过长挤掉证据，路径错导致模板未读，脚本被权限拒绝，checker只看格式漏掉事实错误。修复应对准失败阶段，不是继续添加万能提示。

本地 [research-report包](assets/research-report/SKILL.md) 是自包含的能力产物。当前只在教学`LocalSkillHost`里显式加载，**未安装到任何用户全局产品宿主**；教学事件不是产品部署证据。

## S5.4–S5.5：对照官方宿主，不把字段语义混用

以下于2026-10-20核对原始资料，产品后续版本可能变化。

| 维度 | Claude Code | OpenClaw |
|---|---|---|
| 官方原始来源 | [Skills文档](https://code.claude.com/docs/en/skills) | [仓库skills.md](https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md) |
| 作用域 | personal/project等位置决定可见范围 | workspace、agent、managed、bundled等来源及优先级 |
| 发现与加载 | 常规会话先描述，调用时正文；支持文件按需读 | inventory、readiness、visibility分层；模型读取可见能力资源 |
| 触发 | 相关时自动选择或用户命令；前端字段可控制 | 用户调用与模型选择由宿主设置/字段控制 |
| 权限边界 | `allowed-tools`等宿主字段可能影响当轮权限；不能跨产品照搬 | 依赖就绪或allowlist可见不等于执行工具获准 |

本课程包使用通用name/description，不声明宿主特有授权字段。能力包正文不扩展原任务权限。不能将OpenClaw的eligible等同任意exec允许，也不能断言Claude Code永远忽略技能里的权限字段。

官方资料来源用于理解机制；没有在本机运行产品时，应将部署状态写成“未部署/未验证”。要核真实宿主，应在用户授权的测试workspace内保留实际来源路径、版本、触发记录、资源读取和执行结果。

## MCP、A2A、ACP的协议边界

协议首先定义交互双方和消息契约：

| 协议 | 交互双方 | 典型对象 | 本课程不声称已实现的部分 |
|---|---|---|---|
| [MCP](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) | 工具客户端与server | tools/list、tools/call及结果 | 完整网络服务、协商、认证与宿主集成 |
| [A2A](https://a2a-protocol.org/latest/specification/) | 独立Agent之间 | task、message、artifact | 远程任务服务与端到端互操作 |
| [ACP](https://agentclientprotocol.com/get-started/introduction) | 客户端/编辑器与Agent | session、更新、权限交互 | 真正客户端连接与完整生命周期 |

这里ACP明确指Agent Client Protocol。一个Python字典长得像JSON-RPC，只完成消息形状示意；传输、协商、版本、取消、权限和错误恢复仍需要单独实现。Stage4的本地函数分工也不因此成为A2A。

Skill告诉模型怎样完成一类任务；工具实施动作；协议连接现有接口；宿主维护发现、上下文、权限和生命周期。这四层可以协作，但证据不能互相替代。

## S5.8：区分三种“通过”

1. `quick_validate.py`通过：包结构与元数据合法，不代表触发准确或任务质量提高。
2. 包内`smoke_test.py`通过：检查器覆盖确定的结构错误，并暴露语义局限；没有测试模型uplift。
3. 有无Skill成对实测：在相同模型、题目、来源和输出预算下生成报告，评估事实/引用/缺口/冲突，同时保留额外输入成本。六题单次结果不作统计泛化。

原始响应和成功/失败以 [统一证据页](../evidence/20261020/README.md) 为准。Skill可能只改善格式，可能没有收益，也可能因上下文成本导致截断；这些都需要如实呈现。
