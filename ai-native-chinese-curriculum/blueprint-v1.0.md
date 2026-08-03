# AI Native World Language Curriculum — Architecture Blueprint v1.0

> 视角：World Language Department Chair
> 目标：设计一套 5–10 年内不需要推倒重来的课程架构，先在 Middle School Mandarin（1.2 / 2.1 / 2.2）验证，再无痛扩展到整个 World Language Department（Spanish / French / 未来可能新增的语言）。
> 本文只讨论**架构（Architecture）**，不讨论具体文件/资料夹模板 —— 那是 Step 2（Unit Template v1.0）的任务。

---

## 0. 这份 Blueprint 解决什么问题

v0.1 已经给出了一个可用的 Mandarin Unit 结构（01 Overview ~ 08 Curriculum Intelligence）。但那是**一个语言、一个层级的实现**，还不是架构。如果现在就把这套结构当成"标准"往下建，三年后 Department 想加 Spanish 或 French 时，会发现：

- 汉字 / 拼音 / 声调这些 Mandarin-only 的概念被写死在核心结构里
- Standards 只认 ACTFL Can-Do，换一套框架（IB、州标准）就要改 schema
- 每个语言各建一套"资源库"、"Rubric"、"AI Prompt"，Department 层面无法共享和沉淀

Blueprint v1.0 的任务，是把 v0.1 中"对 Mandarin 成立"的部分，拆成**架构层（永远稳定）**和**语言层（可替换/可扩展）**，让 Mandarin 只是这套架构的第一个实例，而不是架构本身。

---

## 1. 九条设计公理（Design Axioms）

这套系统要撑住 5–10 年，必须满足：

1. **课程即数据，产出即视图**：Slides / HTML / PDF / Assessment / AI Tutor 都是 Curriculum Database 的"渲染结果"，不是独立维护的文件。
2. **核心语言无关，语言层可插拔**：架构核心不假设"这门语言长什么样"；拼音、汉字、性数配合、动词变位等各语言特有的东西，都作为可挂载的扩展，而不是核心字段。
3. **标准是插件，不是地基**：ACTFL Can-Do 现在是主要标准，但 schema 必须允许同一个 Unit 同时挂多套标准框架（IB、州标准、Department 自订标准），换标准不改架构。
4. **结构稳定，内容流动**：Department → Language Program → Course → Unit → Module 这条主干，未来十年基本不变；每年变的是里面的内容（生词、活动、评量）。
5. **教师专业判断是一等数据**，不是写在某个人脑子里的经验。Curriculum Intelligence 层的存在，就是为了让"这个活动为什么有效 / 学生在哪里最容易错"变成可查询、可传承的结构化记录，而不是随着老师离职而消失。
6. **AI 是生产者和贡献者，永远不是数据源头**。AI 可以起草、生成、建议，但只有经人审核后才能写入 canonical 数据库——这是保持系统可信、可维护的关键。
7. **每一份内容只有一个"家"，可以有很多种"投影"**。一个生词、一段课文，只存一份，被 Slides / Worksheet / Assessment / AI Tutor 分别引用，而不是复制四份。
8. **版本管理是刚需，不是加分项**。课程每年都会改，必须能像 git 一样看到"去年这个 Unit 长什么样、今年改了什么、为什么改"。
9. **迁移是单向棘轮，不回头**。SMART Notebook 只是"被迁移的对象"，架构设计上永远不依赖、不回写 SMART；一旦进入 Curriculum Database，就不再需要 SMART 这个文件本身。

---

## 2. 四层架构模型

比 v0.1 的资料夹树更抽象一层的看法——把整个系统拆成四个职责分明的层：

