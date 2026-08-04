# AI Native Chinese Curriculum

设计文档项目：把 Middle School Mandarin（1.2 / 2.1 / 2.2）课程从 SMART Notebook 迁移到一套 **AI Native Curriculum Database**，作为所有教学产出（Slides、HTML、PDF、Assessment、AI Tutor）的唯一数据源，并让架构可以扩展到整个 World Language Department。

## 文档

- **[`PROJECT_STATUS.md`](./PROJECT_STATUS.md) — 新开对话/新的 Claude 接手时，先读这个文件。** 这个仓库是唯一的记忆载体，跨对话不会自动保留上下文。
- [`blueprint-v1.0.md`](./blueprint-v1.0.md) — 架构层设计：九条设计公理、四层架构模型（Structural / Content / Generation / Intelligence）、Department 级泛化设计、Import Pipeline、治理与版本管理。
- [`mandarin-1.2/`](./mandarin-1.2/) — Pilot：Mandarin 1.2 课程数据，Markdown + YAML frontmatter 存储，Course 层共享内容（Standards、Syllabus 大纲）在 `00-course-overview.md`，各 Unit 单独建目录。

## Generation Layer（原型）

`generators/family_overview.py` 是第一个渲染器原型：读取 `mandarin-1.2/unit-01-a-day-in-my-life/`
下的 Markdown + YAML（01 Overview、03 Content、04 Culture、05 Resources、06 Assessment），
自动生成一份**家长可读的 Unit 概览 HTML 页面**——不手写，完全从 Content Layer 数据渲染出来，
数据改了重新跑一次脚本就会同步更新。

```
python3 generators/family_overview.py mandarin-1.2/unit-01-a-day-in-my-life <输出路径>.html
```

这一步验证了 Blueprint 里"一份数据、多种产出"的承诺：内部字段（TODO、status、教师
Curriculum Intelligence 笔记）不会出现在这份面向家长的输出里，渲染器只挑家长需要看到的字段。

`generators/student_reference.py` 是第二个渲染器：同一份 Content Layer 数据，渲染成一份
**面向学生的静态检索页面**——不做登录、设备同步、进度追踪，定位是纯参考工具，**不是实时
系统**（教师上完新课后要先把内容整理进 Markdown，再重新跑一次脚本，页面才会更新）。
比家长版内容丰富得多：故事/文化正文（数据里有多少就显示多少，缺失的明确标注"内容整理中"
而不是留空或瞎编）、每个 Cycle 的大致教学顺序、全页可搜索（含一条滚动时始终可见的
sticky 导航+搜索条）。Diagnostic/Summative 这类测验只显示标题和类型，不暴露考题内容
（考题本身不适合公开当复习资料）；Performance Task/Project 类评量则完整显示 Driving
Question/Instructions/Rubric，因为这些本来就是要给学生看的任务说明。经教师反馈后删除了
和 Content/Culture 卡片重复的顶部整表生词表（生词仍保留在各卡片内，且仍可搜索），并换了
区别于家长版的暖棕色配色。**Teaching Flow 板块不展示具体日期/星期**——只按原顺序呈现
每个 Cycle 大致教了什么，因为教师反馈逐日同步实际教学进度的维护成本不现实；这一点和
背后"渲染器颗粒度要服务于维护成本，不能只服务于内容丰富度"的教训记在
[08-curriculum-intelligence.md](./mandarin-1.2/unit-01-a-day-in-my-life/08-curriculum-intelligence.md)。

```
python3 generators/student_reference.py mandarin-1.2/unit-01-a-day-in-my-life <输出路径>.html
```

后续可以为同一份数据做别的渲染器（Slides 大纲等），不需要重新整理数据。

## 存储载体

Content Layer 落地为 **git 仓库里的 Markdown + YAML**（不是 Notion/Airtable/Google Sheets）：
- YAML frontmatter 存结构化字段，Markdown 正文存自然语言内容
- git 天然提供版本历史，不需要额外的治理/审批流程（目前是单人维护）
- 通过对话用自然语言描述要改的内容，由 AI 直接编辑底层文件

## 路线图

1. **Blueprint v1.0**（已完成）— 架构设计，不涉及具体文件模板
2. **Unit Template**（进行中，见 `mandarin-1.2/unit-01-a-day-in-my-life/`）— 目前是 01 Overview / 02 Teaching / 03 Content / 04 Culture / 05 Resources / 06 Assessment / 07 AI Workspace / 08 Curriculum Intelligence 八个模块（合并了原本分开的 Projects 和 Assessment；Stories 改名为更广义的 Content，涵盖故事/新闻/音频/歌曲/视频；新增独立的 Culture 模块，不再依附于 Overview 里的一个字段），在 Pilot 中反复验证调整，暂不单独抽出通用模板文档，等 Pilot 稳定后再回头抽象
3. **SMART Import**（已验证可行）— `.notebook` 文件是 zip 包，内含逐页 SVG（文字可用脚本抓取）+ `imsmanifest.xml`（记录真实页面顺序，不等于文件名数字顺序）；docx 用同样方式解压 `word/document.xml` 抓文字。目前是半自动：AI 抽取 + 人工审核映射到 Module，符合 Blueprint 里"AI 永不直接写入 canonical"的原则
4. **Pilot Unit**（进行中）— Mandarin 1.2 Unit 1「我的一天」，已完成 Cycle 1/2 内容整理 + Diagnostic Test + Student Survey + 生词表 + Course-level Syllabus 归档；仍缺：「我的一天太累了」「中秋节的故事」正文、Final Project 细节、Cycle 3+
5. **Generation Layer**（进行中）— 家长概览渲染器（`family_overview.py`）已定稿；学生检索页面渲染器（`student_reference.py`）已完成第一版，等教师review
