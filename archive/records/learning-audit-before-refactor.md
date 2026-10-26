# Learning Audit｜新手视角的检查与补充

日期：2026-10-14。目标是让概念先于使用出现，并补齐策略学习线。不是把原有个人研究笔记全部改写成入门教材。

后续课程对齐以 [COURSE-ALIGNMENT.md](COURSE-ALIGNMENT.md) 为准：保留主线 Stage 0–8，四本策略课明确改为选修拓展；原先“必修加餐”和“先学 3B 再进 Step 4”的安排已撤销。下面记录术语审查，不代表上游 50 项课程任务全部完成。

## 审查范围与处理原则

扫描根目录、step0–step8 的 Markdown 和 Notebook 解释单元格，并检查主线代码中对应术语的实际职责。重点检查：首次出现是否有解释、前置依赖是否清楚、方法是否混淆、示例是否真能运行、失效路径/命令是否误导、模拟和真实模型是否区分。

已有 SDK/Ollama 原始实验只新增阅读说明并保留代码与个人输出；主线 Notebook 在第一段之后新增前置解释。`step2/docs` 的论文材料和 `step7/agent_permission_research` 属于选修语料/研究设计，保留正文。对这些文件做术语和层级检查，不声称重新核验了每篇论文或重做研究实验。

## 发现的问题及修改

| 原位置/问题 | 为什么影响新手 | 本轮修改 |
| --- | --- | --- |
| Step 1 的 Dispatcher 出现在流程图与部件表 | 看不出是模型、库、算法还是一个函数 | Step 1 前置说明加“字典→取函数→传参”代码；1B Notebook 亲手写分发器与失败测试 |
| Step 1 图把“参数和权限”对应到 JSON Schema | 容易误以为格式符合就代表获准 | 分成参数校验器、权限门、分发与执行；已有正文就地修正 |
| Step 0 一开始使用 AST/CFG | 非代码分析读者不知道是否需要先学编译器 | 首次使用展开名称，标注选修；提供“查资料/算数字”的替换理解方式 |
| Step 0 的 Harness、ReplayModel、call、final 是辅助黑盒 | 没学循环就看到多个类，易误以为每个都要安装 | 先解释各自作用和首次只观察的范围，Step 1/3 分别展开 |
| Step 2 chunk/embedding/cosine/top-k 缺完整前置链 | 会运行向量代码却不知道分数意味着什么 | 增加从原文块到向量、检索、引用的定义与反例 |
| RAG 与 Self-Ask 缺连接 | 不知道复杂问题如何变成多次检索 | 新增 2B，两跳事实、证据链、空证据和错误引用实验 |
| 原教程主要有工具工程，缺决策策略地图 | 容易把所有架构等同于同一个 while loop | 新增学习导航、架构比较、4 本策略专题与原始来源 |
| Reflection / Reflexion 容易混用 | 反复改稿、模型自评、跨尝试经验不是同一机制 | 3B 分开解释 Self-Refine、一般反思、Reflexion 风格记忆，并演示评价器盲点 |
| ToT 与 LLMCompiler 都有图 | 容易把候选搜索、依赖调度、多 agent 当作同义词 | 3C 分别运行搜索树和 DAG，比较节点、边、预算与失败 |
| Step 3 adapter、callback、compaction；Step 4 supervisor | 阅读代码前不知道各层负责什么 | 各章前置词表和职责表，区分规划、分发与监督 |
| API adapter 与研究中的模型 adapter 同名不同义 | 基础接口包装和模型内部模块可能混淆 | 术语表及研究 README 显式区分；研究区标为选修 |
| Step 5 handshake/transport/JSON-RPC；Step 6 fixture/DOM/locator | 未解释的缩写形成新的门槛 | 补通信双方、消息格式、可控页面、当前页面状态与定位定义 |
| Step 7 baseline/消融/成本比较不充分 | 可能用更多调用换来的成功率直接宣称架构更好 | 加固定任务、模型/工具预算、数据划分、失败分类与引用语义评价 |
| Step 3 说相同参数总返回 duplicate_call | 忽略 repeatable 观察工具和环境变化 | 说明默认去重与可重复读取的区别 |
| Step 6 说“重试一次” | 实际先用旧定位器，再换新定位规则 | 改成故意失败→重新定位，与盲目重试区分 |
| 完整 Step 2 说明仍称“7 个工具” | 与实际 schema 表不一致 | 以紧随的 TOOL_SCHEMAS 为准，不写过时固定数量 |
| SDK 阅读入口还给出已迁移的 .py 命令 | 新手照抄会找不到文件 | 导向当前 .ipynb，移除失效运行清单；未宣称复验 SDK API |
| 已有 Step 1 保存着 RUN_LIVE=True | 一键验证会访问尚未启动的服务 | 保留用户设置；验证器增加 --offline，只改执行副本并记录覆盖 |

## 新增的学习交付

- [BEGINNER-GUIDE.md](BEGINNER-GUIDE.md)：课程主线/选修拓展、架构比较和每个方法要问的问题。
- [GLOSSARY.md](GLOSSARY.md)：按学习阶段组织术语，配代码位置与常见混淆。
- 每个 step 的 `00-prerequisites.md`：定义、前置依赖、自检与参考答案，并插入主 Notebook 的代码之前。
- [Step 1B](step1/stage1b-react-learning.ipynb)：分发器与 ReAct；错误反馈、不同观察下不同动作、预算。
- [Step 2B](step2/stage2b-self-ask-learning.ipynb)：Self-Ask；来源链、缺证据、重复提问、引用格式盲点。
- [Step 3B](step3/stage3b-planning-reflection-learning.ipynb)：Plan-and-Execute、重规划、反思、经验复用。
- [Step 3C](step3/stage3c-tot-compiler-learning.ipynb)：ToT 候选搜索、算术候选与 LLMCompiler 风格 DAG 调度。
- [架构阅读笔记](step3/05-agent-architectures.md)：准确名称、原论文/作者实现、本地实现边界。

四本专题都提供可选 Ollama 分支。默认策略替身不是模型；实际执行的是控制流、工具、搜索和调度。静态 DAG 示例不等于完整 LLMCompiler，规则评分反思不等于论文 Reflexion 成绩。真实模型的好坏需按 Step 7 单独评估。

## 验证方式与覆盖

```powershell
python -m learning.verify_notebooks --offline
python -m unittest learning.test_architecture_lessons
```

第一条将 13 本主线/专题和 Stage 2 完整本放入独立 Kernel 执行，保留结果到 `.learning_output/executed/`。`--offline` 仅在副本中关闭显式服务开关；不会跳过离线断言，Stage 6 本地 Chromium 仍实际运行。verification.json 记录每本状态和覆盖的开关。

第二条专门让四本专题的在线分支接“决策替身”运行：验证模型输出怎样进入动作、子问题、重规划、反思记忆、搜索与任务调度，不访问模型服务，也不能当真实推理成绩。

此外检查相对链接、Notebook 格式/UTF-8/语法，保留原有固定回归与集成检查。本次真实 Ollama 服务连接被拒绝，未声称通过真实模型测试。最终运行结果见 [验证记录更新](VALIDATION.md)。

## 以后新增课程内容的约定

术语首次出现给出中文职责和一个具体例子；先教数据流再引入框架名字；每个方法至少有成功、失败、预算或边界实验；说明模型与程序谁负责哪个决定；引用原始来源并标明教学简化。生成器只用于重建对应教材，不能覆盖用户正在写的学习记录。
