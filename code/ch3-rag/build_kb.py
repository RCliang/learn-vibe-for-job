"""Day 9：把企业语料切分、向量化、存入 Chroma（RAG 的「离线入库」阶段）。

用法：
    python build_kb.py                     # 默认 chunk=300, overlap=50
    python build_kb.py --chunk 600         # 换切分参数重建（Day 11 调优用）

流程：读 data/project1-kb/*.md → 手写滑窗切分 → bge-m3 向量化
→ 存入本地 Chroma（目录 chroma_db/）。
"""

import argparse
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 本章只有向量化，不需要对话模型——只用 EMBED_* 三件套
EMBED_API_KEY = os.getenv("EMBED_API_KEY")
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "https://api.siliconflow.cn/v1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")

# 语料目录：仓库根下的 data/project1-kb/（与本脚本的相对位置固定）
KB_DIR = Path(__file__).resolve().parents[2] / "data" / "project1-kb"
DB_DIR = Path(__file__).resolve().parent / "chroma_db"
COLLECTION_NAME = "company_kb"


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """手写滑窗切分：先懂本质，框架（LangChain 切分器）见课程完整路径。

    chunk_size：每块字符数；overlap：相邻块重叠字符数。
    重叠是为了避免「关键句正好被切断在两块边界上」导致两边都检索不到。
    """
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(piece)
        if start + chunk_size >= len(text):
            break
    return chunks


def embed(texts: list[str]) -> list[list[float]]:
    """批量向量化。不同供应商单次条数上限不同，这里按 32 一批保守处理。"""
    client = OpenAI(api_key=EMBED_API_KEY, base_url=EMBED_BASE_URL)
    result: list[list[float]] = []
    for i in range(0, len(texts), 32):
        batch = texts[i : i + 32]
        response = client.embeddings.create(model=EMBED_MODEL, input=batch)
        result.extend(item.embedding for item in response.data)
    return result


def main() -> None:
    if not EMBED_API_KEY:
        raise SystemExit(
            "未读到 EMBED_API_KEY：本章向量化用硅基流动（DeepSeek 不提供 embedding API），"
            "请复制 .env.example 为 .env 并填入硅基流动的 Key"
        )

    parser = argparse.ArgumentParser(description="构建企业知识库")
    parser.add_argument("--chunk", type=int, default=300, help="每块字符数")
    parser.add_argument("--overlap", type=int, default=50, help="相邻块重叠字符数")
    args = parser.parse_args()

    # 1. 读取语料并切分
    all_chunks, all_ids, all_sources = [], [], []
    for md_file in sorted(KB_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        chunks = split_text(text, args.chunk, args.overlap)
        for idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{md_file.stem}_{idx}")
            all_sources.append(md_file.name)
        print(f"{md_file.name}：{len(chunks)} 块")

    # 2. 向量化（显式传入，不依赖 Chroma 默认模型——网络下载且非中文优化）
    print(f"\n共 {len(all_chunks)} 块，正在向量化（{EMBED_MODEL}）...")
    embeddings = embed(all_chunks)

    # 3. 入库。重建知识库时先删旧集合，避免换 chunk 参数后新旧块混杂
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # 首次运行时集合不存在，忽略
    collection = client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # 用余弦距离，和语义相似度直觉一致
    )
    collection.add(
        ids=all_ids,
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=[{"source": s} for s in all_sources],
    )

    print(f"入库完成 → {DB_DIR}（集合 {COLLECTION_NAME}，共 {collection.count()} 块）")
    print(f"\n参数：chunk_size={args.chunk}, overlap={args.overlap}")
    print("第一块预览：")
    print("  " + all_chunks[0][:100].replace("\n", " ") + "...")


if __name__ == "__main__":
    main()
