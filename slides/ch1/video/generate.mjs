// Ch1 Vibe Coding 工作流 · HyperFrames 组合生成器
// 读取 ../script.md，按每页口播字数（260 字/分钟）推算各场景时长，
// 产出静态时序的 index.html（确定性渲染：无时钟、无随机、无网络取材）。
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const script = readFileSync(join(HERE, "..", "script.md"), "utf8");

// ---------- 1. 按口播字数计时 ----------
const CHAR_PER_SEC = 260 / 60;
const sections = [];
for (const m of script.matchAll(/^## (第 (\d+) 页[^\n]*)\n([\s\S]*?)(?=^## |\n---\n[\s\S]*$)/gm)) {
  const body = m[3].replace(/\s+/g, "");
  sections.push({ page: +m[2], chars: body.length });
}
if (sections.length !== 20) throw new Error(`期望 20 页，实际 ${sections.length}`);

let cursor = 0;
const timing = sections.map(s => {
  const dur = Math.max(6, Math.round(s.chars / CHAR_PER_SEC) + 1.8);
  const t = { page: s.page, chars: s.chars, start: +cursor.toFixed(2), dur };
  cursor += dur;
  return t;
});
const TOTAL = +cursor.toFixed(2);

// ---------- 2. 设计系统 ----------
const CSS = `
  @font-face { font-family:'PingFang SC'; src:local('PingFang SC'); }
  @font-face { font-family:'Hiragino Sans GB'; src:local('Hiragino Sans GB'); }
  @font-face { font-family:'Microsoft YaHei'; src:local('Microsoft YaHei'); }
  @font-face { font-family:'Cascadia Code'; src:local('Cascadia Code'); }
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:1920px; height:1080px; overflow:hidden; background:#d8d6cd; }
  body { font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Segoe UI",sans-serif; color:#1d2a25; }
  .mono, code { font-family:"SF Mono","Cascadia Code","JetBrains Mono",Consolas,monospace; }
  #root { position:relative; width:1920px; height:1080px; overflow:hidden; }
  .clip { position:absolute; inset:0; }
  .bg { position:absolute; inset:0; background:#f1f0ea; }
  .bg.deep { background:#e9e8df; }
  .pad { position:absolute; inset:0; padding:130px 160px 150px; display:flex; flex-direction:column; }

  .kicker { font-size:30px; font-weight:700; letter-spacing:.24em; color:#1f5c46; margin-bottom:34px; }
  h1.head { font-size:88px; font-weight:700; letter-spacing:-.01em; line-height:1.18; margin-bottom:56px; }
  h1.head .thin { font-weight:400; color:#68706b; }
  .foot { margin-top:auto; font-size:34px; color:#68706b; }
  .foot b { color:#174a39; }

  .card { display:block; background:#fff; border:2px solid #e2e0d4; border-radius:22px;
          box-shadow:9px 9px 0 0 #dedcce; padding:36px 44px; }
  .card h3 { font-size:40px; margin-bottom:14px; color:#1d2a25; }
  .card p { font-size:33px; line-height:1.55; color:#424b46; }
  .card.pine { background:#1f5c46; border-color:#174a39; box-shadow:9px 9px 0 0 rgba(29,42,37,.18); }
  .card.pine h3, .card.pine p { color:#eef6f1; }
  .card.warn { background:#fbf1df; border-color:#e8cfa0; box-shadow:9px 9px 0 0 rgba(143,90,22,.16); }
  .card.warn h3 { color:#8f5a16; } .card.warn p { color:#6e4a17; }

  .term { display:block; background:#16241e; border:2px solid #0e1b15; border-radius:20px;
          box-shadow:9px 9px 0 0 rgba(29,42,37,.2); padding:36px 44px;
          font-size:32px; line-height:1.7; color:#d9e6de; white-space:pre; }
  .term .c { color:#6e8b7f; } .term .hl { color:#9fd3b4; font-weight:700; }
  .term .err { color:#e88b7a; font-weight:700; }

  .row { display:flex; gap:36px; }
  .row > * { flex:1; min-width:0; }

  .chip { display:inline-block; background:#fff; border:2px solid #e2e0d4; box-shadow:5px 5px 0 0 #dedcce;
          border-radius:999px; padding:12px 34px; font-size:32px; font-weight:600; color:#1f5c46; }
  .chiprow { display:flex; flex-wrap:wrap; gap:22px; }

  .flow { display:flex; align-items:center; gap:14px; }
  .fstep { display:block; background:#fff; border:2px solid #1f5c46; border-radius:16px;
           box-shadow:6px 6px 0 0 #dedcce; padding:16px 28px; font-size:34px; font-weight:700; color:#174a39; }
  .farr { display:block; color:#1f5c46; font-size:38px; font-weight:700; }

  .qrow { display:flex; align-items:center; gap:20px; margin-bottom:22px; }
  .qbadge { display:block; width:72px; height:72px; border-radius:18px; background:#1f5c46; color:#fff;
            box-shadow:5px 5px 0 0 #dedcce; font-size:34px; font-weight:700; text-align:center; line-height:72px; flex:none; }
  .qtext { font-size:36px; line-height:1.4; color:#1d2a25; }
  .qtext small { display:block; font-size:28px; color:#5d655f; margin-top:6px; }

  .num-giant { font-size:340px; font-weight:700; line-height:1; color:#1f5c46;
               text-shadow:14px 14px 0 rgba(31,92,70,.18), 28px 28px 0 rgba(31,92,70,.07); }
  .div-title { font-size:96px; font-weight:700; letter-spacing:-.01em; margin:26px 0 40px; }
  .div-desc { font-size:42px; color:#46564e; line-height:1.6; }

  .stack { position:absolute; right:170px; top:50%; margin-top:-260px; width:470px; height:330px; }
  .stack i { position:absolute; display:block; border-radius:24px; border:2px solid rgba(29,42,37,.08); }
  .stack i:nth-child(1) { width:360px; height:232px; left:0; top:96px; background:#dfe9e2; }
  .stack i:nth-child(2) { width:374px; height:242px; left:44px; top:48px; background:#cdddd2; }
  .stack i:nth-child(3) { width:380px; height:250px; left:90px; top:0; background:#16241e; border-color:#0e1b15; box-shadow:12px 12px 0 0 #dedcce; }
  .stack .prompt { position:absolute; left:132px; top:44px; font-size:46px; font-weight:700; color:#9fd3b4; }

  #brandbar { position:absolute; left:64px; bottom:44px; font-size:24px; color:#6f6d66; letter-spacing:.14em; }
  #progress { position:absolute; left:0; bottom:0; width:1920px; height:12px; background:#dedcce; }
  #progress-fill { display:block; width:100%; height:100%; background:#35a97a; transform-origin:left center; }
`;

// ---------- 3. 场景内容（由口播稿蒸馏） ----------
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const kick = t => `<div class="kicker mono an an-k">${t}</div>`;
const head = t => `<h1 class="head an an-h">${t}</h1>`;

const S = [];
const scene = (id, inner, cls = "") =>
  S.push({ id, cls, inner });

// P1 封面
scene("p01", `
  ${kick("AI 摸鱼的梁师傅 · CH1")}
  ${head('Vibe Coding 工作流<span class="thin">　让 AI 替你写代码</span>')}
  <div class="chiprow an an-c">
    <span class="chip mono">提需求</span><span class="chip mono">读懂</span>
    <span class="chip mono">修改</span><span class="chip mono">运行验证</span>
  </div>
  <div class="foot an an-f">这一章的规矩：<b>AI 负责打字，你负责判断</b>　·　交付一个真的每周一早上会用的周报生成器</div>
  <div class="stack"><i></i><i></i><i></i><span class="prompt mono an an-s">&gt;_</span></div>
`);

// P2 路线
scene("p02", `
  ${kick("本章路线")}
  ${head("四个部分，一条主线")}
  <div class="row an an-c">
    <div class="card"><h3 class="mono">01</h3><p>心智转变<br>五步工作流</p></div>
    <div class="card"><h3 class="mono">02</h3><p>指令四要素<br>一次做对</p></div>
    <div class="card"><h3 class="mono">03</h3><p>实战<br>周报生成器</p></div>
    <div class="card"><h3 class="mono">04</h3><p>调试基本功<br>traceback + 3 bugs</p></div>
  </div>
  <div class="foot an an-f">前两部分几乎不写代码，但<b>别跳</b>——它决定你是一轮拿到能用的代码，还是跟 AI 拉扯十轮</div>
`);

// P3 分隔 01
scene("p03", `
  <div class="num-giant mono an an-n">01</div>
  <div class="div-title an an-h">心智转变与五步工作流</div>
  <div class="div-desc an an-f">Vibe Coding 最大的坑不在技术，在心态——<br>「AI 能写」不等于「我不用懂」</div>
`, "divider");

// P4 副驾
scene("p04", `
  ${kick("PART 01 · 心智转变")}
  ${head("AI 是副驾，你是驾驶员")}
  <div class="row an an-c">
    <div class="card warn"><h3>陷阱：全权代写，你只说「好」</h3><p>项目跑起来了，表现和期待天差地别，<br>而且 review 不动、不知道哪块代码管哪块功能</p></div>
    <div class="card pine"><h3>铁律（全课程适用）</h3><p>AI 生成的代码，你要能说清它在干嘛。<br>说不清的：要么问懂，要么删掉重来</p></div>
  </div>
`);

// P5 五步循环
scene("p05", `
  ${kick("PART 01 · 五步工作流")}
  ${head("是个循环，不是流水线")}
  <div class="flow an an-c" style="margin-bottom:44px">
    <span class="fstep">提需求</span><span class="farr">→</span>
    <span class="fstep">AI 生成</span><span class="farr">→</span>
    <span class="fstep">读懂</span><span class="farr">→</span>
    <span class="fstep">修改</span><span class="farr">→</span>
    <span class="fstep">运行验证</span><span class="farr">→</span>
    <span class="fstep">交付</span>
  </div>
  <div class="chiprow an an-c" style="margin-bottom:40px">
    <span class="chip">报错 / 不满意 → 回到「提需求」</span>
  </div>
  <div class="foot an an-f">「读懂」和「修改」是两种能力——<b>看懂了 ≠ 改得动</b>；循环转三五轮是常态，别因此觉得自己不行</div>
`);

// P6 三问法
scene("p06", `
  ${kick("PART 01 · 读懂代码")}
  ${head("三问法")}
  <div style="margin-bottom:44px" class="an an-c">
    <div class="qrow"><span class="qbadge mono">1</span><div class="qtext">这个文件<small>整体</small>在干什么？<small>标准：一句话说清</small></div></div>
    <div class="qrow"><span class="qbadge mono">2</span><div class="qtext">每个<small>函数</small>在干什么？<small>输入是什么 · 输出是什么 · 谁调用它</small></div></div>
    <div class="qrow"><span class="qbadge mono">3</span><div class="qtext">我<small>改哪里</small>会改变什么？<small>找「拧一下就有效果」的旋钮：prompt、模型名、输出文件名</small></div></div>
  </div>
  <div class="term an an-t" style="font-size:30px">问法模板：<span class="hl">「解释第 X 行到第 Y 行在做什么，为什么要这样写」</span>  <span class="c">#「为什么」比「是什么」值钱</span></div>
`);

// P7 AI 出题
scene("p07", `
  ${kick("PART 01 · AI 出题考核")}
  ${head("让 AI 出题，考你自己")}
  <div class="row an an-c" style="margin-bottom:40px">
    <div class="card"><h3>怎么考</h3><p>让 AI 当严格面试官，出三道阅读理解：<br>整体在做什么 / 某个行为 / 改某处会怎样<br>一次一道，先批改再出下一道</p></div>
    <div class="card pine"><h3 class="mono">及格线 · 三道对两道</h3><p>答错的让它讲解，<br>再出一道同类题重答</p></div>
  </div>
  <div class="foot an an-f">提问是<b>输入</b>，被考核是<b>输出</b>——只有输出才能暴露真实的理解缺口 · 做完考核，弹幕扣个 1</div>
`);

// P8 分隔 02
scene("p08", `
  <div class="num-giant mono an an-n">02</div>
  <div class="div-title an an-h">指令四要素</div>
  <div class="div-desc an an-f">跟 AI 协作，写指令的能力比写代码的能力更稀缺——<br>同一个需求，指令质量决定一轮拿到，还是拉扯十轮</div>
`, "divider");

// P9 差 vs 好
scene("p09", `
  ${kick("PART 02 · 差指令 vs 好指令")}
  ${head("四个要素，一次说清")}
  <div class="row an an-c">
    <div class="term" style="font-size:30px"><span class="c">$</span> 帮我写个周报工具

<span class="c"># AI 只能瞎猜：</span>
<span class="err">?</span> 什么语言
<span class="err">?</span> 输入从哪来
<span class="err">?</span> 调哪个模型
<span class="err">?</span> 输出成什么样</div>
    <div class="card"><h3>四要素齐全</h3><p><b class="mono" style="color:#1f5c46">【任务】</b>做什么、产出什么文件<br><b class="mono" style="color:#1f5c46">【上下文】</b>输入、SDK、.env、模型名<br><b class="mono" style="color:#1f5c46">【约束】</b>单文件、不超过 80 行、四节 Markdown<br><b class="mono" style="color:#1f5c46">【验收】</b>生成 weekly_report.md，四节齐全、动词开头</p></div>
  </div>
  <div class="foot an an-f">把<b>【验收】</b>写清楚，AI 自己都会往这个标准上凑</div>
`);

// P10 速查表
scene("p10", `
  ${kick("PART 02 · 速查表")}
  ${head("每个要素都在回答一个问题")}
  <div class="an an-c">
    <div class="qrow"><span class="qbadge mono">任</span><div class="qtext">做什么、产出什么文件<small>缺了：AI 自由发挥，你返工</small></div></div>
    <div class="qrow"><span class="qbadge mono">境</span><div class="qtext">输入从哪来、用什么库、环境如何<small>缺了：代码跟你的环境对不上——新手最常撞的墙</small></div></div>
    <div class="qrow"><span class="qbadge mono">界</span><div class="qtext">语言、框架、格式、长度边界<small>缺了：它会用你还没学的东西，你看不懂</small></div></div>
    <div class="qrow"><span class="qbadge mono">收</span><div class="qtext">怎么证明做好了<small>缺了最惨：你自己都不知道算不算完成</small></div></div>
  </div>
  <div class="foot an an-f">把【任务】换成任意业务、【约束】加上「输出 JSON」——就是 Ch2 的 Prompt Engineering</div>
`);

// P11 分隔 03
scene("p11", `
  <div class="num-giant mono an an-n">03</div>
  <div class="div-title an an-h">实战：周报生成器</div>
  <div class="div-desc an an-f">完整走一遍五步循环，产出一个你每周一早上真的会用的工具——<br>练的不是脚本本身，是那套循环</div>
`, "divider");

// P12 Step 0
scene("p12", `
  ${kick("PART 03 · STEP 0")}
  ${head("建项目（Ch0 技能复热）")}
  <div class="term an an-t" style="font-size:30px">mkdir weekly-report <span class="c">&amp;&amp;</span> cd weekly-report
python -m venv .venv
.venv\\Scripts\\activate
pip install openai python-dotenv
cp ../ch0-hello-llm/.env .

<span class="hl">(.venv)</span> 出现在行首 <span class="c"># 你人在独立环境里了</span></div>
  <div class="foot an an-f">这一步在偷偷验一件事：<b>建 venv、激活、装包，能不能不看教程独立做完</b>——卡住超十分钟，回 Ch0 排错指引</div>
`);

// P13 Step 1/2
scene("p13", `
  ${kick("PART 03 · STEP 1–2")}
  ${head("提需求 → 生成 + 考核")}
  <div class="flow an an-c" style="margin-bottom:44px">
    <span class="fstep">用自己的话重写四要素</span><span class="farr">→</span>
    <span class="fstep">AI 生成</span><span class="farr">→</span>
    <span class="fstep">先跑通</span><span class="farr">→</span>
    <span class="fstep">出题考核 · 三对两</span>
  </div>
  <div class="foot an an-f">重写是为了逼你把四个要素逐个想清楚，<b>照抄等于没练</b> · 仓库里的参考实现是兜底，不是起点——直接抄等于跳过本章全部训练</div>
`);

// P14 Step 3
scene("p14", `
  ${kick("PART 03 · STEP 3")}
  ${head("多轮修改：这才开始 vibe")}
  <div class="row an an-c" style="margin-bottom:40px">
    <div class="card"><h3>改输出</h3><p>每节最多 5 条，多余的合并；<br>语气正式但不僵硬</p></div>
    <div class="card"><h3>改健壮性</h3><p>API 失败要说人话：<br>「请检查 .env 里的 Key」</p></div>
    <div class="card"><h3>加功能</h3><p>末尾追加「本周关键词」，<br>从流水账提炼 3 个词</p></div>
  </div>
  <div class="foot an an-f"><b>每轮改完都要重跑验证</b>——改完不跑，等于没改，这就是「验收标准」的日常用法</div>
`);

// P15 参考实现
scene("p15", `
  ${kick("PART 03 · 参考实现")}
  ${head("卡壳 20 分钟，再打开对照")}
  <div class="row an an-c">
    <div class="term" style="font-size:29px"><span class="hl">load_dotenv</span>()   <span class="c"># 从 .env 读 Key</span>
<span class="hl">RAW_TEXT</span>       <span class="c"># 你的流水账</span>
<span class="hl">PROMPT_TEMPLATE</span> <span class="c"># 旋钮在这</span>
client.chat.completions.create(...)
<span class="hl">main</span>()          <span class="c"># 先验 Key，try 包 API</span></div>
    <div class="card"><h3>交付清单</h3><p>① 脚本能生成 weekly_report.md<br>② 通过出题考核（三对两）<br>③ .gitignore 里有 .env<br>④ add · commit · push 上 GitHub</p></div>
  </div>
  <div class="foot an an-f">对照重点看三处：prompt 单独成变量 · 先判断 Key 再 try · 报错写成人话　·　跑通的弹幕刷个 🎉</div>
`);

// P16 分隔 04
scene("p16", `
  <div class="num-giant mono an an-n">04</div>
  <div class="div-title an an-h">调试基本功</div>
  <div class="div-desc an an-f">报错不是失败，是 Python 在精确地告诉你哪里出了问题——<br>连文件名、行号、原因都替你打印好了；只练一件事：从下往上读</div>
`, "divider");

// P17 traceback
scene("p17", `
  ${kick("PART 04 · TRACEBACK 解剖")}
  ${head("从下往上读")}
  <div class="row an an-c">
    <div class="term" style="font-size:30px">Traceback (most recent call last):
  File "utils.py", line 3
    from report import *
  File "weekly_report.py", line 12
    print(response.text)
<span class="err">NameError: name 'response' is not defined</span>

<span class="c"># ↑ 最后一行：什么错（先看这）</span>
<span class="c"># ↑ 带行号的：在哪错</span>
<span class="c"># ↑ 再往上：怎么走到这的</span></div>
    <div class="card pine"><h3>三步读法</h3><p>① 最后一行 → 什么错<br>② 带行号那行 → 在哪错<br>③ 再往上 → 调用路径</p><p style="margin-top:18px">零基础阶段，<b>90% 的报错只看这两处就能定位</b></p></div>
  </div>
`);

// P18 贴报错模板
scene("p18", `
  ${kick("PART 04 · 贴报错给 AI")}
  ${head("正确姿势：四段 + 一句")}
  <div class="card an an-c" style="margin-bottom:40px"><h3 class="mono">模板</h3><p>① 完整 traceback（复制文字，<b>别截图</b>）　② 我期望什么　③ 实际发生了什么　④ 我已经试过什么<br><b>最后加一句：请先告诉我原因，再告诉我具体改哪几行</b></p></div>
  <div class="foot an an-f">只贴报错不说期望，AI 只能猜；只要改法不要解释，下次同样的错你还是不会 · 对话越聊越乱？<b>敲 /clear 重开</b>，比在乱局里纠缠快得多</div>
`);

// P19 3 bugs
scene("p19", `
  ${kick("PART 04 · 修复实战")}
  ${head("三段预置 bug，必修")}
  <div class="flow an an-c" style="margin-bottom:40px">
    <span class="fstep">运行</span><span class="farr">→</span>
    <span class="fstep">从下往上读</span><span class="farr">→</span>
    <span class="fstep" style="border-color:#c13f2e;color:#c13f2e">先猜</span><span class="farr">→</span>
    <span class="fstep">贴给 AI 验证</span><span class="farr">→</span>
    <span class="fstep">修复</span><span class="farr">→</span>
    <span class="fstep">再运行</span>
  </div>
  <div class="row an an-c" style="margin-bottom:36px">
    <div class="card"><h3 class="mono">bug1 · NameError</h3><p>变量名拼写，最后一行直指答案</p></div>
    <div class="card"><h3 class="mono">bug2 · IndentationError</h3><p>缩进即层级，多一层少一层都不行</p></div>
    <div class="card warn"><h3 class="mono">bug3 · API 401</h3><p>报错不一定是代码问题——是 Key 没读到，环境问题</p></div>
  </div>
  <div class="foot an an-f"><b>先自己猜，再问 AI</b>——跳过猜测，练习就废了 · 每修完一个，往错题本记一行：报错 → 原因 → 解法</div>
`);

// P20 自测 + CTA
scene("p20", `
  ${kick("通关自测")}
  ${head('从「让 AI 代写」<span class="thin">→</span>「用 AI 辅助开发」')}
  <div class="an an-c">
    <div class="qrow"><span class="qbadge mono">✓</span><div class="qtext">五步工作流能说全，「读懂」和「修改」为何拆开能解释</div></div>
    <div class="qrow"><span class="qbadge mono">✓</span><div class="qtext">不看模板能独立写出四要素指令</div></div>
    <div class="qrow"><span class="qbadge mono">✓</span><div class="qtext">周报生成器和 AI 一起写出来，过了出题考核（三对两）</div></div>
    <div class="qrow"><span class="qbadge mono">✓</span><div class="qtext">三段 bug 全修好，能说清 401 为什么不是代码错误</div></div>
    <div class="qrow"><span class="qbadge mono">✓</span><div class="qtext">任意 traceback 三十秒内说出错误类型和出错行</div></div>
    <div class="qrow"><span class="qbadge mono">✓</span><div class="qtext">周报生成器已 push GitHub，.env 没被推上去</div></div>
  </div>
  <div class="foot an an-f">下一章 Ch2 · Prompt Engineering：四要素搬上业务，稳定输出 JSON · <b>一键三连，评论区贴你的四要素指令</b></div>
`);

// ---------- 4. 组装 ----------
const clips = S.map((s, i) => {
  const t = timing[i];
  const bg = s.cls === "divider" ? '<div class="bg deep"></div>' : '<div class="bg"></div>';
  return `    <section id="${s.id}" class="clip${s.cls ? " " + s.cls : ""}" data-start="${t.start}" data-duration="${t.dur}" data-track-index="1">
      ${bg}
      <div class="pad">${s.inner}
      </div>
    </section>`;
}).join("\n");

const tweens = S.map((s, i) => {
  const t0 = timing[i].start;
  const P = `#${s.id}`;
  // 存在性守卫：场景里没有的动画类直接跳过，避免空目标 tween
  return `
  T("${P} .an-k", ${t0});
  T("${P} .an-h", ${t0 + .15});
  T("${P} .an-n", ${t0});
  T("${P} .an-c", ${t0 + .3});
  T("${P} .an-t", ${t0 + .3});
  T("${P} .an-f", ${t0 + .55});
  T("${P} .an-s", ${t0 + .5});`;
}).join("\n");

const html = `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Ch1 Vibe Coding 工作流 · 视频素材</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>${CSS}</style>
  </head>
  <body>
    <div id="root" data-composition-id="ch1-vibe-workflow" data-start="0" data-width="1920" data-height="1080" data-duration="${TOTAL}">
${clips}
      <div id="brandbar" class="mono">AI 摸鱼的梁师傅 · CH1 VIBE CODING 工作流</div>
      <div id="progress"><i id="progress-fill"></i></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const FROM = { k:{opacity:0,y:26}, h:{opacity:0,y:44}, n:{opacity:0,scale:.9},
                     c:{opacity:0,y:54}, t:{opacity:0,y:40}, f:{opacity:0,y:30}, s:{opacity:0,x:40} };
      function T(sel, at) {
        if (!document.querySelector(sel)) return;
        const key = sel.replace(/^.*\.an-([a-z])$/, "$1");
        const from = FROM[key];
        const vars = { opacity:1, duration:key === "n" ? .7 : .55, ease:"power3.out", immediateRender:false };
        if ("y" in from) vars.y = 0; if ("x" in from) vars.x = 0; if ("scale" in from) vars.scale = 1;
        if (key === "c") vars.stagger = .12;
        tl.fromTo(sel, from, vars, at);
      }
${tweens}
      tl.fromTo("#progress-fill", {scaleX:.012}, {scaleX:1, duration:${TOTAL}, ease:"none", immediateRender:false}, 0);
      window.__timelines["ch1-vibe-workflow"] = tl;
    </script>
  </body>
</html>
`;

writeFileSync(join(HERE, "index.html"), html);
console.log(`scenes=20 total=${TOTAL}s (${Math.floor(TOTAL / 60)}m${Math.round(TOTAL % 60)}s)`);
console.table(timing.map(t => ({ page: t.page, chars: t.chars, start: t.start, dur: t.dur })));
