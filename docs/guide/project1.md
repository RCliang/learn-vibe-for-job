---
title: 项目 1：企业知识库问答机器人（Day 12-14）
outline: [2, 3]
---

# 项目 1：企业知识库问答机器人（Day 12-14，跟做）

> **本章 JD 关键词**：知识库建设、流式输出、Docker、云部署
>
> **学完你能做什么**：把 Ch3 的命令行引擎变成一个**公网可访问、可写上简历**的聊天应用；掌握 Streamlit 这类「数据应用速成界面」的写法；理解并实现流式输出；第一次用 Docker 把应用部署上云。

::: info 📋 三天路线
**Day 12**：Streamlit 一小时上手（心智模型 + 最小聊天界面）
**Day 13**：流式输出 + RAG 内核集成（本地完整跑通）
**Day 14**：Docker 打包 + 阿里云 ECS 部署 + 毕业级 README + 验收
:::

**先看毕业标准再动工**（对齐终点才能不走弯路）：

- [ ] 在线可访问的 RAG 问答 Demo（阿里云 ECS + Docker，`http://公网IP:8501`；暂不付费可走 HF Space 备选 + 演示 GIF）
- [ ] 回答带引用来源；README 说明切分与检索策略，并**附评估结果**
- [ ] GitHub 仓库结构清晰（代码、requirements、README）

