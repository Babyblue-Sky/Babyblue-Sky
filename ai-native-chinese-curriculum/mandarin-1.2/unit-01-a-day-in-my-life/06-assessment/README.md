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

**渲染器不暴露非 Project 类评量的正文内容**（`assessment_card()` 对 Diagnostic/Quiz/Summative
只显示 "See Schoology"，不管 Markdown 里实际写了什么）——所以这些文件可以放心保留完整的真实
考题内容供教师内部查阅，不用担心泄露给学生/家长。只有 Project 类才会把 Instructions/Rubric/
Resources/Examples 完整渲染出来，这类文件放真实内容前要教师明确同意（2026-08-04 教师已确认
Final Project 的内容可以直接引用）。

目前共六份文件：`diagnostic-test.md`、`summative-test.md`（熊猫的故事）、
`wo-tai-lei-le-quiz.md`（我太累了）、`listening-writing-assessment.md`（听一听和写一写）、
`daily-routine-final-project.md`（Project 类，内容对学生/家长可见）。
