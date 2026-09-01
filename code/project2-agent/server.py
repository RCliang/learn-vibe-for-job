"""项目 2 后端：FastAPI + Agent 内核 + 静态前端托管。

启动：uvicorn server:app --reload   →  http://127.0.0.1:8000
接口文档（FastAPI 自动生成）：http://127.0.0.1:8000/docs
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

from agent_core import ChatMemory, SYSTEM_PROMPT, input_filter, run_agent

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

app = FastAPI(title="星辰商城 AI 客服", version="1.0.0")

# 会话记忆：session_id → ChatMemory（内存版——重启即失，生产要换 Redis/数据库）
sessions: dict[str, ChatMemory] = {}

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """惰性创建：没有 Key 时服务仍能启动（健康检查、安全过滤可用）。"""
    global _client
    if _client is None:
        _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    return _client


class ChatRequest(BaseModel):
    """请求体定义——Pydantic 校验（呼应 Ch2）：字段类型不对直接 422，进不了业务逻辑。"""

    message: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(default="default", max_length=64)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    # 第 1 道：注入过滤（调模型之前，不花一分钱）
    ok, reason = input_filter(req.message)
    if not ok:
        return {"reply": f"🛡️ 输入被安全过滤拦截——{reason}", "tools_used": []}

    # 第 2 道：配置检查
    if not API_KEY:
        return JSONResponse(
            status_code=503,
            content={"reply": "服务端未配置 LLM_API_KEY，请联系管理员", "tools_used": []},
        )

    # 第 3 道：业务异常兜底——不让堆栈信息漏给用户
    memory = sessions.setdefault(req.session_id, ChatMemory(SYSTEM_PROMPT))
    try:
        answer, tools_used = run_agent(get_client(), MODEL, memory, req.message)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"reply": "服务开小差了，请稍后重试", "tools_used": []},
        )
    return {"reply": answer, "tools_used": tools_used}


# 静态前端挂载在根路径（必须在 API 路由之后声明）
app.mount("/", StaticFiles(directory=Path(__file__).parent / "frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