```
┌─────────────────────────────────────────────┐
│ Layer 4  Intelligence Layer                  │
│  使用数据 + 教师反思 + 学生表现 → 修订建议     │
└───────────────────▲───────────────────────────┘
                     │ 反馈回流
┌───────────────────┴───────────────────────────┐
│ Layer 3  Generation Layer                     │
│  Slides / HTML / PDF / Assessment / AI Tutor  │
│  （渲染器，不存内容，只读 Layer 2 生成视图）    │
└───────────────────▲───────────────────────────┘
                     │ 读取
┌───────────────────┴───────────────────────────┐
│ Layer 2  Content Layer                        │
│  Standards / Vocabulary / Grammar / Text /     │
│  Media / Assessment Items（结构化数据记录）     │
└───────────────────▲───────────────────────────┘
                     │ 承载于
┌───────────────────┴───────────────────────────┐
│ Layer 1  Structural Layer                     │
│  Department → Language Program → Course →      │
│  Unit → Module（跨语言不变的骨架）              │
└─────────────────────────────────────────────┘
```

**职责边界：**

| 层 | 会变吗 | 谁来改 | 典型问题 |
|---|---|---|---|
| Structural | 十年一变 | Department Chair | "一个 Unit 下面应该有哪些 Module 类型？" |
| Content | 每年都改 | 任课老师 | "这单元的生词表、课文、评量长什么样？" |
| Generation | 按需增加渲染器 | 技术负责人 / AI | "怎么把内容变成 Slides？变成 AI Tutor 的 system prompt？" |
| Intelligence | 持续累积 | 全体教师 + AI 辅助整理 | "这个活动去年效果好不好？学生的坑在哪？" |

新增一种输出格式（比如未来的某个新工具取代 Google Slides），只是在 Layer 3 加一个渲染器，Layer 1/2 完全不受影响——这是"5–10 年不过时"的核心保证。

---

## 3. Department 级别的泛化设计

### 3.1 Language 作为一等参数，而不是假设

Course 的身份不是 "Mandarin 1.2"，而是 `{department, language, level, unit}` 的组合。Mandarin 现在的实现只是 `language = "Mandarin"` 这个参数下的一个实例。

### 3.2 语言特有内容 → 扩展命名空间，不进核心 schema

拼音、声调、部首、汉字这些东西，不应该出现在 Structural Layer 或 Content Layer 的核心字段里，而是作为 **"Script & Phonology Extension"** 挂载在 Vocabulary / Reading 这类内容记录上。西班牙语加动词变位表、法语加性数配合规则，都是同样方式挂自己的扩展命名空间。

结果：Structural Layer + Generation Layer + Intelligence Layer 三层，**Spanish / French 项目组可以直接复用，无需 fork**；只需要自己实现语言特有的扩展命名空间和对应的渲染细节。

### 3.3 Standards 抽象为 "Standard Reference"

一个 ACTFL Can-Do Statement，只是 "Standard Reference" 这个通用类型下的一条实例。Unit 与 Standard Reference 是多对多关系——同一个 Unit 可以同时挂 ACTFL、IB、州标准、Department 自订标准，不需要改架构，只需要多插一条关联记录。

### 3.4 Department Shared Library

Rubric 模板、Project 格式、AI Prompt 模板、评量类型，这些跨语言都用得上的东西，从"某个语言项目自己的资源"提升为 **Department Shared Library**：各语言项目默认继承，允许在自己的 Content Layer 里覆盖（override）。这避免每个语言组重新发明一遍评分标准和活动设计的问题。

---

## 4. 课程数据模型（概念层，非文件格式）

核心实体与关系：

- **Department**（World Language Department）
- **Language Program**（Mandarin / Spanish / French / …）
- **Course**（1.2 / 2.1 / 2.2 / …）
- **Unit**
- **Module**（v0.1 中的 01–08，是 Mandarin 目前已知最好用的一组 Module 类型；架构上必须允许某语言增删 Module 类型，而不破坏整体结构——例如 Spanish 未必需要 "Stories" 这个形态，但可能需要 "Conjugation Drills"）
- **Standard Reference**（与 Unit 多对多）
- **Resource**（媒体/学习单等，被引用而非被复制）
- **Prompt**（AI Workspace 的 Prompt Library 条目，需版本化）
- **Intelligence Record**（反思/反馈条目，必须挂在 "Unit × 学年 × 教学班" 这个粒度，而不只是挂在 Unit 上——这样才能看出跨年趋势，而不是把所有年份的反思混成一团）

