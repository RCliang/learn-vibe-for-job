# learn-vibe-coding

《AI 应用开发速成营》——28 天零基础转行 AI 应用开发课程。

- 课程设计 spec：[docs/superpowers/specs/2026-08-24-ai-app-dev-bootcamp-design.md](docs/superpowers/specs/2026-08-24-ai-app-dev-bootcamp-design.md)
- 在线课程站：GitHub Pages 部署（在仓库 Settings → Pages 开启后由 Actions 自动发布）

## 仓库结构

```
learn-vibe-coding/
├── docs/                # VitePress 课程站（.vitepress/ 配置、guide/ 各章、appendix/ 附录）
├── code/                # 各章可运行示例代码（ch0-hello-llm/ ...）
├── data/                # 项目示例语料与数据集（规划中）
└── .github/workflows/   # VitePress 构建 + GitHub Pages 自动部署
```

## 本地开发课程站

需要 Node.js 18+：

```bash
npm install        # 安装 VitePress
npm run docs:dev   # 本地预览 http://localhost:5173
npm run docs:build # 构建到 docs/.vitepress/dist
```

## 部署

推送到 `main` 分支后，GitHub Actions 自动构建并部署到 Pages。
首次使用需在仓库 **Settings → Pages** 中将 Source 设为 **GitHub Actions**。
