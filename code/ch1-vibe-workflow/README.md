# Ch1 Vibe Coding 工作流：配套代码

章节：[Ch1 Vibe Coding 工作流（Day 3-4）](https://rcliang.github.io/learn-vibe-for-job/guide/ch1)

## 目录结构

| 文件 | 说明 |
| --- | --- |
| `weekly_report.py` | 实战交付物**参考实现**（含课程要求的三个迭代）。先自己用 AI 生成，卡壳超过 20 分钟再对照 |
| `bugs/bug1_name_error.py` | 调试练习 1：NameError |
| `bugs/bug2_indent_error.py` | 调试练习 2：IndentationError |
| `bugs/bug3_api_401.py` | 调试练习 3：API 401（环境问题，不是代码问题） |
| `.env.example` / `requirements.txt` | 环境模板与依赖清单（同 Ch0） |

## 运行周报生成器

```powershell
cd code/ch1-vibe-workflow
python -m venv .venv
.venv\Scripts\activate              # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
# 复制 .env.example 为 .env，填入 LLM_API_KEY
# 修改 weekly_report.py 顶部的 RAW_TEXT 为你自己的流水账
python weekly_report.py             # 生成 weekly_report.md
```

## Bug 练习玩法

对每段代码执行课程第 5.3 节的六步：**运行 → 从下往上读报错 → 说出猜测 → 贴给 AI 验证 → 修复 → 再运行验证**。

修复标准：

| 练习 | 通过条件 |
| --- | --- |
| bug1 | 输出「你好，AI 同学！欢迎进入 Vibe Coding 世界。」 |
| bug2 | 依次输出三行喝茶步骤 |
| bug3 | 打印出模型返回的一句话（需要可用的 `.env`） |