---

## 5. Generation Contract（Layer 2 → Layer 3 的契约）

每一种输出（Slides / HTML / PDF / Assessment / AI Tutor system prompt）在架构上必须声明：

1. **消费哪些 Content Layer 字段**（比如 AI Tutor 需要 Vocabulary + Grammar Focus + Can-Do Statements，但不需要 Rubric）
2. **哪些 Module 输入是必须的，哪些是可选的**
3. **内容与样式分离**：换主题/换排版（品牌视觉、字体、配色）不应该触碰内容数据

新增一种输出类型 = 新增一个渲染器插件，Content Layer 的数据零迁移成本。

---

## 6. 治理与版本管理（Governance & Versioning）

- 每个 Unit 有版本历史；每学年的一次"运行"会产生一个带日期的快照，Curriculum Intelligence 的记录挂在这个快照上，而不是笼统地挂在 Unit 上。
- **草稿 → Canonical 的审批流**：老师（或 AI）产生的修改先是 draft，Department Chair（或指定的 curriculum lead）审核后才合并为 canonical——即"这是这门课当前唯一权威版本，Generation Layer 只读 canonical"。这套流程类似 pull request 的 review 模型，AI 生成的内容永远经过人工确认才能成为数据源头（呼应公理 6）。

---

## 7. Import Pipeline（架构级别）

```
SMART Folder
   │
   ▼
Extractor        —— 抽取文本 / 图片 / 原始结构
   │
   ▼
AI Classifier    —— 把抽取内容映射进 Module 槽位，并打上 Standards 标签
   │
   ▼
Human Review Queue —— 老师确认/修正映射结果
   │
   ▼
Canonical Content Layer
```

关键原则：**AI 永远不直接写入 canonical**，一定经过 Human Review Queue。这既保护了数据可信度，又让"老师纠正 AI 的判断"这件事本身成为 Curriculum Intelligence 的训练信号——教师的修正记录，本身就是最有价值的 Intelligence Record。

---

## 8. 为什么这套架构能撑 5–10 年

- **内容与呈现解耦**：呈现工具会被淘汰（Google Slides 也不例外），但因为内容是数据，换渲染器只是"加一个插件"，不是"重新写一遍课程"。
- **结构与语言解耦**：Department 未来加日语、韩语、ASL，复用 90%+ 的系统，只需实现语言特有的扩展命名空间。
- **标准与结构解耦**：ACTFL 被替换或叠加其他框架，不需要改 schema。
- **教师专业判断被数据化**：老师离职，判断不会跟着离开——Curriculum Intelligence 层把"经验"变成"可查询的机构记忆"。

---

## 9. 与 v0.1 的关系 / 下一步

- v0.1 中给出的资料夹树（01 Overview ~ 08 Curriculum Intelligence）= Structural Layer + Content Layer 在 **Mandarin** 上的第一个具体实现，用来验证本 Blueprint 的抽象模型是否成立。
- **Step 2（Unit Template v1.0）**：把 01–08 正式定义为 Mandarin 在 Content Layer 上的 schema（字段、必填/选填、与 Standard Reference 的挂接方式）。
- **Step 3（SMART Import Workflow）**：按第 7 节实现 Extractor → AI Classifier → Human Review Queue，先在一个 Unit 上跑通。
- **Step 4（Pilot Unit）**：挑一个最完整的 Unit 验证三个问题——AI 是否容易理解？是否容易维护？是否能自动生成不同教学资源？

**Department Chair 的建议**：现在只有 Mandarin 在跑，但语言无关的架构决策（第 3 节）现在做成本最低。等 Mandarin 三门课都按"Mandarin-only 假设"建完，再往 Spanish / French 泛化，返工成本会高得多。现在多花的这一点架构设计时间，就是为了以后不用重来。
