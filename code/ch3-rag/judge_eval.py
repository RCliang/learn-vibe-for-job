"""Day 11 最小路径：LLM as judge 评估——用证据决定调优方向。

对 qa_pairs.json 里的每条问题跑一遍 RAG，再让模型扮演评委打分（1-5），
汇总平均分并记录明细，结果追加写入 eval_results.jsonl，方便多次对比。

用法：
    python judge_eval.py                    # 默认 top-k=3
    python judge_eval.py --k 5              # 对比不同 top-k
    python judge_eval.py --label "chunk600" # 自定义标签（配合不同建库参数）

调优实验（课程 Day 11）：
    python build_kb.py --chunk 300 && python judge_eval.py --label "chunk300"
    python build_kb.py --chunk 600 && python judge_eval.py --label "chunk600"
    然后对比 eval_results.jsonl 里两次的 avg。
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from rag_chat import generate_answer

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

QA_FILE = Path(__file__).resolve().parent / "qa_pairs.json"
RESULT_FILE = Path(__file__).resolve().parent / "eval_results.jsonl"

JUDGE_PROMPT = """你是严格的问答系统评委。根据【问题】【标准答案】【系统回答】【检索到的资料】，
给系统回答打 1-5 分：

5 = 完全正确且完整，有资料依据
4 = 正确但不够完整
3 = 部分正确，有遗漏或多余信息
2 = 大部分错误
1 = 完全错误，或知识库里明明有答案却说没有，或编造答案

严格按此 JSON 结构返回：{{ "score": 1-5 的整数, "reason": "一句话理由" }}"""


def judge(client: OpenAI, question: str, reference: str, response: str, contexts: list[str]) -> dict:
    """让模型当评委。复用 Ch2 的 JSON mode + 校验。"""
    user_content = (
        f"【问题】{question}\n\n【标准答案】{reference}\n\n"
        f"【系统回答】{response}\n\n【检索到的资料】\n"
        + "\n".join(f"[{i}] {c[:200]}" for i, c in enumerate(contexts, 1))
    )
    answer = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.0,  # 评委必须稳定
        response_format={"type": "json_object"},
    )
    return json.loads(answer.choices[0].message.content)


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 LLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    parser = argparse.ArgumentParser(description="LLM as judge 评估")
    parser.add_argument("--k", type=int, default=3, help="RAG 检索 top-k")
    parser.add_argument("--label", type=str, default="", help="本次评估标签，如 chunk600")
    args = parser.parse_args()

    qa_pairs = json.loads(QA_FILE.read_text(encoding="utf-8"))
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    label = args.label or f"k={args.k}"
    print(f"评估开始：{len(qa_pairs)} 条 · label={label}\n")

    per_question = []
    for i, pair in enumerate(qa_pairs, 1):
        response, _ = generate_answer(pair["question"], args.k)
        # 重新检索一次拿 contexts 给评委看（generate_answer 内部已检索过）
        from rag_chat import retrieve

        contexts, _ = retrieve(pair["question"], args.k)
        verdict = judge(client, pair["question"], pair["answer"], response, contexts)
        per_question.append(
            {"question": pair["question"], "score": verdict["score"], "reason": verdict["reason"]}
        )
        print(f"  [{i}/{len(qa_pairs)}] {verdict['score']} 分 - {verdict['reason']}")

    avg = sum(item["score"] for item in per_question) / len(per_question)
    worst = min(per_question, key=lambda item: item["score"])

    print(f"\n平均分：{avg:.2f} / 5")
    print(f"最弱的一题（调优线索）：{worst['question']}（{worst['score']} 分）")

    record = {
        "label": label,
        "k": args.k,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "avg": round(avg, 2),
        "per_question": per_question,
    }
    with RESULT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"\n结果已追加到 {RESULT_FILE.name}（每行一次评估，可直接对比多组参数）")


if __name__ == "__main__":
    main()
