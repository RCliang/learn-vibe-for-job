"""Ch1 实战参考实现：周报生成器。

流水账 → DeepSeek → 结构化 Markdown 周报。
先自己用 AI 结对生成你的版本，卡壳超过 20 分钟再来对照本文件
（本文件已包含课程第 4 节 Step 3 的三个迭代要求）。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 把你本周的流水账粘贴到这里（一行一条）
RAW_TEXT = """周一 开需求会，定了周报自动化的边界
周二 修登录页 bug，和测试对了一轮用例
周三 继续修 bug，顺手把部署脚本改了
周四 写周报花了半小时，感觉在重复劳动
周五 组内分享，讲了讲这周踩的坑
"""

PROMPT_TEMPLATE = """你是一位职场写作助手。请把下面的流水账整理成结构化周报。

要求：
1. 按「本周完成 / 进行中 / 下周计划 / 需要支持」四节组织
2. 每节最多 5 条，多余的合并；每条一行、动词开头
3. 去掉口语和情绪词，语气正式但不僵硬
4. 末尾追加一节「本周关键词」，从流水账提炼 3 个词
5. 输出 Markdown 格式

流水账内容：
{raw_text}
"""


def generate_weekly_report(raw_text: str) -> str:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一位专业的职场写作助手。"},
            {"role": "user", "content": PROMPT_TEMPLATE.format(raw_text=raw_text)},
        ],
    )
    return response.choices[0].message.content


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 LLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    try:
        report = generate_weekly_report(RAW_TEXT)
    except Exception as exc:  # API 调用失败给人能看懂的提示（401 = Key 问题）
        raise SystemExit(
            f"调用模型失败：{exc}\n"
            "排查建议：1) 检查 .env 里的 LLM_API_KEY 是否正确；"
            "2) 网络是否可用；3) 把完整报错贴给 AI 帮你分析。"
        )

    with open("weekly_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("周报已生成 → weekly_report.md")
    print("\n" + report)


if __name__ == "__main__":
    main()
