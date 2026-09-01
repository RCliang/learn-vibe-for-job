"""Ch2 周末实战参考实现：简历优化器。

输入简历文本 → JSON mode 输出 → Pydantic 校验（失败自纠重试一次）
→ 友好打印。这是从「聊天玩具」到「应用」的第一步：输出可被程序消费。

用法：
    python resume_optimizer.py                # 使用 sample_resume.txt
    python resume_optimizer.py 我的简历.txt    # 分析你自己的简历
"""

import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

DEFAULT_RESUME = "sample_resume.txt"
MAX_ATTEMPTS = 2  # 最多调用两次：失败把报错喂回模型自纠


class Issue(BaseModel):
    dimension: str = Field(description="内容 / 表达 / 关键词 / 结构 之一")
    problem: str
    suggestion: str


class StarRewrite(BaseModel):
    original: str
    rewritten: str
    reason: str


class ResumeAdvice(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(max_length=3)
    issues: list[Issue]
    star_rewrites: list[StarRewrite]
    keywords_to_add: list[str]


SYSTEM_PROMPT = """你是一位资深的 AI 应用开发岗位简历顾问。分析用户简历，只给具体可执行的建议。

规则：
1. 每条 issue 的 problem 必须引用简历原文片段
2. star_rewrites 优先挑「职责堆砌、无量化结果」的句子，改写遵循 STAR：情境-任务-行动-量化结果
3. keywords_to_add 从 AI 应用开发岗 JD 高频词中挑 5 个（如 RAG、Function Calling、Agent、Docker、FastAPI）
4. 语气直接，不说客套话

严格按此 JSON 结构返回，不要输出其他内容：
{
  "overall_score": 0 到 100 的整数,
  "strengths": ["最多 3 条"],
  "issues": [{"dimension": "…", "problem": "…", "suggestion": "…"}],
  "star_rewrites": [{"original": "…", "rewritten": "…", "reason": "…"}],
  "keywords_to_add": ["…"]
}"""


def get_advice(client: OpenAI, resume_text: str) -> ResumeAdvice:
    """调用模型并校验；校验失败把报错喂回去自纠重试（生产环境通用模式）。"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"我的简历：\n\n{resume_text}"},
    ]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,  # 结构化输出用低温度
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content

        try:
            data = json.loads(raw_text)
            return ResumeAdvice.model_validate(data)
        except Exception as exc:
            if attempt == MAX_ATTEMPTS:
                raise SystemExit(
                    f"模型输出连续 {MAX_ATTEMPTS} 次未通过校验：{exc}\n"
                    "排查：system prompt 里的 JSON 结构描述是否与 ResumeAdvice 定义一致。"
                )
            print(f"[第 {attempt} 次输出未通过校验，喂回报错自纠重试]\n  {exc}\n")
            messages.append({"role": "assistant", "content": raw_text})
            messages.append(
                {"role": "user", "content": f"上面的 JSON 未通过结构校验：{exc}。"
                 "请修正问题后重新输出完整 JSON。"}
            )

    raise AssertionError("unreachable")  # 循环内必 return 或 raise


def print_advice(advice: ResumeAdvice) -> None:
    line = "=" * 46
    print(line)
    print(f"  简历总分：{advice.overall_score} / 100")
    print(line)

    print("\n[保留的优点]")
    for s in advice.strengths:
        print(f"  + {s}")

    print("\n[问题清单]")
    for i, issue in enumerate(advice.issues, 1):
        print(f"  {i}. [{issue.dimension}] {issue.problem}")
        print(f"     -> 建议：{issue.suggestion}")

    print("\n[STAR 改写示例]")
    for r in advice.star_rewrites:
        print(f"  原句：{r.original}")
        print(f"  改写：{r.rewritten}")
        print(f"  理由：{r.reason}\n")

    print("[建议补充的 JD 关键词] " + "、".join(advice.keywords_to_add))


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 LLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESUME
    try:
        with open(path, encoding="utf-8") as f:
            resume_text = f.read()
    except FileNotFoundError:
        raise SystemExit(f"找不到简历文件：{path}")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    advice = get_advice(client, resume_text)

    print_advice(advice)
    print("\n（输出已通过 Pydantic 校验，可直接用于程序处理——比如存库或生成 HTML）")


if __name__ == "__main__":
    main()
