"""Day 6 演示：让模型输出「程序能用的 JSON」的三种做法。

用法：
    python json_parsing_demo.py step1   # 只靠 prompt 约束（脆弱演示，多跑几次）
    python json_parsing_demo.py step2   # JSON mode（response_format）
    python json_parsing_demo.py step3   # JSON mode + Pydantic 校验

任务：从一句话中抽取联系信息 {name, city, skills}。
"""

import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("GLM_API_KEY")
BASE_URL = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
MODEL = os.getenv("GLM_MODEL", "glm-4-flash")

INPUT_TEXT = "我叫张小明，坐标杭州，会 Python、Docker，最近在学 RAG。"

SCHEMA_HINT = (
    '你是信息抽取助手。严格按此 JSON 结构返回，不要输出任何其他内容：'
    '{"name": "…", "city": "…", "skills": ["…"]}'
)


def call_model(messages: list, json_mode: bool = False) -> str:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        **kwargs,
    )
    return response.choices[0].message.content


def step1() -> None:
    """只靠 prompt 说「只输出 JSON」——可能被 ```json 包裹或加解释文字。"""
    content = call_model(
        [{"role": "user", "content": f"从下面这句话抽取联系信息，只输出 JSON，"
         f"包含 name/city/skills 字段：\n{INPUT_TEXT}"}]
    )
    print("模型原始输出：")
    print(content)
    print("\n现在尝试 json.loads ...")
    try:
        data = json.loads(content)
        print("成功（这次运气不错，多跑几次观察稳定性）：", data)
    except json.JSONDecodeError as exc:
        print(f"失败！这就是第 1 步的脆弱性：{exc}")


def step2() -> None:
    """JSON mode：response_format 指定 json_object，结构描述写进 system。"""
    content = call_model(
        [
            {"role": "system", "content": SCHEMA_HINT},
            {"role": "user", "content": INPUT_TEXT},
        ],
        json_mode=True,
    )
    print("模型原始输出：")
    print(content)
    data = json.loads(content)
    print("\n解析成功（JSON mode 下 content 就是纯 JSON）：", data)


class ContactInfo(BaseModel):
    name: str
    city: str
    skills: list[str]


def step3() -> None:
    """JSON mode + Pydantic：合法 JSON 还要字段类型正确，才算程序可用。"""
    content = call_model(
        [
            {"role": "system", "content": SCHEMA_HINT},
            {"role": "user", "content": INPUT_TEXT},
        ],
        json_mode=True,
    )
    data = json.loads(content)
    info = ContactInfo.model_validate(data)
    print("Pydantic 校验通过，可以像普通对象一样使用：")
    print(f"  姓名：{info.name}")
    print(f"  城市：{info.city}")
    print(f"  技能：{'、'.join(info.skills)}")
    print("\n课程自测练习：把 ContactInfo 里的 skills: list[str] 改成 skills: str，"
          "再跑一次看 ValidationError 报什么，然后改回来。")


def main() -> None:
    if not API_KEY:
        raise SystemExit("未读到 GLM_API_KEY：请复制 .env.example 为 .env 并填入 Key")

    steps = {"step1": step1, "step2": step2, "step3": step3}
    if len(sys.argv) != 2 or sys.argv[1] not in steps:
        raise SystemExit(f"用法：python {sys.argv[0]} step1|step2|step3")
    steps[sys.argv[1]]()


if __name__ == "__main__":
    main()
