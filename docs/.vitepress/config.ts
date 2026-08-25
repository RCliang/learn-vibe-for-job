import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'AI 应用开发速成营',
  description:
    '28 天零基础转行 AI 应用开发：JD 逆向设计，产出两个可写上简历的项目',
  srcExclude: ['**/superpowers/**'],
  themeConfig: {
    nav: [
      { text: '课程', link: '/guide/ch0', activeMatch: '/guide/' },
      { text: '面试题库', link: '/appendix/interview' },
      {
        text: 'GitHub',
        link: 'https://github.com/your-name/learn-vibe-coding',
      },
    ],
    sidebar: [
      {
        text: '开始之前',
        items: [{ text: '课程介绍', link: '/' }],
      },
      {
        text: 'Week 1 · 上手与出活',
        items: [
          { text: 'Ch0 环境与第一行代码', link: '/guide/ch0' },
          { text: 'Ch1 Vibe Coding 工作流', link: '/guide/ch1' },
          { text: 'Ch2 Prompt 工程实战', link: '/guide/ch2' },
        ],
      },
      {
        text: 'Week 2 · RAG 与项目 1',
        items: [
          { text: 'Ch3 RAG 知识库', link: '/guide/ch3' },
          { text: '项目 1：企业知识库问答机器人', link: '/guide/project1' },
        ],
      },
      {
        text: 'Week 3 · Agent 与项目 2',
        items: [
          { text: 'Ch4 Function Calling 与 Agent', link: '/guide/ch4' },
          { text: '项目 2：垂直领域 Agent 助手', link: '/guide/project2' },
        ],
      },
      {
        text: 'Week 4 · 工程化与上云',
        items: [
          { text: 'Ch5 Linux 与服务器基础', link: '/guide/ch5' },
          { text: 'Ch6 Docker 容器化', link: '/guide/ch6' },
          { text: 'Ch7 云服务部署实战', link: '/guide/ch7' },
          { text: 'Ch8 求职冲刺', link: '/guide/ch8' },
        ],
      },
      {
        text: '附录',
        items: [{ text: '面试题库', link: '/appendix/interview' }],
      },
    ],
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一页', next: '下一页' },
    lastUpdated: {
      text: '最后更新',
      formatOptions: { dateStyle: 'short', timeStyle: 'short' },
    },
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
  },
})
