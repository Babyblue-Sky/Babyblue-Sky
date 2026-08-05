---
unit: Unit 1
status: note
last_updated: 2026-08-04
---

# 05 Assessment — 说明

「Project」和「Assessment」原本是两个模块，教师反馈：一个 Unit 的总结性评量，
不管形式是测验（test）还是项目（project），本质都是同一件事——对这个 Unit 的
**总结性评估**，只是呈现形式不同。所以合并成一个模块，每份评量用
`assessment_type` 标注类型，例如：

- `Diagnostic` —— 摸底测验
- `Quiz` —— 随堂小测
- `Summative` —— 总结性测验
- `Summative — Performance Task / Project` —— 以项目/表现性任务形式呈现的总结性评量

**2026-08-04 → 2026-08-05 规则变化**：这套系统 2026-08-04 起已经不是学生/家长检索工具，
是教师个人的 curriculum 作品集（见 PROJECT_STATUS.md 的定位调整），渲染器最初仍沿用了旧规则
（`assessment_card()` 对 Diagnostic/Quiz/Summative 只显示 "See Schoology"，不管 Markdown 里
实际写了什么）。**2026-08-05 教师明确说这个界面不再面向学生，可以直接显示考题**——渲染器
已改成把这些文件的正文（Listening/Reading/Writing/Speaking 或 词/句子/说一说 等任意 `##`
小节）原样渲染出来，`administered` 日期也一并显示。所以这些文件里保留的完整真实考题内容
现在就是页面上会显示的内容，写文件时按这个前提来，不要再假设它们只是"内部备份"。Project 类
一直都是完整渲染 Instructions/Rubric/Resources/Examples，这条没变。

目前共五份文件：`diagnostic-test.md`、`summative-test.md`（熊猫的故事）、
`wo-tai-lei-le-quiz.md`（我太累了）、`daily-routine-final-project.md`（Project 类，
内容对学生/家长可见）。（`listening-writing-assessment.md` 曾经存在过，2026-08-04
教师要求删除，不要重新创建。）
