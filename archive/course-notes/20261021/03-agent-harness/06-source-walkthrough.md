# Stage 3 · 固定源码导读：只解释实际存在的机制

本页完成 S3.1、S3.2 的源码定位，并连接 S3.3–S3.5 的实验。先读 [Harness 设计主线](01-harness.ipynb)，再打开 [上游对照](02-upstream-comparison.ipynb)。以研究报告任务追踪“问题→模型请求→工具→观察→下一次输入→结束”，不以记住框架 API 为目标。

## 固定版本与可检查的本地文件

Agent-Learning-Hub 的路线固定为 `dddf777dde6788228136862f270203424a28efbc`，完整要求见 [参考README](../references/agent-learning-hub/README.md)。本阶段选择 learn-claude-code，固定为 `ce8f9f186058939da54c9d6fead78dfb5d0fd6c3`；各章为独立增量例子，不能把不同章节的能力全部归给 s02。

本地保留 [来源与SHA256清单](../references/learn-claude-code/source.json)、[MIT许可证](../references/learn-claude-code/LICENSE) 以及本节实际检查的三份源文件：

| 文件 | 本地入口 | 为什么读它 |
|---|---|---|
| s02_tool_use | [code.py](../references/learn-claude-code/s02_tool_use/code.py) | 循环与工具分发的最小整体 |
| s03_permission | [code.py](../references/learn-claude-code/s03_permission/code.py) | 明确调用前权限判定 |
| s08_context_compact | [code.py](../references/learn-claude-code/s08_context_compact/code.py) | 大输出、归档、摘要与协议完整性 |

s02 的 SHA256 为 `fa6fdaa4e75ae4304507a96cb22adf98854f115509bec2ecc400f31c202ff19e`。实验加载函数前再次校验；下载的是源码证据，不等于已运行完整原版 CLI。

## 1. agent_loop：模型产生请求，程序才执行

[s02::agent_loop](../references/learn-claude-code/s02_tool_use/code.py#L163) 顺序如下：

1. `client.messages.create` 接收 system、完整当前 messages、TOOLS。
2. 将原 assistant 内容加入 messages；从内容中提取 `tool_use` 块。
3. 没有工具请求则 return；这是生成结束，不是独立事实验收。
4. `TOOL_HANDLERS.get(block.name)` 找函数并实际执行。
5. 将结果作为 user 的 `tool_result` 内容块追加，以 `tool_use_id` 关联原请求。
6. 回到模型调用，让观察影响下一个动作。

研究任务中，步骤2请求“读团队资料”不能证明资料已读；步骤4/5的实际结果才能证明执行。生成“报告完成”不能证明文件已保存或事实有支持。

## 2. registry：接口说明和实现必须同时存在

[TOOLS](../references/learn-claude-code/s02_tool_use/code.py#L138) 将名称、说明、参数schema交给模型；[TOOL_HANDLERS](../references/learn-claude-code/s02_tool_use/code.py#L153) 将名称映射到真实函数。

只加schema会让模型请求一个runtime没有的动作；只加函数但不暴露说明，模型无法从工具列表发现它。本地上游实验把 `count_words` 同时加到两处，并限制工具面以隔离测试。模型填参数、runtime校验、handler副作用是三个边界。

## 3. permission：s02有哪些约束，又缺什么？

s02 的 [safe_path](../references/learn-claude-code/s02_tool_use/code.py#L81) 限制专用文件工具不逃出workspace；[run_bash](../references/learn-claude-code/s02_tool_use/code.py#L63) 有危险字符串denylist和120秒超时。字符串denylist不能构成完整沙箱，也不等于逐动作交互审批。

[s03::check_permission](../references/learn-claude-code/s03_permission/code.py#L201) 进一步组合拒绝列表、规则与 `ask_user`，由 [s03::agent_loop](../references/learn-claude-code/s03_permission/code.py#L217) 在执行前调用。拒绝要作为结果反馈，不能从历史里消失。

本地 `Harness.approve` / `Tool.needs_approval` 是教学实现，未移植上游全部规则。本地对“写文件”拒绝的trace不能当作 s02 原本具有相同安全门的证明。

## 4. session store：明确缺失，也算定位结果

s02 CLI 的 `history=[]` 是进程内会话；没有将完整历史持久化并恢复的 session store。重启后不能靠它知道刚才哪些动作已执行。

s08 的转录归档保留原始消息；后续 [s16::WorkflowJournal](https://github.com/shareAI-lab/learn-claude-code/blob/ce8f9f186058939da54c9d6fead78dfb5d0fd6c3/s16_workflow_runtime/code.py#L329) 记录 workflow运行事件。这两者不能不加说明就等同任意工具可重放的通用会话恢复。读取、生成、写入等动作恢复时需要不同策略；对已发生副作用的动作重试尤其需要稳定ID或幂等契约。

本地 `SessionStore` 来自第02章，保存教学会话；不是上游移植。研究任务应分别保留目标/约束、证据库、动作状态、原始trace，不能只保存最终报告文字。

## 5. context compaction：缩短输入时保留哪些性质？

[s08::ContextCompactor](../references/learn-claude-code/s08_context_compact/code.py#L254) 是固定源码中的真实类。

| 方法/入口 | 状态变化 | 研究任务的检查问题 |
|---|---|---|
| `persist_large_output` / `persisted_preview` | 大工具输出写文件，模型看到预览与位置 | 原始证据还可回读吗？位置是否可信？ |
| `tool_result_budget` | 控制单批工具结果的体积 | 输出是否被误当成已完整读过？ |
| `snip_compact` | 归档旧中间消息并留标记，调整工具交互切点 | 有没有留下孤立tool_result或丢失请求？ |
| `micro_compact` | 已消费旧结果保存后缩短 | 未被模型看见的新观察是否还完整？ |
| `compact_history` | 摘要/保留近期内容，处理当前请求 | 用户约束、来源身份与未解决冲突是否保持？ |

不是“摘要读起来通顺”就说明压缩正确。研究者最容易丢的是证据状态：未读候选被摘要成已核实、冲突被合并成单一结论、拒绝写入被总结成已经保存。

本地 `compact_completed_turns` 仅裁剪已完成问答，既不归档全文也不做模型摘要；不能按方法名把它算作上游完整压缩实现。

## 6. 真实实验与结构示意分开读

[02上游实验](02-upstream-comparison.ipynb) 执行原s02函数，通过桥接替换模型API，并加入窄工具和外部调用预算；这些适配都单独记录。Ollama桥接的实现不等于原生Anthropic部署；本次统一CPU模型适配也有自己的说明。

真实模型行为、原始trace、失败与评分见 [evidence/20261020](../evidence/20261020/README.md)。没有实际请求时，只能说明定义或控制器可运行。真实模型没发工具、发坏参数、超时，都应保留，不用脚本补一条成功轨迹。

完成本页后应能拿一条trace定位：当前模型看到了什么、它提出了什么、执行边界在哪里、哪项状态真的改变、停止是否等于成功。这个回答比“我读过s02”更能证明理解。
