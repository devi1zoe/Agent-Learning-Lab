# Practice Results｜课程缺口的实现与实跑

日期：2026-10-14。本页接续 [课程核对](COURSE-ALIGNMENT.md)：之前的“待补实践”已经补成脚本并进行了真实运行。主线仍是 Stage 0–8，架构专题仍是选修；学习者自己的阅读、判断和总结须自己填写。

## 先准备真实服务

本轮实际模型为 `qwen3:1.7b`（Q4_K_M），embedding 为 `qwen3-embedding:0.6b`（1024 维），Ollama 0.35.0，Python 3.9.13。新环境仍建议 Python 3.10+。模型 digest、请求、响应及 usage 写入每次结果，避免只记录一个会变化的模型名字。

```powershell
ollama serve
# 在另一个终端运行；已安装的模型无需重新拉取
ollama pull qwen3:1.7b
ollama pull qwen3-embedding:0.6b
python -m pip install -r requirements-learning.txt
python -m playwright install chromium
```

这些实践实际调用模型，失败就保存失败，不切换到 ReplayModel 冒充成功。Stage 2 的网页研究、Stage 3 首次下载、Stage 6 公开网页需要网络；离线教材验证不运行这些外部实验。

## 每步现在有怎样的作品

| Stage | 真实实践入口 | 本轮结果与证据目录 |
| --- | --- | --- |
| 1 | [103 行独立最小 agent](step1/minimal_agent.py)、[普通对话/JSON/工具循环入口](learning/course_practice.py) | 三种调用已实跑，12×34 工具结果为 408；`.learning_output/course-practice/stage1` |
| 2 | [现有诊断本的真实 RAG 实验](learning/stage2_live.py)、[公开文档搜索/阅读/报告](learning/research_lab.py) | 真实 embedding 检索和带来源回答完成；文件、SQLite、算术工具实际调用；`.learning_output/stage2-live`；逐句引用的联网报告在 `.learning_output/research-live-final` |
| 3 | [固定版本上游实验](learning/upstream_lab.py) | 实际执行上游 s02 原循环，注册 count_words；上游和裸循环都调用模型两次并正确返回 4，另保存单次调用预算失败；`.learning_output/upstream-lab-normalized` |
| 4 | [真实角色协作及压力实验](learning/coordination_lab.py) | 写作/审核完成；修订上限、任务 ID 漂移、错误 schema、300 字证据上限检查通过；`.learning_output/coordination-live-fixed` |
| 5 | [能力包发现/按需加载/效果对照](learning/skill_eval.py) | 6 题×2 条件共 12 次真实生成；固定自动评分无 skill 0/6、有 skill 5/6；`.learning_output/skill-eval` |
| 6 | [公开网页 browser agent](step6/public_agent.py) | 真实 Chromium 读取公开页面，模型请求读取并生成摘要，程序核验/提取原文片段；`.learning_output/public-agent-accepted` |
| 7 | [20 题真实 agent 评测](learning/live_evaluation.py) | 初版与修复后回归均为 16/20，4 个失败保留原回答与分类；当前 CSV/JSON/逐题 trace 在 `.learning_output/live-eval-current` |
| 8 | [交付验收](learning/delivery_check.py)、[CLI](learning/cli.py)、[具体操作审批](learning/approval.py) | 新 venv 不装第三方包，复制当前交付文件后离线/真实查询成功，无证据/超预算正确退出；批准/拒绝/改参数检查通过；`.learning_output/delivery-check-verified` |

各阶段统一入口：

```powershell
python -m learning.course_practice --stage 1
python -m learning.course_practice --stage 2
# 同样支持 3、4、5、6、7、8；按学习进度逐个运行
```

也可以直接执行表中的模块。不要为了看到绿色通过而无条件重跑整套联网实验；默认教材和离线回归用于日常维护。

## 怎样理解这些结果

