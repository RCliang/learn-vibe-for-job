# Ch0 视频用幻灯片设计（2026-08-30）

## 目标

为 Ch0《环境与第一行代码》录制 10-15 分钟精简跟课视频，提供一份单文件幻灯片 `slides/ch0/slide.html`。

## 需求结论（已与用户确认）

- 定位：精简跟课版，覆盖全章主干，约 16-20 页
- 形态：单文件原生 HTML，零依赖、离线可用，最适合录屏
- 风格：浅色简洁风，强调色与站点一致（VitePress 绿 `#3eaf7c`）

## 内容结构（方案 A：两天时间线，20 页）

1. 封面：Ch0 环境与第一行代码 · 28 天速成营
2. 本章路线 + JD 关键词（Python / API 调用 / Git）
3. 分隔页：Day 1 上午 · 装好三样东西
4. VSCode 安装 + 终端四条命令（合并原 1.1 / 1.3）
5. Python 安装：必勾 Add to PATH
6. 分隔页：Day 1 下午 · 接入 AI 结对程序员
7. 工具链总览：VSCode + Claude Code + DeepSeek（10 元够全程、零翻墙）
8. 开通 API Key + 三条安全红线
9. 安装 Claude Code（Node LTS + Git + npm）
10. 配置 settings.json 指向 DeepSeek + 配置过时兜底三步
11. 第一次对话验证（/status）
12. 分隔页：Day 2 上午 · HTTP 与 API
13. 餐厅类比：前端 / 后端 / API
14. 一次请求的解剖 + 必认 5 个状态码
15. JSON 三条语法
16. 分隔页：Day 2 下午 · Python 三件套 + Git
17. import / pip / venv 一页三卡（含 ModuleNotFoundError 两步排错）
18. Git 四条命令 + .gitignore 红线
19. 交付物：跑通 hello_llm.py（全章知识串联图）
20. 自测门槛清单 + 下章预告

内容来源：`docs/guide/ch0.md`；命令面向 Windows / PowerShell（与课程一致）。

## 技术设计

- 1280×720 设计基准，`transform: scale()` 等比缩放满屏（resize 自适应）
- 幻灯片为 `<section class="slide">`，仅激活页显示
- 交互：`←/→/空格/PgUp/PgDn` 翻页、`Home/End` 首末页、`F` 全屏、点击翻页
- 底部细进度条 + 右下角页码；无自动动画，录屏节奏完全手动控制
- 字体：系统字体栈（PingFang SC / Microsoft YaHei）；代码浅色 GitHub 风格

## 明确不做

- 不做演讲者视图、过渡动画、在线分享（录屏用不上）
- 不引入 reveal.js 等外部依赖
- 设计文档不自动 commit（工作区有大量未提交改动，由用户决定）
