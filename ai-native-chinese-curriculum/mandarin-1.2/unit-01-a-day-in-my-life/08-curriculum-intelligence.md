---
unit: Unit 1
status: active
last_updated: 2026-08-03
---

# 08 Curriculum Intelligence — Unit 1

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

## 2026-08-03 — 新增独立的 Culture 模块
**发现**：教师指出「文化」板块还是缺失的——之前只是 01 Overview 里的一个字段
（`cultural_focus`），而「中秋节的故事」被当成 03 Content 的一个 story 条目处理，
这样处理没有单独体现文化板块的重要性。文化对应两条独立的 Course Standard
（WL.4 关系文化实践与视角、WL.5 文化比较），且每个 Unit 都固定有一个文化模块位，
值得单独成为一个模块，而不是附属在别处。

重新梳理已上传的材料后，还发现 Cycle 1（9/18）的**笔画/书法**教学，其实也是一次
「其他文化活动」（教师提到的手工/技艺类），此前被当成普通教学内容记录在
02 Teaching 里，没有被识别为 Culture 内容。

**调整为**：新增 **04 Culture** 模块，插在 03 Content 之后：
01 Overview / 02 Teaching / 03 Content / **04 Culture** / 05 Resources /
06 Assessment / 07 AI Workspace / 08 Curriculum Intelligence（共 8 个模块）。
- 「中秋节的故事」从 03 Content 移到 04 Culture（`culture_type: reading`）
- 新增「笔画与书法」条目于 04 Culture（`culture_type: craft`），内容从
  02-teaching/cycle-1.md 中已记录的 9/18 教学内容提炼而来
- 一个 Unit 的 Culture 模块下可以有不止一个条目，用 `culture_type` 字段
  （reading / project / craft / field-trip / other）区分类型

**建议**：以后从 SMART slides 里做 Import 时，凡是涉及节日、书法、饮食体验、
field trip 这类内容，应该主动往 04 Culture 归类检查，而不是默认归进 02 Teaching
或 03 Content——这是这次漏掉笔画/书法的根本原因。

## 2026-08-03 — Generation Layer 设计教训（面向家长的第一个渲染器）
**发现**：`generators/family_overview.py` 第一版给教师看后，收到五点反馈，对以后任何
新渲染器（学生练习单、Slides 大纲等）都适用，记在这里避免重复犯错：

1. **视觉设计要真的有吸引力，不只是"干净"**——面向家长/学生甚至更大范围分享的页面，
   平淡的灰绿色块+细边框读起来不够吸引人。要有一个真正的视觉焦点（这次用了贴合
   本单元"早上/上午/下午/晚上"主题的日夜渐变色带做头图）。
2. **标题/分类至少中英双语；需要解释的句子直接用英文**——受众不是中文母语者，
   尤其是家长。栏目标题双语，但一句话说明（比如页面副标题、Transfer Goal 的补充说明）
   应该直接写英文，不要写中文再指望家长看懂。
3. **矩形 pill 标签是个好设计**，同一个视觉语言可以用在 Content/Culture/Assessment
   任何列表上，标示"这是什么类型"，不同 Unit 内容不同但形式统一——值得保留并推广到
   以后所有渲染器。
4. **中文翻译不确定时，宁可省略，不要瞎翻**——"评量安排"和"assessment"对不上，
   "期末项目"里的"期末"暗示学期末，但这只是一个 Unit，不是学期；"Transfer Goal"
   这类 UbD/ACTFL 术语本身没有固定通用译名。渲染器生成双语标题时，翻译不确定的直接
   留英文，不要为了"凑双语"硬翻。
5. **不展示具体到某一天的进度日期**——教学进度每年都会漂移（这一点在 04 Culture
   的"动态填充"里也提过），家长看的页面只需要"单元大概什么时候开始、期末评量大概
   什么时候"这种粗粒度信息，不需要"9/16 (Day B)"这种具体到某年某天的记录。
   源数据（06-assessment 的 `administered` 字段）仍然可以保留具体日期作为内部历史
   记录，只是**渲染器要自己决定对外展示的颗粒度**，不是原样透传所有字段。

**建议**：以后设计任何新的 Generation Layer 渲染器时，先问一句"这份数据里，哪些是
给这个受众看的、哪些是内部字段"，不要把 Content Layer 的所有字段不加选择地渲染出去。

## 2026-08-03 — 家长概览渲染器第二轮修订
**发现**：教师给了 Canva 上四个模版截图作参考（"不要照抄设计，但可以参考视觉效果、
统一色彩和板块"），并提出四点具体修订：

1. 视觉效果沿用"色块 Header Bar + 白底描边卡片"的结构（模版共有的特征），
   每个板块一个纯色 Header Bar，配色复用 pill 已有的色系（plum/vermilion/gold/teal），
   让"板块级别的颜色"和"条目级别的 pill 颜色"呼应。
