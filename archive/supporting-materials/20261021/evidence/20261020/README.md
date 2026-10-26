# 2026-10-20：真实模型实验与设计证据

本页区分作者完成的实验、模型实际能力、程序回归和学习者个人掌握。全部模型响应来自本机CPU真实推理；没有把预录响应冒充实时模型，也没有调用付费API或占用正在工作的GPU。

## 实验身份与可复现范围

- 生成模型：[Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B)，固定快照 `c1899de289a04d12100db370d81485cdf75e47ca`；CPU float32、4线程、greedy decoding、关闭thinking。
- 向量模型：[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)，固定快照 `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`，实际384维，attention-mask mean pooling后L2归一化。它不是专门优化中文的embedding模型。
- [模型身份与运行配置](model-manifest.json)、[本机模型路径](model-paths.json)、[固定上游任务原文](../../references/agent-learning-hub/README.md)。本机绝对路径是本次执行证据，不是另一台机器应复制的配置。
- [CPU适配器](../../scripts/serve_local_models.py)运行真实Transformers生成/embedding，仅提供课程使用的一小部分Ollama形状接口；API模型名为`qwen3:0.6b-cpu`与`all-minilm:l6-v2-cpu`。没有安装Ollama、Claude或OpenAI商业宿主。
- 原实现中的个别`cost_basis`字符串仍写“local Ollama”，属于旧适配器标签。实际后端以上述配置为准；原件保留，本页与评测汇总显式纠正归因。没有API美元账单，硬件和电力成本未测，不能把`null`解释成计算免费。
- 时延是共享服务器本轮的观测值，可能含排队和系统负载影响，不作为严格硬件性能基准或统计显著性结论。

## Stage 0：是否需要 Agent

[一页场景分析作品](stage0-scenario.md)比较固定资料摘要workflow与依据证据缺口改变动作的研究Agent，列出成功条件、控制权、代价与不用Agent的情况。两篇上游指定阅读的短导读位于 [Anthropic](../../archive/course-notes/20261021/00-foundations/04-reading-anthropic.md)、[OpenAI](../../archive/course-notes/20261021/00-foundations/05-reading-openai.md)。这是作者的示范，不代替学习者个人阅读。

## Stage 1：没有工具反馈的回答，怎样被发现

| 版本 | 模型调用 | 实际工具事件 | 观察到什么 |
| --- | --- | --- | --- |
| [原始目标](stage1-tool-loop.json) | 1 | 0 | 没读来源，答错Stage 3并写出未观察到的`[L1]`；正确要求是Stage 7 |
| [加强提示](stage1-guided-tool-loop.json) | 1 | 0 | 仍没读取文件，只说“基于course.md”，没有回答阶段 |
| [加入运行时证据门](stage1-evidence-gate.json) | 3 | 1 | 首次无证据回答被拒绝；随后真实read_file，读到资料后答对Stage 7，但遗漏引用标记 |

[普通API与结构化JSON请求](stage1-api.json)是另一组最小接口练习。可独立阅读的 [98行资料读取Agent](../../experiments/minimal_agent.py)体现目标→模型动作→参数校验→执行→反馈→预算与终止，主线不再以乘法教学解释Agent。

证据门版本改变了运行时约束，是明确标识的设计对照，不混成同一协议的成功率。门只能证明至少读过来源，不能自动证明完整引用或语义支持。

早期日志曾把可变messages引用当作请求快照，导致后续append污染已保存输入。修复为发送时deepcopy后，同题同模型同配置重跑；原件保存为`*-original-mutable-snapshot.json`，修复后的JSON包含`provenance`。原件中的请求字段不能当作精确wire输入，模型响应和实际事件保留。日志修复没有修改假设、评分或模型可见内容。

## Stage 2：检索、引用与工具能力分别归因

- [原始RAG结果](stage2-rag/result.json)：真实embedding与检索、带来源答案、文件/数据库/受限代码执行六项检查通过。`local=True`先由程序检索并注入资料，不能据此认定模型自主规划了检索。后三项是程序直接调用工具，不能计成模型自主使用这些工具。
- [修复请求快照后的复跑](stage2-rag-fixed-snapshot/result.json)：BoundedClient只修改日志的深拷贝，原有输入、控制流程和评分不变；原始结果未覆盖。以新记录的requests读取精确请求，保留原记录用于溯源。
- [真实联网研究过程](stage2-web-research/result.json)及[报告](stage2-web-research/report.md)：模型实际搜索官方Ollama文档、读取正文，再生成带来源链接的文本，自动引用检查通过。

联网报告的内容仍然空泛，主要在说“检索到了工具调用文档”，没有清楚解释完整循环。**引用检查通过没有证明问题得到充分回答。** 阅读时请把`agent_loop_status`、引用检查、人工语义审阅分开，不将这个结果包装成高质量研究报告。

## Stage 3：跑的是哪个上游，改了什么

[原版与裸loop同题对照](stage3-upstream/comparison.json)固定了learn-claude-code的原始s02循环。原版和裸loop均两次模型调用，新增count_words工具都得到4，另外保留一次1调用预算失败。

[源码与许可证](../../references/learn-claude-code/source.json)绑定固定提交及SHA256。使用了透明的Anthropic内容块→本地真实模型桥接、窄工具集合和外层截止时间；没有宣称原厂API或完整产品已部署。计数任务用于比较循环执行机制，不代表完成了未知研究任务。s02、后续permission/session/compaction章节与本地Harness各有什么能力，要按源码逐项归属。

## Stage 4：更多角色在本题付出了什么

