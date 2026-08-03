# AI Native Chinese Curriculum

设计文档项目：把 Middle School Mandarin（1.2 / 2.1 / 2.2）课程从 SMART Notebook 迁移到一套 **AI Native Curriculum Database**，作为所有教学产出（Slides、HTML、PDF、Assessment、AI Tutor）的唯一数据源，并让架构可以扩展到整个 World Language Department。

## 文档

- [`blueprint-v1.0.md`](./blueprint-v1.0.md) — 架构层设计：九条设计公理、四层架构模型（Structural / Content / Generation / Intelligence）、Department 级泛化设计、Import Pipeline、治理与版本管理。

## 路线图

1. **Blueprint v1.0**（本目录，已完成）— 架构设计，不涉及具体文件模板
2. **Unit Template v1.0** — 把 Blueprint 落地为 Mandarin 的标准 Unit 数据 schema
3. **SMART Import Workflow** — Extractor → AI Classifier → Human Review Queue
4. **Pilot Unit** — 挑一个最完整的 Unit 验证可行性
