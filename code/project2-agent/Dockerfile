# 项目 2 的 Docker 镜像：FastAPI 后端 + 静态前端 + Agent 内核
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY server.py agent_core.py ./
COPY frontend ./frontend
COPY data/ ./data/

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
