# 《AI 应用开发速成营》课程设计（Spec）

- 日期：2026-08-24
- 状态：已获用户批准的设计，待编写实施计划（2026-08-25 补充：效果评估、Prompt Injection 安全、多轮记忆管理、SSE 流式、示例数据，28 天排期不变）
- 项目仓库：`learn-vibe-coding`（本仓库）

## 1. 背景与目标

**要解决的问题**：零基础转行者想进入 AI 开发岗位，但现有课程两极分化——
easy-vibe 类"vibe coding"课程偏工具、广而浅，产出偏玩具；算法/论文类课程对小白门槛过高。
而真实岗位 JD（腾讯/字节/京东/灵犀互娱等，2026 年在招）的高频要求高度一致且可速成：
Prompt Engineering、RAG、Function Calling、Agent 开发、Linux/Docker/云部署、完整可在线访问的项目经验。

**课程目标**：28 天速成（4 周 × 每天 2 小时），零基础学员毕业时具备：

1. 两个可在线访问、可写上简历的 AI 项目
2. 覆盖 AI 应用开发岗 JD 高频关键词的技能集
3. 真实生产链路认知：原型（Streamlit）→ 前后端分离（FastAPI）→ 生产部署（Docker + 云服务器）

**成功标准**：

- 零基础学员按课程节奏学完并产出 2 个达到毕业标准的项目
- 课程内容覆盖目标岗位 JD 高频技能 ≥ 90%（以附录 JD 关键词对照表为准）
- 每天有可验证的交付物；每章有自测门槛

## 2. 目标学员

- 无编程基础、想转行 AI 开发岗位的成人学习者
- 每天可投入约 2 小时，持续 4 周
- 全程零翻墙：使用国内模型（GLM/DeepSeek）与国内可注册工具
- 可接受小额工具订阅（GLM Coding Plan，每月一杯奶茶价位）与可选的云服务器开销（约几十元/月，提供零成本备选路径）

## 3. 定位与差异化

| 维度 | 本课程 | easy-vibe 类课程 |
|---|---|---|
| 定位 | 就业直通（窄而深） | 通用创作（广而浅） |
| 设计方法 | JD 逆向设计 | 工具功能覆盖 |
| 产出 | 2 个对标岗位的项目 | 多个小作品 |
| 工程化 | Linux/Docker/云部署完整链路 | 无或极少 |

教学法：**Vibe Coding 作为手段而非目的**——学员用 AI 结对编程降低编码门槛，但必须达到"能读懂、能修改、能调试 AI 生成的代码"的水平，因为岗位要求会写代码。

## 4. 设计原则

1. **JD 逆向设计**：每章开头标注「本章对应哪些岗位关键词」与「学完你能做什么」
2. **最小知识集**：不在目标岗位 JD 里的内容不讲；文首放明确的「不讲清单」
3. **每天有交付物**：每天结束有一件能看/能用/能晒的东西，防弃坑
4. **双路径**：每章区分「最小路径」（必做核心）与「完整路径」（选做进阶），学不完可降级为 5-6 周
5. **自测门槛**：每章末尾有通关清单，卡住时有排错指引

## 5. 技术栈

| 类别 | 选型 | 理由 |
|---|---|---|
| 开发环境 | VSCode + Claude Code（TUI 主选）/ ZCode（GUI 备选） | 行业主流工具栈、简历辨识度高；智谱 GLM Coding Plan 驱动，国内零翻墙 |
| 语言 | Python 3.10+ | JD 压倒性主流；只教读懂 AI 代码所需最小集 |
| LLM 接入 | `openai` SDK + `base_url` 指向 GLM/DeepSeek | OpenAI 兼容格式，切换模型零成本 |
| 向量库 | Chroma | pip 安装即用、本地内嵌、零运维 |
| 快速界面 | Streamlit | 项目 1 用，几行代码出聊天界面 |
| 生产后端 | FastAPI | LLM 应用后端事实标准，同语言零额外学习成本 |
| 前端 | AI 生成的极简 HTML/JS 页面 | 只要求能看懂、能小改 |
| 容器 | Docker + docker compose | JD 高频；打包项目 2 |
| 服务器 | 国内轻量云服务器（阿里云/腾讯云） | 生产部署实战 |
| 课程站 | VitePress + GitHub Pages | 中文生态好、易部署、easy-vibe 同款 |

## 6. 课程结构（3+1 周，28 天）

### Week 1 —— 上手与出活（建立信心）

**Ch0 环境与第一行代码（Day 1-2）**
- 开发环境：VSCode（主选，安装配置简单）+ Claude Code（TUI 主选）/ ZCode（GUI 备选），由 GLM Coding Plan 驱动，国内零翻墙
- 开通 GLM Coding Plan 并申请 API Key（一个 Key 同时驱动编程工具与 API 调用；附按量付费备选）
- HTTP 与 API 基础（约半天）：什么是前后端、请求/响应、JSON、状态码——调用 LLM API 本身就是一次 HTTP 请求
- Python 最小集（重点讲工程三件套）：import（模块与包、ModuleNotFoundError 排错）、pip（requirements.txt、换国内源）、venv（创建/激活/退出、Windows 多终端差异、VSCode 选择解释器）；变量/函数/字典/列表压缩为「读懂 AI 代码速查表」
- Git/GitHub 最小集：init/add/commit/push
- 交付物：跑通第一个 LLM API 调用并 push 到 GitHub
- JD 关键词：Python、API 调用、Git

