---
title: Ch3 RAG 知识库（Day 8-11）
outline: [2, 3]
---

# Ch3 RAG 知识库（Day 8-11）

> **本章 JD 关键词**：Embedding、RAG、知识库建设、效果评估、Ragas
>
> **学完你能做什么**：解释 RAG 的完整原理（这是面试必考题）；把一批文档切分、向量化、存进向量库；写一个带引用标注、会诚实说「不知道」的知识库问答引擎；用测试集量化评估检索和回答质量，用证据决定调优方向。本章产出就是项目 1 的核心引擎。

::: info 📋 本章路线
**Day 8**：Embedding 原理与实验 · **Day 9**：切分与 Chroma 入库 · **Day 10**：检索增强问答 · **Day 11**：效果评估驱动调优（完整路径：Ragas / GraphRAG 迷你实验）
:::

---

## 1. 为什么需要 RAG

直接问大模型「我们公司年假几天」，它会一本正经地编一个答案——因为**它根本没见过你公司的制度**。模型的知识有两个边界：训练数据截止日期之后的它不知道，私有数据（公司制度、产品文档、你的笔记）它更没见过。

两条解决路线的对比（面试常考）：

| | 微调 Fine-tuning | RAG 检索增强生成 |
| --- | --- | --- |
| 原理 | 把知识「练进」模型参数 | 把资料放在模型「手边」，答题时翻阅 |
| 成本 | 需要 GPU、数据准备、训练周期 | 只要 API 调用 |
| 知识更新 | 重新训练 | 换文档重建索引即可，分钟级 |
| 适合 | 改变风格/专业语气 | **私有知识问答（本课程主线）** |

**RAG = 给模型开卷考试**：把你的资料准备好，考试（提问）时先把相关页码（检索）翻出来递给它，它照着答（生成）。整个流程分两个阶段：

```
离线入库（做一次）：
  文档 → 切分成小块 → 每块向量化 → 存入向量库

在线问答（每次提问）：
  问题向量化 → 在向量库里找最相似的 k 块 → 拼进 prompt → 模型生成带引用的回答
```

