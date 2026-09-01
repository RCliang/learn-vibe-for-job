"""Day 10：检索增强问答——项目 1 的引擎（命令行版）。

用法：python rag_chat.py [--k 3]
先运行 build_kb.py 建好知识库，再运行本脚本进入问答循环。
输入 q 退出。
"""

import argparse
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
# 向量化走硅基流动（DeepSeek 不提供 embedding API），与对话模型是两套凭证
EMBED_API_KEY = os.getenv("EMBED_API_KEY")
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "https://api.siliconflow.cn/v1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")

DB_DIR = Path(__file__).resolve().parent / "chroma_db"
COLLECTION_NAME = "company_kb"

SYSTEM_PROMPT = """你是「星辰科技」的内部知识库助手。严格遵守：

1. 只根据【参考资料】回答问题，不允许使用你自己的知识补充
2. 回答中引用资料的地方标注编号，如 [1] [2]
3. 如果参考资料不足以回答，明确说「知识库中没有找到相关内容」，不要编造
4. 回答简洁直接，先给结论再给依据"""


def get_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_or_create_collection(COLLECTION_NAME)


def retrieve(query: str, k: int = 3) -> tuple[list[str], list[dict]]:
    """检索：问题向量化 → Chroma 找最相似的 k 块。返回 (文档块, 元数据)。"""
    embed_client = OpenAI(api_key=EMBED_API_KEY, base_url=EMBED_BASE_URL)
    response = embed_client.embeddings.create(model=EMBED_MODEL, input=[query])
    query_embedding = response.data[0].embedding

    result = get_collection().query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas"],
    )
    return result["documents"][0], result["metadatas"][0]


def build_prompt(query: str, chunks: list[str]) -> str:
    """把检索到的资料编号拼进 prompt——「检索增强」的增强就发生在这里。"""
    reference = "\n\n".join(
        f"[{i}] {chunk}" for i, chunk in enumerate(chunks, start=1)
    )
    return f"【参考资料】\n{reference}\n\n【问题】\n{query}"


def generate_answer(query: str, k: int = 3) -> tuple[str, list[dict]]:
    """完整 RAG 链路：检索 → 拼 prompt → 生成。返回 (回答, 引用来源)。"""
    chunks, metadatas = retrieve(query, k)
    openai_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(query, chunks)},
        ],
        temperature=0.2,  # 知识问答要稳定，不要发散
    )
    return response.choices[0].message.content, metadatas


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 LLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    parser = argparse.ArgumentParser(description="企业知识库问答（命令行版）")
    parser.add_argument("--k", type=int, default=3, help="检索返回的块数 top-k")
    args = parser.parse_args()

    if get_collection().count() == 0:
        raise SystemExit("知识库是空的：请先运行 python build_kb.py")

    print(f"企业知识库问答（top-k = {args.k}），输入问题开始，输入 q 退出\n")
    while True:
        query = input("你：").strip()
        if not query:
            continue
        if query.lower() in {"q", "quit", "exit"}:
            break
        try:
            answer, sources = generate_answer(query, args.k)
        except Exception as exc:
            print(f"（调用失败：{exc}）\n")
            continue
        print(f"\n助手：{answer}")
        files = sorted({m["source"] for m in sources})
        print(f"来源：{'、'.join(files)}\n")


if __name__ == "__main__":
    main()
