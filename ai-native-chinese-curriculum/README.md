# AI Native Chinese Curriculum

设计文档项目：把 Middle School Mandarin（1.2 / 2.1 / 2.2）课程从 SMART Notebook 迁移到一套 **AI Native Curriculum Database**，作为所有教学产出（Slides、HTML、PDF、Assessment、AI Tutor）的唯一数据源，并让架构可以扩展到整个 World Language Department。

## 文档

- [`blueprint-v1.0.md`](./blueprint-v1.0.md) — 架构层设计：九条设计公理、四层架构模型（Structural / Content / Generation / Intelligence）、Department 级泛化设计、Import Pipeline、治理与版本管理。
- [`mandarin-1.2/`](./mandarin-1.2/) — Pilot：Mandarin 1.2 课程数据，Markdown + YAML frontmatter 存储，Course 层共享内容（Standards、Syllabus 大纲）在 `00-course-overview.md`，各 Unit 单独建目录。

## 存储载体

Content Layer 落地为 **git 仓库里的 Markdown + YAML**（不是 Notion/Airtable/Google Sheets）：
- YAML frontmatter 存结构化字段，Markdown 正文存自然语言内容
- git 天然提供版本历史，不需要额外的治理/审批流程（目前是单人维护）
- 通过对话用自然语言描述要改的内容，由 AI 直接编辑底层文件

## 路线图

1. **Blueprint v1.0**（已完成）— 架构设计，不涉及具体文件模板
2. **Unit Template**（进行中，见 `mandarin-1.2/unit-01-a-day-in-my-life/`）— 01–08 模块结构 + YAML schema，在 Pilot 中反复验证调整，暂不单独抽出通用模板文档，等 Pilot 稳定后再回头抽象
3. **SMART Import**（已验证可行）— `.notebook` 文件是 zip 包，内含逐页 SVG（文字可用脚本抓取）+ `imsmanifest.xml`（记录真实页面顺序，不等于文件名数字顺序）；docx 用同样方式解压 `word/document.xml` 抓文字。目前是半自动：AI 抽取 + 人工审核映射到 Module，符合 Blueprint 里"AI 永不直接写入 canonical"的原则
4. **Pilot Unit**（进行中）— Mandarin 1.2 Unit 1「我的一天」，已完成 Cycle 1/2 内容整理 + Diagnostic Test + Student Survey + 生词表 + Course-level Syllabus 归档；仍缺：「我的一天太累了」「中秋节的故事」正文、Final Project 细节、Cycle 3+
