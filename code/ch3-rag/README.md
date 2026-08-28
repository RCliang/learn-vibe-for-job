# Ch3 RAG 知识库：配套代码

章节：[Ch3 RAG 知识库（Day 8-11）](https://rcliang.github.io/learn-vibe-for-job/guide/ch3)

语料在仓库根目录 `data/project1-kb/`（星辰科技：请假制度 / 报销制度 / 产品 FAQ），
可整体替换为你自己领域的文档。

## 目录结构

| 文件 | 对应课程 | 说明 |
| --- | --- | --- |
| `embedding_lab.py` | Day 8 | 相似度实验：亲眼看「语义相近 = 向量距离近」 |
| `build_kb.py` | Day 9 | 切分 + 向量化 + Chroma 入库（支持 `--chunk/--overlap`） |
| `rag_chat.py` | Day 10 | 检索增强问答（项目 1 的引擎，带引用与拒答） |
| `qa_pairs.json` | Day 11 | 10 条测试问答集（与语料对应） |
| `judge_eval.py` | Day 11 | 最小路径：LLM as judge 打分，结果追加到 `eval_results.jsonl` |
| `ragas_eval.py` | Day 11 | 完整路径（选做）：Ragas 四指标 |
| `graph_rag_mini.py` | Day 11 | 完整路径（选做）：GraphRAG 迷你实验——LLM 抽关系建小图，对比向量 RAG 答枢纽/多跳问题 |
| `.env.example` / `requirements.txt` | | 环境模板与依赖（chromadb 为本章新增） |

## 运行（按 Day 顺序）

```powershell
cd code/ch3-rag
python -m venv .venv
.venv\Scripts\activate              # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
# 复制 .env.example 为 .env，填入 GLM_API_KEY

python embedding_lab.py             # Day 8：相似度实验
python build_kb.py                  # Day 9：建库（默认 chunk=300/overlap=50）
python rag_chat.py                  # Day 10：问答（输入 q 退出）
python judge_eval.py                # Day 11：评估

# 调优对比实验（Day 11）：
python build_kb.py --chunk 600
python judge_eval.py --label "chunk600"
# 然后打开 eval_results.jsonl 对比两次的 avg
```

## 产物说明

- `chroma_db/`：本地向量库（可随时删除，重跑 `build_kb.py` 重建）
- `eval_results.jsonl`：每次评估一行，用于多组参数对比
