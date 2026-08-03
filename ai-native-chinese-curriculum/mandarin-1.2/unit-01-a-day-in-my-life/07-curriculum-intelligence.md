---
unit: Unit 1
status: active
last_updated: 2026-08-03
---

# 07 Curriculum Intelligence — Unit 1

这个文件记录课程随时间演化的知识，不是静态内容。每条记录带日期，说明是谁发现的、
针对哪个学年/哪次教学。

## 2026-08-03 — Syllabus 与实际教学出现偏差
**发现**：Course Syllabus（`00-course-overview.md` 所引用的原始文档）里 Unit 1 的评量
列表写着 "The Rabbit Story" 和 "A Scary Story"，但 "A Scary Story" 实际上**不是正式课程
内容**——它是万圣节应景的机动/加课活动：如果班级进度比预计快，老师会带学生看一个
万圣节短视频，让学生用中文 retell，不计入正式 Assessment。

**建议**：
1. Unit Template 需要区分「正式课程内容」和「机动/加课活动」两类，后者不应出现在
   05 Assessment 或 03 Content（当时称 03 Stories）里，避免误导未来备课或生成教学资源时把它当成必修内容。
2. Syllabus 作为「计划层」文档，容易随年份漂移而不更新；Curriculum Database 应该是
   「实际教学」的权威记录，Syllabus 之后可以从 Database 反向生成，而不是让两者各自
   维护、逐渐失去同步。

## 2026-08-03 — 每个 Unit 的「文化」模块位是动态填充的
**发现**：每个 Unit 固定留一个 Culture 模块位，但具体内容不是写死在 Unit 里的——
根据当年教学日历实际落点决定：
- 如果 Unit 教学周期内覆盖中国重大节日（中秋节 / 春节 / 端午节 之一），优先安排该节日
  的文化内容（例如本学年 Unit 1 因为开学时间与中秋节临近，选择了「中秋节的故事」）。
- 否则安排其他类型的文化活动，例如书法 (calligraphy)、点餐/奶茶 field trip 等。

**建议**：Unit Template 的 `cultural_focus` 字段应该设计成"选择规则 + 当年实例"两层，
而不是只记录当年选了什么——这样明年即使日历变化、选了不同节日，规则本身不用重写，
只需要更新"今年的实例"。（`01-overview.md` 里的 `cultural_focus` 已经按这个思路起草。）

## 2026-08-03 — Module 顺序调整：Resources 应前置于 Projects / Assessment
**发现**：最初起草时把顺序定为 01 Overview / 02 Teaching / 03 Stories / 04 Projects /
05 Assessment / 06 Resources / 07 AI Workspace / 08 Curriculum Intelligence，教师指出
06 Resources 应该前置——因为 Resources（图片、视频、生词表等素材）是 Projects 和
Assessment 的前置输入，逻辑上应该先出现。

**调整为**：01 Overview / 02 Teaching / 03 Stories / **04 Resources** /
**05 Projects** / **06 Assessment** / 07 AI Workspace / 08 Curriculum Intelligence。

**建议**：这个顺序目前只在 Pilot Unit 里生效，等确认在其他 Unit 上也适用后，
再回头把它写进正式的 Unit Template 文档（见项目 README 路线图第 2 项）。

## 2026-08-03 — 再次调整：合并 Projects 与 Assessment；Stories 改名 Content
**发现**：教师进一步指出两点：
1. Project 和 Assessment 本质是同一件事——都是对 Unit 的**总结性评量**，只是呈现形式
   不同（测验 vs 项目/表现性任务），不该分成两个模块。
2. "Stories" 这个名字太局限——介绍新内容时，除了故事，也常用新闻、音频、歌曲、视频。

**调整为**：
- 04 Resources / **05 Assessment**（合并了原 Projects，用 `assessment_type` 区分
  Diagnostic / Summative / Summative — Performance Task 等类型）/ **06 AI Workspace** /
  **07 Curriculum Intelligence**（原 06/07/08 依次前移一位）
- 03 Stories → **03 Content**，用 `content_type` 字段（story / news / song / video / audio）
  标注具体类型，"Reading" 一节改名为通用的 "Text / Media"

**当前完整模块顺序**：01 Overview / 02 Teaching / 03 Content / 04 Resources /
05 Assessment / 06 AI Workspace / 07 Curriculum Intelligence（共 7 个模块，
比最初 v0.1 设计的 8 个少一个，因为 Projects 并入了 Assessment）。

## 待补充的观察类型（模板，供未来使用）
- 哪些活动最成功
- 学生最容易犯的错误 / Vocabulary 难点
- 每年修改建议
- Student Feedback
