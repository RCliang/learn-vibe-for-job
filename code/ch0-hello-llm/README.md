# Ch0 交付物：第一个 LLM API 调用

20 行代码完成一次完整的 LLM API 调用，串起 Ch0 全部知识点：import / pip / venv / HTTP / Git。

## 运行步骤（Windows PowerShell 为例）

```powershell
# 1. 进入本目录
cd code/ch0-hello-llm

# 2. 创建并激活虚拟环境（只需一次）
python -m venv .venv
.venv\Scripts\activate        # Git Bash 用：source .venv/Scripts/activate

# 3. 按清单安装依赖
pip install -r requirements.txt

# 4. 准备你的 Key：复制 .env.example 为 .env，填入 LLM_API_KEY

# 5. 运行
python hello_llm.py
```

## 前置条件

- Python 3.10+（终端 `python --version` 可用）
- DeepSeek 开放平台 API Key：[platform.deepseek.com](https://platform.deepseek.com) 注册后，在「API Keys」页面创建并充值少量金额（按量计费）

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `hello_llm.py` | 主脚本：读 `.env` → 创建客户端 → 发起对话 → 打印回复 |
| `.env.example` | 环境变量模板（复制为 `.env` 后填写，`.env` 已被 .gitignore 排除） |
| `requirements.txt` | 依赖清单：openai（SDK）+ python-dotenv（读 .env） |

## 常见问题

- `ModuleNotFoundError: No module named 'openai'` → 终端没激活 venv，或没跑 `pip install -r requirements.txt`
- 返回 `401` → `.env` 里的 Key 有误
- 返回 `429` → 请求太频繁，稍等重试
- 下载慢 → `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
