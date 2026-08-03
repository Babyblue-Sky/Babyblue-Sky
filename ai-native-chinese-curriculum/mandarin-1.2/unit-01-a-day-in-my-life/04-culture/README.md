---
unit: Unit 1
status: note
last_updated: 2026-08-03
---

# 04 Culture — 说明

之前把「文化」内容当成 01 Overview 里的一个字段（`cultural_focus`），或者混在
03 Content 的故事里，教师指出这样处理丢失了文化板块本身的重要性——它单独对应两条
Course Standard（WL.4 / WL.5），且每个 Unit 都固定有一个文化模块位，值得单独成为一个模块。

## 设计规则（继承自 01-overview.md 的 cultural_focus）
每个 Unit 固定有一个 Culture 模块位，但具体内容依据教学当年的真实日历动态决定：
- 若 Unit 教学周期内恰好覆盖中国重大节日（中秋节 / 春节 / 端午节之一），优先安排该节日的
  文化内容（阅读/故事类）
- 否则安排其他文化活动（如书法、点餐/奶茶 field trip 等，手工/技艺/体验类）

一个 Unit 的 Culture 模块下可以有**不止一个**内容条目（本 Unit 就有两个：
一个节日故事 + 一次书法活动），每个条目用 `culture_type` 字段标注类型
（`reading` / `project` / `craft` / `field-trip` / `other`）。

## 本 Unit 的内容
- [zhongqiujie-de-gushi.md](./zhongqiujie-de-gushi.md) —— `culture_type: reading`（中秋节的故事）
- [shufa-calligraphy.md](./shufa-calligraphy.md) —— `culture_type: craft`（笔画与书法）
