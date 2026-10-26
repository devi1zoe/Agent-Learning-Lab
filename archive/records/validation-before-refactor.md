# Validation｜本次交付验证

## 2026-10-15：按阅读顺序重排九章

每个 Step 改为一页连续课程：分析题目与产出 → 推导实现思路 → 原有 Markdown 与 Notebook 逐步讲解/代码 → 运行验证 → 原课程验收与个人总结。取消内容标签切换；目录只滚动定位，实验按钮移到实现之后，原文与选修入口在章末。Step 1 的 dispatcher 在循环之前解释；Step 2 完整诊断本直接接在基础实验之后。代码高亮与原始复制保留。

新增 `learning/web_course.py` 保存九章的教学衔接和材料编排，不复制 Notebook 代码；原单元格编号、源文件与下载保持可追溯。Stage 1 原讲解中「默认跳过」与已保存 `RUN_LIVE=True` 不一致，已改为解释开关和网页离线副本的区别，未改代码或保存的开关。

本轮 `python -m unittest learning.test_web_learning` 6/6 通过，包含九章代码保留顺序、全部 50 项任务与来源引用检查。`python -m learning.check_web_ui --live` 17 项通过，无浏览器脚本错误：实际验证连续阅读、九章任务、目录不切页、旧链接定位、跨 Notebook 复制、进度/笔记持久化、离线内核运行、真实 Ollama 实践、代码高亮和手机无横向溢出。已查看桌面正文、dispatcher 讲解、完整研究 Agent 和 390px 手机阅读页截图；产物在 `.learning_output/web-qa/`。以下网页记录是先前版本的验证。

## 2026-10-15：本机网页学习站

代码阅读新增本地 Highlight.js 语法高亮与深绿配色，Notebook / Python 源码和 Markdown 标注语言的代码块均启用；额外加载 PowerShell 语法。实际浏览器检查确认 Python 关键词/字符串着色、复制保持原始代码（兼容 Windows 换行），Markdown PowerShell 围栏正确着色。当前无模型 UI 回归共 11 项通过，无脚本错误；依赖与许可证保存于 web/vendor，不依赖运行时 CDN。

新增网页首页、九阶段路线、四组拓展、完整资料与源码阅读、概念搜索、目录/上一课/下一课、任务与个人笔记持久化、Notebook 下载、交互式循环演示，以及本机实验运行入口。所有课程正文从现有 Markdown / Notebook 提取，生成目录不作为另一份教材维护。

网页提供两类明确按钮：默认离线 Notebook 独立内核执行；主线 Stage 1–8 的真实实践脚本（连接本机 Ollama，指定阶段还会访问公开资源）。实验输出直接显示，关闭窗口后可恢复查看；原始 Notebook 不覆盖。学习进度只由自己标记，不能用程序执行通过代替。

实际检查：`python -m unittest learning.test_web_learning`，5/5 通过；`python -m learning.check_web_ui --live`，10 项交互检查通过且无浏览器脚本错误，包含真实离线内核运行与真实 Ollama 实践按钮。桌面、阅读页、实验窗口和 390px 手机页面已截图检查，结果在 `.learning_output/web-qa/`。

本机执行边界同时检查：任意代码/路径拒绝、未知模式拒绝、非本页请求拒绝、错误 Host 拒绝、目录列表拒绝。单进程一次只运行一个课程实验；不提供任意代码在线编辑或公网执行服务。Windows 端口重复绑定已禁用，重复启动会识别并复用现有学习站。

新增 `web/dist` 属于生成目录、vendor 属于第三方依赖，课程材料审查排除它们的重复副本，再检查原始 20 本 Notebook、相对链接及代码语法。网页构建本轮收录 127 份原始学习材料和辅助文件；新增材料后这个数量会自动变化。

仅在用户本机运行，没有部署到外部站点。启动和维护说明见 [web/README.md](web/README.md)。

---

## 2026-10-14：实践缺口补齐与真实运行

