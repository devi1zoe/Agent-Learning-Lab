# 在 Linux 服务器上打开 MiniAgent

当前项目目录：`/mnt/data/projectnew/miniAgent`。第一课是 `00-foundations/01-what-is-an-agent.ipynb`。

Notebook 内核、浏览器实验和输出文件都在服务器；自己的电脑显示编辑器或网页。正文阅读不需要模型服务。

## 1. 用 VS Code Remote SSH

1. 连接服务器，在远程窗口打开整个项目目录。
2. 在远程主机启用 Python 和 Jupyter 扩展。
3. 打开第一课，选择 `/usr/local/python3.10/bin/python3`。自建环境则选择 `.venv/bin/python`。
4. 先读正文，运行时从该页第一格代码顺序执行。

在 Notebook 中执行下面两行可以确认实际内核：

```python
import sys
print(sys.executable)
```

安装缺失模块时，使用这里显示的解释器，安装后重启内核。

## 2. 用浏览器打开 JupyterLab

在服务器执行：

```bash
cd /mnt/data/projectnew/miniAgent
MINIAGENT_PYTHON=/usr/local/python3.10/bin/python3 bash scripts/start-jupyter-linux.sh
```

也可以省略 `MINIAGENT_PYTHON`：脚本优先用项目 `.venv/bin/python`，否则用当前 `python3`。服务监听服务器的 `127.0.0.1:8888`，终端显示登录 token。

在自己电脑另开终端，将 `user@server` 换成实际 SSH 地址：

```bash
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8888:127.0.0.1:8888 user@server
```

保持两端终端运行，本机打开 `http://127.0.0.1:8888/lab`，输入服务器终端中的 token。也可以用 VS Code 的 Ports 面板转发服务器 8888，并打开面板给出的地址。

本机 8888 被占用时，把 SSH 命令左侧端口改为 18888，再打开 `http://127.0.0.1:18888/lab`。服务器端口被占用时，用 `MINIAGENT_PORT=8889` 启动，并把转发目标改成 8889。

停止服务：在服务器启动终端按 `Ctrl+C`；停止转发：在本机转发终端按 `Ctrl+C`。关闭网页标签不会自动停止内核。

## 3. 新建环境

使用 Python 3.10 或以上版本，在项目根目录运行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --sys-prefix --name miniagent --display-name "Python (MiniAgent)"
```

再为 Notebook 选择该环境。移动项目后应在新位置重建环境；不要复制其他项目或其他操作系统的虚拟环境。

若缺少 `ensurepip` 或系统共享库，需要安装与解释器及系统匹配的组件。现有服务器默认分支可运行，不代表已经验证全新安装完整依赖。

## 4. 浏览器章节

第 06 章默认会启动无头 Chromium，需要给实际使用的环境安装浏览器：

```bash
.venv/bin/python -m playwright install chromium
```

已有解释器则将命令中的 `.venv/bin/python` 换成实际路径。无需服务器桌面或 X11，截图写入本次输出目录。

浏览器缺系统库时，需要由具备相应权限的人安装适配当前 Linux 的依赖。旧系统已有浏览器可运行，与最新版全新安装可用是两件事；不要直接升级正在使用的环境来排查教学代码。

## 5. 可选真实模型实验

Notebook 使用的 `127.0.0.1:11434` 指服务器自身。先确认本地服务可用，并将 `MODEL`、向量模型名称改成服务实际提供的名称，再开启所需页面的 `RUN_LIVE`。阅读和默认程序检查可以一直保持关闭。

已有 Ollama 服务时，可以先运行 `ollama list` 查看模型。课程默认名称示例是 `qwen3:1.7b` 与 `qwen3-embedding:0.6b`；它们不是历史 CPU 实验使用的名称。

项目另带 CPU Transformers 教学适配器，提供课程使用的一部分兼容接口。需要复现历史模式时，在单独环境安装 `requirements-live.txt`，准备模型，再启动服务：

```bash
python3 scripts/prepare_local_models.py --cache-dir /mnt/data/cache/huggingface-miniagent-course
python3 scripts/serve_local_models.py --threads 4 --manifest outputs/local-model-paths.json
```

准备脚本会生成本机模型配置，未缓存的模型需要下载。此服务提供的生成模型名称是 `qwen3:0.6b-cpu`，向量模型名称是 `all-minilm:l6-v2-cpu`。它是本地教学适配器，不是 Ollama 产品。

默认不需要启动这些服务；真实分支会额外占用计算资源，联网研究还需要服务器能够访问来源站点。

## 6. 常见问题

| 现象 | 先检查什么 |
| --- | --- |
| 文件找不到 | 是否完整打开项目，路径大小写是否正确，工作目录是否在项目内 |
| 模块找不到 | `sys.executable` 与安装依赖的解释器是否一致 |
| 本机网页打不开 | 服务是否仍在，转发端口是否对应，token 是否正确 |
| 11434 连接失败 | 服务器模型服务是否启动，模型名称是否存在 |
| Chromium 启动失败 | 当前 Python 环境的浏览器和系统库是否齐全 |
| 本机请求出现代理错误 | 给 `127.0.0.1`、`localhost` 和 `::1` 配置代理例外 |
| socket 报无权限 | 在允许本机 socket 的普通 SSH 环境运行 |

结果、截图和 Notebook 保存到服务器。长时间运行可在已安装的 tmux 会话中启动；断开 SSH 后需要重新连接查看，不能据此推断进程已经完成。
