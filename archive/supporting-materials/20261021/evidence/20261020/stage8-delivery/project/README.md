# Mini Agent · 笔记研究助手

面向阅读学习笔记的同学。输入问题和 docs/ 中的 UTF-8 Markdown，输出带来源的答案、状态和 trace。
本目录由教学 Notebook 的 definitions 单元格导出；可以独立复制，运行不依赖原仓库或 Jupyter。
Python 3.9+，离线与本地 Ollama 模式只使用标准库。不要在生成的 Python 中长期维护课程源码，应修改 Notebook 后重新导出。

## 从空环境运行

在本目录打开终端。创建环境：`python -m venv .venv`。
Windows 使用 `.venv\Scripts\python.exe`；macOS/Linux 使用 `.venv/bin/python` 代替下面的 python。

```powershell
python -m miniagent --question "Agent 如何依据反馈行动？" --output outputs/run-1
python -m miniagent --question "ZXQVVUNMATCHED" --output outputs/run-2
```

查看对应 outputs/ 中的 result.json。成功退出码 0；无证据、调用失败、预算不足或拒绝导出为 2。
PowerShell 通过 `$LASTEXITCODE` 查看退出码。无效参数也以 2 退出。
每次运行请使用不同 --output，避免覆盖之前的结果。

## 接入真实模型

安装启动 Ollama，执行 `ollama pull qwen3:1.7b`，再运行：

```powershell
python -m miniagent --live --model qwen3:1.7b --question "Agent 与 workflow 有何区别？" --timeout 120 --output outputs/live
```

服务固定为 127.0.0.1:11434，不需要 API key。离线模式是抽取式检索基线，只有 --live 会调用真实模型。
`--max-steps` 限制模型轮次，`--max-output-tokens` 限制单次生成，总 `--max-tokens` 在请求间检查，是软上限。
暂时网络错误最多重试一次，共用时间预算。本地模型没有 API 美元账单，cost_usd 为 null。
接入远程模型时应新增 adapter，并从环境变量读取凭据；不要把凭据写进 Notebook、报告或 trace。

## 资料、审批与扩展

`--docs` 可以指定语料目录；仅读第一层、非符号链接、64 KB 以下的 Markdown。默认只读教学资料。
加 `--export-report reports/answer.md` 后，终端展示内容、路径及 SHA256，并等待你输入完整批准口令。
拒绝、内容或参数变化、目标已存在都不写出，已经批准过的动作不可重复使用。没有自动发送或发布功能。
要扩展工具，请在课程 Notebook 的 tools 表注册 Tool(schema(...), function)，然后重新导出。
写工具应有具体动作的审批；超时不保证外部动作没有发生，需要另行设计幂等和恢复。

## 限制与核对

检索是词汇基线；引用校验只检查编号，不判断事实是否得到支持。需要结合固定评测任务和人工审阅。
trace 是记录，不是恢复点。本项目是单进程教学作品，没有并发服务、账号权限体系或生产 SLA。
本地新 venv 通过不等于已经验证另一台机器；交接时请记录 Python/模型版本、配置、实际退出码和人工审阅结论。
