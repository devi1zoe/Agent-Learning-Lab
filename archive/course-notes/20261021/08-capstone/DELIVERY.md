# 资料研究助手：Linux 交付与验收

面向阅读 Agent 学习资料的同学。输入一个问题及 Markdown 目录，输出带证据编号的答案、状态和 trace；明确要求时，经本人确认再创建报告。学习设计请读 [01-research-assistant.ipynb](01-research-assistant.ipynb)，独立交付验证请读 [02-delivery-check.ipynb](02-delivery-check.ipynb)。

本说明适用于由课程导出的 `project/` 目录；它不是要求在本章节目录运行 `python -m miniagent`。当前实际导出路径与测试结果请看 [本次证据](../evidence/20261020/README.md)。

## 如何使用

在导出的 `project/` 目录打开 Linux 终端，使用 Python 3.9 或以上版本。离线分支仅用标准库，不需要 API key：

```bash
python3 -m miniagent --question "Agent 如何依据反馈行动？" --output outputs/offline-1
python3 -m miniagent --question "ZXQVVUNMATCHED" --output outputs/missing-1
```

第一条应给出可检索资料中的答案；第二条预期 `no_evidence`。在 VS Code Remote SSH 里直接读取对应 `result.json`；CLI 无网页端口，不需要为它转发 8888 或 4173。

真实 Agent 分支需要本机 Ollama 服务和已安装模型：

```bash
python3 -m miniagent --live --model qwen3:1.7b \
  --question "Agent 与 workflow 有何区别？" \
  --timeout 120 --max-steps 6 --max-tokens 12000 \
  --max-output-tokens 512 --output outputs/live-1
```

模型名必须与本机已安装模型一致；以上是现有 adapter 的使用示例，不是本次运行已使用该模型的声明。当前服务地址固定为 `127.0.0.1:11434`，不需要 key；如扩展远程模型，凭据从环境变量读取，避免写进代码、资料或 trace。

每次使用新的 `--output` 路径保留历史。退出码 0 表示 `completed`；无证据、预算不足、调用失败或拒绝导出均返回 2；无效参数也为 2。Linux 中运行后 `echo $?` 可查看上一条命令退出码。

## 报告导出由人确认

```bash
python3 -m miniagent --question "Agent 如何依据反馈行动？" \
  --output outputs/review-1 --export-report reports/answer-1.md
```

终端显示具体内容、绝对路径和 SHA256，等待本人输入完整批准口令。拒绝、取消、参数或内容变化、目标已存在、批准重复使用都不创建报告。测试中的模拟批准输入不代表真实用户授权。默认运行日志在 `--output` 保存；额外报告写入使用独立确认机制。

## 能力边界

默认模式是抽取式检索基线；只有 `--live` 才由模型选择检索动作。资料加载只读第一层、非符号链接、64 KB 以下 `.md`，不提供任意文件搜索、账号登录、发送、发布或付款。

引用检查主要验证编号存在，不自动判断每句事实是否被原文支持；请按证据逐句审阅。临时传输错误最多重试一次，总 token 在请求间检查为软限制，单次输出也有上限。本地模型无 API 美元账单记录，不等于没有计算和等待成本。

trace 用于复盘，尚不支持中断点恢复。该作品是单进程 CLI，没有多用户权限体系、并发服务和生产 SLA。新进程在本机通过，不代表已经验证另一台机器。扩展工具时在课程 Notebook 的工具表注册 schema、函数与权限边界，再导出，固定题集回归后才能比较质量。

## 如何核验这份交付

在本次证据中核对导出项目路径、manifest 哈希、解释器身份、命令、退出码、结果状态和授权测试；在 `eval.csv` 查看真实模型逐题结果。缺少某个产物时保持未验证，不使用历史目录或示意轨迹代替此次结果。
