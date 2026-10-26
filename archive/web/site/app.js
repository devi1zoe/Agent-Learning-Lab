/* Repository content remains the single source of truth. Progress stays in this browser. */
(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const icon = `<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 18V6l8 8 8-8v12" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const glyphs = ['◇','↻','▤','⌘','⋈','⊞','▧','✓','↗'];
  let catalog, lessons = new Map(), current = null, api = null, pollTimer = null, filter = 'all';
  let readingTargets = new Map(), readingObserver = null;
  const activeJobs = new Map();
  let pollGeneration = 0;
  let progress;
  try { progress = JSON.parse(localStorage.getItem('miniagent-learning-v1')) || {}; } catch { progress = {}; }
  if(typeof progress!=='object'||Array.isArray(progress))progress={};
  if(!Array.isArray(progress.done))progress.done=[];
  if(!progress.tasks||typeof progress.tasks!=='object')progress.tasks={};
  if(!progress.notes||typeof progress.notes!=='object')progress.notes={};
  const persist = () => { try { localStorage.setItem('miniagent-learning-v1', JSON.stringify(progress)); } catch { toast('浏览器存储不可用，本次进度暂未保存'); } };
  function toast(message) { $('#toast').textContent = message; $('#toast').classList.add('show'); setTimeout(() => $('#toast').classList.remove('show'), 2800); }
  const stageUrl = (stage, tab='lesson') => `#stage/${stage}/${tab}`;
  const readUrl = id => `#read/${encodeURIComponent(id)}`;
  const completed = () => catalog.stages.filter(s => progress.done.includes(s.lesson)).length;
  const nextStage = () => catalog.stages.find(s => !progress.done.includes(s.lesson)) || catalog.stages[0];
  const footer = () => `<footer class="footer"><span>miniAgent · 从理解到实践，慢慢把能力长出来。</span><a href="${readUrl('COURSE-ALIGNMENT.md')}">课程来源与对齐说明 ↗</a></footer>`;

  function shell(content, section='home', breadcrumb='学习路线') {
    const done = completed();
    $('#app').innerHTML = `<aside class="sidebar" aria-label="学习导航">
      <a class="brand" href="#home"><span class="brand-mark">${icon}</span>miniAgent</a><div class="brand-sub">LEARN · BUILD · REFLECT</div>
      <nav><a href="#home" class="nav-link ${section==='home'?'active':''}"><span class="nav-icon">▦</span>学习路线</a>
      <a href="#extensions" class="nav-link ${section==='extensions'?'active':''}"><span class="nav-icon">⌁</span>拓展图谱 <span class="tiny">4</span></a>
      <a href="#library" class="nav-link ${section==='library'?'active':''}"><span class="nav-icon">▤</span>资料与源码</a>
      <a href="${readUrl('GLOSSARY.md')}" class="nav-link ${section==='glossary'?'active':''}"><span class="nav-icon">Aa</span>概念词典</a></nav>
      <div class="nav-label">THE LEARNING PATH</div><nav class="stage-nav">${catalog.stages.map(s => `<a class="stage-link ${current?.stage===s.id?'active':''} ${progress.done.includes(s.lesson)?'done':''}" href="${stageUrl(s.id)}"><span class="stage-number">${progress.done.includes(s.lesson)?'✓':s.id}</span>${esc(s.title)}</a>`).join('')}</nav>
      <div class="sidebar-bottom"><div class="sidebar-note"><strong>按自己的节奏，持续向前 ↗</strong>已学 ${done} / 9 个阶段<br>进度与笔记保存在当前浏览器</div><div class="tiny" style="margin:16px 5px 0;font-size:9px">基于 Agent Learning Hub · 主线 0—8</div></div>
    </aside><div class="shell"><header class="topbar"><div class="breadcrumbs"><button class="mobile-menu" data-action="menu" aria-label="展开导航">☰</button><span class="root-crumb">个人学习空间</span><span class="root-crumb">/</span><strong>${esc(breadcrumb)}</strong></div><div class="top-actions"><button class="search-trigger" data-action="search" aria-label="搜索课程"><span>⌕</span><span class="search-label">搜索课程与概念</span><kbd>Ctrl K</kbd></button><span class="mode-pill"><span class="mode-dot"></span>${api?'本地实验已连接':'阅读模式'}</span></div></header><main class="content" id="main" tabindex="-1">${content}${footer()}</main></div>`;
  }

  function home() {
    current = null;
    const next = nextStage(), count = completed(), pct = Math.round(count/9*100);
    shell(`<section class="hero"><div class="hero-copy"><div class="eyebrow">A FIELD GUIDE TO BUILDING AGENTS</div><h1>把 Agent 学成<br><em>你自己的能力。</em></h1><p>从第一轮工具调用，到一个可以交付的作品。<br>不再迷失在文件夹里，沿着一条清晰的路线，边理解，边动手。</p><div class="hero-actions"><a class="primary" href="${stageUrl(next.id)}">${count?'继续学习':'从第 0 课开始'} <span>↗</span></a><a class="text-link" href="#playground">先看懂一轮 Agent 循环 <span>→</span></a></div></div>
      <div class="hero-art" aria-hidden="true"><div class="orbit"><div class="orbit-ring"></div><span class="spark">✧</span><div class="orbit-center">${icon}</div><div class="orbit-label ol-1"><span>◎</span><div>观察环境 <small>OBSERVE</small></div></div><div class="orbit-label ol-2"><span>⌁</span><div>选择行动 <small>DECIDE</small></div></div><div class="orbit-label ol-3"><span>↗</span><div>执行与反馈 <small>ACT</small></div></div><span class="art-caption">ONE LOOP. MANY POSSIBILITIES.</span></div></div></section>
      <div class="stats-bar"><span><b>9</b> 个主线阶段</span><span class="stats-divider"></span><span><b>4</b> 组策略拓展</span><span class="stats-divider"></span><span><b>50</b> 项学习任务</span><span class="stats-note"><span class="mode-dot"></span>源自真实 Notebook 与学习笔记</span></div>
      <div class="progress-strip"><div class="progress-ring" style="--progress:${pct}%"><span>${pct}%</span></div><div><h3>${count?'上次学到这里，今天再前进一步。':'一切从理解「什么是 Agent」开始。'}</h3><p>${count?`下一阶段：${esc(next.title)}`:'无需先学一堆框架，带着一个具体的问题出发。'}</p></div><a class="text-link" href="${stageUrl(next.id)}">${count?'接着学':'开始第一课'} →</a></div>
      <section id="roadmap"><div class="section-heading"><div><h2>你的学习路线</h2><p>按顺序打好基础。每一步都有讲解、代码与可以交出的作品。</p></div><span class="quiet-tag">CORE PATH · 主线</span></div><div class="roadmap">${catalog.stages.map(s => `<a href="${stageUrl(s.id)}" class="stage-card ${s.id===next.id?'current':''}"><div class="card-top"><span class="card-step">STEP ${String(s.id).padStart(2,'0')} / ${s.english.toUpperCase()}</span><span class="card-glyph">${glyphs[s.id]}</span></div><h3>${esc(s.title)}</h3><div class="card-sub">${esc(s.subtitle)}</div><p>${esc(s.description)}</p><div class="card-bottom"><span>${s.task_count} 个任务 · ${esc(s.outcome)}</span><span class="card-arrow">${progress.done.includes(s.lesson)?'✓':'↗'}</span></div></a>`).join('')}</div></section>
      <section class="extension-section"><div class="section-heading"><div><h2>好奇心，往旁边多走一步</h2><p>学过对应基础后再探索。拓展不会打断你的主线。</p></div><a class="text-link" href="#extensions">全部拓展 ↗</a></div>${extensionGrid()}</section>`);
  }
  function extensionGrid() { return `<div class="extension-grid">${catalog.extensions.map(e => `<a class="extension-card" href="${readUrl(e.lesson)}"><span class="eyebrow">OPTIONAL · STEP ${e.after} 之后</span><h3>${esc(e.title)} <span style="float:right;font:14px var(--sans);color:#a2b293">↗</span></h3><p>${esc(e.description)}</p></a>`).join('')}</div>`; }
  function extensions() { current=null; shell(`<div class="page-heading"><span class="eyebrow">OPTIONAL EXPLORATIONS</span><h1>先理解问题，再选择策略。</h1><p>ReAct、规划、反思、搜索和并发调度解决不同的问题。这些是主线旁的拓展，不是下一课的入场券。</p></div>${extensionGrid()}<div class="tip">工具调用是动作接口；ReAct 是结合观察继续决策的方式。planner / executor 是职责，并不要求多买一个模型。先观察一个小任务的状态、反馈和停止，再读架构名字。</div><a class="primary" href="${readUrl('step3/05-agent-architectures.md')}">比较方法与原始论文 →</a>`, 'extensions','策略拓展'); }

  function markdown(source, path) {
    const html = DOMPurify.sanitize(marked.parse(source, {gfm:true, breaks:false}), {FORBID_TAGS:['iframe','style','form','input','script']});
    const div = document.createElement('div'); div.innerHTML = html;
    div.querySelectorAll('a').forEach(a => {
      const href=a.getAttribute('href') || '';
      if (/^https?:\/\//i.test(href)) { a.target='_blank'; a.rel='noopener noreferrer'; return; }
      if (href.startsWith('#')) return;
      if (/^[a-z]+:/i.test(href)) { a.removeAttribute('href'); return; }
      try {
        const resolved = new URL(href, 'https://course.local/'+path);
        const id=decodeURIComponent(resolved.pathname.slice(1));
        if (readingTargets.has(id)) { const target=readingTargets.get(id);a.href=stageUrl(current.stage,target);a.dataset.scroll=target; }
        else if (lessons.has(id)) a.href=readUrl(id);
        else { a.href='files/'+id; a.setAttribute('download',''); }
      } catch { a.removeAttribute('href'); }
    });
    div.querySelectorAll('img').forEach(img=> {img.remove();});
    return div.innerHTML;
  }
  function highlightCode(root) {
    if(!window.hljs)return;
    const aliases={py:'python',js:'javascript',ts:'typescript',html:'xml',sh:'bash',ps1:'powershell',ps:'powershell',text:'plaintext',txt:'plaintext'};
    root.querySelectorAll('pre > code').forEach(block=>{
      const match=block.className.match(/(?:^|\s)language-([\w+-]+)/);
      if(!match)return; // Unlabelled diagrams and output remain plain text.
      const language=aliases[match[1].toLowerCase()]||match[1].toLowerCase();
      if(!hljs.getLanguage(language))return;
      block.classList.remove(match[0].trim());
      block.classList.add('language-'+language);
      hljs.highlightElement(block);
    });
  }
  function codeCell(lesson, c, index) {
    return `<div class="code-cell"><div class="code-toolbar"><span>${esc(lesson.path.split('/').pop())} · ${c.number?`第 ${c.number} 格`:`${(c.language||'python').toUpperCase()} / ${index+1}`}</span><button class="copy-button" data-source="${esc(lesson.id)}" data-copy="${index}">复制代码</button></div><pre><code class="language-${esc(c.language||'python')}">${esc(c.source)}</code></pre>${c.outputs.length?`<details class="output-cell"><summary>已保存的输出 · 不代表本次执行</summary><pre>${esc(c.outputs.join('\n'))}</pre></details>`:''}</div>`;
  }
  function lessonBody(lesson) {
    return lesson.cells.map((c,index) => c.type==='markdown' ? markdown(c.source, lesson.path) : codeCell(lesson,c,index)).join('');
  }
  function readingNode(node) {
    const lesson=lessons.get(node.lesson), cell=node.cell!==undefined?lesson.cells[node.cell]:null;
    if(cell?.type==='code')return codeCell(lesson,cell,node.cell);
    let source=node.source??cell?.source??'';
    // Unit titles are part of the course outline; source subheadings stay subordinate.
    if(lesson.main)source=source.replace(/^## \d+\.[^\n]*\n*/, '').replace(/^## 练习与自检\s*\n*/, '');
    if(source.startsWith('---\n'))source=source.replace(/^---\n([\s\S]*?)\n---\n/, '```yaml\n$1\n```\n');
    const fragment=document.createElement('div');fragment.innerHTML=markdown(source,lesson.path);
    fragment.querySelectorAll('h1,h2,h3').forEach(h=>{const sub=document.createElement(h.tagName==='H3'?'h5':'h4');sub.textContent=h.textContent;h.replaceWith(sub);});
    return `<div class="reading-fragment" data-source-path="${esc(lesson.path)}">${fragment.innerHTML}</div>`;
  }
  function taskChecks(root) {
    root.querySelectorAll('tr').forEach(tr=>{
      const cell=tr.querySelector('td');if(!cell)return;const id=cell.textContent.trim();if(!/^S\d+\.\d+$/.test(id))return;
      cell.innerHTML=`<label class="task-check"><input type="checkbox" data-task="${esc(id)}" ${progress.tasks[id]?'checked':''}><span>${esc(id)}</span></label>`;
    });
  }
  function bindNotes(id) {
    $('#lesson-notes').addEventListener('input',e=>{progress.notes[id]=e.target.value;persist();});
  }
  const noteBox = id => `<div class="lesson-note"><label for="lesson-notes">写下你的理解与实验记录 <span class="tiny">· 自动保存在当前浏览器</span></label><textarea id="lesson-notes" placeholder="我的场景是什么？观察到了什么？哪里失败了，怎样修复？">${esc(progress.notes[id]||'')}</textarea></div>`;
  function stagePage(stage) {
    const r=stage.reading, lesson=lessons.get(stage.lesson);
    current=lesson;progress.last=lesson.id;persist();
    readingTargets=new Map([[stage.lesson,'course-walkthrough'],[stage.tasks,'course-tasks']]);
    r.units.forEach((unit,i)=>[...unit.before,...unit.body,...unit.after].forEach(node=>{if(!readingTargets.has(node.lesson))readingTargets.set(node.lesson,`course-unit-${i}`);}));
    const covered=new Set(readingTargets.keys()), extensions=catalog.extensions.filter(e=>e.after===stage.id);
    const unitHtml=r.units.map((unit,i)=>{
      const sources=[...new Set([...unit.before,...unit.body,...unit.after].map(n=>n.lesson))];
      return `<section class="course-unit" id="course-unit-${i}"><h3><span class="unit-number">${String(i+1).padStart(2,'0')}</span>${esc(unit.title)}</h3>${unit.before.map(readingNode).join('')}${unit.body.map(readingNode).join('')}${unit.after.map(readingNode).join('')}<div class="source-note">本节原文：${sources.map(id=>`<a href="${readUrl(id)}">${esc(id.split('/').pop())}</a>`).join(' · ')}</div></section>`;
    }).join('');
    const sections=[['course-problem','1. 分析题目'],['course-thinking','2. 如何实现'],['course-walkthrough','3. 按步骤实现'],...r.units.map((u,i)=>[`course-unit-${i}`,u.title,'unit']),['course-experiment','4. 运行与验证'],['course-tasks','5. 验收与总结'],['course-resources','6. 继续学习']];
    const next=catalog.stages[stage.id+1],prev=catalog.stages[stage.id-1];
    shell(`<header class="page-heading course-heading"><div class="lesson-meta"><span class="eyebrow">STEP ${String(stage.id).padStart(2,'0')} / ${stage.english.toUpperCase()}</span><span class="tag">主线课程</span></div><h1>${esc(stage.title)}</h1><p>${esc(stage.description)}</p><div class="reading-order">分析题目 <span>→</span> 推导思路 <span>→</span> 逐步实现 <span>→</span> 实验与总结</div></header>
      <div class="reader-layout course-layout"><article class="reader course-reader"><div class="prose" id="lesson-content">
        <section id="course-problem" class="course-chapter"><h2>1. 分析题目</h2><p class="course-question">${esc(r.question)}</p><p>${esc(r.analysis)}</p><p class="deliverable"><strong>本章要交什么</strong>${esc(r.deliverable)}</p></section>
        <section id="course-thinking" class="course-chapter"><h2>2. 如何实现</h2><p>${esc(r.thinking)}</p><ol class="implementation-flow">${r.flow.map(s=>`<li>${esc(s)}</li>`).join('')}</ol></section>
        <section id="course-walkthrough" class="course-chapter"><h2>3. 按步骤实现</h2><p>按下面的顺序读解释和代码。先预测结果，再运行整章；想改一格验证猜想时，用章末的 Notebook 在本机编辑。</p>
          <div class="course-setup"><h3>运行前准备</h3><p>这格只定位仓库、导入后面会用到的辅助函数。代码按原 Notebook 顺序保留；网页实验会在独立内核中从头执行。</p>${r.setup.map(readingNode).join('')}<p class="execution-note">先分清两种运行：离线实验验证程序流程；真实实践验证模型与外部工具的表现。<code>ReplayModel</code> 返回预先写好的响应，不会自己推理。页面中保存的输出也不代表本次执行。</p></div>
          ${unitHtml}</section>
        <section id="course-experiment" class="course-chapter"><h2>4. 运行与验证</h2><p>读完实现后，先运行本章离线实验，核对实际输出。${stage.id>0?'再运行真实实践，记录模型、工具结果和失败；运行结束后仍需按下方任务单判断作品是否达标。':'本章用回放观察控制流程，下一章再连接真实模型。'}</p><div class="lesson-actions"><button class="primary" data-action="run" data-lesson="${esc(lesson.id)}">运行本章实验</button>${stage.id>0?`<button class="secondary" data-action="practice" data-lesson="${esc(lesson.id)}">真实实践</button>`:''}<a class="text-link" href="${esc(lesson.download)}" download>下载 Notebook，修改代码 ↗</a></div>${stage.id===2?`<p class="execution-note">上面的完整诊断本有独立定义和服务开关。<button class="inline-action" data-action="run" data-lesson="step2/step2_stage2_diagnostics_fixed.ipynb">运行完整诊断本的离线测试</button>；真实 embedding 与联网研究使用「真实实践」。</p>`:''}${r.exercise.map(readingNode).join('')}</section>
        <section id="course-tasks" class="course-chapter"><h2>5. 验收与总结</h2><p class="course-recap">${esc(r.recap)}</p><p>对照原课程逐项检查。勾选记录自己的完成情况；实验运行通过不会自动完成课程验收。</p><div class="assessment">${readingNode(r.assessment)}</div></section>
        </div>${noteBox(lesson.id)}<div class="course-completion"><button class="secondary" data-action="complete" data-lesson="${esc(lesson.id)}">${progress.done.includes(lesson.id)?'✓ 已学完本阶段':'标记本阶段已学完'}</button><span>保存学习进度后，可以继续下一章。</span></div>
        <section id="course-resources" class="course-resources"><h2>6. 继续学习</h2><p>${esc(r.next)}</p>${extensions.length?`<p>可选拓展：${extensions.map(e=>`<a href="${readUrl(e.lesson)}">${esc(e.title)}</a>`).join(' · ')}。不影响进入下一主线阶段。</p>`:''}<details><summary>查看本章原始文件与补充资料</summary><p class="tiny">正文已按学习顺序展开所需材料；这里供查阅原文与深入源码。</p><div class="appendix-links">${[stage.lesson,...stage.resources].map(id=>`<a href="${readUrl(id)}">${esc(id)}${covered.has(id)?' · 已融入正文':''}</a>`).join('')}</div></details></section></article>
        <aside class="toc" aria-label="本章阅读目录"><div class="toc-label">本章阅读顺序</div><div id="toc-links">${sections.map(([id,title,kind])=>`<a class="${kind==='unit'?'toc-unit':''}" href="${stageUrl(stage.id,id)}" data-scroll="${id}">${esc(title)}</a>`).join('')}</div><div class="reading-position" aria-live="off">顺着正文阅读即可，目录可直接定位。</div></aside></div>
      <nav class="reader-bottom">${prev?`<a href="${stageUrl(prev.id)}"><small>← STEP ${prev.id}</small>${esc(prev.title)}</a>`:'<a href="#home"><small>← 学习路线</small>回到课程首页</a>'}${next?`<a href="${stageUrl(next.id)}"><small>STEP ${next.id} →</small>${esc(next.title)}</a>`:'<a href="#extensions"><small>继续探索 →</small>选择策略拓展</a>'}</nav>`, 'home',`Step ${stage.id} · ${stage.title}`);
    highlightCode($('#lesson-content'));taskChecks($('#lesson-content'));bindNotes(lesson.id);
    if('IntersectionObserver' in window){
      readingObserver=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(!entry.isIntersecting)return;$('#toc-links .active')?.classList.remove('active');document.querySelector(`#toc-links [data-scroll="${entry.target.id}"]`)?.classList.add('active');});},{rootMargin:'-5% 0px -75% 0px'});
      sections.forEach(([id])=>readingObserver.observe(document.getElementById(id)));
    }
  }
  function lessonPage(lesson) {
    if (!lesson) { shell('<div class="empty">这份资料不存在。<a href="#home">返回路线</a></div>'); return; }
    current=lesson;
    const stage=catalog.stages[lesson.stage];
    const download = lesson.kind==='notebook'?`<a class="secondary" href="${esc(lesson.download)}" download>↓ 下载 Notebook</a>`:'';
    const run=lesson.runnable?`<button class="secondary" data-action="run" data-lesson="${esc(lesson.id)}" aria-label="运行本章实验">▷ 运行本章实验</button>${lesson.main&&lesson.stage>0?`<button class="secondary" data-action="practice" data-lesson="${esc(lesson.id)}" aria-label="真实实践">↗ 真实实践</button>`:''}`:'';
    shell(`<div class="page-heading"><div class="lesson-meta"><span class="eyebrow">${lesson.track==='extension'?'OPTIONAL EXPLORATION':'SOURCE MATERIAL'}</span></div><h1>${esc(lesson.title)}</h1><p>${esc(lesson.path)}</p>${stage?`<a class="text-link" href="${stageUrl(stage.id)}">← 回到 Step ${stage.id} 连续课程</a>`:''}<div class="lesson-actions">${run}${download}</div></div>
      <div class="reader-layout"><article class="reader"><div class="prose" id="lesson-content">${lessonBody(lesson)}</div>${noteBox(lesson.id)}</article><aside class="toc"><div class="toc-label">原文目录</div><div id="toc-links"></div></aside></div>`,lesson.id==='GLOSSARY.md'?'glossary':lesson.track==='extension'?'extensions':'library',stage?`Step ${stage.id} · 原始资料`:'学习资料');
    highlightCode($('#lesson-content'));
    let toc='';$('#lesson-content').querySelectorAll('h1,h2,h3').forEach((h,i)=>{h.id='section-'+i;if(h.tagName!=='H3')toc+=`<a href="#${h.id}" data-scroll="${h.id}">${esc(h.textContent)}</a>`;});$('#toc-links').innerHTML=toc;
    bindNotes(lesson.id);taskChecks($('#lesson-content'));
  }
  function resourceItem(l) { if(!l)return '';return `<a class="resource-item" href="${readUrl(l.id)}"><div><h3>${esc(l.title)}</h3><p>${esc(l.path)}</p></div><span class="quiet-tag">${l.kind==='notebook'?'Notebook':l.kind==='source'?'源码':'笔记'} ↗</span></a>`; }
  function library() {
    current=null;
    let list=catalog.lessons.filter(l=>filter==='all'||(filter==='notebook'?l.kind==='notebook':filter==='notes'?l.kind==='document':l.kind==='source'));
    shell(`<div class="page-heading"><span class="eyebrow">YOUR LEARNING LIBRARY</span><h1>内容都在，入口更清楚。</h1><p>课程讲解、原有笔记、实验、论文阅读和源码完整收录。课程正文是起点，资料库是随时可以回来的书架。</p></div><div class="filter-row">${[['all','全部 '+catalog.lessons.length],['notes','学习笔记'],['notebook','Notebook'],['source','代码与配置']].map(([key,label])=>`<button class="filter-chip ${filter===key?'active':''}" data-filter="${key}">${label}</button>`).join('')}<button class="filter-chip" data-action="search">⌕ 搜索全部内容</button></div><div class="resource-list">${list.map(resourceItem).join('')}</div>`,'library','资料与源码');
  }
  let demoStep=0;
  function playground() {
    current=null;
    shell(`<div class="page-heading"><span class="eyebrow">ONE LOOP, EXPLAINED</span><h1>先看一轮，再读代码。</h1><p>用户要买 4 支铅笔，但我们还不知道单价。点击下一步，看看程序、模型和工具分别做什么。</p></div><div class="flow-demo"><span class="tag">交互演示 · 使用固定规则，不调用 LLM</span><div class="flow-steps">${['任务输入','选择工具','执行工具','观察反馈','给出答案'].map((t,i)=>`<span class="flow-node ${i===demoStep?'active':''}">${i+1}. ${t}</span>`).join('')}</div><div class="flow-caption" id="flow-caption"></div><pre id="flow-code" style="font:13px/1.9 Consolas,monospace;white-space:pre-wrap;padding:18px;background:#fff9;border-radius:8px"></pre><div class="flow-buttons"><button class="primary" data-action="demo-next">${demoStep===4?'再看一遍':'下一步 →'}</button><a class="secondary" href="${stageUrl(1)}">去课程里亲手实现 ↗</a></div></div><div class="tip">关键区别：模型提出工具请求，程序执行函数，工具返回观察。模型说“算好了”不代表工具真的执行过；日志与结果让这条链可以核查。</div>`,'home','交互小实验');
    const messages=[['问题出现了','用户想知道总价，但缺少单价。任务由人提出，后续需要根据返回的信息决定。','question = "4 支铅笔多少钱？"'],['选择下一步','教学策略先请求查询单价。模型负责提出动作；分发器只按工具名找到函数。','action = {"name": "lookup_price", "arguments": {"item": "铅笔"}}'],['程序执行工具','registry 是名字到函数的映射；handler(**arguments) 才真正执行。','handler = registry[action["name"]]\nprice = handler(**action["arguments"])  # 3 元'],['观察改变后续动作','知道单价后才有依据计算。如果工具说查不到，就应该承认资料不足。','observation = {"price": 3}\nnext_action = {"name": "multiply", "arguments": {"a": 4, "b": 3}}'],['基于工具结果结束','4 × 3 = 12。观察、决策、执行形成闭环，停止条件保证它不会无限行动。','result = multiply(4, 3)\nanswer = "4 支铅笔共 12 元。"']];
    $('#flow-caption').textContent=messages[demoStep][0]+'：'+messages[demoStep][1];$('#flow-code').textContent=messages[demoStep][2];
  }
  function route() {
    const hash=location.hash.slice(1)||'home';
    if(hash.startsWith('section-'))return;
    readingTargets=new Map();readingObserver?.disconnect();
    const parts=hash.split('/');
    if(parts[0]==='stage') {const s=catalog.stages[Number(parts[1])];if(!s)return home();stagePage(s);}
    else if(parts[0]==='read')lessonPage(lessons.get(decodeURIComponent(parts.slice(1).join('/'))));
    else if(hash==='extensions')extensions();else if(hash==='library')library();else if(hash==='playground')playground();else home();
    window.scrollTo(0,0);
    if(parts[0]==='stage'){
      const target=({prerequisite:'course-unit-0',tasks:'course-tasks',resources:'course-resources'})[parts[2]]||parts[2];
      if(target?.startsWith('course-'))document.getElementById(target)?.scrollIntoView({behavior:'instant'});
    }
  }
  function openSearch() {$('#search-dialog').showModal();$('#search-input').value='';search('');$('#search-input').focus();}
  function search(query) {
    const q=query.toLocaleLowerCase().trim();
    const results=q?catalog.lessons.filter(l=>(l.title+' '+l.path+' '+l.cells.map(c=>c.source).join('\n')).toLocaleLowerCase().includes(q)).slice(0,30):catalog.stages.map(s=>lessons.get(s.lesson));
    $('#search-results').innerHTML=results.length?results.map(l=>{
      const text=l.cells.map(c=>c.source).join(' '),index=text.toLocaleLowerCase().indexOf(q);
      const excerpt=q?text.slice(Math.max(0,index-30),index+100).replace(/[#*`\n]/g,' '):l.path;
      const stage=l.stage===null?null:catalog.stages[l.stage];
      const inCourse=stage&&[stage.lesson,stage.prerequisite,stage.tasks].includes(l.id);
      const target=l.id===stage?.tasks?'course-tasks':l.id===stage?.prerequisite?'course-unit-0':'lesson';
      return `<a class="search-result" href="${inCourse?stageUrl(stage.id,target):readUrl(l.id)}" data-search-result><strong>${esc(l.title)}</strong><p>${esc(excerpt)}</p><small>${esc(l.path)}</small></a>`;
    }).join(''):'<div class="empty">没有找到这个词，试试 dispatcher、RAG 或 reflection。</div>';
  }
  async function runLesson(id, mode='offline') {
    const generation = ++pollGeneration, jobKey = id + ':' + mode;
    const l=lessons.get(id);$('#run-dialog').showModal();$('#run-title').textContent=l.title;$('#run-output').textContent='';$('#run-actions').innerHTML='';
    $('#run-description').textContent='用独立内核运行本章的默认离线实验，关闭外部模型/联网开关。浏览器章节会实际启动本地 Chromium。';
    if(mode==='practice') $('#run-description').textContent='运行本阶段已有的真实实践脚本，连接本机 Ollama，结果保存在独立目录。'+([2,3,6].includes(l.stage)?'本阶段还会读取公开资料或下载固定版本源码。':l.stage===8?'本阶段会创建验收环境与测试报告。':'模型成绩与失败请查看实际输出。');
    if(!api) {$('#run-status').textContent='当前是阅读模式，需要本机学习服务才能执行 Python。';$('#run-output').textContent='在项目根目录启动：\n\npython -m learning.web_server\n\n然后打开终端显示的本地地址。可直接在网页运行实验；想修改代码则下载 Notebook 在 VS Code / Jupyter 打开。';return;}
    $('#run-status').className='run-status';$('#run-status').textContent=mode==='practice'?'正在启动本阶段真实实践…':'正在启动独立 Python 内核…';
    try {
      let body;
      if(activeJobs.has(jobKey))body={id:activeJobs.get(jobKey)};
      else{const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json','X-MiniAgent-Token':api.token},body:JSON.stringify({lesson:id,mode})});
        body=await response.json();if(!response.ok)throw Error(body.error||'无法启动实验');activeJobs.set(jobKey,body.id);}
      const poll=async()=>{const r=await fetch('/api/jobs/'+body.id);const job=await r.json();if(generation!==pollGeneration)return;$('#run-output').textContent=job.log||'内核正在启动，请稍等…';
        $('#run-status').textContent=job.status==='running'?'实验运行中 · 不影响原始 Notebook':job.status==='passed'?(mode==='practice'?'✓ 真实实践运行结束（成绩见输出）':'✓ 实验执行通过'):'实验未通过 · 请查看实际错误';
        $('#run-status').className='run-status'+(job.status==='failed'?' error':'');
        if(job.status==='running')pollTimer=setTimeout(poll,900);else{activeJobs.delete(jobKey);if(job.status==='passed')$('#run-actions').innerHTML='<div class="tip">这是代码运行结果。阅读和任务完成情况请自行勾选。</div>';}
      };await poll();
    } catch(error) {$('#run-status').className='run-status error';$('#run-status').textContent=error.message;}
  }
  document.addEventListener('click',async event=>{
    const el=event.target.closest('[data-action],[data-copy],[data-scroll],[data-filter],[data-search-result]');if(!el)return;
    if(el.hasAttribute('data-search-result'))$('#search-dialog').close();
    if(el.dataset.scroll){event.preventDefault();document.getElementById(el.dataset.scroll)?.scrollIntoView({behavior:'smooth'});return;}
    if(el.dataset.copy!==undefined){const source=lessons.get(el.dataset.source)?.cells[Number(el.dataset.copy)]?.source;if(source===undefined)return;try{await navigator.clipboard.writeText(source);toast('代码已复制');}catch{toast('复制受浏览器限制，请在代码框内选择复制');}return;}
    if(el.dataset.filter){filter=el.dataset.filter;library();return;}
    switch(el.dataset.action){case 'menu':$('.sidebar').classList.toggle('open');break;case 'search':openSearch();break;case 'close-search':$('#search-dialog').close();break;case 'close-run':$('#run-dialog').close();break;case 'run':runLesson(el.dataset.lesson);break;case 'practice':runLesson(el.dataset.lesson,'practice');break;
      case 'complete':{const id=el.dataset.lesson;progress.done=progress.done.includes(id)?progress.done.filter(v=>v!==id):[...progress.done,id];persist();const top=window.scrollY;route();window.scrollTo({top,behavior:'instant'});toast(progress.done.includes(id)?'已记录学习进度':'已取消完成标记');break;}
      case 'demo-next':demoStep=(demoStep+1)%5;playground();break;
    }
  });
  document.addEventListener('change',e=>{if(e.target.dataset.task){progress.tasks[e.target.dataset.task]=e.target.checked;persist();}});
  document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch();}});
  $('#search-input').addEventListener('input',e=>search(e.target.value));
  window.addEventListener('hashchange',route);
  $('#run-dialog').addEventListener('close',()=>{clearTimeout(pollTimer);pollGeneration++;});
  async function init(){try{
    const response=await fetch('catalog.json');if(!response.ok)throw Error('课程内容未生成');catalog=await response.json();lessons=new Map(catalog.lessons.map(l=>[l.id,l]));
    try{const status=await fetch('/api/status');if(status.ok&&status.headers.get('content-type')?.includes('application/json'))api=await status.json();}catch{}
    route();
  }catch(error){$('#app').innerHTML=`<div class="empty"><h1>学习站还差一步准备</h1><p>${esc(error.message)}</p><pre>python -m learning.web_server</pre></div>`;}}
  init();
})();
