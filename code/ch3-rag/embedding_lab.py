"""Day 8 实验：亲眼看「语义相近 = 向量距离近」。

把几句话用 bge-m3 向量化，两两计算余弦相似度，
观察语义关系如何在数字上体现。运行：python embedding_lab.py
"""

import math
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 本章只做向量化实验，只用 EMBED_* 三件套（硅基流动，见 .env.example）
EMBED_API_KEY = os.getenv("EMBED_API_KEY")
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "https://api.siliconflow.cn/v1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")

# 三组句子：前两句同主题（请假）、中间两句同主题（报销）、最后两句与工作无关
SENTENCES = [
    "我想请年假去旅游",
    "年假的申请流程是什么",
    "出差住宿一晚能报销多少钱",
    "报销发票最晚什么时候提交",
    "今天天气真不错",
    "推荐一部最近上映的电影",
]


def embed(texts: list[str]) -> list[list[float]]:
    """调用 embedding API，把一组文本变成一组向量。"""
    client = OpenAI(api_key=EMBED_API_KEY, base_url=EMBED_BASE_URL)
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """余弦相似度：两个向量方向的接近程度，范围 -1 到 1，越接近 1 越相似。"""
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm


def main() -> None:
    if not EMBED_API_KEY:
        raise SystemExit(
            "未读到 EMBED_API_KEY：向量化用硅基流动（见 .env.example），填入其 Key 后重试"
        )

    vectors = embed(SENTENCES)
    print(f"模型：{EMBED_MODEL}，每句话变成了一个 {len(vectors[0])} 维向量\n")

    pairs = []
    for i in range(len(SENTENCES)):
        for j in range(i + 1, len(SENTENCES)):
            score = cosine_similarity(vectors[i], vectors[j])
            pairs.append((score, SENTENCES[i], SENTENCES[j]))

    pairs.sort(reverse=True)
    print("相似度从高到低（观察：同主题的是不是都排在前面？）：\n")
    for score, a, b in pairs:
        print(f"  {score:.4f}  「{a}」 × 「{b}」")

    print("\n结论：语义相近的句子向量夹角小、相似度高——")
    print("这就是「用向量距离做语义检索」的全部原理。")


if __name__ == "__main__":
    main()
