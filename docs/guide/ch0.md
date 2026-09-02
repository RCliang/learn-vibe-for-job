---
title: Ch0 环境与第一行代码（Day 1-2）
outline: [2, 3]
---

# Ch0 环境与第一行代码（Day 1-2）

> **本章 JD 关键词**：Python、API 调用、Git
>
> **学完你能做什么**：搭好本地开发环境（VSCode + Claude Code）、看懂一次 HTTP 请求、管得住 Python 的包（import / pip / venv）、把代码推上 GitHub，并跑通人生第一个 LLM API 调用。

::: info 📋 本章路线
**Day 1**：装好工具（VSCode、Python、Claude Code）→ 接入你的 AI 结对程序员
**Day 2 上午**：HTTP 与 API 基础 · **下午**：Python 工程三件套（import / pip / venv）· **收尾**：Git + 第一个 LLM API 调用
:::

本章是全程唯一的「装环境」章节。**装环境是零基础弃坑的第一高峰**，卡住时直接查本章末尾的[排错指引](#_9-排错指引)，或把报错完整贴给 AI。

---

## 1. Day 1 上午：装好三样东西

### 1.1 安装 VSCode

VSCode 是微软出品的免费代码编辑器，几乎所有公司都在用——**它本身就是简历上合格的一行字**。

1. 打开 [https://code.visualstudio.com](https://code.visualstudio.com)，下载 **Windows** 版（User Installer，x64）
2. 一路下一步安装（勾选「将"通过 Code 打开"操作添加到资源管理器目录上下文菜单」更好用）
3. 装完打开，按 `Ctrl+Shift+X` 打开扩展面板，搜索 **Chinese**，安装「中文（简体）语言包」，按提示重启

::: tip ✅ 验收
能打开 VSCode，界面是中文。
:::

### 1.2 安装 Python（Windows 最大的坑在第一步）

1. 打开 [https://www.python.org/downloads](https://www.python.org/downloads)，下载最新的 Python 3.12+ 安装包
2. **⚠️ 关键一步**：安装第一屏**必须勾选最下方的 `Add python.exe to PATH`**，再点 Install Now

   > 不勾这个，后面所有 `python`、`pip` 命令都会报「不是内部或外部命令」。这是零基础第一天最常见的事故。
3. 安装完成后，**重新打开**一个终端（VSCode 里按 `` Ctrl+` `` 即可打开），输入：

```bash
python --version
# 输出示例：Python 3.13.1
```

::: details 装的时候忘了勾 PATH 怎么办？
最省事的修复：重新运行安装包 → 选 Modify → 一路下一步（它会补上 PATH）；或手动把 Python 安装目录加进系统环境变量 PATH 后重启终端。
:::

### 1.3 终端：你和电脑对话的地方

后面所有命令都在**终端（Terminal）**里敲。三种打开方式，任选：

- VSCode 内按 `` Ctrl+` ``（推荐，终端会自动定位到当前项目目录）
- Windows 开始菜单搜「PowerShell」
- 资源管理器地址栏输入 `powershell` 回车

你需要会的只有这几条命令（今天就会反复用到）：

| 命令 | 作用 | 类比 |
| --- | --- | --- |
| `cd 目录名` | 进入某个文件夹 | 双击打开文件夹 |
| `cd ..` | 返回上一级 | 返回按钮 |
| `dir`（PowerShell 也支持 `ls`） | 看当前文件夹里有什么 | 打开文件夹看文件列表 |
| `cls`（Git Bash 是 `clear`） | 清屏 | 擦黑板 |

---

## 2. Day 1 下午：接入你的 AI 结对程序员

本课程的「Vibe Coding」工具链：**VSCode 写代码 + Claude Code 当结对程序员**，模型能力由 **DeepSeek API** 提供，全程国内可用、不需要海外账号。DeepSeek 按量计费、价格便宜，**充值 10 元足够支撑整个课程**。

::: info 为什么是 DeepSeek
注册即用（手机号）、按量付费不用订阅、价格是主流模型里最低的一档、官方提供 Anthropic 兼容端点可以直接驱动 Claude Code。课程所有代码也默认指向 DeepSeek，但配置全部抽在 `.env` 里——**以后想换智谱、月之暗面等任何 OpenAI 兼容厂商，改两行环境变量即可，代码零改动**（第 3.2 节你会明白为什么）。
:::

### 2.1 开通 DeepSeek API

1. 打开 DeepSeek 开放平台 [https://platform.deepseek.com](https://platform.deepseek.com)，手机号注册登录
2. 左侧「API Keys」→ 创建 API Key，**立即复制保存**（只显示一次）
3. 左侧「充值」→ 充值 10 元左右（按量扣费，用不完一直在）

::: warning 🔑 API Key 就是你的密码
Key 等同于付费凭证：**不发群里、不贴截图、不写进代码提交到 GitHub**。后面我们会用 `.env` 文件保管它。
:::

::: tip 💰 动手前先看一眼价格
各模型现价以[官方价格页](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)为准。放心：本课程全部 API 调用（含 RAG、Agent 项目）总花费大约一杯奶茶的零头。
:::

### 2.2 安装 Claude Code

Claude Code 是一个跑在终端里的 AI 编程助手（TUI，命令行界面）。Windows 安装需要先有 **Node.js 18+** 和 **Git**：

1. **Node.js**：打开 [https://nodejs.org/zh-cn/download](https://nodejs.org/zh-cn/download)，下载 LTS 版安装（一路下一步）
2. **Git**：打开 [https://git-scm.com/install/windows](https://git-scm.com/install/windows) 下载安装（一路下一步，选 VSCode 当默认编辑器更好）
3. **重新打开终端**，安装 Claude Code：

```bash
npm install -g @anthropic-ai/claude-code
claude --version   # 能输出版本号即成功
```

### 2.3 配置 Claude Code 使用 DeepSeek

Claude Code 原生只认 Anthropic 的接口格式，而 DeepSeek 官方提供了 **Anthropic 兼容端点**——只需告诉 Claude Code「把请求发到 DeepSeek」即可（配置方法来自[DeepSeek 官方文档](https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/claude_code/)）。

用编辑器打开 `C:\Users\你的用户名\.claude\settings.json`（文件不存在就新建，注意 `.claude` 是文件夹、`settings.json` 是文件），填入：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "你的DeepSeek api-token",
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "deepseek-v4-pro[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-pro[1m]",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4-flash"
  }
}
```

::: details 抢到了 GLM Coding Plan？也可以用它
如果你订阅了智谱 GLM Coding Plan，把端点、Token 和模型名换成智谱的即可：`ANTHROPIC_BASE_URL` 改为 `https://open.bigmodel.cn/api/anthropic`、Token 用智谱 Key、模型名按[智谱官方文档](https://docs.bigmodel.cn/cn/guide/develop/claude)填写。课程主线按 DeepSeek 讲，用 GLM 不影响任何练习——这正是「配置与代码解耦」的好处。
:::

::: warning ⚠️ 这段配置是全课程最可能「过期」的地方
Claude Code 和模型厂商都在快速迭代，端点 URL、环境变量名、模型名都可能变化。**如果照抄上面没配成功，不要反复重试**，直接去 [DeepSeek 官方的 Claude Code 接入文档](https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/claude_code/)抄最新版配置，再用[排错指引](#_9-排错指引)末尾的「配置过时兜底三步」排查。
:::

### 2.4 第一次对话验证

```bash
mkdir hello-claude && cd hello-claude
claude          # 启动，进入对话界面
```

进入后输入 `/status`，确认模型指向 DeepSeek 即配置成功。试着让它「写一个 Python 的 hello world 并解释每一行」。

### 2.5 备选路径：ZCode（图形界面）

如果命令行实在不适应，可以用 **ZCode** 桌面版（GUI）：官网下载安装后，配置一个 DeepSeek 或其他模型的 API Key 即可使用，无需改配置文件。功能上同样是「AI 结对编程」，后续课程内容两种工具通用。

::: tip 本课程以 Claude Code 为主线讲解
终端里的 AI 编程助手还有 Codex、DeepSeek Harness 等同类可选，课程统一以 Claude Code 为例。ZCode 用户可以照做所有练习，只是操作入口不同。
:::

---

## 3. Day 2 上午：HTTP 与 API 基础（约半天）

**为什么先学这个**：你后面写的每一个 AI 应用，核心动作都是「发一次 HTTP 请求调用 LLM API」。看懂它，后面所有章节的报错你都能自己读一半。

### 3.1 前后端是什么

把一个网站想象成一家餐厅：

- **前端**：大堂和菜单——你看到的界面（网页、按钮、聊天窗口）
- **后端**：后厨——真正做菜的地方（跑在服务器上的程序，负责算出结果）
- **API**：服务员——你（前端）点单，服务员把需求递给后厨（后端），再把菜端回来

「点单」和「上菜」就是两次数据传递，规矩就是 HTTP 协议。

### 3.2 一次 HTTP 请求长什么样

你（客户端）→ 服务器：

| 组成 | 例子 | 说明 |
| --- | --- | --- |
| 方法 | `GET` / `POST` | GET 是「查」，POST 是「交」（提交数据） |
| URL | `https://api.deepseek.com/chat/completions` | 请求打到哪个「窗口」 |
| 请求头 | `Authorization: Bearer 你的Key` | 附带的身份信息 |
| 请求体 | `{"model": "deepseek-chat", "messages": [...]}` | 你提交的数据，JSON 格式 |

服务器 → 你（响应）：

| 组成 | 例子 | 说明 |
| --- | --- | --- |
| 状态码 | `200` | 三位数「暗号」，见下表 |
| 响应体 | `{"choices": [{"message": {...}}]}` | 服务器返回的数据 |

**必须认识这 5 个状态码**（后面天天见）：

| 状态码 | 含义 | 在 LLM 开发中通常意味着 |
| --- | --- | --- |
| `200` | 成功 | 一切正常 |
| `401` | 未授权 | API Key 错了 / 没传 |
| `404` | 找不到 | URL 写错了 |
| `429` | 请求太频繁 | 触发限流，稍等重试 |
| `500` | 服务器内部错误 | 对方的问题，重试或换模型 |

### 3.3 JSON：数据的世界语

API 传递数据几乎都用 JSON（一种文本格式），语法只有三条：

```json
{
  "name": "小明",          // 键: 值（字符串要双引号）
  "age": 18,               // 数字不用引号
  "skills": ["Python", "RAG"], // 数组用 []
  "is_vip": true            // 布尔值 true/false
}
```

::: details 亲眼看见一次真实请求
打开任意网站按 `F12` → Network（网络）面板 → 刷新页面 → 点任意一条请求，看看它的 URL、状态码和 Response。以后调 API 出问题，第一反应就是「打开 Network 看看实际发出去/收回来什么」。
:::

---

## 4. Day 2 下午：Python 最小集——重点讲 import / pip / venv

::: info 教学法：AI 写语法，你管环境
在 Vibe Coding 工作流里，**语法定义让 AI 写，你负责读懂**；但 import / pip / venv 是环境问题，AI 在你电脑上替你做不了主，也是每天都会撞见的报错来源——所以这三件是本章重点，变量/函数等语法压缩成最后的速查表。
:::

### 4.1 import：Python 的积木机制

**一个 `.py` 文件就是一个模块（module），一个装着模块的文件夹就是一个包（package）。** `import` 就是「把别的文件里的代码拿过来用」：

```python
import os                    # 用标准库：Python 自带，无需安装
from openai import OpenAI    # 从第三方包 openai 里，只拿 OpenAI 这个类
import numpy as np           # 太长了，起个短别名
```

三层代码来源，排错时先分清是哪层：

| 来源 | 例子 | 装了吗 |
| --- | --- | --- |
| 标准库（Python 自带） | `os`、`json`、`datetime` | 不用装，直接 import |
| 第三方包 | `openai`、`streamlit` | 要先 `pip install` |
| 你自己写的文件 | `from my_utils import helper` | 文件要放在当前目录 |

**`ModuleNotFoundError: No module named 'xxx'` 排错两步法**（后面每天都会用）：

1. 是**第三方包**吗？→ 是：忘了装或装错环境，`pip install xxx`（见 4.2）
2. 是**自己的文件**吗？→ 是：文件不在当前目录、文件名/大小写打错

### 4.2 pip：装积木的工具

pip 是 Python 的包管理器，从 PyPI（全球包仓库）下载代码包：

```bash
pip install openai          # 安装一个包
pip install openai==1.40.0   # 安装指定版本
pip list                    # 看当前环境装了哪些包
pip uninstall openai        # 卸载
```

**`requirements.txt`——项目的购物清单**：把依赖写进一个文本文件，别人（或服务器、Docker）一条命令装齐：

```bash
pip install -r requirements.txt   # 按清单安装（ Day 24 Docker 章还会再见它）
pip freeze > requirements.txt     # 把当前环境的包导出成清单
```

**国内加速：pip 换源**（PyPI 服务器在国外，慢或超时就换国内镜像）：

```bash
# 临时用一次（清华镜像）
pip install openai -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4.3 venv：每个项目一个独立的盒子

**为什么需要它**：如果所有项目共用一个全局 Python，项目 A 要 `openai 1.x`、项目 B 要 `openai 0.x` 时就会互相打架，卸载重装来回折腾。**虚拟环境（venv）= 给每个项目一个独立、干净的 Python 环境**，互不干扰。

```bash
cd 你的项目目录
python -m venv .venv        # 在项目下创建名为 .venv 的虚拟环境（只需一次）
```

**激活**——不同终端写法不同（这是 Windows 专属的坑）：

| 你用的终端 | 激活命令 |
| --- | --- |
| PowerShell / cmd | `.venv\Scripts\activate` |
| Git Bash | `source .venv/Scripts/activate` |

激活成功后命令行开头会出现 `(.venv)` 标记。之后 `pip install` 装的包都只进这个盒子：

```bash
(.venv) pip install openai   # 只装进本项目
(.venv) deactivate            # 退出虚拟环境
```

::: details PowerShell 报「禁止运行脚本」？
PowerShell 默认安全策略会拦截 activate 脚本。以当前用户身份放开一次即可（只需一次）：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
:::

::: tip 让 VSCode 记住你的虚拟环境
`Ctrl+Shift+P` → 输入 `Python: Select Interpreter` → 选带 `.venv` 的那项。之后点右上角 ▶ 运行脚本，就会自动用这个环境。
:::

### 4.4 读懂 AI 代码速查表

AI 生成的代码里出现这些语法，能看懂即可，**不要求默写**：

| 看到 | 意思是 |
| --- | --- |
| `name = "小明"` | 变量：给值起个名字 |
| `def add(a, b): return a + b` | 函数：一段可复用的逻辑，接收输入返回输出 |
| `user = {"name": "小明", "age": 18}` | 字典：键值对集合，`user["name"]` 取值 |
| `items = [1, 2, 3]` | 列表：有序集合，`items[0]` 是第一个 |
| `for item in items:` | 循环：逐个处理列表元素 |
| `if x > 0: ... else: ...` | 分支判断 |
| `f"你好，{name}"` | f-string：把变量嵌进字符串 |
| `class Bot:` | 类：把数据和函数打包成一个「物件」 |
| `None` / `True` / `False` | 空值 / 真 / 假 |

---

## 5. Day 2 收尾：Git 与你的第一个 GitHub 仓库

Git 是版本管理工具（存档/读档），GitHub 是放代码的云仓库——**也是你未来简历的项目展示地**。今天只用会 4 条命令：

```bash
git init                      # 在当前目录创建一个 Git 仓库（开新存档）
git add .                     # 把所有改动加入暂存（选择要存的内容）
git commit -m "第一个LLM调用"   # 提交存档，-m 后是说明
git push                      # 推送到 GitHub（远端备份）
```

推送前需要先在 GitHub 建一个空仓库并关联（第一次会要求登录）：

```bash
git remote add origin https://github.com/你的用户名/hello-llm.git
git push -u origin main
```

::: warning 提交前必看：别把 API Key 推上去
项目根目录放一个 `.gitignore` 文件，写上 `.env`——这个文件专门列出「Git 不要追踪的东西」。我们放 Key 的 `.env` 文件必须在清单里，否则等于把密码公开。
:::

---

## 6. 交付物：跑通第一个 LLM API 调用

课程仓库 [code/ch0-hello-llm/](https://github.com/RCliang/learn-vibe-for-job/tree/main/code/ch0-hello-llm) 提供了完整代码。**这一步把今天所有知识串起来**：

```bash
# 1. 把代码下载/复制到你的项目目录
cd ch0-hello-llm

# 2. 创建并激活虚拟环境（4.3 节）
python -m venv .venv
.venv\Scripts\activate          # PowerShell/cmd

# 3. 按清单安装依赖（4.2 节）
pip install -r requirements.txt

# 4. 复制 .env.example 为 .env，填入你的 DeepSeek API Key

# 5. 运行！
python hello_llm.py
```

看到模型返回一句话，就是 **Day 2 的交付物**。然后把整个目录（确认 `.gitignore` 里有 `.env`）`add → commit → push` 到你自己的 GitHub 仓库。

**这个脚本里发生了什么**：`import` 拿到 OpenAI SDK（4.1）→ SDK 在 venv 里（4.3）→ pip 从 requirements.txt 装的（4.2）→ 它向 `https://api.deepseek.com/chat/completions` 发了一次 **POST 请求**（第 3 节）→ 带着 JSON 请求体 → 拿到 JSON 响应 → 打印出来。**今天一天的知识，全在这一段 20 行的代码里。**

---

## 7. 自测门槛

进入 Ch1 前，确认你能：

- [ ] `python --version` 能输出版本号
- [ ] Claude Code 能对话，`/status` 显示 DeepSeek 模型
- [ ] 能说清 200 / 401 / 404 / 429 分别是什么意思
- [ ] **独立**在一个新目录创建 venv、激活、安装一个包
- [ ] 能说出遇到 `ModuleNotFoundError` 时的两步排错法
- [ ] `hello_llm.py` 跑通，且代码已 push 到 GitHub（`.env` 没被推上去）

卡住超过 30 分钟 → 查下面的排错指引 → 还不行就把**完整报错**贴给 Claude Code（这正是 Ch1 要练的）。

---

## 8. 最小路径 vs 完整路径

- **最小路径（必做）**：1-6 节全部 + 自测门槛
- **完整路径（选做）**：
  - 用浏览器 F12 Network 观察一次完整的请求/响应
  - 把 `hello_llm.py` 改成多轮对话（追问两次），体会 messages 列表追加
  - 了解 `pip config set global.index-url` 永久换源

## 9. 排错指引

| 报错/现象 | 原因 | 解法 |
| --- | --- | --- |
| `python 不是内部或外部命令` | 装时没勾 Add to PATH | 重跑安装包装 Modify；或手动加 PATH 后**重开终端** |
| `pip 不是内部或外部命令` | 同上 | 同上 |
| `npm 不是内部或外部命令` | Node.js 没装好 | 重装 Node LTS，重开终端 |
| `claude` 无响应或连不上 | 环境变量/配置未生效 | 检查 `.claude/settings.json` 的 JSON 格式（多逗号/少引号都会失效），**重开终端**再试 |
| `claude` 报 401 / 404 / model not found | 端点或模型名已变化 | 走下面的「配置过时兜底三步」 |
| API 返回 `401` | Key 错/没生效 | 核对 `.env` 里的 Key；DeepSeek 后台重新复制 |
| API 返回 `404` | 模型名写错 | 打开[官方模型列表](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)核对 `.env` 里的 `LLM_MODEL` |
| API 返回 `429` | 请求太频繁 | 等几秒重试 |
| `ModuleNotFoundError: No module named 'openai'` | 没装 / 没激活 venv | 确认终端前面有 `(.venv)`，再 `pip install -r requirements.txt` |
| PowerShell「禁止运行脚本」 | 执行策略限制 | 见 4.3 节 details 框 |
| pip 下载极慢/超时 | 默认源在国外 | 加 `-i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 脚本输出乱码 | Windows 终端编码 | 终端先执行 `chcp 65001` 切 UTF-8 |
| `git push` 要求登录 | 首次使用 | 按提示浏览器登录 GitHub 即可 |

### 配置过时兜底三步（教程跟不上现实时用）

工具和模型迭代快，本教程里写死的 URL / 环境变量名 / 模型名**以官方文档为准**。照抄后不成功，按这三步走：

1. **找官方最新配置**：Claude Code 接入看 [DeepSeek 官方文档](https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/claude_code/)；API 调用看 [DeepSeek API 文档](https://api-docs.deepseek.com/zh-cn/)；模型名和价格看[价格页](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)。
2. **只换值、不改结构**：把文档里的新 URL / 变量名 / 模型名填进原来的位置——`.claude/settings.json` 的结构、`.env` 的三个变量名（`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`）是不变的。
3. **还不行就问 AI**：把「我的 `.claude/settings.json` 内容 + 完整报错」贴给 Claude Code（或把 `.env` 内容**隐去 Key** 后贴出来），让它帮你对照最新文档找差异。这也是 Ch1 要练的核心动作。
