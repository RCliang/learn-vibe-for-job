"""Ch3 完整路径（选做）：GraphRAG 迷你实验——体验「知识图谱补向量检索的短板」。

流程：
  1. 建图：对 data/project1-kb/*.md 各做一次 JSON mode 调用，抽取实体与三元组关系
  2. 对比问答：三个问题分别用「向量 RAG」（rag_chat）和「小图 + LLM 走边」回答

前置：已完成本章最小路径（建好 chroma_db、配好 .env）。
用法：python graph_rag_mini.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from rag_chat import generate_answer

load_dotenv()

API_KEY = os.getenv("GLM_API_KEY")
BASE_URL = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
MODEL = os.getenv("GLM_MODEL", "glm-4-flash")

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "project1-kb"

EXTRACT_PROMPT = """你是信息抽取专家。从下面的公司制度文本中抽取实体和关系，用于构建知识图谱。

规则：
1. 实体包括：角色（如「部门总监」）、事项（如「事假」「报销」）、条件（如「超过3天」）等
2. 关系用三元组表示：head-relation-tail，例如「事假-审批人-部门总监」
3. 忠于原文，不要推断原文没有的关系
4. 每条关系尽量带上适用条件（可并入 relation 描述）

严格按此 JSON 结构返回，不要输出其他内容：
{"entities": ["…"], "relations": [{"head": "…", "relation": "…", "tail": "…"}]}

文本：
{doc_text}"""

GRAPH_QA_PROMPT = """你是基于知识图谱的问答助手。下面是图谱的全部边（head - relation - tail）：

{edges}

请沿关系边推理回答问题；图中信息不足以回答时明确说明。问题：{question}"""

# 三类问题：枢纽（跨文档聚合）、实体聚合、简单事实（向量 RAG 的主场）
QUESTIONS = [
    "部门总监负责审批哪些事项？",
    "和「财务经理」相关的流程有哪些？",
    "年假可以结转吗？",
]


def extract_graph(client: OpenAI) -> list[dict]:
    """对每份语料做一次关系抽取，汇总成边列表。"""
    edges: list[dict] = []
    for md_file in sorted(KB_DIR.glob("*.md")):
        doc_text = md_file.read_text(encoding="utf-8")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": EXTRACT_PROMPT.format(doc_text=doc_text)}
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        edges.extend(data.get("relations", []))
        print(f"{md_file.name}：抽取到 {len(data.get('relations', []))} 条关系")
    return edges


def graph_answer(client: OpenAI, edges: list[dict], question: str) -> str:
    """图很小（几十条边），直接把全部边给模型让它沿边推理——迷你版的「图检索」。"""
    edge_lines = "\n".join(f"{e['head']} - {e['relation']} - {e['tail']}" for e in edges)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": GRAPH_QA_PROMPT.format(edges=edge_lines, question=question)}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 GLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    print("=" * 50)
    print("第 1 步：建图（LLM 抽取实体关系）")
    print("=" * 50)
    edges = extract_graph(client)
    print(f"\n共 {len(edges)} 条边：")
    for edge in edges:
        print(f"  {edge['head']} -[{edge['relation']}]-> {edge['tail']}")

    print("\n" + "=" * 50)
    print("第 2 步：同题对比（向量 RAG vs 图）")
    print("=" * 50)
    for question in QUESTIONS:
        vector_answer, _ = generate_answer(question, k=3)
        g_answer = graph_answer(client, edges, question)
        print(f"\n【问题】{question}")
        print(f"\n— 向量 RAG：{vector_answer}")
        print(f"\n— 图方式：{g_answer}")

    print(
        "\n观察要点：前两题（枢纽/聚合）图方式应更完整——它把散在两份文档里、"
        "靠同一实体关联的信息拼齐了；第三题（简单事实）两者都行，向量 RAG 甚至更直接。"
        "\n结论：没有银弹，只有合适——真实 GraphRAG 的图构建成本很高，"
        "工程上先用轻方案，评估证明不够再升级。"
    )


if __name__ == "__main__":
    main()