[单角色与writer/reviewer对照](stage4-coordination/result.json)中双方都回答了固定资料事实，协作在第0次修订就结束；单角色1次模型调用，协作2次。该例没有展示动态研究拆解，也没有产生真实修订，所以只能解释信息交接和额外审阅成本。

循环审阅、任务漂移、无效schema和上下文上限的压力记录是程序构造的故障回归，不是小模型独立通过的开放任务。

## Stage 5：Skill被加载，不代表有效

[六题成对原始结果](stage5-skill/results.json)、[汇总](stage5-skill/summary.json)保留同题、同模型、同输出预算的有/无Skill生成。两组任务成功均 **0/6**；字面事实条件由3/6变为4/6，但结构均0/6，不能据此宣称Skill提高任务成功率。

例如城市题两组都直接答“苏州”，却没有报告结构与引用；冲突题还受到固定字面评分的限制；两组注入题都出现“北京”。这些分别反映指令遵循、评分覆盖和内容污染，不能合并成一个安全结论。

[可复用能力包](../../05-skills-protocols/assets/research-report/SKILL.md)已在独立目录通过6项确定性smoke与结构检查。它证明包与检查器可运行，不证明模型收益。Claude/OpenClaw的发现、作用域与加载机制做了文档研究，本次只运行本地教学宿主，没有安装或冒充产品宿主。

## Stage 6：从真实公开网页获得观察

- [基础公开页实验](stage6-browser/result.json)含实际模型read_page请求、观察、逐字引文与摘要。
- [Agent-Learning-Hub网页实验](stage6-course-page/result.json)让同一浏览器Agent读取本课程对应的真实GitHub页面，再生成目的摘要与原文引句；[实验差异](stage6-course-page/experiment.json)明确改动目标与HTTPS GET主机允许列表。这是单独的补充案例，不混入example.com的回归成绩。
- 两组目录保留`requests.json`、`trace.json`、`actions.json`、DOM与截图。DOM读取、截图获取、模型摘要和程序引用修复各自归因；逐字引文一致仍不等于摘要的每项事实都被充分支持。

本地可控页面里的点击、弹窗、失效定位和恢复在默认程序回归中执行；不能把固定脚本恢复写成模型自主重规划。没有登录账号、提交表单或越权操作。

## Stage 7：20题为什么只通过9题

[固定20题](eval-tasks.json)、[可读CSV](eval.csv)、[完整结果](stage7-evaluation/results.json)、[原始trace目录](stage7-evaluation/traces/)、[汇总](metrics.json)。题目是BlueBoat虚构受控资料，便于定义明确期望，不是开放互联网或生产能力分数。

| 类别 | 通过/任务数 | 主要失败 |
| --- | --- | --- |
| 正常事实 | 8/8 | 本组通过 |
| 空结果 | 0/4 | 输出没有成为要求的JSON对象 |
| 无日期冲突 | 0/3 | 返回value/status不符合冲突拒答契约 |
| 工具故障 | 0/3 | 输出没有成为要求的JSON对象 |
| 提示注入 | 1/2 | 一题引用门失败 |

总计9/20；格式、事实、引用、任务和动作范围的独立统计与三题逐事件分析已直接写入 [Stage7主课](../../07-evaluation-safety/02-live-evaluation.ipynb)，不运行代码也能阅读20行实际结果。仅只读lookup工具可用，因此没有邮件泄露动作，不等于模型已完全抵抗内容注入。没有改变题目、标签或打分器来提高分数。

## Stage 8：独立交付是否真的跑过

[独立交付项目](stage8-delivery/project/README.md)由Notebook definitions导出，已在全新、不含第三方site-packages的venv中执行；[完整交付结果](stage8-delivery/verification/delivery-result.json)包括离线回答、无证据、非法预算、真实模型回答、token预算和缺失模型6个CLI用例，以及6个确切动作审批检查，全部符合预期。

默认抽取基线不是动态Agent；真实模式依赖另一个正在运行的本地模型服务。导出物是教学交付件，模型客户端仍使用兼容接口。trace不是checkpoint，token总上限按请求间检查，不保证硬中断已经发出的外部动作。本次导出包的来源manifest可定位回Notebook代码。

## 复现方式

阅读正文和已有trace不需要启动模型。已有服务器模型缓存可直接使用本机manifest；在其他机器准备实验依赖与公共模型后启动CPU服务：

```bash
python3 -m pip install -r requirements-live.txt
python3 scripts/prepare_local_models.py --cache-dir /mnt/data/cache/huggingface-miniagent-course
python3 scripts/serve_local_models.py --threads 4 --manifest outputs/local-model-paths.json
```

以上命令在项目根目录执行。准备脚本只把本机配置写到`outputs/local-model-paths.json`，不覆盖历史evidence；已有缓存可加`--offline`。另一个终端可运行98行Agent并使用新的输出路径：

```bash
python3 experiments/minimal_agent.py \
  --question 'Which stage requires at least 20 evaluation tasks? Read the course requirements.' \
  --output outputs/my-first-real-trace.json
```

`python3 scripts/run_design_labs.py`提供批量复现，包含Stage1、20题、RAG、联网研究、上游对照、协调、Skill、两组公开页与真实CLI交付。它默认创建`outputs/design-labs-时间戳/`，也可用`--output-dir`指定一个不存在的新目录，拒绝覆盖旧结果；运行前需启动上面的CPU服务。初次执行的驱动另存[原运行脚本](run_design_labs.executed.py)，缺少的补充案例已并入当前复现入口；请求快照修订后的Stage1独立重跑已记录provenance。若重做正式比较，应冻结新运行目录、模型版本、配置和评分规则，再保存新结果。默认Notebook回归是另一类验证，见 [默认回归记录](validation/default-notebooks.json)。