先前课程核对列出的实现缺口已新增可运行脚本，统一入口 `python -m learning.course_practice --stage N`（N=1–8），并连接本机实际 Ollama。原始模型请求/响应、digest、usage、浏览器观察、逐题表格及失败记录保存在 `.learning_output/`。逐项入口和范围见 [PRACTICE-RESULTS.md](PRACTICE-RESULTS.md)。

| 实践 | 实际结果 |
| --- | --- |
| Stage 1 普通对话、JSON、103 行独立循环 | 真实调用完成，工具计算 12×34=408 |
| Stage 2 既有 RAGStore / ResearchAgent | 真实 1024 维 embedding、检索、带引用回答；文件/SQLite/受限算术实际运行 |
| Stage 2 搜索→筛选→读页→报告 | 实时官方站点 sitemap 搜索，读取官方 Markdown 正文，最终报告逐句引用；保留前几次搜索/网络/引用失败 |
| Stage 3 固定上游循环 + 自定义工具 + 裸循环对照 | 原循环通过真实 API bridge 执行，两条路径均返回正确计数；另保存单次调用预算失败 |
| Stage 4 写作/审核与边界实验 | 真实角色调用完成；停止、任务 ID 漂移、非法 schema、证据长度上限检查通过 |
| Stage 5 有无 skill 对照 | 6 题双条件、12 次真实生成；报告任务自动评分 0/6→5/6，冲突题有明确评分器误判，未改写原始分数 |
| Stage 6 公开网页 agent | 真实 Chromium 读取→模型摘要→原文定位完成；原文引号的改写被拒绝后由程序提取源文本 |
| Stage 7 真实评测及修复后回归 | 均为 16/20，4 个失败完整保留；真实模型配受控虚构工具资料，独立于离线 27 项 |
| Stage 8 新 venv 与 CLI | 无第三方包的环境实际跑离线/模型/无证据/预算退出；创建报告的批准/拒绝/改参数检查完成 |

维护检查：10 本主线与 4 本拓展 Notebook 离线独立内核通过；`learning.test_course_labs`、`learning.test_integrations`、`learning.test_architecture_lessons` 共 15/15 通过；固定契约回归 27/27。全仓相对链接、Notebook 格式、Python 和 73 个教程代码格语法检查通过，50 项任务编号和 9 项产出对应完整，代码/输出与用户服务开关保持。源材料清单在 `.learning_output/course-audit.json`。

没有把模型失败或评分器误判算成成功；没有把教学 SkillHost 说成产品宿主安装，没有把新 venv 当前代码副本称为远程 clone/跨机器部署。总 token 仍是请求间软检查；单请求输出上限和轮次上限已设置，本地 API 美元账单不适用。个人阅读心得与阶段总结仍由学习者完成。

公开网页 observation-1.png 已查看，页面原文与最终摘要/程序提取片段一致；额外使用不存在的本地 fixture 验证导航失败能记录 failed 并非零退出，不把它计作公开网页成功。先前“无结果”用例因为含中文检索词而误召回，改用不匹配的固定英文词；新 venv 检查曾暴露相对 --output 在子进程工作目录下失效，路径已统一解析为绝对值后验收通过。

以下是同日早先的核对及历史记录，先前“未运行真实模型”等描述对应当时范围；当前实践状态以上面的结果为准。

---

## 2026-10-14：按上游课程重新对齐

依据 Agent Learning Hub 提交 `dddf777dde6788228136862f270203424a28efbc`，新增 [课程核对](COURSE-ALIGNMENT.md) 与 9 份 COURSE-TASKS，逐项对应 50 个学习任务及 9 个阶段产出。课程有材料不等于学习或实跑完成，具体缺口保持未完成状态。

主线恢复 Stage 0–8，四本架构专题明确为选修拓展；Stage 2 完整诊断本属于主线实践。主线/拓展分类同步到 README、前置知识、Notebook 导航及生成器，Stage 4 不再要求先学 Step 3B。补充 Stage 5 宿主加载与效果对照方法，其他缺失实践写成可执行的验收任务，不伪造运行结果。

