"""项目 1 的 RAG 内核：从 Ch3 命令行引擎提炼，供 Streamlit 界面复用。

分层原则：检索与生成逻辑放这里（纯函数，方便测试），
界面与状态放 app.py（Streamlit 专属）。
"""

from pathlib import Path

import chromadb
from openai import OpenAI

# 语料位置双路径兼容：
# 1) 项目目录内 ./data/project1-kb —— 部署形态（Docker 构建前把语料拷进项目）
# 2) 仓库根 data/project1-kb     —— 课程仓库本地开发形态
_PROJECT_KB = Path(__file__).resolve().parent / "data" / "project1-kb"
_REPO_KB = Path(__file__).resolve().parents[2] / "data" / "project1-kb"
KB_DIR = _PROJECT_KB if _PROJECT_KB.exists() else _REPO_KB
DB_DIR = Path(__file__).resolve().parent / "chroma_db"
COLLECTION_NAME = "company_kb"

# 策略参数：Ch3 Day 11 评估实验选出的配置（见课程 5.2 节）
CHUNK_SIZE = 300
OVERLAP = 50
TOP_K = 3

SYSTEM_PROMPT = """你是「星辰科技」的内部知识库助手。严格遵守：
1. 只根据【参考资料】回答问题，不允许使用你自己的知识补充
2. 回答中引用资料的地方标注编号，如 [1] [2]
3. 如果参考资料不足以回答，明确说「知识库中没有找到相关内容」，不要编造
4. 回答简洁直接，先给结论再给依据"""


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """滑窗切分（同 Ch3 build_kb：先懂本质，不引框架）。"""
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(piece)
        if start + chunk_size >= len(text):
            break
    return chunks


def embed_texts(client: OpenAI, embed_model: str, texts: list[str]) -> list[list[float]]:
    """批量向量化（不同供应商单次条数上限不同，按 32 一批保守处理）。"""
    result: list[list[float]] = []
    for i in range(0, len(texts), 32):
        batch = texts[i : i + 32]
        response = client.embeddings.create(model=embed_model, input=batch)
        result.extend(item.embedding for item in response.data)
    return result


def build_kb(api_key: str, base_url: str, embed_model: str):
    """读语料 → 切分 → 向量化 → 入 Chroma。返回 collection（app.py 会缓存它）。"""
    client = OpenAI(api_key=api_key, base_url=base_url)

    all_chunks, all_ids, all_sources = [], [], []
    for md_file in sorted(KB_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        chunks = split_text(text)
        for idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{md_file.stem}_{idx}")
            all_sources.append(md_file.name)

    embeddings = embed_texts(client, embed_model, all_chunks)

    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma_client.get_or_create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    collection.add(
        ids=all_ids,
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=[{"source": s} for s in all_sources],
    )
    return collection


def retrieve(
    client: OpenAI, embed_model: str, collection, query: str, k: int = TOP_K
) -> tuple[list[str], list[str]]:
    """问题向量化 → 语义检索 top-k。返回 (文档块, 来源文件名)。"""
    response = client.embeddings.create(model=embed_model, input=[query])
    result = collection.query(
        query_embeddings=[response.data[0].embedding],
        n_results=k,
        include=["documents", "metadatas"],
    )
    chunks = result["documents"][0]
    sources = [m["source"] for m in result["metadatas"][0]]
    return chunks, sources


def build_prompt(query: str, chunks: list[str]) -> str:
    """检索结果编号拼进 prompt——「增强」发生的地方。"""
    reference = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(chunks, 1))
    return f"【参考资料】\n{reference}\n\n【问题】\n{query}"


def stream_answer(client: OpenAI, model: str, query: str, chunks: list[str]):
    """流式生成：yield 一段段增量文本，由界面负责渲染（Day 13 主角）。"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(query, chunks)},
        ],
        temperature=0.2,
        stream=True,  # ← 唯一的关键区别：不等全部生成完，边生成边吐出
    )
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