**Stage 3：** 下载固定提交的 `s02_tool_use/code.py`，核验 SHA256 `fa6fdaa4e75ae4304507a96cb22adf98854f115509bec2ecc400f31c202ff19e`，保存上游 MIT LICENSE。保留原 `agent_loop` 和注册方式，通过明确的 API bridge 将内容块转换为真实 Ollama tool call。实验只开放计数工具，并在外层加调用数/时限；没有使用假的模型决策，也没有声称已部署完整 Claude Code。权限、记忆和压缩所在后续章节见 [固定版本导读](REFERENCE-WALKTHROUGH.md)。

有一次真实响应把动作写进 content 的 JSON，而未提供原生 tool_calls。适配层仅在完整对象恰好为 name/arguments、工具已注册时把这个**模型实际提出的动作**转成工具请求；原响应仍保存。普通 JSON 答案和工具不可见时不会执行。裸循环采用相同兼容方式；本轮对照仍各调用模型两次，另保存一轮预算导致的失败。

**Stage 5：** 固定评分器要求规范报告和指定事实。无 skill 的回答大多事实正确，但缺少约定章节/引用，因此报告任务未通过；不能解读成“模型一题事实都答不对”。冲突题已说“资料不一致”，却没有字面词“冲突”，被关键词 oracle 判失败：这是评分器误差，保留自动 5/6，同时记录来源审阅后的纠正。此结果说明本次小样本中的报告格式改善，不能推导普遍质量提升。宿主是项目内教学 `LocalSkillHost`，显式触发并按需读模板；它不是 Claude Code/OpenClaw 的产品安装记录。

**Stage 6：** 开始时真实模型给零参数工具额外添加 URL，随后又重复读页。工具接口改为明确的允许 URL，静态页面读取成功后关闭读能力以进入完成阶段。模型还把原文的 “This is not a service” 改写成 “It is not a service”，这能用于摘要，却不能当原文引号；程序拒绝该引文并按字符位置提取实际源文本。最终摘要已对照页面，没有沿用先前无来源的法律保证说法。公开页面只用于本次示例，日常测试使用本地 fixture。

**Stage 7：** 20 题使用真实模型与明确标为虚构的受控工具资料，覆盖正常、无证据、来源冲突、工具超时、注入。8 个正常、3 个工具故障、2 个注入均通过；无证据 3/4、冲突 0/3。失败不是删除或改答案后再打勾。成绩不等于开放互联网研究质量；每题期望、实际、usage、时延、失败类别齐全，后续可使用相同冻结任务回归。

**联网研究：** 初版通用搜索网页没有给出可解析链接，记录失败后改用官方站点的实时 sitemap 搜索，实际读取 `.md` 正文。这是特定官方站点的搜索，不冒充全网搜索服务。网页超大/超时、伪来源 ID 和句尾引用缺失都有记录；最终用结构化句子+程序化引用排版生成两句报告，使用的来源正文已保存。

**Stage 8：** CLI 会保留无引用的原始答案并在剩余预算内尝试一次引用修复，仍失败则非零退出。`--max-output-tokens` 限制每次生成，`--max-steps` 限制模型轮次；总输入+输出 token 仍在请求间检查。当前本地模型没有 API 美元账单，不声称有远程计费硬预算。干净环境验收使用当前未提交文件副本与新 venv，不是远程 git clone 或另一台硬件。

## 人工批准一份具体报告

```powershell
python -m learning.cli --live --question "Agent 与 workflow 有何区别？" --export-report .learning_output/my-report.md
```

先显示已生成报告、绝对目标路径和内容 SHA256，输入屏幕给出的完整 `APPROVE <SHA256>` 才创建文件。改参数、拒绝、已有同名文件或重复使用批准均不得覆盖。验收中使用程序化输入测试这三条路径，明确不把测试输入冒充真人批准。

## 初次学习仍需自己留下的记录

Stage 0 的一页场景判断、两篇阅读心得、各 step 的个人总结不由脚本代写。执行记录证明教材与作品可运行；你还需要解释一次成功、一次失败、为何选择该策略以及普通 workflow 是否足够。完成这些记录后再勾自己的课程任务单。
