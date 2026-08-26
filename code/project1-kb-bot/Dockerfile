# 项目 1 的 Docker 镜像：代码 + 依赖 + 语料 打成一个可移植的整体
FROM python:3.12-slim

WORKDIR /app

# 先只拷依赖清单再安装：利用 Docker 层缓存——改代码不用重装依赖（Ch6 详讲）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 代码与语料（语料需先拷进项目目录：cp -r 仓库根/data/project1-kb ./data/）
COPY app.py rag_core.py ./
COPY data/ ./data/

# .env 被刻意排除在镜像外（见 .dockerignore）——密钥运行时注入，绝不打进镜像
EXPOSE 8501

# 容器内必须监听 0.0.0.0，否则端口映射后外面访问不到（高频坑）
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
