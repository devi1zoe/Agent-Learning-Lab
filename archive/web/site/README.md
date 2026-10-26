# miniAgent 网页学习站

在项目根目录双击 [start-learning.bat](../start-learning.bat)，或运行：

```powershell
python -m learning.web_server --open
```

打开终端显示的 `http://127.0.0.1:8765`。关闭终端会停止该次启动的服务；下次双击即可。如果学习站已在运行，重复启动只打开现有页面，不再启动第二个服务器。端口被其他程序占用时可加 `--port 8766`。服务器只监听本机，不需要注册账号。

## 怎么学

首页选阶段后，顺着同一页读完：**分析题目 → 推导实现思路 → 逐步阅读讲解与代码 → 运行验证 → 验收与总结 → 下一课**。九章各自有具体问题、产出和设计推导，前置概念、相关 Markdown 笔记与 Notebook 单元格按使用顺序融入正文；不需要切换「前置 / 讲解 / 验收」标签。右侧目录只滚动定位，正文始终展开。

例如 Step 1 在循环代码前解释 JSON、schema、dispatcher 与消息历史；Step 2 在切块、向量、检索、记忆四个小实验后，继续展开原有完整研究 Agent 诊断本。原始文件入口留在各节出处和章末，四组 ReAct 等架构拓展在对应章节结束后推荐，不阻塞主线。

- **运行本章实验**：用独立 Python 内核运行已有 Notebook 的默认离线路径。输出在网页显示，保留原文件和你保存的服务开关。Stage 6 会实际启动本地 Chromium。
- **真实实践**：主线 Stage 1–8 调用已有实践脚本，需要对应的 Ollama 模型/依赖。Stage 2、3、6 会访问文档说明的公开资源；运行结果与模型成绩分开解释。
- **下载 Notebook**：需要自由修改代码、单步调试时，下载后用 VS Code 或 Jupyter 打开。网页当前提供只读代码和整章运行，未提供任意 Python 在线编辑器。
- **进度和笔记**：自动保存在当前浏览器的 localStorage；清除站点数据或换浏览器后不会自动同步。标记已学完是个人记录，不代表测试替你判定学会了。
- **资料与源码 / 搜索**：收录现有 Markdown、Notebook、学习脚本和配置；资料之间的链接会转为站内阅读。

## 为什么采用网页 + 本地 Python + Notebook

网页适合连续阅读、路线导航、查词和可视化；本地 Python 保留 Ollama、文件、数据库和 Playwright 的实际环境；Notebook 适合自由改代码和保留逐格实验。JupyterLite 的 Python 在浏览器内运行，不能直接当作本机环境的完整替代，见 [官方说明](https://jupyterlite.readthedocs.io/en/stable/)。

## 内容维护

课程代码、实验讲解和验收表仍以原 Markdown 和 Notebook 为准。`learning/web_course.py` 只补每章的问题分析、设计推导和总结，并声明材料编排顺序；不复制维护 Notebook 代码。构建时读取原文件、保留单元格出处与原始编号。修改材料后，执行 `python -m learning.web_catalog` 并刷新；启动服务也会构建，服务已运行时先构建再刷新即可。已保存输出明确标为历史输出。

页面源文件：`web/index.html`、`web/style.css`、`web/app.js`；内容提取：`learning/web_catalog.py`；课程编排：`learning/web_course.py`；本地服务：`learning/web_server.py`。`web/dist` 为生成目录，已忽略。Markdown 渲染与 HTML 清理依赖固定版本的本地 vendor 文件，首次构建后无需 CDN。

Notebook、源码和 Markdown 中标明语言的代码块提供语法高亮，包括 Python、JSON、Shell / PowerShell、JavaScript、HTML、SQL 等。配色位于 `web/highlight.css`，高亮依赖保存在本地；复制仍使用原始代码。未标语言的图示和实验输出保留原样。

## 检查

```powershell
python -m unittest learning.test_web_learning
python -m learning.check_web_ui
# 安装并启动 Ollama 后，额外验证网页上的真实实践按钮
python -m learning.check_web_ui --live
```

UI 检查需要先启动服务，使用独立的无头 Chromium 测试搜索、导航、进度持久化、真实离线执行、交互演示和手机布局；不操作个人浏览器。截图与结果写入 `.learning_output/web-qa`。
