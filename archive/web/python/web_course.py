"""Compose a continuous lesson from existing sources, with a short teaching bridge.

This is reading order, not a second copy of the notebooks. Referenced cells retain
their source and index so highlighting, copying and downloads use the same code.
"""
import re


PLANS = [
    {
        "question": "同样是回答「12 × 34 等于多少」，为什么有的程序只是脚本，有的却叫 Agent？",
        "analysis": "先别急着接模型。这个题目的输入和运算规则都是确定的，普通函数已经足够。我们故意用同一道题比较三种执行方式，排除任务差异，观察到底是谁决定下一步。最后再选择一个真正需要根据反馈改变行动的场景。",
        "deliverable": "一份自己的场景判断：用户是谁、哪里存在不确定性、普通流程能做到什么、什么反馈会改变下一步。",
        "thinking": "先写最简单的乘法函数作为基线；再把「提出工具请求」和「实际执行工具」拆开，跟踪结果怎样回到下一轮。最后用这个区别判断自己的场景。计算器只是观察控制流程的放大镜，不是为了证明乘法需要 Agent。",
        "flow": ["确定任务", "普通函数基线", "观察工具反馈", "判断是否需要 Agent"],
        "recap": "先问下一步能否提前写死，再决定是否引入 Agent。模型负责提出请求，程序负责执行，环境提供反馈；回放能演示这条链，不能证明模型具有决策能力。",
        "next": "下一章把今天看到的反馈循环拆开，亲手写出工具分发和循环退出。",
    },
    {
        "question": "怎样让模型通过计算器回答「12 × 34」，并且能证明它真的调用过工具？",
        "analysis": "只得到「408」还不能说明工具被执行了。我们需要同时看到模型的请求、函数收到的参数、工具结果回传的消息，以及循环结束的原因。还要考虑模型选错工具、参数不合法、一直不停止的情况。",
        "deliverable": "一个能运行的最小循环，以及正常调用、错误反馈和停止条件的真实记录。",
        "thinking": "从普通 Python 函数开始，再用 schema（接口约定）向模型说明参数。模型提出请求后，由 dispatcher（工具分发器）按名字找函数、组织校验和执行；把结果追加到 messages（消息历史），模型才有依据继续。先用可重复的响应检查程序，再换真实模型，避免同时排查两类问题。",
        "flow": ["函数与 schema", "模型提出请求", "分发、校验、执行", "结果写回消息", "继续或停止"],
        "recap": "工具名和参数是一份请求。schema 是接口约定，校验器落实约定，dispatcher 组织分发，函数完成执行；messages 和停止上限把它们连成闭环。",
        "next": "下一章给这个循环接上文档、检索与记忆，让回答能带着证据。",
    },
    {
        "question": "给助手几份学习笔记，它怎样根据原文回答问题，并在没有证据时停下来？",
        "analysis": "把全部文档塞给模型很难定位错误。先拆成资料处理、检索、回答、引用检查四个环节，分别观察输入和输出。还要分清搜索摘要与已读正文、当前对话与长期记忆。",
        "deliverable": "一条可追溯的资料链；再完成联网研究，保留真实来源、正文片段、引用及失败记录。",
        "thinking": "先用三段短文和能手算的向量看清原理，再逐步替换为真实 embedding 与完整 ResearchAgent。切块时保留位置，检索时允许空结果，生成后核对每条引用。记忆单独验证生命周期，不把保存过的信息误当作事实证据。",
        "flow": ["文档切块", "向量与索引", "检索证据", "生成并核对引用", "接入完整研究助手"],
        "recap": "检索分数、引用格式与事实正确是三个不同检查。主实验的词汇向量用于解释机制；完整诊断本和真实实践才连接 embedding、网页与模型。",
        "next": "下一章把这些能力放入统一的 Harness，管理权限、预算、状态和日志。",
    },
    {
        "question": "最小循环已经能用工具了，为什么还需要 Harness？",
        "analysis": "当工具能保存笔记、历史越来越长、请求可能重复时，「循环能跑」还不够。要能回答谁批准了写入、为什么停止、出错在哪一层，以及压缩后还能找回哪些证据。用同一任务对比，才能看清新增控制的价值。",
        "deliverable": "本地与上游实现的对应说明，一次真实上游运行，以及自己增加工具后的成功和拒绝记录。",
        "thinking": "沿模型调用 → 工具分发 → 提前返回的路径读代码，不从第一行背类定义。每次只验证一个不变量：拒绝前不能写入、错误必须可定位、预算必须能停止、进行中的工具请求与结果不能被压缩拆开。再对照上游实现看差异。",
        "flow": ["定位调用入口", "读 trace", "验证权限门", "管理会话和上下文", "测试失败路径"],
        "recap": "Harness 围绕模型管理执行。规划、反思等策略可以放在其中，但策略不能替代权限、预算和状态检查。trace 是运行证据，不是模型内部思维。",
        "next": "下一章才把任务交给多个角色，观察交接与协调增加了什么成本。",
    },
    {
        "question": "把研究、写作、审核分给不同角色，真的比一个助手更好吗？",
        "analysis": "先固定同一个带引用的写作任务。每个角色需要拿到什么、交出什么？审核不通过时由谁安排修订？如果永远不通过怎么办？这些问题比角色数量更重要。",
        "deliverable": "一条 research → write → review → revise 的交接记录，并与单 Agent 基线比较质量和成本。",
        "thinking": "先定义状态和输入输出契约，再让 supervisor 控制转移。第一稿故意漏引用，观察驳回与修订，随后验证没有证据和修改次数耗尽的停止路径。默认角色函数让流程可重复，最后再替换为真实模型调用。",
        "flow": ["证据交接", "生成草稿", "审核问题", "有限修订", "与单角色比较"],
        "recap": "角色是职责，不等于模型或线程。协作是否有效取决于交接信息、外部验收与停止规则，多个角色一致同意也不能代替事实证据。",
        "next": "下一章把反复使用的研究流程封装成 Skill，再区分不同协议的边界。",
    },
    {
        "question": "怎样把「写一份有证据的研究报告」变成可复用、可检查的能力？",
        "analysis": "先明确哪些经验可以复用：何时使用、按什么步骤做、采用什么模板、怎样验收。写好说明不等于宿主会自动发现它，格式检查通过也不等于模型表现变好了。还需分清能力包与外部工具协议。",
        "deliverable": "一个包含说明、模板与检查器的 Skill；保留发现或手动加载记录，以及同条件有/无 Skill 的效果对照。",
        "thinking": "先阅读现有 research-report 能力包，再用好坏报告验证检查器。然后固定模型、资料、任务与预算做成对实验。最后观察 MCP 的发现与调用消息，把「任务怎么做」和「跨进程怎样调用」分开。",
        "flow": ["说明与模板", "检查报告", "比较加载效果", "理解工具协议"],
        "recap": "Skill 封装工作方法，Tool 提供动作，MCP 连接工具接口；A2A 与 ACP 面向另外的协作边界。手动读取文件、宿主自动发现、模型效果提升必须分别留证据。",
        "next": "下一章让工具进入真实浏览器，处理可变化的页面状态。",
    },
    {
        "question": "页面要点击后才显示证据，助手怎样找到内容，并在按钮改名后正确停止或修复？",
        "analysis": "HTTP 返回成功并不保证获得页面当前内容。需要浏览器执行 JavaScript，观察 DOM，选择动作，等待变化并再次观察。固定脚本与模型选择动作也要在同一环境里区分。",
        "deliverable": "可控页面与公开网页上的运行记录，包含当前 DOM、截图、动作日志，以及一次定位失败的解释。",
        "thinking": "先读课堂页面，知道点击前后有什么差别，再运行 Playwright 验证动作。故意让旧定位器失效，检查程序是否根据新观察修复。最后把读取和点击包装为受控工具，由模型选择下一步。",
        "flow": ["观察页面", "定位与点击", "等待状态变化", "重新读取", "保存操作证据"],
        "recap": "定位器依赖当前页面。操作后要重新观察；页面成功加载、内容成功提取、最终事实正确应分别验收。Playwright 执行动作，模型参与与否决定了这里是固定流程还是动态循环。",
        "next": "下一章用固定任务评估这些系统，避免只挑一次成功演示。",
    },
    {
        "question": "改了提示词、Skill 或架构之后，怎样知道系统真的变好了？",
        "analysis": "先写任务和成功标准，再运行系统。正常回答、证据不足、工具失败、越权、提示注入都要计入分母。正确拒绝应该得分；脚本顺利结束不等于每个模型任务都成功。",
        "deliverable": "至少 20 个固定任务的结果表、真实模型输出与失败分类，并能从 trace 定位具体问题。",
        "thinking": "先用确定性测试检查 runtime 契约，再在同一任务集运行真实模型。保留答案、引用、耗时、调用量与失败原因；比较方案时固定模型、资料和总预算。挑一次攻击查看执行边界，但不据此声称所有攻击都被解决。",
        "flow": ["固定任务与标准", "运行基线", "保存结果", "分类失败", "同条件比较"],
        "recap": "测试通过说明覆盖的行为符合约定；真实模型成绩说明这组任务上的表现。格式、事实、权限和预算要分别检查，质量提升也要同时报告成本。",
        "next": "最后一章把配置、错误处理、产物和运行说明一起交给新的使用者。",
    },
    {
        "question": "把仓库交给另一位同学，他能在干净环境里运行，并且知道成功或失败了吗？",
        "analysis": "Notebook 中保留着输出，不代表别人当前能跑通。交付还需要依赖、模型配置、输入范围、结果文件、退出码和失败说明。先限定为本地笔记研究助手，再验证完整使用过程。",
        "deliverable": "可安装运行的 CLI、配置说明、独立结果目录，以及干净环境中的成功、无证据和拒绝验收。",
        "thinking": "先定义用户任务与成功标准，再用独立进程启动 CLI。读取 result.json 核对答案与 trace，故意提出超出资料的问题检查退出码。最后在新环境重跑，并确认真实模型配置与人工审批不能被绕过。",
        "flow": ["明确用户与配置", "启动 CLI", "检查产物", "验证失败路径", "干净环境交接"],
        "recap": "交付包含成功和失败两条路径。结果、日志、会话与恢复点各有用途；本地单用户验收不能直接推出并发服务能力。",
        "next": "完成主线后，选一个真实任务回到评测，再决定是否引入 ReAct、规划、反思或并发调度。",
    },
]


