---
title: 企业知识库问答机器人
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.49.1"  # ← 走 HF 备选路径时，以创建 Space 自动生成的版本为准
app_file: app.py
pinned: false
---

# 企业知识库问答机器人（RAG）

> 《AI 应用开发速成营》项目 1 · 跟做项目
> 输入关于公司制度/产品的问题，应用检索语料后**带引用**作答；知识库没有的内容会诚实拒答。

**在线 Demo**：`http://你的服务器公网IP:8501`（阿里云 ECS + Docker 部署，见下文）
**演示 GIF**：`docs/demo.gif`（本地运行后用 [ScreenToGif](https://www.screentogif.com/) 录制）

## 架构

```
                 离线（启动时执行一次，st.cache_resource 缓存）
 ┌──────────────────────────────────────────────┐
 │ 语料 *.md → 滑窗切分(300/50) → GLM embedding-3 │
 │            → Chroma 向量库（余弦距离）           │
 └──────────────────────────────────────────────┘
                 在线（每次提问）
 ┌──────────────────────────────────────────────┐
 │ 用户问题 → 向量化 → top-3 检索 → 编号拼接 prompt │
 │   → glm-4-flash 流式生成 → 引用标注 + 拒答纪律  │
 └──────────────────────────────────────────────┘
```

## 切分与检索策略（附评估结果）

- **切分**：chunk_size=300 字符、overlap=50。依据：Ch3 Day 11 用 10 条测试问答集对比过 chunk=300 与 600，300 平均分更高（见下表）。
- **检索**：top-k=3，余弦相似度。对比过 k=3 与 k=5，得分持平，取更省 token 的 3。
- **幻觉抑制**：system prompt 三条纪律（只用资料 / 标注引用 / 诚实拒答）。

| 配置 | 测试集平均分（LLM as judge，5 分制） |
| --- | --- |
| chunk=300, k=3（本应用） | （贴你 Ch3 的评估结果） |
| chunk=600, k=3 | （贴你 Ch3 的评估结果） |
| chunk=300, k=5 | （贴你 Ch3 的评估结果） |

> 上表数字来自 `judge_eval.py` 的 `eval_results.jsonl`——**有评估的调优才是工程**。

## 本地运行

```bash
python -m venv .venv && .venv\Scripts\activate   # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
# 复制 .env.example 为 .env，填入 GLM_API_KEY
# 课程仓库内开发时语料读仓库根 data/project1-kb/，无需额外操作
streamlit run app.py
```

## 部署：阿里云 ECS + Docker（主路径）

```bash
# 1. 服务器：阿里云购买 ECS 或轻量应用服务器（Ubuntu 22+，新用户约几十元/月），
#    控制台「安全组/防火墙」放行 TCP 8501 端口
# 2. 本地 SSH 连接（Ch5 会系统学，今天先照用）：
ssh root@你的服务器公网IP

# 3. 服务器安装 Docker（阿里镜像加速，国内不翻墙）：
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# 4. 拉代码并准备语料与密钥：
git clone https://github.com/你的用户名/你的仓库.git && cd 你的仓库/code/project1-kb-bot
cp -r ../../data/project1-kb ./data/        # 若仓库未含项目内语料
cp .env.example .env && nano .env           # 填入 GLM_API_KEY

# 5. 构建并运行：
docker build -t kb-bot .
docker run -d --name kb-bot -p 8501:8501 --env-file .env kb-bot

# 6. 手机开流量访问 http://服务器公网IP:8501 —— 这就是简历上的链接
docker logs -f kb-bot                        # 出问题先看日志
```

## 零成本备选路径：Hugging Face Space

暂不购买服务器时：HF 新建 Streamlit Space，上传 `app.py`/`rag_core.py`/`requirements.txt`/`data/`，
Settings → Secrets 添加 `GLM_API_KEY`。本文件顶部的 YAML frontmatter（`sdk: streamlit`、
`app_file: app.py` 等）可直接作为 Space 的 README 配置（sdk_version 以 Space 自动生成的为准）。
注意 HF 国内访问不稳，README 需附演示 GIF 与本地运行说明兜底。

## 目录结构

```
project1-kb-bot/
├── app.py            # Streamlit 界面（聊天 + 流式 + 引用 + 缓存建库）
├── rag_core.py       # RAG 内核（切分/向量化/检索/流式生成，纯函数）
├── Dockerfile        # Docker 打包（本地与服务器同一份镜像）
├── .dockerignore     # .env 等绝不进镜像
├── requirements.txt
└── .env.example
```
