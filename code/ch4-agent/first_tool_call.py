"""Day 15：Function Calling 单次调用全流程——看清工具调用的 4 个步骤。

运行：python first_tool_call.py

模型并不执行任何工具！它只是「声明要调用哪个函数、给什么参数」，
真正的执行永远发生在你的代码里（这是第 17 天安全课的认知地基）。
"""

import json
import os
import random

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


def get_weather(location: str) -> dict:
    """本地 mock 实现——真实项目里这里会去调天气 API 或查数据库。"""
    return {
        "location": location,
        "weather": random.choice(["晴", "多云", "小雨"]),
        "temp_c": random.randint(18, 32),
    }


# 第 1 步：用 JSON Schema 告诉模型「有什么工具可用」
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市当前的天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名，如：北京"}
                },
                "required": ["location"],
            },
        },
    }
]


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 LLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    question = "上海今天天气怎么样？适合跑步吗？"
    messages = [{"role": "user", "content": question}]

    # 第 2 步：发起请求，模型决定是否调用工具
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,          # ← 把工具清单交给模型
        tool_choice="auto",   # ← auto：模型自己决定用不用
    )
    message = response.choices[0].message
    print(f"问题：{question}")
    print(f"模型想调用工具吗：{'是' if message.tool_calls else '否'}")

    if not message.tool_calls:
        print("模型直接回答了（没用到工具）：", message.content)
        return

    # 第 3 步：解析模型的决定，真正执行工具（在你的代码里！）
    tool_call = message.tool_calls[0]
    print(f"模型请求调用：{tool_call.function.name}")
    print(f"参数（JSON 字符串，需 json.loads）：{tool_call.function.arguments}")

    args = json.loads(tool_call.function.arguments)
    result = get_weather(**args)          # ← 执行的永远是你写的 Python 函数
    print(f"本地执行结果：{result}")

    # 第 4 步：把「模型的决定 + 工具结果」回填，让模型生成最终回答
    messages.append(message)  # 含 tool_calls 的 assistant 消息必须原样入历史
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result, ensure_ascii=False)}
    )
    final = client.chat.completions.create(model=MODEL, messages=messages)
    print(f"\n最终回答：{final.choices[0].message.content}")


if __name__ == "__main__":
    main()
