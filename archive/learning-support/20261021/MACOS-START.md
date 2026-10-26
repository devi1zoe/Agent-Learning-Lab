# 在 Mac 上打开 MiniAgent

完整保留项目目录，第一课是 `00-foundations/01-what-is-an-agent.ipynb`。后续章节会加载前面章节的定义，不能只复制单个 Notebook。

以下是 Mac 使用步骤；本轮没有 Mac 实机验证。

## 1. 创建环境

在终端进入项目根目录，确认 Python 3.10 或以上版本，然后执行：

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --sys-prefix --name miniagent --display-name "Python (MiniAgent)"
```

这个环境需要在 Mac 本机创建。移动目录后应重新建立，不能沿用 Windows 或服务器的虚拟环境。

## 2. 打开课程

在同一目录执行：

```bash
.venv/bin/jupyter lab
```

打开第一课，选择 `Python (MiniAgent)` 内核，先读正文，运行时按代码顺序执行。也可以用 VS Code 打开整个项目，为 Notebook 选择 `.venv/bin/python`。

以后进入项目后再次运行 `.venv/bin/jupyter lab` 即可，无需重复安装。停止时在终端按 `Ctrl+C`。

## 3. 浏览器章节

第 06 章需要实际 Chromium：

```bash
.venv/bin/python -m playwright install chromium
```

Playwright 和浏览器需要与当前 macOS 版本兼容。若安装或启动失败，先检查工具对本机版本的支持；Linux 离线检查通过不能替代 Mac 实机结果。

## 4. 可选真实模型

默认模型分支关闭，阅读正文和大多数程序检查不需要模型服务。需要真实生成时，先启动本机兼容服务，并将 Notebook 中的模型名称改成实际安装的名称，再开启 `RUN_LIVE`。

如果使用已有 Ollama，可以用 `ollama list` 检查。课程默认示例名称为 `qwen3:1.7b` 与 `qwen3-embedding:0.6b`。历史 CPU 实验另使用项目自带 Transformers 适配器及不同模型标签，不能混称。

Mac 本机内核中的 `127.0.0.1:11434` 指 Mac 自己；远程 SSH 内核中的同一地址则指服务器。先明确实际执行位置，再排查连接。

## 5. 常见问题

| 现象 | 处理 |
| --- | --- |
| `ModuleNotFoundError` | 核对 Notebook 内核，用同一解释器安装依赖后重启 |
| 找不到浏览器 | 给所选 Python 环境安装 Chromium |
| 找不到项目根目录 | 保留完整项目和 `scripts/lesson_loader.py`，从项目中启动 |
| 模型连接失败 | 确认本机服务和名称，暂不运行模型时保持开关关闭 |
| 输出路径不同 | 本机运行会产生自己的路径，历史日志路径不需要照搬 |

当前课程共 22 本 Notebook；`outputs/` 保存本次运行，`evidence/` 保留历史原始实验，旧说明和早期材料集中在 `archive/`。
