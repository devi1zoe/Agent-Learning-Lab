# Course Alignment｜与 Agent Learning Hub 对齐

核对日期：2026-10-14。依据 [Agent Learning Hub 固定版本](https://github.com/datawhalechina/Agent-Learning-Hub/blob/dddf777dde6788228136862f270203424a28efbc/README.md) 的 **Learning Todo List（Stage 0–8）**，共 50 项任务和 9 项阶段产出。上游提交：`dddf777dde6788228136862f270203424a28efbc`。以后上游变更时需重新核对，不能把本页当作自动同步的成绩单。

**结论：九阶段教材与先前缺少的实践入口已补齐，并已保存真实运行证据。** 上游循环实跑、真实 RAG、skill 对照、公开网页 agent、20 题真实评测和新 venv 交付检查均已执行，详见 [实践结果](PRACTICE-RESULTS.md)。模型评测包含失败，产品宿主与生产环境能力仍有范围限制；个人阅读和总结须学习者完成。

## 怎么使用这份核对

主线始终是 `step0 → step1 → … → step8`。每一步按 `README → 00-prerequisites → 主 Notebook → COURSE-TASKS → 个人总结` 学习。Stage 2 的完整诊断本承接主 Notebook 的简化实验，也属于主线实践。

每个 [阶段任务单](step0/COURSE-TASKS.md) 都按上游条目编号，列出本地材料、现状、验收动作。编号如 `S3.3` 表示上游 Stage 3 第三项，`S3.O` 表示阶段产出。条目不预先打勾：有教材、有回归、有真实运行、有自己的解释，是不同层次的证据。

| Stage / 任务数 | 本地材料与条目核对 | 当前差距；不能据此认定结业 |
| --- | --- | --- |
| 0 / 5 | [概念、两篇阅读、场景笔记](step0/COURSE-TASKS.md) | 例子齐备；是否读完、能否解释自己的场景由学习者完成 |
| 1 / 6 | [普通对话、JSON、工具闭环](step1/COURSE-TASKS.md) | 真实调用完成，103 行独立作品已实跑；学习者继续改工具/解释失败 |
| 2 / 5 | [工具、RAG、记忆与研究报告](step2/COURSE-TASKS.md) | 真实 1024 维 embedding 与公开文档搜索/阅读已接通；检索/引用格式仍不能自动证明事实质量 |
| 3 / 5 | [现代 harness 深读与复现](step3/COURSE-TASKS.md) | 固定版本 s02 原循环加计数工具，与裸循环实测对照；使用明确的真实 Ollama API bridge，未整体部署上游产品 |
| 4 / 5 | [角色交接与协调](step4/COURSE-TASKS.md) | 真实写作/审核完成，漂移/结构/上下文/轮次压力检查完成；固定虚构任务评分不是通用写作评价 |
| 5 / 8 | [能力包与效果测试](step5/COURSE-TASKS.md) | 6 题双条件真实生成，自动报告评分 0/6→5/6；项目教学宿主已加载，不冒充产品宿主安装 |
| 6 / 5 | [浏览器观察、动作与复盘](step6/COURSE-TASKS.md) | 公开页模型读取、摘要、原文摘录与复盘已完成；仅允许固定页面，非任意桌面系统 |
| 7 / 6 | [固定评测与安全](step7/COURSE-TASKS.md) | 离线 27 项 + 真实模型 20 题（16 通过、4 失败）；后者用受控资料，不是开放互联网能力分数 |
| 8 / 5 | [可运行项目交付](step8/COURSE-TASKS.md) | 真实 CLI、新 venv、输出上限/预算退出及参数绑定审批已验证；本地费用不适用、总 token 限制仍是软限 |

## 全部材料的归属

核对覆盖仓库内 Markdown、Notebook、Python、依赖说明、模板、浏览器 fixture 和生成/验证脚本；不包含 Git 内部文件、环境依赖和忽略目录中的历史运行产物。保留的个人实验做定位与说明检查，不把未重跑的外部 SDK 接线宣布为通过。

| 路径或文件类别 | 定位 | 如何计入课程 |
| --- | --- | --- |
| `step0`–`step8` 的 README、`stageN-learning.ipynb` | 主线教材 | 对应同号 Stage；运行教学代码只是第一轮练习 |
| `step*/00-prerequisites.md`、[术语表](GLOSSARY.md) | 主线辅助 | 解释代码需要的词，不是另一个阶段，也无需整本背诵 |
| `step*/COURSE-TASKS.md` | 主线任务与验收 | 50 项要求、9 项产出及待办证据；不自动勾选学习完成 |
| `step0/01`–`05`、`step1/01`–`04` 笔记 | 原有阅读与个人记录 | 继续使用；生成的示例回答不能当个人结业记录 |
| `step2/step2_stage2_diagnostics_fixed.ipynb`、`requirements.txt` | 主线完整实践 | 承接搜索、embedding、数据库等；服务开关关闭不等于已实跑 |
| `step1/codex_sdk/`、`step1/ollama_mini_loop/` | 保留的实现路线 | 可选其中一种完成 Stage 1；无需每种 SDK 都学，旧输出不算本次验证 |
| `stage1b`、`stage2b`、`stage3b`、`stage3c` 和架构笔记 | **选修拓展** | ReAct、Self-Ask、规划反思、ToT、LLMCompiler；不阻塞进入下一主线阶段 |
| `step2/docs/`、`learning/demo_docs/` | RAG 语料 | 用来测试检索；安全论文不是 Stage 2 前置必读 |
| `step7/agent_permission_research/` | 个人进阶研究设计 | 不计作已实现的权限系统，不作为 Stage 7 入门前提 |
| `step5/skills/research-report/` | 主线阶段作品 | 文件齐全与提高模型效果分别验收 |
| `step6/browser_demo.py`、`fixture.html` | 主线教学执行层 | 真实 Chromium + 可控页面；与公开网页完整产出分开验收 |
| `learning/runtime.py`、`cli.py`、`evaluation.py` | 共用教学实现 | 分别支撑循环、交付、回归；有意简化不隐瞒 |
| `learning/course_practice.py`、`*_lab.py`、`stage2_live.py`、`skill_eval.py`、`live_evaluation.py`、`delivery_check.py`、`step1/minimal_agent.py`、`step6/public_agent.py` | 主线真实实践 | 补齐阶段作品和可重复验收，使用真实服务；结果范围见 PRACTICE-RESULTS |
| `learning/test_*.py`、`verify_notebooks.py` | 材料验证 | 测控制流与代码可运行性；不是学习者成绩或论文复现 |
| `learning/build_*.py`、`update_learning_guidance.py`、`sync_course_guidance.py` | 教材维护 | 普通学习不需要运行生成器；重建前另存自己的练习 |
| [参考导读](REFERENCE-WALKTHROUGH.md) | 源码阅读辅助 | 固定版本路径导读不等于完成上游安装和实验 |
| [学习导航](BEGINNER-GUIDE.md)、[新手审查](LEARNING-AUDIT.md)、[验证记录](VALIDATION.md) | 导航与证据范围 | 课程状态以本页及阶段任务单为准；历史测试记录按日期解释 |
| 其余依赖配置、`.gitignore`、图片/HTML/报告模板 | 支持材料 | 支撑运行，不独立产生课程完成证据 |

## 拓展安放原则

上游本身在资源区推荐 ReAct、Reflexion 等，但没有把每种架构列成独立必做阶段。这里按需要的基础就近挂接；学习多种策略不应挤掉上游的工具、harness、评测和交付任务。

| 拓展 | 接在哪一步之后 | 先有的基础 | 可选练习与回归位置 |
| --- | --- | --- | --- |
| [ReAct](step1/stage1b-react-learning.ipynb) | Stage 1 | 工具请求、观察回传、停止条件 | 同一问题因观察不同选不同动作；Stage 7 比较调用数 |
| [Self-Ask](step2/stage2b-self-ask-learning.ipynb) | Stage 2 | 检索、来源、证据不足时停止 | 两跳问题逐跳追溯；与一次检索比较 |
| [Plan-and-Execute / Reflection](step3/stage3b-planning-reflection-learning.ipynb) | Stage 3，或学完 Stage 4 回看 | 状态、执行、反馈、预算 | 失败后重规划、有限修订；与单循环比较 |
| [ToT / LLMCompiler](step3/stage3c-tot-compiler-learning.ipynb) | Stage 3 后的进阶支线，可延后到 Stage 7 | 候选评分 / 任务依赖 / 并发基础 | 搜索树与任务 DAG 分开实验；测成本与失败传播 |

Stage 4 **主线仍须认识 planner、executor、reviewer、critic、router 这些职责**；完整 Plan-and-Execute 或 Reflexion 算法实验属于拓展，两者不矛盾。`dispatcher` 是 Stage 1 主线必须解释的工具分发代码，不是新架构，也不要求先完成 ReAct 才能理解。

## 补充资料如何读

以下补充以解决当前阶段的问题为限，不要求换路线或把另一套课程全学完。

- Stage 0–1：对照 [Hugging Face Agents Course 的 Agent 定义](https://huggingface.co/learn/agents-course/unit1/what-are-agents)，画出模型、程序、工具和环境之间的一轮数据流。
- Stage 1–4 的策略拓展：参考 [Datawhale Hello Agents](https://github.com/datawhalechina/hello-agents) 的经典范式与实践部分。先完成本地对应 Stage，再用同一任务对比策略；原论文入口在 [架构笔记](step3/05-agent-architectures.md)。
- Stage 5：按 [技能宿主与效果验收](step5/01-skill-hosts-and-evaluation.md) 阅读上游明确要求的 Claude Code / OpenClaw 官方 Skills 文档。
- Stage 7：先分清格式正确、工具正确、事实正确和任务完成；再比较策略。离线替身成绩、LLM 自评和人工事实审核须分列。

## 维护与验证

主线验证：`python -m learning.verify_notebooks --offline --scope core`（9 本主教材 + Stage 2 完整实践）。拓展验证：`python -m learning.verify_notebooks --offline --scope extensions`（4 本）。省略 scope 则验证全部 14 本。结果记载 track，不混算课程完成率。

只同步说明与分类用 `python -m learning.sync_course_guidance`；它保留 Notebook 代码、输出和已保存的服务开关。验证器也只改执行副本。所有实际结果及限制见 [VALIDATION.md](VALIDATION.md)。
