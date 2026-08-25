---
title: Ch2 Prompt 工程实战（Day 5-7）
outline: [2, 3]
---

# Ch2 Prompt 工程实战（Day 5-7）

> **本章 JD 关键词**：Prompt Engineering
>
> **学完你能做什么**：写出专业级的 system prompt；用 few-shot 让输出稳定可控；知道温度什么时候调高调低；让模型输出**程序能直接消费的 JSON**（JSON mode + Pydantic 校验）；算清每次调用的 token 成本。交付一个你自己求职就用得上的简历优化器。

::: info 📋 本章路线
**Day 5**：消息角色、few-shot、温度与参数、token 成本意识
**Day 6**：结构化输出——从脆弱到可靠（JSON mode + Pydantic）
**Day 7**：周末实战——简历优化器
:::

---

## 1. 从「指令四要素」到 Prompt Engineering

Ch1 你学会了给**编程助手**写指令。本章把同样的思想用在**模型本身**上——这就是 Prompt Engineering，目标岗位 JD 里出现频率第一的技能词，也是后面所有章节的地基：Ch3 RAG 的「检索结果拼接模板」是 prompt，Ch4 Agent 的「系统指令与工具描述」还是 prompt。**prompt 写不好，上层架构再漂亮也没用。**

四要素的映射关系：

| 给编程助手（Ch1） | 给模型（Ch2） |
| --- | --- |
| 任务 | system prompt 里的角色与任务定义 |
| 上下文 | user 消息里的输入材料 |
| 约束 | 输出格式、语气、规则 |
| 验收标准 | few-shot 示例 + 结构化校验（Pydantic） |

---

## 2. messages 的三种角色（Day 5 上午）

你在 Ch0 已经见过 `messages` 列表，现在正式认识它的三个角色：

```python
messages = [
    {"role": "system", "content": "你是一位资深简历顾问，只给具体可执行的建议。"},  # 全局设定
    {"role": "user", "content": "我的简历是：……"},                               # 本次输入
    {"role": "assistant", "content": "好的，我先看工作经历部分……"},                # 模型的历史回复
]
```

| 角色 | 作用 | 类比 |
| --- | --- | --- |
| `system` | 定义「它是谁、守什么规矩」 | 员工手册 |
| `user` | 每次的具体输入 | 工单 |
| `assistant` | 模型之前的回复 | 聊天记录 |

两个要点：

1. **多轮对话 = 往列表里追加消息**。模型本身没有记忆，你看到的「连续对话」，是程序把历史消息每次都完整重发。这个机制 Ch4 讲记忆管理时会变成必须亲手处理的问题，现在先记住结论。
2. **system 的优先级高于 user**。所以角色、规则、输出格式都应该写进 system，而不是每次在 user 里重复。

**好 system prompt 的公式**（四件套）：

> **角色**（你是谁）＋ **任务**（做什么）＋ **规则/边界**（必须怎样、绝不怎样）＋ **输出格式**（以什么形式返回）

---

## 3. few-shot：给例子胜过给描述

当你要求一种「格式难描述、风格难定义」的输出时，与其写一堆形容词，不如直接给一对示例（few-shot）。

**反例（描述式）**：「把简历句子改写得更好，要专业、有力、量化。」

**正例（few-shot）**：

> 请按下面的风格改写简历句子。
> 输入：负责公司内部系统的开发维护工作
> 输出：独立负责 3 个内部系统的开发与迭代，将工单处理时长从 2 天压缩至 4 小时
>
> 现在改写：用 Python 写接口，也用过一些 AI 相关的接口

给例子时注意：**例子本身也在消耗 token**（见第 4.3 节），且例子要覆盖你想控制的边界（比如量化数字、动词开头、成果导向都体现在例子里了）。

---

## 4. 温度、参数与 token 账本（Day 5 下午）

### 4.1 temperature：模型的性格旋钮

| temperature | 效果 | 适用任务 |
| --- | --- | --- |
| `0 - 0.3` | 刻板、稳定、可复现 | 结构化输出、分类、改写（**本章简历优化器**） |
| `0.4 - 0.7` | 平衡 | 周报、总结、通用问答 |
| `0.8 - 1.0` | 发散、有惊喜也有惊吓 | 头脑风暴、创意文案 |

