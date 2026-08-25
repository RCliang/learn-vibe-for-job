---
title: 企业知识库问答机器人
emoji: 🏢
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.49.1"  # ← 以你创建 Space 时自动生成的版本为准
app_file: app.py
pinned: false
---

# 企业知识库问答机器人（RAG）

> 《AI 应用开发速成营》项目 1 · 跟做项目
> 输入关于公司制度/产品的问题，应用检索语料后**带引用**作答；知识库没有的内容会诚实拒答。

**在线 Demo**：[Hugging Face Space](https://huggingface.co/spaces/你的用户名/你的Space名)（部署步骤见下文）
**演示 GIF**：`docs/demo.gif`（示例占位：本地运行 `README` 中的录屏命令自制）

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
streamlit run app.py
```

语料在仓库根目录 `data/project1-kb/`，可整体替换为你自己领域的 Markdown 文档。

## 目录结构

```
project1-kb-bot/
├── app.py            # Streamlit 界面（聊天 + 流式 + 引用 + 缓存建库）
├── rag_core.py       # RAG 内核（切分/向量化/检索/流式生成，纯函数）
├── requirements.txt
└── .env.example
```

## 部署到 Hugging Face Space（零成本路径）

1. 注册 [huggingface.co](https://huggingface.co)，新建 Space：SDK 选 **Streamlit**（自动生成带 `sdk_version` 的 README frontmatter）
2. Space 仓库根目录放入：`app.py`、`rag_core.py`、`requirements.txt`，以及 `data/project1-kb/`（语料）
3. Space 的 `README.md` 保留自动生成的 frontmatter，正文可复用本 README
4. **Settings → Variables and secrets** 添加 Secret：`GLM_API_KEY`
5. git push（国内不通时用 [hf-mirror.com](https://hf-mirror.com) 镜像地址替代 `huggingface.co`）
6. Space 冷启动会自动重建向量库（约 1 分钟，embedding 花费不到 1 分钱）

录演示 GIF（README 毕业标准要求）：Windows 用 Xbox Game Bar（Win+G）或 [ScreenToGif](https://www.screentogif.com/)。
