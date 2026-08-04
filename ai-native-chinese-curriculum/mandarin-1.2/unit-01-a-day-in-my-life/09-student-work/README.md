---
unit: Unit 1
status: empty
last_updated: 2026-08-04
---

# 09 Student Work — Unit 1

新增模块（2026-08-04，项目定位调整为教师个人作品集之后）——展示往年学生的项目作品
（例如 Final Project 的电子书），作为课程设计成果的具体例证。见
[`generators/student_reference.py`](../../../generators/student_reference.py) 里的
`student_work_card()`，渲染成页面上独立的"学生作品 Student Work"板块。

## 隐私规则（不是建议，是硬约束）
- **不放学生姓名、不放照片**——教师 2026-08-04 明确说了这两条，上传前会自己先处理好
  （去掉姓名、不用有学生本人的照片）。
- **`student_work_card()` 的 schema 里没有"学生姓名"这个字段**，不是空着不填，是从设计上
  没有这个槽位——以后加新字段时不要加回去，这是故意的，防止以后有人"顺手"填了姓名进去
  然后忘记删。
- 如果上传的材料里还是不小心带了姓名/可识别信息（比如作品封面上学生自己写的名字），
  接手的 Claude 发现了要提醒教师，不要自己悄悄打码或裁剪之后就当没看见——教师原话
  "如果你发现问题可以提醒我处理"，处理这一步应该教师自己确认，不是 Claude 代劳。

## 文件格式
每个作品一个文件，frontmatter 至少包含：
```yaml
title: "E-book Sample — Healthy vs. Unhealthy Routine"   # 描述性标题，不是学生名字
medium: "E-book (Book Creator)"                           # 展示成一个 pill 标签
responds_to: "Daily Routine Final Project"                # 对应哪个 Assessment/Project（可选）
status: draft | canonical
```
正文分两节：`## Description`（这份作品是什么、完成了什么任务）、`## Highlights`
（教师视角：这份作品好在哪、为什么值得当例子）。

## 目前状态
还没有任何作品文件——教师还没上传。渲染器已经接好了（空目录时页面显示"内容整理中 ·
Student work coming soon"，不是报错），等教师上传第一份作品后再补具体文件。