def md_parts(lesson):
    """Split only level-two headings outside fences; keep source wording intact."""
    parts, lines, title, fenced = [], [], "", False
    for line in lesson["cells"][0]["source"].splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        if not fenced and line.startswith("## "):
            if "".join(lines).strip():
                parts.append((title, "".join(lines).strip()))
            title, lines = line[3:].strip(), []
        else:
            lines.append(line)
    if "".join(lines).strip():
        parts.append((title, "".join(lines).strip()))
    return parts


def clean_intro(text):
    text = re.sub(r"^# [^\n]+\n*", "", text)
    text = re.sub(r"<!-- beginner-navigation -->\s*\n[^\n]*\n*", "", text)
    return text.strip()


def compose(stage, lessons):
    by_id = {lesson["id"]: lesson for lesson in lessons}
    main = by_id[stage["lesson"]]
    units, setup, exercise = [], [], []
    for index, cell in enumerate(main["cells"]):
        source = cell["source"]
        node = {"lesson": main["id"], "cell": index}
        if cell["type"] == "markdown" and re.match(r"## \d+\.", source):
            heading = source.splitlines()[0]
            units.append({"title": re.sub(r"^## \d+\.\s*", "", heading), "before": [], "body": [node], "after": []})
        elif source.startswith("## 练习与自检"):
            exercise.append(node)
        elif units:
            units[-1]["body"].append(node)
        elif cell["type"] == "code":
            setup.append(node)

    def add(path, unit, where="before", headings=None, keep_intro=False):
        lesson = by_id[path]  # Missing teaching sources must fail the build.
        chosen = []
        for title, source in md_parts(lesson):
            if headings is not None and not any(h in title for h in headings):
                continue
            if not title:
                source = clean_intro(source)
                if headings is None and not keep_intro:
                    continue
            if source:
                chosen.append({"lesson": path, "source": ("#### " + title + "\n\n" if title else "") + source})
        units[unit][where].extend(chosen)

    # Concepts appear immediately before their first concrete use.
    pre = stage["prerequisite"]
    n = stage["id"]
    if n == 0:
        add(pre, 0, headings=["三个参与者", "最小准备"])
        add(pre, 1, headings=["代码里"])
        add("step0/01-concepts.md", 0)
        add("step0/02-agent-loop.md", 1)
        add("step0/03-anthropic-building-effective-agents.md", 3, keep_intro=True)
        add("step0/04-openai-practical-guide.md", 3, "after", keep_intro=True)
    elif n == 1:
        add(pre, 0, headings=["JSON"])
        add("step1/01-tool-use-and-harness.md", 0)
        add(pre, 1, headings=["dispatcher"])
        add("step1/03-minimal-agent-loop.md", 1, headings=["最小组成部分", "退出条件"])
        add("step1/02-codex-sdk-experiments.md", 3, "after")
    elif n == 2:
        add(pre, 0, headings=["检索链"])
        # The opening paragraph defines RAG before any retrieval terminology.
        intro = clean_intro(md_parts(by_id[pre])[0][1])
        units[0]["before"].insert(0, {"lesson": pre, "source": intro})
        add(pre, 3, headings=["三种记忆"])
        add(pre, 4, headings=["完整诊断"])
        full = by_id["step2/step2_stage2_diagnostics_fixed.ipynb"]
        # Embed the original complete implementation in order, without another page hop.
        units[4]["title"] = "从小实验走到完整研究 Agent"
        units[4]["body"] = [{"lesson": full["id"], "source": "先把上面四个小实验对应到完整实现。下面按原诊断本的顺序展开：RAG、网页工具、文件/数据库、配置、记忆、运行时，最后是在线实验与离线测试。长代码框可以独立滚动；这里的函数与类需按顺序定义，不能单独复制最后一格执行。"}]
        units[4]["body"].extend({"lesson": full["id"], "cell": i} for i in range(len(full["cells"])))
        # Remove a file-hopping instruction now that the prerequisite is above.
        units[4]["body"][1]["source"] = re.sub(
            r"初学建议先读 \[[^\]]+\]\([^)]+\)，再回来读完整类。", "",
            full["cells"][0]["source"])
    else:
        add(pre, 0, keep_intro=True)
    if n == 5:
        add("step5/skills/research-report/SKILL.md", 0, "after", keep_intro=True)
        add("step5/skills/research-report/assets/report-template.md", 0, "after")
        add("step5/01-skill-hosts-and-evaluation.md", 1, "after", keep_intro=True)
    if n >= 2:
        add("REFERENCE-WALKTHROUGH.md", 0 if n == 3 else len(units) - 1,
            "before" if n == 3 else "after", headings=[f"Stage {n}："])
    tasks = by_id[stage["tasks"]]
    task_text = clean_intro(tasks["cells"][0]["source"])
    # Navigation and run-entry announcements belong to the original reference;
    # the reader has its own experiment block immediately above this task table.
    table_start = task_text.index("| 编号")
    task_text = task_text[table_start:]
    return {**PLANS[n], "setup": setup, "units": units, "exercise": exercise,
            "assessment": {"lesson": tasks["id"], "source": task_text}}
