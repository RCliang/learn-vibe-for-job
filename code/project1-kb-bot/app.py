"""项目 1：企业知识库问答机器人（Streamlit 版）。

本地运行：streamlit run app.py
云端部署：Hugging Face Space（见 README.md 部署一节）
"""

import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from rag_core import CHUNK_SIZE, KB_DIR, OVERLAP, TOP_K, build_kb, retrieve, stream_answer

load_dotenv()


def get_secret(name: str) -> str | None:
    """本地读 .env；HF Space 读 Settings 里配置的 secrets。一个函数兼容两端。"""
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


API_KEY = get_secret("GLM_API_KEY")
BASE_URL = get_secret("GLM_BASE_URL") or "https://open.bigmodel.cn/api/paas/v4"
MODEL = get_secret("GLM_MODEL") or "glm-4-flash"
EMBED_MODEL = get_secret("GLM_EMBED_MODEL") or "embedding-3"

# ---------- 页面骨架 ----------
st.set_page_config(page_title="企业知识库问答", page_icon="🏢", layout="centered")
st.title("🏢 星辰科技 · 企业知识库问答")
st.caption("基于 RAG：检索公司制度与产品文档，回答带引用、不编造")

with st.sidebar:
    st.header("⚙️ 检索策略")
    st.markdown(
        f"- 切分：`chunk={CHUNK_SIZE}` / `overlap={OVERLAP}`\n"
        f"- 检索：`top-k={TOP_K}`（余弦相似度）\n"
        f"- 模型：`{MODEL}` / `{EMBED_MODEL}`\n\n"
        "参数依据见 README 的评估结果一节。"
    )
    st.divider()
    st.markdown(f"📚 语料目录：`{KB_DIR.name}/`（三份制度文档，可整体替换）")

if not API_KEY:
    st.error(
        "未配置 GLM_API_KEY：本地请在项目根目录放 `.env`（参考 .env.example）；\n"
        "HF Space 请在 Settings → Variables and secrets 添加名为 GLM_API_KEY 的 Secret。"
    )
    st.stop()

openai_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ---------- 知识库：只建一次，进程内缓存 ----------
@st.cache_resource(show_spinner="正在构建知识库（首次约 1 分钟，之后走缓存）…")
def get_collection():
    return build_kb(API_KEY, BASE_URL, EMBED_MODEL)


collection = get_collection()


# ---------- 聊天界面 ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史对话（Streamlit 每次交互都会重跑整个脚本，靠 session_state 找回历史）
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("问点公司制度或产品的问题，例如：年假可以结转吗？")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        chunks, sources = retrieve(openai_client, EMBED_MODEL, collection, question, TOP_K)

        # 引用来源可折叠查看——「可回溯」是本项目毕业标准之一
        with st.expander("📖 引用来源（点开查看检索到的原文）"):
            for i, (chunk, source) in enumerate(zip(chunks, sources), 1):
                st.markdown(f"**[{i}] {source}**")
                st.text(chunk[:200] + ("…" if len(chunk) > 200 else ""))

        answer = st.write_stream(stream_answer(openai_client, MODEL, question, chunks))

    st.session_state.messages.append({"role": "assistant", "content": answer})