本轮实际执行：

| 验证 | 结果 | 能说明什么 |
| --- | --- | --- |
| `python -m learning.verify_notebooks --offline --scope core` | 10/10 通过 | 9 本主教程 + Stage 2 完整实践能离线运行；Stage 6 实际启动本地 Chromium |
| `python -m learning.verify_notebooks --offline --scope extensions` | 4/4 通过 | 拓展中的控制流、失败路径与断言可运行 |
| `python -m unittest learning.test_integrations learning.test_architecture_lessons` | 9/9 通过 | 模拟 provider 接线和真实本地浏览器集成；不证明模型质量 |
| `python -m learning.evaluation` | 27/27 通过 | 固定 runtime 契约回归 |
| 材料静态检查 | 107 个源材料/配置文件纳入清单；69 份 Markdown、20 本 Notebook | 文档和 Notebook 相对链接无缺失；全部 Notebook 格式有效；73 个教程代码格及 Python 文件语法检查通过 |
| 对齐/保留检查 | 50 项编号、9 项产出、10 本 core、4 本 extension、6 本原有实验 | 导航同步幂等；Notebook 代码/输出保留；Step 1 保存的 RUN_LIVE=True 未改 |
| `git diff --check` | 通过 | 无空白错误；Git 提示部分旧文件的 LF/CRLF 转换策略 |

按范围的执行记录为 `.learning_output/executed/verification-core.json` 和 `verification-extensions.json`；`verification.json` 始终代表最近一次命令范围，不能据它推断其他范围本轮失败或未运行。材料清单与静态核对结果在 `.learning_output/course-audit.json`，这些产物不提交。

本轮没有重跑真实模型/embedding/外部 SDK、部署上游 harness 或验证公开网页 agent，也没有运行真实 skill 效果对照与干净环境交付。具体待办见课程核对和各章任务单；后续历史记录不应覆盖这些限制。

---

## 2026-10-14：新手术语与架构补充

本次新增 4 本策略专题和 9 份章节前置解释。完整变更理由见 [LEARNING-AUDIT.md](LEARNING-AUDIT.md)，推荐学习顺序见 [BEGINNER-GUIDE.md](BEGINNER-GUIDE.md)。

运行 `python -m learning.verify_notebooks --offline`：13 本主线/策略教程，加 Stage 2 完整本，共 14 本独立 Kernel 执行通过。新增专题内的成功/失败/预算断言均执行；Stage 6 仍运行真实本地 Chromium。Step 2 完整本的 30 项离线测试通过。

新增 `python -m unittest learning.test_architecture_lessons`：4/4 通过，四本专题的可选在线分支均用明确标记的决策替身运行，检查接线与控制流。原有 5 项集成测试和 27 项固定回归也通过。

首次按保存配置运行时，Step 1 中用户保存的 RUN_LIVE=True 访问本地服务失败。该配置保留；新增 --offline 仅在执行副本中置 False，并在 verification.json 记录覆盖位置。没有把这次失败计为真实模型成功，其他可选 LLM 分支也没有声称经过真实模型质量验收。

检查了 Markdown/Notebook 相对链接、格式、UTF-8 与新增代码语法。新版生成器读取章节前置说明；另有 `learning/update_learning_guidance.py` 只更新解释单元格，保留已有代码和输出；`learning/build_architecture_notebooks.py` 只重建四本新专题，重建前应另存个人练习。

以下为 2026-09-29 的历史验证记录，数量与旧命令描述以当时范围为准；当前自动验证建议使用上面的 --offline 命令。

---

验证日期：2026-09-29。本文描述已执行的范围，不把教程编写完成等同于真实模型能力通过。

## 环境

Windows，实际验证 Python 3.9.13，nbformat 5.5.0、nbclient 0.5.13、ipykernel 6.15.2、Playwright 1.50.0、Chromium 133.0.6943.16（Playwright build 1155）。新安装建议使用 Python 3.10+；没有升级用户现有 Python。为本次浏览器验证下载了对应的 Chromium 与 headless shell。

