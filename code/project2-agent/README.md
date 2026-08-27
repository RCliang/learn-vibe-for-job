# 垂直领域 Agent 助手（FastAPI 前后端分离）

> 《AI 应用开发速成营》项目 2 · 独立完成 · 三选一
> 本目录提供 **选题 A 的完整参考实现** 与 B/C 的起步指引。

## 选题指引（三选一）

| 选题 | 场景 | 工具设计（≥2 个） | 数据 | 难度 |
| --- | --- | --- | --- | --- |
| **A：AI 客服**（参考实现） | 查订单 + 退改政策 | `get_order` / `list_orders` / `get_refund_policy` / `get_current_time` | `data/project2-orders.json` | ★★ |
| **B：数据分析 Agent** | CSV 上传 + 自然语言问答出图表 | `describe_column`（列统计）/ `chart`（按列画图存 PNG 返回路径） | `data/project2-sales.csv`（pandas + matplotlib） | ★★★ |
| **C：工作流助手** | 会议纪要 → 拆任务 → 待办清单 | `parse_minutes`（LLM 抽任务清单）/ `add_todo` + `list_todos`（内存待办） | 无需数据文件 | ★ |

**B/C 起步法**：复制本目录 → 保留 `server.py` 骨架与 `ChatMemory`/`input_filter` → 只改 `agent_core.py` 的工具部分和 `SYSTEM_PROMPT` → 前端改标题与欢迎语即可。选题 B 的图表可用 `<img src="后端返回的图片路径">` 展示。

## 目录结构（选题 A 参考实现）

```
project2-agent/
├── server.py            # FastAPI 后端：/api/chat、/api/health、静态前端托管、三层错误兜底
├── agent_core.py        # Agent 内核（Ch4 提炼）：4 工具 + Agent Loop + ChatMemory + 注入过滤
├── frontend/index.html  # 极简聊天前端（原生 JS：fetch + JSON + DOM，约 130 行）
├── Dockerfile           # Ch6/Ch7 部署用（含打包说明注释）
├── requirements.txt
└── .env.example
```

## 本地运行

```bash
cd code/project2-agent
python -m venv .venv && .venv\Scripts\activate   # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
# 复制 .env.example 为 .env，填入 GLM_API_KEY
uvicorn server:app --reload
# 浏览器打开 http://127.0.0.1:8000（接口文档自动生成在 /docs）
```

试这句（触发链式多工具）：`我（张小明）有哪些订单？第一单到哪了？`

## Docker 部署（Ch6 系统化、Ch7 上云，命令先备好）

```bash
mkdir data && cp ../../data/project2-orders.json data/   # 语料拷进项目目录（镜像内自包含）
docker build -t agent-app .
docker run -d --name agent-app -p 8000:8000 --env-file .env agent-app
```

（服务器需在安全组/防火墙放行 8000 端口——步骤同项目 1，Ch7 完整走一遍。）

## 硬性要求对照（毕业标准）

- ✅ ≥2 个工具调用（4 个）· 多轮对话（ChatMemory 按 session 隔离）· 错误处理（Pydantic 422 / 注入拦截 / 503 配置 / 500 兜底，不泄露堆栈）
- SSE 流式输出为**加分项**，实现见课程第 6 节完整路径