**Ch1 Vibe Coding 工作流（Day 3-4）**
- 完整循环：提需求 → AI 生成 → 读懂 → 修改 → 修 bug
- 如何写好给 AI 的指令：任务上下文、约束、验收标准
- 调试基本功：看报错、贴报错给 AI
- 交付物：用 AI 结对完成一个小脚本并解决至少一个报错
- JD 关键词：AI 辅助开发

**Ch2 Prompt 工程实战（Day 5-7）**
- System/User 角色、few-shot、温度与参数
- 结构化输出：JSON mode + Pydantic 解析
- Token 成本意识、上下文长度
- 周末小实战：简历优化器小工具（输入简历文本 → 输出结构化改进建议）
- 交付物：可运行的简历优化器
- JD 关键词：Prompt Engineering

### Week 2 —— RAG 与项目 1（第一个简历项目）

**Ch3 RAG 知识库（Day 8-11）**
- Embedding 概念与 API 调用
- 文档加载与切分策略（chunk size / overlap）
- Chroma 入库与相似度检索
- 检索增强生成：检索 → 拼接 prompt → 生成 → 引用标注
- 效果评估驱动调优（约半天，与原调优内容合并）：最小路径为手写 10 条测试问答集 + LLM as judge 打分脚本，对比不同 top-k / 切分参数的得分；完整路径为 Ragas 四指标（faithfulness、answer relevancy、context precision、context recall）
- 交付物：本地可跑的 RAG 问答脚本 + 一份评估对比结果
- JD 关键词：Embedding、RAG、知识库建设、效果评估、Ragas

**项目 1：企业知识库问答机器人（Day 12-14，跟做）**
- 完整链路：文档解析 → 切分 → 向量化 → 检索 → 带引用回答
- Streamlit 聊天界面（含流式输出）
- 部署：Hugging Face Space（首选）或本地 + 演示 GIF
- 毕业标准见第 7 节
- JD 关键词：知识库建设、流式输出

### Week 3 —— Agent 与项目 2（前后端分离实战）

**Ch4 Function Calling 与 Agent（Day 15-18）**
- 工具定义、参数 schema、调用流程
- 手写 mini Agent Loop：while 循环 + 工具调用 + 结果回填（先懂本质再谈框架）
- 多轮对话记忆管理（约半天）：历史消息拼接、滑动窗口截断、token 预算控制
- 安全：Prompt Injection 基础（约半天）：注入原理（用户输入覆盖 system 指令）、工具调用场景的风险、防御三板斧——输入过滤 / 指令与数据隔离 / 工具权限最小化；最小路径为给 mini Agent 加一条输入过滤
- MCP 是什么、解决什么问题（概念级）；LangChain/LangGraph 何时需要（阅读材料）
- 交付物：支持多轮对话、具备基础输入过滤的 mini Agent
- JD 关键词：Function Calling、Agent 开发、LLM 应用安全

**项目 2：垂直领域 Agent 助手（Day 19-21，独立完成，三选一，最后 1 天用于验收打磨）**
- 选题 A：AI 客服（查订单 + 退改政策问答）
- 选题 B：数据分析 Agent（CSV 上传 + 自然语言问答出图表）
- 选题 C：工作流助手（如会议纪要 → 拆任务 → 生成待办）
- 架构：FastAPI 后端 + AI 生成的极简 HTML/JS 聊天页前端，学员亲手体验前后端通过 API 通信
- 硬性要求：≥2 个工具调用、多轮对话、错误处理（错误处理含对异常/恶意输入的兜底——不触发危险工具动作）
- 加分项（完整路径选做）：SSE 流式输出（FastAPI SSE 接口 + 前端 EventSource 消费）
- JD 关键词：Agent 开发、业务流程自动化、前后端分离

### Week 4 —— 工程化与上云（生产链路 + 求职）

**Ch5 Linux 与服务器基础（Day 22-23）**
- SSH 连接服务器、文件操作、常用命令（ls/cd/cp/mv/cat/grep/ps/kill）
- 进程管理、看日志排错、环境变量
- 交付物：在云服务器上跑起一个 Python 脚本并查看日志
- JD 关键词：熟悉 Linux 环境

**Ch6 Docker 容器化（Day 24-25）**
- 镜像与容器概念、Dockerfile 编写、docker compose
- 把项目 2 打包成镜像并本地运行
- 交付物：项目 2 的 Docker 镜像 + compose 文件
- JD 关键词：Docker、容器化部署

**Ch7 云服务部署实战（Day 26-27）**
- 国内轻量云服务器选购（新用户约几十元/月）、安全组与端口
- 部署项目 2 上线公网；域名与 HTTPS 概念
- 零成本备选路径：Hugging Face Space 部署 + 演示 GIF
- 交付物：公网可访问的项目 2（或零成本等效物）
- JD 关键词：云服务、工程化上线

