"""Day 11 完整路径（选做）：用 Ragas 四指标做标准化评估。

最小路径（judge_eval.py）已经够用；本脚本升级为业界标准框架 Ragas，
四个指标各管一件事（0-1 分，越高越好）：

- Faithfulness       回答是否忠于检索资料（不编造）
- AnswerRelevancy    回答是否切题
- ContextPrecision   检索结果中相关内容的占比（检索准不准）
- ContextRecall      标准答案需要的信息被检索覆盖的程度（检索全不全）

前置（选做依赖，不在 requirements.txt 里）：
    pip install "ragas>=0.2" langchain-openai

注意：Ragas 版本迭代较快，本脚本按 0.2.x API 编写；
若报 ImportError，先用 pip show ragas 核对版本再对照官方文档调整。

用法：python ragas_eval.py [--k 3]
"""

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from rag_chat import generate_answer, retrieve

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
# 向量化走硅基流动（DeepSeek 不提供 embedding API），与对话模型是两套凭证
EMBED_API_KEY = os.getenv("EMBED_API_KEY")
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "https://api.siliconflow.cn/v1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")

QA_FILE = Path(__file__).resolve().parent / "qa_pairs.json"


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 LLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    parser = argparse.ArgumentParser(description="Ragas 四指标评估（选做）")
    parser.add_argument("--k", type=int, default=3, help="RAG 检索 top-k")
    args = parser.parse_args()

    try:
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from ragas import EvaluationDataset, SingleTurnSample, evaluate
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from ragas.llms import LangchainLLMWrapper
        from ragas.metrics import (
            AnswerRelevancy,
            ContextPrecision,
            ContextRecall,
            Faithfulness,
        )
    except ImportError as exc:
        raise SystemExit(
            f"缺少选做依赖（{exc}）。安装：pip install \"ragas>=0.2\" langchain-openai"
        )

    # 评委模型走 DeepSeek，向量指标走硅基流动（与 RAG 本身同一套配置）
    evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(model=MODEL, api_key=API_KEY, base_url=BASE_URL, temperature=0)
    )
    evaluator_embeddings = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(model=EMBED_MODEL, api_key=EMBED_API_KEY, base_url=EMBED_BASE_URL)
    )

    qa_pairs = json.loads(QA_FILE.read_text(encoding="utf-8"))

    # 1. 跑一遍 RAG，收集 Ragas 需要的四个字段
    samples = []
    for pair in qa_pairs:
        response, _ = generate_answer(pair["question"], args.k)
        contexts, _ = retrieve(pair["question"], args.k)
        samples.append(
            SingleTurnSample(
                user_input=pair["question"],
                retrieved_contexts=contexts,
                response=response,
                reference=pair["answer"],
            )
        )

    # 2. 评估
    result = evaluate(
        EvaluationDataset(samples),
        metrics=[Faithfulness(), AnswerRelevancy(), ContextPrecision(), ContextRecall()],
        evaluator_llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    print("\nRagas 四指标（0-1，越高越好）：")
    for name, value in result.items():
        print(f"  {name:22s} {value:.3f}")
    print("\n读数指南：Context 系列低 → 优化检索（top-k/切分）；")
    print("          Faithfulness 低 → 收紧 system prompt 的拒答约束；")
    print("          AnswerRelevancy 低 → 检查 prompt 是否答非所问。")


if __name__ == "__main__":
    main()
