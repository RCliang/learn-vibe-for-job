---
title: 项目 1：企业知识库问答机器人（Day 12-14）
outline: [2, 3]
---

# 项目 1：企业知识库问答机器人（Day 12-14，跟做）

> **本章 JD 关键词**：知识库建设、流式输出
>
> **学完你能做什么**：把 Ch3 的命令行引擎变成一个**公网可访问、可写上简历**的聊天应用；掌握 Streamlit 这类「数据应用速成界面」的写法；理解并实现流式输出；学会把带 Secret 的应用部署到云端。

::: info 📋 三天路线
**Day 12**：Streamlit 一小时上手（心智模型 + 最小聊天界面）
**Day 13**：流式输出 + RAG 内核集成（本地完整跑通）
**Day 14**：部署 HF Space + 毕业级 README + 验收
:::

**先看毕业标准再动工**（对齐终点才能不走弯路）：

- [ ] 在线可访问的 RAG 问答 Demo（HF Space；README 附本地运行说明 + 演示 GIF）
- [ ] 回答带引用来源；README 说明切分与检索策略，并**附评估结果**
- [ ] GitHub 仓库结构清晰（代码、requirements、README）

参考实现在 [code/project1-kb-bot/](https://github.com/your-name/learn-vibe-coding/tree/main/code/project1-kb-bot)（`app.py` 界面层 + `rag_core.py` 内核层）。跟做 ≠ 照抄：每一节先自己写，卡壳 20 分钟再对照。

---

## 1. Day 12：Streamlit 一小时上手

### 1.1 为什么是 Streamlit

写个 Web 界面 traditionally 要学 HTML/CSS/JS + 前端框架——而 Streamlit 让你**只用 Python** 就出可交互页面，它和 FastAPI 一样是 Python 数据/AI 应用的事实标准（JD 里「快速搭建 Demo/看板」默认指它）。项目 2 你会换成 FastAPI 前后端分离——两种形态都见过，面试聊架构才有对比素材。

### 1.2 最小聊天界面（先跑起来）

```bash
cd 你的项目目录
python -m venv .venv && .venv\Scripts\activate
pip install streamlit
streamlit run my_first_app.py
```

`my_first_app.py`——20 行，一个能记历史的聊天壳子：

```python
import streamlit as st

st.title("我的第一个聊天应用")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("说点什么")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        st.markdown("（这里先假装是模型回复）")
    st.session_state.messages.append({"role": "assistant", "content": "（假装回复）"})
```

常用元素速查：`st.title/text/markdown/caption`（展示）、`st.chat_input`（输入框）、`st.chat_message`（气泡）、`st.expander`（折叠）、`st.sidebar`（侧栏）、`st.error/warning/success`（提示）、`st.stop()`（中断渲染）。

### 1.3 必须建立的心智模型：重跑 + session_state

Streamlit 的运行方式和普通脚本**完全不同**，不理解这一点后面全是玄学：

> **用户每一次交互（发消息、点按钮），Streamlit 都会把你的脚本从头到尾重新执行一遍。**

那对话历史怎么不丢？——`st.session_state`，一个横跨重跑的字典。两个推论：

| 现象 | 原因 |
| --- | --- |
| 改了消息列表但界面不更新 | 修改要先写进 `session_state`，渲染读它 |
| 变量每次交互都「归零」 | 脚本重跑了；持久状态只能放 `session_state` 或缓存 |

::: tip 验证心智模型
把 `st.title` 改成 `st.title(f"重跑次数：{st.session_state.get('n', 0)}")`，并在收到消息时 `st.session_state.n = st.session_state.get('n', 0) + 1`。发几条消息，看数字怎么变。
:::

---

## 2. Day 13：流式输出与 RAG 集成

### 2.1 流式输出：为什么和怎么做

**为什么**：生成 500 字要 10 秒+，用户盯着空白会以为卡死了；流式让首字在 1 秒内出现，体验质变。JD 把「流式输出」列为高频词，正因为它是 LLM 应用的标配。

**怎么做**：两步。第一步，API 调用加 `stream=True`，返回的不再是完整响应而是**迭代器**，每 yield 一小段：

```python
def stream_answer(...):
    response = client.chat.completions.create(..., stream=True)
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta          # 生成器：一段一段往外吐
```

第二步，界面用 `st.write_stream(生成器)` 消费——它会边收边渲染，最后返回完整文本（正好存进历史）。

```python
answer = st.write_stream(stream_answer(...))   # 打字机效果 + 拿到全文
```

### 2.2 集成 RAG 内核

参考实现分两层，这个分层值得学（面试可讲）：

```
app.py        界面层：Streamlit 组件、session_state、密钥读取
rag_core.py   内核层：切分/向量化/检索/流式生成（纯函数，不依赖 Streamlit）
```

好处：内核可以被命令行、评估脚本、明天的部署**原样复用**，界面挂了也不影响核心逻辑。

**密钥读取的兼容函数**（本地 `.env`、云端 `st.secrets` 一网打尽，Day 14 部署的伏笔）：

```python
def get_secret(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets[name]      # HF Space 的 Secrets 机制
    except Exception:
        return None
```

### 2.3 建库只做一次：st.cache_resource

每次用户发消息都重建向量库（重新 embedding）既慢又烧钱。Streamlit 给了缓存装饰器：

```python
@st.cache_resource(show_spinner="正在构建知识库…")
def get_collection():
    return build_kb(API_KEY, BASE_URL, EMBED_MODEL)

collection = get_collection()   # 首次调用真的执行；之后直接返回缓存
```

**里程碑**：`streamlit run app.py`，问「年假可以结转吗」看到带引用的打字机式回答；问「CEO 是谁」看到诚实拒答——**本地版毕业**。截个图，今天可以晒了。

---

## 3. Day 14：部署 HF Space + 毕业级 README

### 3.1 部署六步（零成本路径）

1. 注册 [huggingface.co](https://huggingface.co)（邮箱即可，免费）
2. 新建 Space：名字如 `company-kb-bot`，SDK 选 **Streamlit**——HF 会生成带 frontmatter 的 `README.md`（`sdk: streamlit`、`sdk_version`、`app_file: app.py`，**保留它自动生成的版本号**）
3. 把 `app.py`、`rag_core.py`、`requirements.txt` 和 `data/project1-kb/` 推到 Space 仓库（网页上传或 `git clone` 你的 Space 后 push）
4. **Settings → Variables and secrets** → 添加 Secret：名称 `GLM_API_KEY`，值为你的智谱 Key——**Secret 不进代码、不进 Git**（呼应 Ch1 的红线）
5. 打开 Space 页面等构建：冷启动会自动建库（约 1 分钟，embedding 成本不到 1 分钱）
6. 访问你的 `https://huggingface.co/spaces/用户名/空间名`——这就是简历上能放的链接

::: warning 国内访问不稳怎么办
HF 部分时段国内直连不畅，对策按序尝试：① git 推送地址换成镜像 `hf-mirror.com`；② 换网络/手机热点重试；③ 实在不行走**兜底路径**：GitHub 仓库 + README 里放本地运行的演示 GIF（ScreenToGif 录制），并在 Ch7 用国内云服务器部署项目 2 补回「真机部署」经历。
:::

### 3.2 毕业级 README（简历视角的写作法）

面试官打开你的仓库，90 秒内要能看懂「做了什么、怎么做的、做得怎么样」。结构照抄参考实现的 README：

1. **一句话定位** + 在线 Demo 链接 + 演示 GIF（**先给结果**）
2. **架构图**：离线入库 / 在线问答两段 ASCII 图——面试画图的底稿
3. **切分与检索策略 + 评估结果表**：把 Ch3 `eval_results.jsonl` 的结论贴成表格。**这张表是整个项目的差异化亮点**：大多数人只会说「我做了个 RAG」，你能说「chunk=300 是我对比 600 测出来的，平均分 4.6 对 4.1」
4. 本地运行说明 + 目录结构 + 部署步骤

### 3.3 毕业验收（对照开头三条逐项打勾）

- [ ] Space 链接发给自己手机，移动网络能打开并正常问答
- [ ] 库内问题带引用、库外问题拒答（各测 3 条）
- [ ] README 含架构图、策略+评估表、本地运行说明、演示 GIF
- [ ] GitHub 仓库推送完成，`.env` 没有被提交（`git status` 确认）
- [ ] 面试自问自答一遍：「为什么 chunk 取 300？」「拒答是怎么实现的？」

---

## 4. 排错指引

| 现象 | 原因 | 解法 |
| --- | --- | --- |
| `streamlit` 命令不存在 | venv 没激活 | 终端确认有 `(.venv)` 前缀 |
| 界面一交互状态就丢 | 没用 `session_state` | 见 1.3 心智模型 |
| 每次发消息都重新建库 | 没挂 `@st.cache_resource` | 见 2.3 |
| 流式没效果、一次全出 | 调用没加 `stream=True` 或没用 `st.write_stream` | 核对两步都做了 |
| `st.secrets` 报错 | 本地没有 secrets 文件 | 正常，`get_secret` 已容错；确认 `.env` 存在 |
| Space 一直 building/报错 | 依赖缺失或版本不符 | 看 Space 页面 Logs；确认 `requirements.txt` 已上传、frontmatter 未被改坏 |
| Space 运行但报无 Key | Secret 名字不一致 | 必须恰好是 `GLM_API_KEY`，无空格 |
| Space 白屏/超时 | 冷启动建库中 | 等待 1 分钟刷新；仍是则看 Logs 的 embedding 调用是否报错 |
| 国内打不开 Space | 网络问题 | 见 3.1 warning 的三步对策 |

## 5. 完整路径（选做进阶）

- `st.file_uploader`：让用户上传自己的 Markdown/PDF 文档动态入库（真正的「知识库建设」）
- 多轮上下文：把最近几轮对话也拼进 prompt（注意 token 预算，呼应 Ch2）
- 侧栏参数面板：让用户调 top-k/chunk 实时对比（把 Ch3 评估实验变成产品功能）
- 用 Ch1 的「AI 出题考核」让 AI 针对你的 `app.py` 出 3 道题——项目代码也要读懂