本章代码在 [code/ch3-rag/](https://github.com/RCliang/learn-vibe-for-job/tree/main/code/ch3-rag)，语料在 `data/project1-kb/`（虚构公司「星辰科技」的三份制度文档）——**建库脚本不挑文档，随时可以换成你感兴趣领域的资料**。

---

## 2. Embedding：给文本一个语义坐标（Day 8）

### 2.1 直觉

Embedding 模型把一段文本变成一个很长的数字列表（向量，比如 2048 个数），它像一个「语义坐标」：**意思相近的文本，坐标就靠近**。「我想请年假」和「年假申请流程」虽然字面不同，但向量距离很近——这就是机器做「语义检索」的全部秘密。

衡量两个向量「方向有多一致」用**余弦相似度**（-1 到 1，越接近 1 越相似）。数学不神秘，几行代码就能算，我们在实验里亲手写一遍。

### 2.2 调用 Embedding API（硅基流动）

**一个预告过的分叉**：DeepSeek 只有对话 API，不提供 embedding。本章向量化改用**硅基流动（SiliconFlow）**——国内手机号注册（[cloud.siliconflow.cn](https://cloud.siliconflow.cn)，注册送免费额度），`bge-m3` 中文向量模型**免费**，且同样是 OpenAI 兼容接口：同一套 SDK，换个 base_url 和模型名而已。

> **实操**：去硅基流动控制台「API 密钥」新建一个 Key，填进 `.env` 的 `EMBED_API_KEY`。对话仍走 DeepSeek 的 `LLM_API_KEY`——**从本章起 `.env` 里有两把钥匙，各管一件事**（`.env.example` 里有注释说明）。

```python
client = OpenAI(api_key=EMBED_API_KEY, base_url="https://api.siliconflow.cn/v1")
response = client.embeddings.create(
    model="BAAI/bge-m3",           # 免费中文向量模型，本章全程花费 0 元
    input=["我想请年假去旅游", "年假的申请流程是什么"],
)
vectors = [item.embedding for item in response.data]  # 每句话一个 1024 维向量
```

（[硅基流动 Embeddings API 文档](https://docs.siliconflow.cn/cn/api-reference/embeddings/create-embeddings)：OpenAI 兼容格式，单条输入最长 8192 token。）

### 2.3 实验：亲眼看见语义距离

运行 `embedding_lab.py`：六句话（两组同主题 + 两句无关），两两算余弦相似度后从高到低排序。你会看到**同主题句对稳定排在无关句对前面**——这就是第 1 节整个 RAG 大厦的地基。

---

## 3. 文档切分与入库（Day 9）

### 3.1 为什么要切分

| 不切的问题 | 切分的作用 |
| --- | --- |
| 整篇文档塞进 prompt：超窗口、贵 | 每块独立检索，按需取用 |
| 检索粒度太粗：问「餐补」，检索出整篇报销制度 | 块小了，检索才「准」 |

两个关键参数（**面试高频**）：

- **chunk_size**：每块多大（中文常用 300-500 字）。太大 → 检索不精准；太小 → 上下文碎、语义不完整。
- **overlap**：相邻块重叠多少（常用 50）。防止关键句正好被切断在边界上，两边都检索不到。

```
|────── 块1 ──────|
           |────── 块2 ──────|
                      |────── 块3 ──────|
            ←重叠→
```

课程**手写滑窗切分**（`build_kb.py` 里的 `split_text`，十几行）——先懂本质；LangChain 的 `RecursiveCharacterTextSplitter` 是同样思想的工程化版本，放完整路径了解。

### 3.2 Chroma：能按语义查找的抽屉

Chroma 是本地内嵌的向量数据库：`pip install chromadb` 即用，数据落在 `chroma_db/` 目录，零运维。三个动作：

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("company_kb")

# 存：id + 原文 + 向量（我们显式传入 bge-m3 的向量，不依赖 Chroma 默认模型）
collection.add(ids=["leave_0"], documents=["年假 10 天..."], embeddings=[[0.1, ...]])

# 查：把问题也向量化，找余弦距离最近的 k 块
result = collection.query(query_embeddings=[[0.2, ...]], n_results=3)
```

::: warning 为什么显式传向量？
Chroma 默认会自动下载一个英文向量化模型（国内下载慢且中文效果差）。我们显式传入 bge-m3 的结果，**检索质量我们自己说了算**——这也是理解「向量库只管存和查，语义在 embedding 模型」的关键。
:::

### 3.3 实操

```powershell
python build_kb.py                # 默认 chunk=300, overlap=50
python build_kb.py --chunk 600    # Day 11 调优实验会用到
```

观察输出：三份文档各切成几块、向量维度、入库总数。试着把 chunk 调成 600，看看块数怎么变（然后调回 300，Day 11 会正式做对比实验）。

---

## 4. 检索增强生成（Day 10）

`rag_chat.py` 把三个环节串成完整链路，也是**项目 1 的引擎**：

### 4.1 检索 → 拼接 → 生成

```python
chunks, sources = retrieve("年假可以结转吗", k=3)      # ① 语义检索
prompt = build_prompt(question, chunks)                 # ② 编号拼接进 prompt
answer = client.chat.completions.create(...)            # ③ 生成
```

第 ② 步就是「增强」发生的地方——模型看到的 prompt 长这样：

```text
【参考资料】
[1] 年假当年有效，最多可结转 5 天到次年 3 月底……
[2] 请年假需提前 3 个工作日在 OA 系统提交……
【问题】年假可以结转吗？
```

### 4.2 幻觉抑制：三条 prompt 纪律

system prompt 里写死三条（`rag_chat.py` 的 `SYSTEM_PROMPT`，**面试答「怎么处理幻觉」的标准答案之一**）：

1. **只用资料**：只根据【参考资料】回答，不许用自己的知识补充
2. **标注引用**：引用处标 [1] [2]，可回溯可验证
3. **诚实拒答**：资料不足就明确说「知识库中没有找到相关内容」，禁止编造

### 4.3 必做实验

```powershell
python rag_chat.py
```

- 问知识库内的：「报销发票最晚什么时候交？」「餐补要发票吗？」——看引用标注
- 问知识库**外**的：「公司 CEO 是谁？」「上海办公室在哪？」——看它是否诚实拒答
- 问需要跨块拼答案的：「入职 3 年的员工年假和事假审批流程分别是什么？」

---

## 5. 效果评估驱动调优（Day 11）

### 5.1 为什么不能凭手感

把 chunk 从 300 改到 600、top-k 从 3 改到 5，效果是变好还是变差？「感觉差不多」不算数。**没有评估的调优是玄学，有评估的调优才是工程**——这也是普通使用者和工程师的分水岭，面试里「你的 top-k 为什么是 3」一问就见分晓。

### 5.2 最小路径：LLM as judge

三个文件协作（都在 `code/ch3-rag/`）：

- `qa_pairs.json`：10 条测试问答（问题 + 标准答案），从语料里出的题
- `judge_eval.py`：对每条问题跑 RAG → 让模型扮演评委，按 1-5 分打分（复用 Ch2 的 JSON mode）
- `eval_results.jsonl`：每次评估追加一行，天然支持多组对比

**调优实验（照着跑一遍）**：

```powershell
python build_kb.py --chunk 300
python judge_eval.py --label "chunk300"
python build_kb.py --chunk 600
python judge_eval.py --label "chunk600"
python judge_eval.py --k 5 --label "chunk300-k5"   # 先把库切回 chunk300

# 打开 eval_results.jsonl：三行记录，对比 avg，找到最弱的一题
```

结论要能落成一句话：「在我的测试集上，chunk=300 平均 4.6 分、chunk=600 平均 4.1 分、k=5 与 k=3 持平，所以选 300/3」——**这就是面试时关于调参的有据回答**。

### 5.3 完整路径：Ragas 四指标

业界标准框架 [Ragas](https://docs.ragas.io/) 把评估拆成四个正交维度（0-1 分，越高越好）：

| 指标 | 评什么 | 低分说明什么 |
| --- | --- | --- |
| Faithfulness | 回答忠于检索资料（不编造） | system 约束不够，出现幻觉 |
| AnswerRelevancy | 回答切题 | prompt 指令模糊 |
| ContextPrecision | 检索结果里相关内容的占比 | 检索**不准**：调 chunk / 换 embedding |
| ContextRecall | 标准答案被检索覆盖的程度 | 检索**不全**：调大 top-k / 改切分 |

运行 `ragas_eval.py`（选做，需 `pip install "ragas>=0.2" langchain-openai`），评委模型走 DeepSeek、向量指标走硅基流动（复用 `.env` 里那两把钥匙）。四个数字出来后按上表第三列定位问题——**先定位维度，再动手改参数**。

---

## 6. 进阶视野：GraphRAG（完整路径）

### 6.1 向量 RAG 的两个短板

top-k 检索是「按语义相似度拿最像的几块」，它天然不擅长两类问题：

- **多跳/枢纽问题**：「部门总监负责审批哪些事项？」——答案一半在请假制度、一半在报销制度，靠「部门总监」这个实体把两份文档**关联**起来，而语义相似度不知道什么叫关联。
- **全局性问题**：「这套制度的整体设计思路是什么？」——答案散落在所有文档里，top-k 块装不下全貌。

### 6.2 GraphRAG 的思路（概念级）

GraphRAG 用 LLM 从语料中抽取**实体和关系**（三元组：头-关系-尾，如「事假-审批人-部门总监」），构建知识图谱；检索时沿图的边多跳推理或按实体聚合，再交给模型作答。

| | 向量 RAG（本章主线） | GraphRAG |
| --- | --- | --- |
| 索引 | 切分 → 向量化 | 抽实体关系 → 建图 |
| 擅长 | 局部事实查找 | 多跳关联、全局汇总 |
| 代价 | 低（一次 embedding） | 高（图构建要大量 LLM 调用，更新需重算） |
| 怎么选 | 默认首选 | 向量 RAG 明显答不好的多跳/全局场景再上 |

**面试一句话**：「向量 RAG 擅长局部事实检索，多跳和全局性问题会漏；GraphRAG 用实体关系图补这个短板，代价是图构建的 LLM 成本——所以我默认用向量 RAG，用评估证明它不够时才考虑 GraphRAG。」（把「用评估证明」挂在嘴边，呼应第 5 节的工程观）

### 6.3 迷你实验：亲手建一张小图

运行 [graph_rag_mini.py](https://github.com/RCliang/learn-vibe-for-job/tree/main/code/ch3-rag)（选做，约 10 分钟）：

1. **建图**：对三份语料各做一次 JSON mode 调用，抽取实体和三元组关系，打印全部边
2. **对比问答**：三个问题分别用向量 RAG 和图方式回答，并排观察——
   - 「部门总监负责审批哪些事项？」（枢纽：图应把两份文档的边聚合齐）
   - 「和财务经理相关的流程有哪些？」（实体聚合）
   - 「年假可以结转吗？」（简单事实：向量 RAG 反而更直接）

预期观察：前两题图方式更完整，第三题两者都行——**没有银弹，只有合适**。这也是真实 GraphRAG（如[微软 GraphRAG](https://github.com/microsoft/graphrag)）把构建成本做高的原因，工程上先用轻方案、评估不过关再升级。

---

## 7. 自测门槛

进入项目 1 前确认你能：

- [ ] 白板画出 RAG 两阶段流程图（离线入库 / 在线问答），并解释每个箭头
- [ ] 解释 chunk_size 和 overlap 各自解决什么问题、设大设小分别什么后果
- [ ] 说清「向量库、embedding 模型、对话模型」三者的分工
- [ ] 库外问题（如「CEO 是谁」）被正确拒答；能指出是哪条 prompt 纪律在起作用
- [ ] 完成 5.2 的调优实验，用一句话说出你选的参数和证据
- [ ] （完整路径）解释 Faithfulness 和 ContextRecall 的区别（一个管生成、一个管检索）
- [ ] （完整路径）能说出向量 RAG 和 GraphRAG 各自适合的问题类型，以及为什么课程默认前者

## 8. 最小路径 vs 完整路径

- **最小路径（必做）**：第 1-5 节（5.3 除外）+ 自测门槛
- **完整路径（选做）**：
  - Ragas 四指标跑通并解读
  - 第 6 节 GraphRAG：概念阅读 + `graph_rag_mini.py` 迷你实验
  - 用 LangChain 的 `RecursiveCharacterTextSplitter` 重写切分，与手写版对比效果
  - 把 `qa_pairs.json` 扩充到 20 条，观察更多测试题下调优结论是否稳定
  - 阅读概念：混合检索（关键词 + 向量）、重排序（rerank）——面试加分项

## 9. 排错指引

| 现象 | 原因 | 解法 |
| --- | --- | --- |
| `chromadb` 安装慢/失败 | 依赖较多，默认源在国外 | `pip install chromadb -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 检索返回空 / 报集合不存在 | 没先建库 | 先 `python build_kb.py`；核对集合名是否为 `company_kb` |
| embedding 报参数错误 | 单条超 3072 token 或单次超 64 条 | `build_kb.py` 已分批；自写代码时注意同样限制 |
| 回答不标引用 | system 约束被弱化 | 核对 `SYSTEM_PROMPT` 三条纪律完整 |
| 库外问题也在编答案 | 拒答纪律没生效 | temperature 调到 0.2；检查资料编号格式是否被破坏 |
| 评委打分忽高忽低 | judge 用了高温度 | 核对 `judge_eval.py` 的 `temperature=0.0` |
| 改了 chunk 没效果 | 旧库未重建 | `build_kb.py` 每次会重建集合，确认真的重新运行过 |
| GraphRAG 实验抽取结果为空/解析失败 | 关系抽取输出不稳定 | 重跑一次；确认开了 `response_format`（脚本已内置）|