2. 标题定稿为：学习目标 Learning Objectives / 学习材料 Learning Materials /
   文化 Culture / 单元考核 Unit Assessments / 核心词汇语法 Key Vocabulary & Grammar，
   **删除了 Transfer Goal 板块**——期末项目本来就作为一条 Performance Task 出现在
   单元考核列表里，单独一个板块是冗余的。
3. 每个标题下的正文内容要用英文——这暴露了一个数据缺口：`01-overview.md` 的
   Learning Objectives 之前只存了中文改写版，没有保留 Syllabus 原始的英文版本。
   已经在 `01-overview.md` 里补了一个 "Learning Objectives (English)" 小节存
   原始英文句子，渲染器面向家长时读这个英文版本，教师内部版本（中文）保留不变——
   这是"同一份数据，不同受众看不同投影"的又一个真实案例。
4. 所有中文用楷体（Kaiti）——通过 CSS `font-family` fallback 顺序实现
   （`Kaiti SC` / `STKaiti` / `KaiTi` 排在西文字体之后、CJK 黑体/苹方之前），
   不需要给每个中文片段单独加样式，浏览器按字符自动挑字体。

**建议**：以后新渲染器如果同时面向教师和家长，"内容中英双语"不能只在渲染器里做翻译，
应该在 Content Layer 里就存好对应受众需要的语言版本（就像这次给 Learning Objectives
补的英文版），渲染器只负责挑选，不负责翻译——翻译应该是人工/教师确认过的数据，
不是生成时现造的。

## 2026-08-03 — 学生检索页面渲染器（第二个 Generation Layer 渲染器）设计决策
**背景**：`generators/family_overview.py` 定稿后，下一步是面向学生的静态检索页面
（`generators/student_reference.py`），复用同一份 Content Layer 数据，但受众和用途不同——
学生自己在学/复习，需要比家长版更完整的内容。写的过程中做了几个和家长版不同的取舍，记下来
避免以后重新纠结：

1. **测验类 Assessment 不显示考题内容，只显示标题+类型+"见 Schoology"**——Diagnostic /
   Summative Test 是评量工具，不适合当复习资料公开挂在检索页面上；但 Performance Task /
   Project（如 Final Project）完整显示 Driving Question / Instructions / Rubric，因为
   这些内容本来就是设计给学生看、指导他们完成任务的，不是"考题"。用 `assessment_type`
   字段里是否含 project/performance task 关键词区分这两种展示方式。
2. **Cycle 教学日期"保留展示，但加免责说明"，和家长版的"完全不展示具体日期"不同**——
   学生检索页面的定位就是要展示"每个 Cycle 的真实教学流程"，去掉日期会丢失顺序信息；
   但教学日期每年会漂移（这一点前面几条记录已经反复出现），所以页面在 Teaching Flow
   板块开头加了一句"这是上次教学时的参考日期，今年实际进度请查 Schoology"，而不是
   像家长版一样直接砍掉日期字段。同一个"日期会漂移"的问题，在不同渲染器上可以有不同的
   处理方式，取决于该渲染器的受众到底需不需要顺序信息。
3. **缺失内容明确标注"内容整理中"，不留空白也不瞎编**——沿用家长版"宁可省略，不要瞎翻"
   的原则，但学生版的处理方式更进一步：检测到某个 section 只有一行"> 待补充"或
   "> TODO..."时，渲染成统一的斜体提示文字，而不是直接把内部开发用的 TODO 原文
   （通常是写给教师/AI 看的下一步提示，比如"待教师提供内容"）暴露给学生看到。
4. **链接（Quizlet/YouTube/Worksheet）目前基本都渲染不出来，因为数据里还没有真实
   URL**——slides 里提到"附 Quizlet 链接""YouTube 视频"，但目前的 Content Layer 文件
   只记录了"这里应该有个链接"这件事，没有实际 URL 字符串。渲染器支持解析 Markdown 的
   `[文字](链接)` 语法并转成可点击链接，但不会主动生成或猜测链接——等教师/后续 Import
   把真实 URL 补进对应 Markdown 正文里，链接会自动在页面上出现，不需要改渲染器代码。
5. **生词表是"全 Unit 汇总"而不是分散在各 Content/Culture 文件里各看各的**——页面顶部
   有一个合并了 05-resources 生词表 + 每个 Content/Culture 条目自己的生词表的总表，
   同一个词如果在多个来源出现，就出现多行（各自标注来源），不做"智能去重合并"，避免
   把不同来源里可能不一致的释义强行合并成一条"正确答案"。

**建议**：以后再写新渲染器时，先问一句"这个渲染器的受众，和已有渲染器的受众有什么不同"，
同一份数据在不同渲染器上完全可以有不同的取舍（比如这次的日期展示方式），不需要不同渲染器
必须遵守完全相同的规则——规则应该服务于受众，不是反过来。

## 待补充的观察类型（模板，供未来使用）
- 哪些活动最成功
- 学生最容易犯的错误 / Vocabulary 难点
- 每年修改建议
- Student Feedback
