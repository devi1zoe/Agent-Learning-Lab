# MiniAgent：看懂模型与运行程序怎样配合

本仓库保存 Agent 基本机制的实现、实验与学习记录，包含 22 本主线 Notebook，覆盖模型调用、工具循环、检索记忆、运行控制、协作、Skill、浏览器及评估。真实模型记录、固定回放与未执行分支在正文中分别标明。

**唯一学习入口：[从一条任务看懂 Agent](00-foundations/01-what-is-an-agent.ipynb)。**

你已经熟悉 LLM 和训练，可以直接研究一个问题：模型只生成输出，为什么一段输出能变成读取文件、运行工具，再影响下一次生成？这套 Notebook 用“查资料并回答问题”解释这条链路。先跟完一次运行，再了解更多架构。

## 第一遍只学这四步

| 顺序 | 必学内容 | 动手做什么 |
| --- | --- | --- |
| 1. 看懂一次运行 | [模型提出请求，程序执行工具](00-foundations/01-what-is-an-agent.ipynb) | 先看 `papers.csv` 的教学例子，再读已保存的真实请求、工具返回和下一次输入 |
| 2. 看懂保留哪些消息 | [最小循环](01-agent-loop/01-minimal-loop.ipynb) | 观察 `messages` 如何加入用户问题、模型请求与工具结果；用可核对的算术结果检查循环 |
| 3. 看懂失败与停止 | [运行程序怎样管理循环](03-agent-harness/01-harness.ipynb) → [如何判断任务完成](07-evaluation-safety/01-contract-evaluation.ipynb) | 找到拒绝、错误、重复调用和预算分支，解释模型停止为什么不等于任务答对 |
| 4. 改一条规则并验证预测 | 回到[最小循环的预算练习](01-agent-loop/01-minimal-loop.ipynb#change-one-rule) | 把工具次数上限从 2 改为 1，先预测未知工具请求会不会占次数，再对照实际消息 |

第一遍不需要重新调用模型。`ReplayModel` 是按预写顺序返回消息的替代对象，用于检查程序；首课的历史记录则来自保存下来的真实模型运行。两者各自说明什么，页面中会直接标明。

读完后，拿一条工具记录回答：模型当时看到了什么、提出了什么、程序执行了什么、结果怎样进入下一次请求、为什么停止。再去 [codextimeline](https://github.com/devi1zoe/CodexTimeline/blob/main/README.md) 对照 Codex 的记录格式和源码；先读其中的 [真实搜索与阅读案例](https://github.com/devi1zoe/CodexTimeline/blob/main/codex-rollout-atlas/docs/HARNESS_CASES.md#real-run)，再比较 Codex 的审批、压缩、记忆与调度实现。基本循环仍按这里的四步学习。

## 理解循环以后再看

按自己要研究的机制选择，不必把全部 22 本当成一条必修长课。

| 想追的问题 | 阅读位置 |
| --- | --- |
| 实际模型接口怎样发送和解析消息 | [真实模型请求](01-agent-loop/02-live-model.ipynb) |
| 资料怎样进入上下文，记忆怎样跨轮保留 | [检索与记忆](02-tools-rag-memory/01-rag-and-memory.ipynb) → [研究助手实现](02-tools-rag-memory/02-research-agent.ipynb) → [本地与联网案例](02-tools-rag-memory/03-web-research.ipynb) |
| 换一个运行框架，工具注册与返回形式怎样变化 | [上游循环对照](03-agent-harness/02-upstream-comparison.ipynb) |
| 为什么需要分角色，交接会丢什么 | [协作流程](04-multi-agent/01-coordination.ipynb) → [真实角色交接](04-multi-agent/02-live-coordination.ipynb) |
| 方法说明怎样被发现、加载和复用 | [Skill 与工具协议](05-skills-protocols/01-skills-and-protocols.ipynb) → [有无 Skill 的结果](05-skills-protocols/02-skill-comparison.ipynb) |
| 浏览器观察与动作怎样配合 | [本地页面](06-browser-agent/01-browser-basics.ipynb) → [公开网页案例](06-browser-agent/02-public-page-agent.ipynb) |
| 实际模型为什么失败 | [20 题历史结果](07-evaluation-safety/02-live-evaluation.ipynb) |
| 怎样把所学组合成独立命令行程序 | [研究助手](08-capstone/01-research-assistant.ipynb) → [独立进程运行](08-capstone/02-delivery-check.ipynb) |

ReAct、规划、反思、候选搜索等方法放在首课末尾的可选地图中，需要时再读对应的 [ReAct](01-agent-loop/03-extension-react.ipynb)、[Self-Ask](02-tools-rag-memory/04-extension-self-ask.ipynb)、[规划与反思](03-agent-harness/03-extension-planning-reflection.ipynb)、[搜索与依赖调度](03-agent-harness/04-extension-tot-compiler.ipynb)。先问它改变了哪一步，再记方法名称。

面向 Agent RSI 安全时，可以沿这条机制链继续追问：修改后的方法或代码在哪里进入下一轮输入？旧约束怎样保留？谁检查修改和操作范围？这一课程提供观察这些位置的基础，没有进行 RSI 实验，也没有证明某种自改进方法安全。

## 打开与运行

阅读正文和现有输出不需要启动模型。需要运行课程时，使用 Python 3.10+ 和已配置好的 Notebook 环境；项目依赖列在 [requirements.txt](requirements.txt)，辅助导入由 [miniagent_course.py](miniagent_course.py) 提供。需要另行准备环境时可参考下面的命令。

```bash
python -m pip install -r requirements.txt
python -m jupyter lab
```

先读当前页“代码说明”，再决定运行哪些单元格。真实模型分支用 `RUN_LIVE` 或 `RUN_NEW_MODEL_CALLS` 控制，默认关闭；浏览器基础页即使不开模型也会启动 Chromium；最后一页会生成独立项目和新环境。不要在不了解这些行为时对整套课程执行“全部运行”。

## 怎样理解已有结果

课程保存了 2026-10-20 的 CPU 模型运行：生成模型为 Qwen3-0.6B，向量模型为 MiniLM。首课中的程序提示模型读取指定资料，之后答对原课程的评测阶段，但仍缺引用；这条记录适合看清反馈路径。其他章节也保留失败：Skill 两组完整任务均为 0/6，固定评测为 9/20。它们属于特定任务与配置，不是通用能力结论。

正文中的 `Stage 7` 等字样若出现在历史问题、原始答案或上游资源中，指当时的课程名称；保留它们是为了让记录与原文对应。现在的阅读路线以上面的四步为准。

教学代码和必要资源保存在 Notebook 内。大段历史记录和第三方源码默认折叠，来源与许可证随资源保留；[archive/](archive/) 保存原始材料与旧记录，无需作为另一套课程阅读。运行时的新产物写入 `archive/runs/`。读取旧记录不是重新运行模型，程序测试通过也不是学习者已经掌握。
