# Ch2 Prompt 工程实战：配套代码

章节：[Ch2 Prompt 工程实战（Day 5-7）](https://rcliang.github.io/learn-vibe-for-job/guide/ch2)

交付物 `resume_optimizer.py` 的输出形态：**终端打印五板块结构化报告**（总分/优点/问题清单/STAR 改写/关键词），示例与验收口径见课程第 6 节「输出要求」。

## 目录结构

| 文件 | 对应课程 | 说明 |
| --- | --- | --- |
| `temperature_lab.py` | Day 5 | 温度实验：同一 prompt 在 0.2 / 0.7 / 1.0 下的输出对比 |
| `json_parsing_demo.py` | Day 6 | 结构化输出三步演进：prompt 约束（脆弱）→ JSON mode → Pydantic 校验 |
| `resume_optimizer.py` | Day 7 | **交付物参考实现**：简历优化器（JSON mode + Pydantic 校验 + 失败自纠重试） |
| `sample_resume.txt` | Day 7 | 测试用「典型差简历」；建议再用你自己的简历 |
| `.env.example` / `requirements.txt` | | 环境模板与依赖（pydantic 为本章新增） |

## 运行

```powershell
cd code/ch2-prompt
python -m venv .venv
.venv\Scripts\activate              # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
# 复制 .env.example 为 .env，填入 LLM_API_KEY

python temperature_lab.py                 # Day 5 实验
python json_parsing_demo.py step1         # Day 6：逐步运行 step1/2/3
python resume_optimizer.py                # Day 7：分析 sample_resume.txt
python resume_optimizer.py 我的简历.txt    # Day 7：分析你自己的简历
```

## 开发提醒

参考实现直接可用，但课程的设计路径是**先自己从 v0（prompt 约束版）写到 v2**，
卡壳超过 20 分钟再对照——`resume_optimizer.py` 就是 v2 完成后的样子。