其他两个参数知道存在即可：`max_tokens`（输出长度上限，当「保险丝」用，防失控烧钱）；`top_p`（和 temperature 类似的另一档旋钮，一般不动）。

### 4.2 实验：亲眼看温度的差异

课程提供 [code/ch2-prompt/temperature_lab.py](https://github.com/your-name/learn-vibe-coding/tree/main/code/ch2-prompt)：同一个 prompt「用一个比喻解释什么是 temperature 参数」，分别在 0.2 / 0.7 / 1.0 下各跑一次，对比三次输出的差异。**调参之前先看现象**，这是本章的实验精神。

### 4.3 token 与成本账本

- **token 是模型计费和计算长度的单位**。直觉：1 个汉字 ≈ 1~2 token，1 个英文单词 ≈ 1 token。
- **上下文窗口** = 模型一次能「看到」的 token 上限。聊天记录越长，每次重发的 token 越多——**越贵也越慢**，这就是 Ch1 说「对话太乱就 `/clear`」的底层原因。
- **成本 =（输入 token ＋ 输出 token）× 单价**。`glm-4-flash` 免费适合练习；付费模型的价格在[智谱定价页](https://open.bigmodel.cn/pricing)查询。养成习惯：每次调用后看一眼响应里的 `usage` 字段——它告诉你这次花了多少 token。

::: details 在代码里看 usage
```python
response = client.chat.completions.create(...)
print(response.usage)  # prompt_tokens / completion_tokens / total_tokens
```
:::

---

## 5. 结构化输出：让程序能消费模型的话（Day 6）

### 5.1 为什么需要这一节

Ch0 讲过「JSON 是数据的世界语」。模型输出的是**文本**，而你的程序（后面的 RAG 引用、Agent 工具）需要**结构化数据**——这一节就是把文本变成数据，是从「聊天玩具」到「应用」的分水岭。

### 5.2 三步演进（跟着 [json_parsing_demo.py](https://github.com/your-name/learn-vibe-coding/tree/main/code/ch2-prompt) 逐步运行）

**第 1 步：只靠 prompt 约束（脆弱）**。在 prompt 里写「只输出 JSON」，然后 `json.loads(text)`。常见翻车：模型给 JSON 套上 ```` ```json ```` 代码块、前后加说明文字——解析直接崩。它不是「错」，只是不可靠。

**第 2 步：JSON mode（可靠）**。GLM 支持在调用时声明输出格式（[官方文档](https://docs.bigmodel.cn/cn/guide/capabilities/struct-output)）：

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是信息抽取助手。按此 JSON 结构返回："
         '{"name": "…", "city": "…", "skills": ["…"]}'},   # 结构写进 system
        {"role": "user", "content": "我叫张小明，在杭州，会 Python 和 Docker"},
    ],
    response_format={"type": "json_object"},  # ← 开启 JSON mode
)
data = json.loads(response.choices[0].message.content)      # content 就是纯 JSON
```

要点：结构描述写进 **system** 消息；开启后 `content` 是可直接解析的纯 JSON。

**第 3 步：Pydantic 校验（就业级）**。JSON mode 只保证「是合法 JSON」，不保证**字段和类型符合你的约定**（比如把 `skills` 写成了字符串）。用 Pydantic 定义结构，一劳永逸：

```python
from pydantic import BaseModel

class ContactInfo(BaseModel):
    name: str
    city: str
    skills: list[str]

info = ContactInfo.model_validate(data)   # 类型不对会在这里精确报错
print(info.skills[0])                     # 之后有代码补全，像用普通对象一样用
```

Pydantic 是 JD 里的常客（FastAPI 的内置校验库，Ch4 项目 2 会再遇到它），`pip install pydantic` 即可。

### 5.3 失败了怎么办：把报错喂回去

校验失败时不要人工修补，**把错误信息作为新消息发回模型重试一次**——「你返回的 JSON 中 skills 应为数组，请修正后重新输出」。这是生产环境处理模型输出的通用模式（自纠重试），简历优化器里会实现它。

---

## 6. 周末实战：简历优化器（Day 7）

**需求（用四要素自己先写一遍指令）**：输入一段简历文本 → 输出结构化改进建议。

**Pydantic 输出模型设计**（先想清楚要什么，再写 prompt——**结构先行**是 Prompt Engineering 的进阶心法）：

| 字段 | 含义 |
| --- | --- |
| `overall_score` | 总分 0-100 |
| `strengths` | 保留的优点，最多 3 条 |
| `issues` | 问题清单：维度（内容/表达/关键词/结构）＋问题＋建议 |
| `star_rewrites` | STAR 改写示例：原句 → 改写 → 理由 |
| `keywords_to_add` | 建议补充的 JD 关键词 |

::: tip STAR 法则提前剧透
 Situation（情境）Task（任务）Action（行动）Result（量化结果）——Ch8 求职冲刺的主力方法论，你的简历每一句经历都应该经得起 STAR 检验。
:::

**开发路径（也是本章知识的完整复览）**：

1. `v0`：prompt 约束版——体验脆弱性（跑 5 次，总有一次解析失败？）
2. `v1`：开 JSON mode，system 里写清结构——稳定了
3. `v2`：加 Pydantic 校验 + 失败自纠重试 + 友好打印（参考实现的样子）
4. 迭代练习：把 temperature 从 0.7 调到 0.2 对比建议稳定性；往 prompt 里加一对 few-shot 改写示例，看 `star_rewrites` 质量变化

**测试素材**：[code/ch2-prompt/sample_resume.txt](https://github.com/your-name/learn-vibe-coding/tree/main/code/ch2-prompt) 是一份「典型差简历」（口语化、无量化、职责堆砌）——先跑它，再用你自己真实的简历（这工具从今天起就是你的求职装备）。

完成后执行 Ch1 学过的 **AI 出题考核**：让 AI 针对你的 Pydantic 模型设计出 3 道题（比如「如果模型把 overall_score 返回成 "85 分" 字符串会发生什么」），3 对 2 通关。

---

## 7. 自测门槛

进入 Ch3 前确认你能：

- [ ] 默写 system prompt 四件套公式，并说出为什么规则要放 system 而不是 user
- [ ] 给「简历改写」和「团队脑暴取名」两个任务各配一个合适的 temperature 并说理由
- [ ] 能解释：JSON mode 和 Pydantic **各自**解决什么问题（提示：合法 JSON ≠ 字段正确）
- [ ] 亲手把 Pydantic 模型里 `overall_score: int` 改成 `overall_score: str`，跑一次看 ValidationError 长什么样，再改回来
- [ ] 简历优化器能处理 `sample_resume.txt` 并通过 Pydantic 校验；看一眼 `usage` 能说出这次调用大约花了多少 token
- [ ] 已 push 到 GitHub

## 8. 最小路径 vs 完整路径

- **最小路径（必做）**：第 1-6 节 + 自测门槛
- **完整路径（选做）**：
  - 用官方文档提到的 `jsonschema` 库做一次校验，对比 Pydantic 的开发体验
  - 把简历优化器改成命令行参数输入：`python resume_optimizer.py 我的简历.txt`
  - 同一份简历分别发给 `glm-4-flash` 和一个付费模型，对比建议质量与 token 成本

## 9. 排错指引

| 现象 | 原因 | 解法 |
| --- | --- | --- |
| `json.JSONDecodeError` | 没开 JSON mode，或 system 里没写清结构 | 加 `response_format`；把目标结构写进 system |
| `ValidationError`（Pydantic） | 模型返回的字段类型/名称与模型定义不符 | 按第 5.3 节把报错喂回模型重试；检查 system 里的结构描述 |
| 输出说了一半就停了 | `max_tokens` 太小 | 调大；或在 prompt 里要求精简输出 |
| 建议「又空又水」 | prompt 只有角色没有规则 | 补四件套里的「规则/边界」（如「每条建议必须引用简历原文」） |
| `429` 限流 | 短时间调用太密 | `import time; time.sleep(2)` 后重试 |
| few-shot 加了反而更贵 | 例子太长 | 例子精简到一行输入一行输出 |