## 交付与要求对应

| 用户目标 | 交付证据 | 验证方式 |
| --- | --- | --- |
| 按路线一点点学习 | step0–step8 各一本 stageN-learning.ipynb | 每本包含中文解释、代码、断言、练习和自检 |
| 尽量用 ipynb | 9 本新教程，加保留的现有实验 | nbformat 校验、代码编译、独立内核顺序执行 |
| 专门解释参考仓库每一步 | REFERENCE-WALKTHROUGH.md | 核对 4 个参考仓库提交与源码入口，Stage 对应及 s01–s17 逐章说明 |
| 接近现有仓库格式 | stepN/、README、04-my-takeaways、中文内容/英文标题 | 对照原有 Stage 0/1 风格；保留现有实验与个人笔记 |
| 从例子走向可运行项目 | learning/runtime.py、cli.py、Stage 8 | 正常查询与无证据退出路径均实际执行 |
| 评估表与失败记录 | Stage 7、evaluation.py | 27 项固定任务包含期望/实际、失败分类、次数与统计 |

## 已执行的检查

```powershell
python -m learning.verify_notebooks
python -m learning.evaluation
python -m unittest learning.test_integrations
python step6/browser_demo.py
```

- 9 本新 Notebook 均从新 Kernel 自上而下执行通过；Stage 2 原完整本的默认离线路径也通过。
- 完整 Stage 2：30 项测试，0 failure、0 error。
- 新 runtime 固定回归：27/27 通过。
- 集成测试：5/5 通过，验证模型角色交接、真实浏览器重复观察、暂时性网络错误重试、HTTP 400 不重试、Ollama 请求/返回适配。
- 浏览器：实际启动 Chromium，先制造定位超时，再处理弹窗、点击和提取可见证据。已查看 after.png，文字完整可读。
- 公开网页模式曾单独读取 example.com 并保存正文/DOM/截图；它不是固定回归依赖，后续无需重复访问。
- research-report 能力包通过 skill-creator 的 quick_validate；报告 smoke test 检查不合格/合格输出。
- 检查新 Notebook 的 UTF-8、代码语法、文档相对链接；git diff --check 无空白错误。

`learning.test_integrations` 对可选模型分支使用明确的假 provider，同时浏览器仍是真实 Chromium。它证明接线与状态更新，不证明 LLM 理解或判断正确。

执行副本和逐本结果保存在 `.learning_output/executed/`，评测 CSV/JSON 在 `.learning_output/eval/`，浏览器产物在 `.learning_output/browser/`。这些目录被 git 忽略，可重跑生成。

## 未声称已验证的部分

本机 127.0.0.1:11434 的 Ollama 服务未运行。因此没有把真实模型、真实 embedding、多角色推理质量、模型驱动浏览器任务或真实网页研究记为通过。相应代码和运行步骤已提供，默认关闭；启动服务后按 Notebook 的 RUN_LIVE / RUN_LIVE_AGENT 运行，并人工核对答案。

旧 Codex SDK、MCP 和 Ollama 实验保留，本次未重新认证或运行。上游项目用于源码学习，没有整体部署；课程不承诺复刻所有参考仓库或 Project Ladder 的全部选修产品。

引用检查证明编号可追溯，不证明语义蕴含；离线 token 为 0，费用为空；同步工具没有通用硬中断机制。没有将本地 CLI 标记为生产服务。

## 如何继续维护

日常学习直接编辑 Notebook。`learning/build_notebooks.py` 是初始教程生成器，重新运行会覆盖九本新教程，已有个人笔记请先保存到独立文件。验证器只写 `.learning_output/`，不会覆盖课程 Notebook。

新增工具后运行固定回归；修改角色或浏览器接线后运行集成测试；修改 Notebook 后用干净 Kernel 执行相应课程。不要把保存下来的旧输出当成新代码验证结果。
