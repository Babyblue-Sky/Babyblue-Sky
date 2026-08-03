---
last_updated: 2026-08-03
branch: claude/ai-native-chinese-curriculum-vlnr10
---

# Project Status — 给下一次接手这个项目的 Claude 看

> 如果你是一个新对话里的 Claude，第一次看到这个项目：**先读这个文件**，
> 再按需读下面链接的文件，不要从零开始猜项目在做什么。这个仓库本身就是
> 唯一的记忆载体——没有别的地方存着之前对话的上下文。

## 项目是什么

把 Tian（Mandarin 老师）的 Middle School Mandarin 课程从 SMART Notebook 迁移到一套
Markdown+YAML 的 **AI Native Curriculum Database**，作为所有教学产出（家长概览页面、
学生检索页面、Slides、Assessment 等）的唯一数据源。详见 [`blueprint-v1.0.md`](./blueprint-v1.0.md)。

## 目前进度（做到哪一步）

1. **Blueprint v1.0** — 完成。架构层设计：九条公理、四层模型、Department 级泛化。
2. **Pilot Unit** — 进行中。`mandarin-1.2/unit-01-a-day-in-my-life/` 已经有
   Cycle 1/2 教学内容、Diagnostic Test、Student Survey、生词表、Culture 模块
   （中秋节的故事 + 笔画书法）。**还缺**：Cycle 3-6、「我的一天太累了」和
   「中秋节的故事」的正文、Final Project 细节。
3. **存储载体已定案** — git 里的 Markdown + YAML，不用 Notion/Airtable/Sheets。
4. **Unit Template 结构（当前 7 个模块，随时可能因为新发现再调整，以
   `mandarin-1.2/unit-01-a-day-in-my-life/` 里实际的资料夹为准，不要相信这里的
   文字描述会一直准确）**：
   `01-overview / 02-teaching / 03-content / 04-culture / 05-resources / 06-assessment / 07-ai-workspace / 08-curriculum-intelligence`
5. **Generation Layer（渲染器）**：
   - `generators/family_overview.py` — 面向家长的 Unit 概览页面，**已经做了 4 轮设计迭代，教师确认"目前够用"**。关键设计原则都写在脚本开头的 docstring 里。
   - `generators/student_reference.py` — 面向学生的"Unit 检索页面"，**第一版已写完，等教师 review**（还没经过像家长版那样的多轮反馈）。定位是纯静态检索/参考工具，不做设备同步、进度追踪、登录。比家长版丰富：全 Unit 汇总生词表（页面内可搜索/筛选）、故事/文化正文（数据里有多少显示多少，缺失的标注"内容整理中"）、每个 Cycle 的真实教学时间线（标注"去年参考日期"）。测验类 Assessment 不暴露考题内容，Performance Task/Project 类完整显示任务说明。Quizlet/YouTube 等链接目前渲染不出来——不是渲染器的问题，是 Content Layer 里还没有真实 URL，等数据补上会自动出现。设计取舍详见 [08-curriculum-intelligence.md](./mandarin-1.2/unit-01-a-day-in-my-life/08-curriculum-intelligence.md) 最新一条记录。
   - **下一步**：把 `student_reference.py` 的输出给教师看，收集反馈后迭代（预计和家长版一样需要几轮）。

## 关键设计决策 + 为什么（不要重新踩一遍坑）

**所有这些都记在 [`mandarin-1.2/unit-01-a-day-in-my-life/08-curriculum-intelligence.md`](./mandarin-1.2/unit-01-a-day-in-my-life/08-curriculum-intelligence.md)**，
开始任何新工作前建议先读这个文件。里面按时间记录了：
- Culture 模块必须独立成模块，且内容是"规则+当年实例"两层（不能写死）
- Assessment 和 Project 合并成一个模块（一个 Unit 的总结性评量，不管形式）
- Content 模块不限于故事（新闻/音频/歌曲/视频都算）
- Generation Layer 渲染器设计教训（视觉、双语、翻译、日期颗粒度等一整套原则）
- Syllabus 会过时，和实际教学的差异要被记录而不是被忽略

## 下次对话，别再问一遍的事

- 存储载体：git 里的 Markdown+YAML，已定案，不用再讨论
- 多语言泛化（Spanish/French）：teacher 明确说了现在不需要，等真的加第二语言再说
- 家长页面的字体/配色/翻译：已经定稿（见 `generators/family_overview.py` 的
  docstring 和历史 commit message），除非教师主动要求再改，不要自己重新设计一遍

## 我（未来的 Claude）应该怎么"更新记忆"

我没有跨对话的记忆。每次都要靠读这个仓库重新获得上下文。所以规则是：
1. **重大决策、设计教训 → 写进 `08-curriculum-intelligence.md`**（针对某个 Unit 的具体决策）
   或这个文件（针对整个项目的进度/状态）。
2. **每次做完一段有意义的工作，都要 commit + push**，不要攒着不提交——
   下一个对话（不管是不是我）只能看到已经 push 的内容。
3. **这份 `PROJECT_STATUS.md` 要随进度更新**，尤其是"目前进度"和"下一步"这两节，
   避免下次对话花时间重新梳理一遍现状。
