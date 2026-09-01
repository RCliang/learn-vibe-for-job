"""Day 5 实验：同一个 prompt，三种温度，对比输出差异。

运行前：激活虚拟环境并安装依赖（pip install -r requirements.txt）、
配好 .env。运行：python temperature_lab.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

PROMPT = "用一个新鲜的比喻，解释大模型的 temperature 参数是什么。不超过两句话。"
TEMPERATURES = [0.2, 0.7, 1.0]


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 LLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    for temp in TEMPERATURES:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
            temperature=temp,
        )
        print("=" * 44)
        print(f"temperature = {temp}")
        print("=" * 44)
        print(response.choices[0].message.content)
        u = response.usage
        print(f"\n[token] 输入 {u.prompt_tokens} · 输出 {u.completion_tokens} · 合计 {u.total_tokens}\n")


if __name__ == "__main__":
    main()