参考实现在 [code/project1-kb-bot/](https://github.com/RCliang/learn-vibe-for-job/tree/main/code/project1-kb-bot)（`app.py` 界面层 + `rag_core.py` 内核层 + `Dockerfile`）。跟做 ≠ 照抄：每一节先自己写，卡壳 20 分钟再对照。

::: tip 今天「先用起来」，原理后面学
Day 14 会用到 Docker 和云服务器——JD 里「Docker / 云部署 / Linux」三大关键词一次点亮。
策略是**先照做跑通建立全局感**：Docker 原理与优化在 Ch6 系统化，Linux 命令在 Ch5 深入。
先开车再学发动机，是速成期的正确顺序。
:::

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

好处：内核可以被命令行、评估脚本、Docker 镜像**原样复用**，界面挂了也不影响核心逻辑。

**密钥读取的兼容函数**（本地 `.env`、云端环境变量一网打尽，Day 14 部署的伏笔）：

```python
def get_secret(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets[name]      # HF Space 备选路径的 Secrets 机制
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

## 3. Day 14：Docker 打包 + 阿里云 ECS 部署

### 3.1 Docker 最小三概念（今天够用版）

| 概念 | 一句话 | 类比 |
| --- | --- | --- |
| 镜像 image | 打包好的应用模板（代码 + 依赖 + 运行环境） | 菜谱 |
| 容器 container | 镜像跑起来的实例 | 按菜谱做出的菜 |
| 端口映射 `-p 8501:8501` | 把服务器的 8501 转发进容器的 8501 | 前台转分机 |

**为什么部署要用 Docker**：「我本地能跑」到「服务器也能跑」之间隔着系统、依赖版本、路径一万个坑。Docker 把应用连同环境整体打包，**本地和服务器跑的是同一个东西**——这就是 JD 里 Docker 的真实用途（Ch6 展开原理）。

### 3.2 Dockerfile：打包说明书

项目目录下的 `Dockerfile`（参考实现已含，逐行读懂再照抄）：

```dockerfile
FROM python:3.12-slim            # 基础镜像：一个干净的 Python 环境
WORKDIR /app
COPY requirements.txt .           # 先拷依赖清单
RUN pip install --no-cache-dir -r requirements.txt -i 清华镜像源   # 再装依赖（层缓存：改代码不用重装）
COPY app.py rag_core.py ./        # 后拷代码
COPY data/ ./data/                # 语料也要进镜像
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

三个今天必须懂的点：

1. **顺序有讲究**：依赖清单先拷先装、代码后拷——改代码重新 build 时依赖层直接复用缓存，秒级完成（Ch6 讲层缓存原理）
2. **`0.0.0.0` 是天坑**：容器内默认监听 `localhost` 的话，端口映射后外面根本访问不到
3. **`.env` 绝不进镜像**：`.dockerignore` 把它排除；密钥在**运行时**用 `--env-file` 注入——镜像可能被分享，等于密码不能被打包

::: details Windows 本地想先验证？
装了 Docker Desktop 的话，本地就能走一遍 3.5 的 build/run 流程再上服务器；没装也不必装——直接在服务器上做，步骤完全一样。
:::

### 3.3 阿里云服务器准备（三步）

1. **购买**：[阿里云官网](https://www.aliyun.com) → 搜索「轻量应用服务器」或 ECS（新用户都有特价，约几十元/月；学生有学生价）。系统选 **Ubuntu 22 以上**，地域选离你近的。付款后控制台能看到**公网 IP**。
2. **放行端口**：控制台找到「防火墙」（轻量）或「安全组」（ECS）→ 添加规则：**TCP 8501** 放行（22 端口默认已开，那是 SSH 用的）。
3. **SSH 连接**：Windows 终端直接敲（密码在控制台「重置密码」后设置，重置后记得重启实例）：

```bash
ssh root@你的服务器公网IP
# 第一次连会问 yes/no，输 yes；然后输密码（输入时屏幕不显示，正常）
```

看到命令提示符变成服务器的样子，你就已经「在云端」了——这三条命令今天先用，Ch5 系统学 Linux。

### 3.4 服务器安装 Docker（一条命令）

```bash
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
docker -v    # 能打印版本号即成功
```

（`--mirror Aliyun` 走阿里镜像下载，国内速度有保障。）

### 3.5 部署上线（今天的高潮）

在**服务器**上执行：

```bash
# 1. 拉取你的代码（先 push 到 GitHub；服务器上 git clone 不需要翻墙）
git clone https://github.com/你的用户名/你的仓库.git
cd 你的仓库/code/project1-kb-bot

# 2. 准备语料：把仓库根的语料拷进项目目录（Dockerfile 会 COPY data/）
cp -r ../../data/project1-kb ./data/

# 3. 准备密钥（服务器上新建 .env，只留在服务器上）
cp .env.example .env
nano .env        # 填入 GLM_API_KEY，Ctrl+O 保存 Ctrl+X 退出

# 4. 构建镜像并运行
docker build -t kb-bot .
docker run -d --name kb-bot -p 8501:8501 --env-file .env kb-bot

# 5. 验证
docker ps                 # STATUS 应为 Up
docker logs -f kb-bot     # 看启动日志，Ctrl+C 退出查看
```

**验收时刻**：手机关掉 WiFi 用流量，浏览器打开 `http://服务器公网IP:8501`——你的应用在公网上了。这个 URL 就可以写进简历和 GitHub README。

### 3.6 零成本备选路径（暂不付费的学员）

Hugging Face Streamlit Space：上传 `app.py`/`rag_core.py`/`requirements.txt`/`data/`，Settings → Secrets 加 `GLM_API_KEY`（README 顶部 frontmatter 已备好）。注意 HF 国内访问不稳，README 必须附演示 GIF 与本地运行说明兜底；服务器真机部署经历留到 Ch7 用项目 2 补回。

### 3.7 毕业级 README（简历视角的写作法）

面试官打开你的仓库，90 秒内要能看懂「做了什么、怎么做的、做得怎么样」。结构照抄参考实现的 README：

1. **一句话定位** + 在线 Demo 链接 + 演示 GIF（**先给结果**）
2. **架构图**：离线入库 / 在线问答两段 ASCII 图——面试画图的底稿
3. **切分与检索策略 + 评估结果表**：把 Ch3 `eval_results.jsonl` 的结论贴成表格。**这张表是整个项目的差异化亮点**：大多数人只会说「我做了个 RAG」，你能说「chunk=300 是我对比 600 测出来的，平均分 4.6 对 4.1」
4. 本地运行说明 + Docker 部署命令 + 目录结构

### 3.8 毕业验收（对照开头三条逐项打勾）

- [ ] 手机流量访问 `http://公网IP:8501` 能正常问答（或备选路径 Space 可访问）
- [ ] 库内问题带引用、库外问题拒答（各测 3 条）
- [ ] README 含架构图、策略+评估表、本地运行说明、**Docker 部署命令**、演示 GIF
- [ ] GitHub 仓库推送完成，`.env` 没有被提交、没进镜像（`docker history kb-bot` 里看不到 Key）
- [ ] 面试自问自答一遍：「为什么 chunk 取 300？」「拒答怎么实现？」「为什么用 Docker 部署？」

---

## 4. 排错指引

| 现象 | 原因 | 解法 |
| --- | --- | --- |
| `streamlit` 命令不存在 | venv 没激活 | 终端确认有 `(.venv)` 前缀 |
| 界面一交互状态就丢 | 没用 `session_state` | 见 1.3 心智模型 |
| 每次发消息都重新建库 | 没挂 `@st.cache_resource` | 见 2.3 |
| 流式没效果、一次全出 | 没加 `stream=True` 或没用 `st.write_stream` | 核对两步都做了 |
| SSH 连不上服务器 | 安全组没放行 22 / 密码没重置 | 控制台检查规则；重置密码后**重启实例** |
| `docker` 命令不存在 | 安装脚本没跑完 | 重跑 3.4 命令；`docker -v` 验证 |
| `docker build` 卡在下载依赖 | 默认源在国外 | Dockerfile 已配清华源；确认用的是参考实现的 Dockerfile |
| build 报 `COPY data/` 失败 | 项目目录里没有 `data/` | 先执行 `cp -r ../../data/project1-kb ./data/` |
| 容器跑了但公网打不开 | ① 安全组没放行 8501 ② 没监听 0.0.0.0 ③ 用了 https | ① 补规则 ② 核对 CMD 参数 ③ 浏览器用 `http://` 不是 `https://` |
| 页面打开但报无 Key | `--env-file .env` 没带 / .env 为空 | `docker logs kb-bot` 看提示；确认 .env 与 Key |
| 容器反复重启 | 启动即崩溃 | `docker logs kb-bot` 定位（Ch1 的读报错法同样适用于容器日志） |
| 改了代码服务器没变化 | 只改了本地没重新构建 | git push → 服务器 `git pull` → 重新 build/run（先 `docker rm -f kb-bot`） |

## 5. 完整路径（选做进阶）

- `st.file_uploader`：让用户上传自己的 Markdown/PDF 文档动态入库（真正的「知识库建设」）
- 多轮上下文：把最近几轮对话也拼进 prompt（注意 token 预算，呼应 Ch2）
- 侧栏参数面板：让用户调 top-k/chunk 实时对比（把 Ch3 评估实验变成产品功能）
- 用 Ch1 的「AI 出题考核」让 AI 针对你的 `Dockerfile` 出 3 道题（比如「FROM python:3.12-slim 的 slim 是什么」「为什么先 COPY requirements.txt」）
- 给 `docker run` 加 `--restart=always`：服务器重启后容器自动拉起（Ch6 展开）