**Ch8 求职冲刺（Day 28）**
- README 架构写法（架构图、技术选型理由）
- 简历项目描述模板（STAR 法则）
- 高频面试题清单：RAG 原理、幻觉处理、切分策略、Agent Loop、Linux/Docker/部署、RAG 效果评估（Ragas 指标）、Prompt Injection 防御
- 项目深挖题：「你的 top-k 为什么是 5」「幻觉率怎么量化」「如果用户诱导 Agent 调用危险工具怎么办」
- 求职期继续学习路线（微调、LangGraph、多智能体作为进阶方向）；延伸资源附对标参考课程：mlabonne/llm-course、datawhalechina/llm-universe、huggingface/agents-course、huggingface/mcp-course、Shubhamsaboo/awesome-llm-apps
- 交付物：一份含两个项目的简历项目描述

## 7. 项目毕业标准

**项目 1（跟做）：企业知识库问答机器人**
- 在线可访问的 RAG 问答 Demo（HF Space 首选；README 附本地运行说明 + 演示 GIF）
- 回答带引用来源；README 说明切分与检索策略，并附评估结果（测试问答集得分）
- GitHub 仓库结构清晰（代码、requirements、README）

**项目 2（独立）：垂直领域 Agent 助手**
- FastAPI 后端 + 极简前端，前后端分离
- ≥2 个工具调用、多轮对话、错误处理（含异常/恶意输入兜底）
- 公网可访问（真机路径）或 HF Space + 演示 GIF（零成本路径）
- README 含架构图与设计决策说明，面试时能讲清"为什么这样设计"

## 8. 仓库与文档站结构

```
learn-vibe-coding/
├── docs/                      # VitePress 课程站
│   ├── .vitepress/config.ts   # 站点配置（中文、导航、侧边栏）
│   ├── index.md               # 课程介绍 + 承诺 + 大纲
│   ├── guide/                 # ch0-ch8 + project1 + project2
│   └── appendix/              # 面试题库、FAQ、不讲清单、JD 关键词对照表、延伸资源
├── code/                      # 各章可运行示例代码
│   ├── ch0-hello-llm/
│   ├── ch2-prompt/
│   ├── ch3-rag/
│   ├── ch4-agent/
│   ├── project1-kb-bot/       # 项目 1 完整参考实现
│   └── project2-agent/        # 项目 2 三选一起始骨架 + 参考实现
├── data/                      # 示例语料与数据集（学员可替换为自己领域文档）
│   ├── project1-kb/           # 项目 1 企业知识库文档（制度/产品手册 markdown）
│   ├── project2-orders.json   # 项目 2 选题 A mock 订单数据
│   └── project2-sales.csv     # 项目 2 选题 B 示例数据
├── .github/workflows/         # VitePress 构建 + GitHub Pages 自动部署
└── README.md                  # 项目介绍
```

## 9. 部署策略（学员侧双路径）

- **真机路径（推荐）**：轻量云服务器部署项目 2，面试可答部署细节；成本约几十元/月
- **零成本路径**：HF Space 部署 + 演示 GIF，给暂不付费的学员；课程明确说明两条路径的取舍

## 10. 防弃坑机制

- 每章末尾自测门槛：能独立完成 X 才进入下一章；卡住时的排错指引
- 每章标注最小路径（必做）vs 完整路径（选做）；3+1 周学不完可降级为 5-6 周
- 每天有交付物；全程零翻墙

## 11. 不讲清单（明确排除）

Transformer 原理、微调/SFT、数学基础、多智能体高级编排、LangChain/LangGraph 上手实战（仅概念级）、前端框架（React/Vue）教学、Kubernetes。

排除理由：目标岗位 JD 中为少数派要求或超出速成定位；作为附录"进阶路线"指引有需要的学员自学。

## 12. 风险与对策

| 风险 | 对策 |
|---|---|
| 零基础学员卡在环境配置 | VSCode/Python 一键安装包路线；Claude Code 配置步骤按智谱官方文档核对；Ch0 全程排错指引 |
| 4 周学不完 | 双路径设计，可降级 5-6 周；每章独立可暂停 |
| 学员不愿付云服务器费用 | 零成本部署路径兜底 |
| HF Space 国内访问不稳 | 真机路径为主推；零成本路径附演示 GIF 与本地运行说明 |
| AI 生成的代码学员完全看不懂 | Ch1 专设"读懂代码"训练 + 各章自测门槛 |
| 评估/安全内容增加学员负担 | 最小路径各控制在半天；手写测试集不依赖新框架，Ragas 仅完整路径 |

## 13. 后续工作

- 使用 writing-plans 技能编写实施计划：文档站搭建 → 各章内容 → 示例代码 → 项目实现 → 部署流水线
- 实施顺序建议：先搭 VitePress 站点骨架与部署流水线（早可见），再按 Ch0→Ch8 顺序产出内容与配套代码
