"""练习 3：修一个 API 401 错误（鉴权失败）。

提示：这不是代码逻辑错误，是凭证/环境问题——回忆 Ch0 的 .env 机制，
答案藏在 code/ch0-hello-llm/hello_llm.py 里。

修复标准：运行后打印出模型返回的一句话。
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-这是一个故意写错的Key",
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用一句话夸夸正在修 bug 的我"}],
)
print(response.choices[0].message.content)
