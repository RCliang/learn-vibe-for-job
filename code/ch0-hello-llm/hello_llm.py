"""Ch0 交付物：第一个 LLM API 调用。

运行前（详见同目录 README.md）：
1. 创建并激活虚拟环境
2. pip install -r requirements.txt
3. 复制 .env.example 为 .env，填入你的 DeepSeek API Key
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# 从 .env 文件加载环境变量：Key 不写进代码、不进 Git
load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


def main() -> None:
    if not API_KEY:
        raise SystemExit(
            "未读到 LLM_API_KEY：请复制 .env.example 为 .env，填入你的 DeepSeek API Key"
        )

    # OpenAI SDK + base_url 指向 DeepSeek：以后换模型只改 .env，不用改代码
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages = [
        {"role": "system", "content": "你是一位耐心的编程入门教练。"},
        {"role": "user", "content": "用一句话向零基础学员解释什么是 API。"},
    ]

    try:
        response = client.chat.completions.create(model=MODEL, messages=messages)
    except Exception as exc:  # 新手阶段先兜底，把报错贴给 AI 帮你排查（Ch1 会教方法）
        raise SystemExit(f"调用失败，把下面这段报错完整复制给 AI 排查：\n\n{exc}")

    answer = response.choices[0].message.content
    print("模型返回：")
    print(answer)
    print(f"\n（本次对话模型：{MODEL} · 端点：{BASE_URL}）")


if __name__ == "__main__":
    main()
