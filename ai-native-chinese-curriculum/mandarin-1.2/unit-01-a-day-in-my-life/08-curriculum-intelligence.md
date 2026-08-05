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

## 2026-08-03 — 学生检索页面第一轮教师反馈
**发现**：`student_reference.py` 第一版给教师看后，收到五点反馈：

1. 检索功能、Teaching Flow 板块两点都直接认可，不用改。
2. **教师提出一个关键问题：这个页面会不会随她每次上完课更新的 PPT 自动同步？**
   ——答案是不会。这个渲染器不是实时系统，是"把当前 Content Layer 数据渲染成一次
   静态快照"。她的 SMART Notebook / PPT 内容要先走 Blueprint 里定义的 Import Pipeline
   （Extractor 抽取 → AI Classifier 归类 → Human Review 教师确认）落地成 Markdown，
   再重新跑一次生成脚本，页面才会更新。这不是这次才发现的新规则（Blueprint v1.0 第 7
   节本来就这么设计），但值得记一笔：**渲染器的落地说明（docstring/README）必须显式
   说清楚"是快照还是实时"，不能假设用户会自己推断**——教师第一次看到成品页面，第一反应
   就是这个问题，说明这一点不写清楚，用户会想不到、也问不出"数据到底怎么进来的"。
3. 生词表大表和 Content/Culture 卡片内容重复，页面太长——删掉顶部大表，生词只保留在
   各卡片自己的小生词表里。为了不牺牲"搜生词"这个教师最喜欢的功能，把每张卡片自己的
   生词也编进了该卡片的搜索关键词（而不是给每一行生词单独挂搜索属性）——这样搜一个词，
   会展示教这个词的整篇故事/文化卡片（带上下文），而不是抽出来的一行孤立翻译，效果
   比原来的大表还好。
4. 页面变长后，中间位置无法回到顶部重新检索/切换分类——加了一条 `position: sticky`
   固定在视口顶部的迷你导航条（含压缩版搜索框，和主搜索框双向同步 + 分类跳转链接 +
   回到顶部），滚动到哪里都能用。**这是一个可复用的组件模式**：以后任何页面变长到
   需要分类导航的渲染器（学生检索页、以后可能的 Slides 大纲等），都应该默认带这种
   sticky 导航，而不是等用户反馈"卡在中间出不去"才加。
5. 配色要和家长版区分开——家长版用的是蓝绿色系（`--bar: #3E5D66`），学生版换成暖棕色
   （`--bar: #8A5A3B`，clay/terracotta），项目级别的 pill 色板（plum/jade/gold/vermilion/teal）
   保持不变，只换了"板块级别"的强调色。**这确认了一条新原则**：多个渲染器共享同一套
   pill 色板（保持"这是什么类型内容"的视觉语言一致），但每个渲染器的"结构强调色"
   （header bar/hero 背景）应该各自独立、可辨识，不需要跟家长版统一。

**建议**：
- 任何新渲染器的 docstring 开头就要说明"数据从哪来、多久更新一次"，不要假设这是显而易见的。
- Sticky 导航 + 双搜索框同步是好模式，直接抄，不用每次重新设计。
- 渲染器之间："item 级别的颜色语言"要统一复用，"结构级别的强调色"应该各自区分，不是所有渲染器都要用同一个主色调。

## 2026-08-03 — 教师提出核心维护成本问题：不可能逐日同步实际教学
**发现**：给教师看完第一轮修订版后，教师明确提出一个更根本的问题——即使这个渲染器
本身不难跑，"每天上完课把 PPT 变化同步进 Content Layer、再重新生成页面"这件事本身
工作量就不现实，尤其是 Teaching Flow 板块试图逐日记录具体日期和活动的设计。

**回应/结论**：
1. **"渲染器能不能自动同步"和"数据要不要维护成这么细"是两个问题，不能只回答第一个**。
   第一个问题的答案是"不能完全自动"，这是 Blueprint 里"AI 永不直接写入 canonical"
   原则决定的架构事实，不是当前的技术局限——以后就算加了自动抓取 PPT 内容的 Extractor，
   写入 canonical 前依然需要教师确认这一步。真正能改善体验的，是把"教师确认"这一步做得
   足够轻（口头描述改动，AI 代劳编辑+重新生成），而不是假装能做到全自动。
2. **更关键的解法是降低数据本身需要维护的颗粒度**，而不是死磕自动化。教师选择把
   Teaching Flow 从"逐日期+活动"降级为"Cycle 级别的大致教学顺序"——不再解析/展示
   `02-teaching/cycle-N.md` 里 `### 9/10（Day F）` 这类日期/星期标头，只保留每个
   时间块下的内容本身，按原顺序合并展示，用一条细分隔线做视觉分组（不带日期或序号）。
   这样即使教师某天临时换了一个活动的顺序或替换了一个环节，也不需要回来更新页面——
   页面本来就没有承诺"这一天做了什么"，只承诺"这个 Cycle 大概会经历哪些环节"。
3. **这暴露了一条更通用的经验**：源 Markdown 里保留逐日历史记录本身没问题（`cycle-N.md`
   文件仍然按日期组织，这是从 SMART slides 忠实抽取来的历史记录，值得留着），但**渲染器
   要自己决定往学生/家长展示时收敛到多粗的颗粒度**，不需要把源数据的颗粒度原样透传——
   这条其实是"05 家长概览"设计教训第 5 条（不展示具体日期）的延伸：那次是"渲染器展示
   什么"的问题，这次进一步说明"渲染器展示的颗粒度，应该以维护成本是否现实为约束条件
   之一，不能只从'内容是否对受众有用'单一维度决定"。

**建议**：以后任何新板块，落笔前先问"这个信息教师需要多久更新一次，更新一次的代价
是什么"，如果代价明显超过教师实际会投入的精力，宁可从一开始就设计成粗颗粒度，
不要等做完了教师用不起来才回头改。

## 2026-08-04 — 停用家长概览渲染器，学生检索页面身兼两职

**发现**：教师明确提出，同时维护 `family_overview.py`（家长版）和 `student_reference.py`
（学生版）两份渲染器，对单人维护来说工作量太大——每个 Unit 的内容定稿后，两份渲染器都要
重新跑一次、都要过一轮教师 review，长期无法持续。教师的决定：**删除 `family_overview.py`，
只保留 `student_reference.py`，同一份学生页面直接发给家长看**。

**回应/结论**：
1. 已经把 `generators/family_overview.py` 从仓库删除（不是标记废弃，是物理删除——git 历史
   里还能找回，但工作目录不再有这个文件，也不该再有人重新创建它）。
2. `family_overview.py` 当年 4 轮设计迭代留下的教训（配色语言、"渲染器展示颗粒度要服务于
   维护成本"、双语原则、日期展示的取舍等）**不因为文件删除而失效**——这份 08 文件里所有
   提到"家长版"的历史记录原样保留，作为设计参考，只是不会再有对应的独立渲染器代码。
3. **这进一步印证了本文件最后一条建议**（"渲染器展示的颗粒度应该以维护成本是否现实为
   约束条件"）——这次不是某一个板块的颗粒度问题，而是整个"要不要为同一份数据维护第二个
   受众专属渲染器"这件事本身的维护成本问题。同一个教训在不同尺度上反复出现：先是"日期
   要不要逐日展示"，现在是"要不要为每个受众单独出一份页面"，都是"能力上做得到"和"实际
   维护得起"之间的取舍，后者才是真正的约束。
4. 由于学生页面现在同时面向家长，其中原本"只给学生看"的设计假设需要重新检视——目前已知
   受影响的一条：Culture / Teaching Flow 板块正文改成全英文（2026-08-04 同一天的另一项
   变更，见 `generators/student_reference.py` 的 git 历史），原因是"学生是非母语者读不了
   中文"，但这条规则现在也适用于家长（同样可能不是中文母语者），属于同一个决定的自然延伸，
   不需要因为受众变成"学生+家长"而重新讨论一遍。

**建议**：以后再有"要不要为某个受众单独做一份产出"的提议，先问同一个问题：这份产出定稿后，
每次数据变化要不要跟着重新过一轮 review，这个频率乘以受众数量，教师实际投入得起吗——如果
答案含糊，默认先做一份通用的，不要预先拆分受众。

## 2026-08-04 — 教师上传大批 Unit 1 材料，补齐三个故事正文 + Final Project + 四份 assessment

**发现**：教师在同一次对话里陆续上传了十几个文件（中秋节故事的 summary worksheet/Cold
Character Reading pptx/插图 PDF，熊猫的故事 pptx，我太累了故事 PDF，多份练字表 PDF，
Final Project 的两份 docx，四份真实 quiz/考试 docx，两份教师朗读录音 mp4），并且明确区分了
两类材料的处理规则：
1. **quiz/考试类**（我太累了 考试+复习、熊猫的故事 考试+复习、Diagnostic Test、
   T1 Writing Assessment）——教师原话"不要在学生概览中直接使用考试真实内容"。
2. **Project 类**（Final Project 的两份 docx）——教师原话"可以直接引用"。

**回应/结论**：
1. 这正好对应 `generators/student_reference.py` 里 `assessment_card()` 已有的行为：
   非 Project 类（Diagnostic/Quiz/Summative）从来不渲染 body 正文，只显示
   "具体安排与提交方式请在 Schoology 查看"；只有 `assessment_type` 含 "project" 或
   "performance task" 的条目才会把 Driving Question/Instructions/Rubric/Resources/Examples
   完整渲染出来。**所以四份 quiz/考试文件可以放心把真实题目原文存进 Markdown**（供教师内部
   查阅、以后调整时对照），不违反"不暴露"的要求——约束在渲染器这一层，不需要在 Content
   Layer 这一层自我阉割内容。以后再收到"这是真实考试，别直接用"的材料，判断标准就是这条：
   只要 `assessment_type` 不是 project/performance task，正文本身想存多详细都可以。
2. **故事类正文（Culture/Content 的 Text / Media）采用"中文原文逐行 + em dash + 英文翻译"的
   格式**，不是这两个模块"正文一律英文"规则的例外，而是对那条规则的正确应用方式——学生要读
   的是中文（这是语言课的教学内容本身），但家长/非母语读者需要能看懂发生了什么，所以每行
   中文后面直接跟一句英文翻译，而不是整段替换成英文叙述、也不是整段保留纯中文不给翻译。
   中秋节的故事（16 行）、熊猫的故事（9 行）、我太累了（6 行书信）三处都用了这个格式，
   以后新故事正文进来时延续。
3. **ArchChinese Worksheet Maker 生成的练字表 PDF（daily_routine.pdf、时间.pdf 这类）是可靠的
   拼音/英文释义来源**——这类 PDF 每个字都标了拼音和英文意思，比 docx 里"意思"栏留白等学生
   填写的练习表格更适合拿来做数据源。以后遇到同一批"生词表格空白"的 docx，先问教师是否有配套
   的 ArchChinese 练字表，而不是直接假设没有别的数据来源、只能空着或瞎翻。
4. **教师本人朗读故事的录音（mp4）暂时不能直接放进渲染页面**——和书法视频/Quizlet 链接是
   同一个已知的老问题（见"目前进度"第 5 条）：这个仓库不存二进制媒体文件，音频/视频要等教师
   把文件传到公开可访问的地方（Drive/YouTube 等）拿到真实 URL 后，再补进对应 Markdown 的
   Text/Media 小节，渲染器会自动识别链接，不需要改代码。目前只在两个故事文件里留了一句
   "有录音，但还没有可用链接" 的记录，避免以后重复问一遍"有没有录音"。
5. **原故事文件里前后署名不一致（我太累了这封信"发送人：李朋"，落款"您的学生：王朋"）
   照抄原文，不要"纠正"**——这是原始教学材料本身的小瑕疵，Content Layer 的角色是忠实转录
   上传的材料，不是校对教师的教案；真发现明显错字/矛盾，在旁边加一句 note 说明即可，不要
   擅自改写正文本身。

## 2026-08-04 — Cycle 页面太长，改成 Do-Now / Objective / Main Activities 三项定式

**发现**：教师反馈现有 Cycle 1/2 的教学内容太长太细（逐条语法点、课堂常规模板文字说明、
Cycle 级生词汇总、备注段落全都写进去了），"学生们不会看的，太多信息等于无效信息"。同一次
反馈里也指出 Cycle 3-7 一直没有整理进 Content Layer——之前只是把对应 `.notebook` 转成了
课堂 Slides（`import-pipeline/notebook_to_pptx.py`），但那条路径不喂 Content Layer，
需要另外走 Extractor → 人工整理这条路。

**回应/结论**：
1. **新的 Cycle 文件格式**：每节课只保留三项——**Do-Now**（开场问答/热身）、
   **Objective**（"我会..."句型改写成"I can..."）、**Main Activities**（当天主要课堂活动，
   来自 slides 里"我们今天会做..."后面用"·"分隔的清单）。不再写课堂常规模板的文字说明
   （开场问答→今天的报告→新内容→休息一下→收尾这个结构本身已经在 Cycle 1 最早的版本里
   记录过一次，不需要每个 Cycle 重复解释）、不逐条记录语法点深挖、不放 Cycle 级生词汇总
   （核心词汇已经在对应故事/文化卡片自己的 Vocabulary 表里，重复放会violate"生词不重复"
   的既有原则）、**不写"备注"段落**——这条格式规则以后新增/编辑任何 Cycle 文件都要延续。
2. **SMART Notebook 源文件本身有一个很规整、可直接复用的三段式结构**：每天的第一页永远是
   "Please open your notebook, answer the questions"（=Do-Now），中间夹一页"今天的报告"
   （=课堂口语报告环节，属于课堂常规模板，不需要每次抄），然后一页"我(今天)会...
   我们今天会做..."（前半句=Objective，后半句"·"分隔清单=Main Activities）。以后再收到
   新的 `.notebook` 或对应的 pptx，直接按这三个锚点抽取，不需要通读全部 slides 逐句判断。
3. **quiz/小考的阅读理解原文不要抄进 Cycle 的 Do-Now/Activities 里**——沿用这次对话确立的
   "quiz 类内容不暴露具体题目"原则，Cycle 3 的 10/16 那天源 slides 里有一段完整的阅读理解
   短文（"后羿杀了十个太阳..."），只在 Main Activities 里写"短测验（阅读理解）"这样的活动
   标签，不把原文誊抄进 Cycle 文件。
4. **不同 `.notebook` 文件之间发现了重复的"模板尾页"**——Cycle 4 和 Cycle 5 两份文件末尾
   都有一组几乎完全相同的 slides（同样的日期"10/17"或"10/18"、同样的"我今天读一读我太累了"
   内容），推测是教师复制上一个 Cycle 文件当模板时忘记清掉的遗留页面，不是真的教了两遍。
   处理方式：只在 Cycle 4 保留一次，Cycle 5 里跳过这组重复内容，不再重复记录。以后遇到
   两个 Cycle 文件出现几乎相同的整组 slides，先怀疑是复制模板的遗留，不要当成真实的两次
   独立教学内容都抄进去。
5. **Cycle 6（一个可怕的故事/女人的故事，鬼故事）目前没有对应的 03-content 故事文件**——
   和熊猫的故事/中秋节的故事/我太累了不一样，这个故事还没有走"整理成独立故事正文"这一步，
   只在 Cycle 6 的 Main Activities 里提了一下、带了一个真实 YouTube 链接
   （https://www.youtube.com/watch?v=mU3vsjvP10w）。如果教师后续确认要把这个故事正式收进
   Content Layer，可以按熊猫的故事/中秋节的故事同样的 Cold Character Reading 格式补一个
   `03-content` 文件——但目前源 slides 里没有抽出完整的故事正文（只有零散的对话式练习句），
   需要教师上传更完整的材料才能补。
6. **意外收获**：Cycle 7（Final Project 准备周）的 slides 里带了教师自己写的范文
   "聊老师的一天"（Ms. Liao's Day），完整正文已经补进
   `06-assessment/daily-routine-final-project.md` 的 Examples 小节——这填上了之前
   "Final Project 没有范例"的缺口，虽然不是学生作品，但是教师自己示范用的模板范文，同样
   有参考价值。以后处理 Cycle 的 slides 时，除了 Do-Now/Objective/Activities 三个锚点，
   如果中间夹着一整段可复用的范文/正文（不是零散练习句），值得顺手补进对应的
   Content/Assessment 文件，不用等教师专门再传一次。

## 2026-08-04 — 项目定位从"学生检索工具"转向"教师个人作品集"，落地了哪些改动

**发现**：教师把这个页面和学校实际在用的 Schoology 一比较，发现 Schoology 本身就能做
多格式（PPT/视频/PDF）、可交互的资源分发，这套系统再做一个更简陋的静态检索页是重复
造轮子。教师决定把整个项目重新定位成**教师个人的 curriculum 设计归档 + 求职/职业发展
作品集**（详见 PROJECT_STATUS.md"项目是什么"一节），服务于她的 EdTech Explorer /
leadership 职业叙事。这一节记录这次定位讨论之后，同一次对话里实际落地的技术决策，
后续接手的 Claude 应该延续，不需要重新讨论。

**落地的决定**：
1. **课堂 Slides 直接嵌入页面，取代逐日 Do-Now/Objective/Activities 列表**——教师原话
   "不需要每次汇报 Slides 更新让你生成新页面"。技术上是 Cycle frontmatter 加
   `slides_embed_url` 字段（Google Slides File > Share > Publish to web 生成的嵌入链接，
   普通分享链接不能嵌入），`cycle_card()` 读到就渲染 iframe，读不到就显示占位提示
   （不是报错）。**"Publish to web" 会让这份 Slides 变成"有链接就能看"**——这个操作
   本身教师需要自己在 Slides 里点，Claude 做不了，也不该替她做这个决定（她已经知情，
   见对话记录，不需要每次都重新提醒一遍这一条，除非她自己问）。
2. **逐日细节没有被删除，只是不渲染**——之前那一轮"Do-Now/Objective/Main Activities"
   格式的内容，仍然完整保留在每个 `cycle-N.md` 里，只是标题从"## 教学内容时间线"改成
   "## 逐日细节（内部记录，不渲染到页面，见上面的 Slides 嵌入）"，渲染器现在只读
   "## Overview"。以后如果教师想恢复展示逐日细节（比如某个 Cycle 还没有 Slides 链接），
   数据都还在，不需要重新整理。
3. **配色改用教师指定的莫兰迪色板**（21 个具体色号，教师直接截图发的调色卡）。用法：
   - 页面基础色（bg/surface/ink/muted/line）固定一套，不随 Unit 变。
   - Pill 徽章（Story/Craft/Diagnostic/Quiz 等分类标签）从"描边+文字上色"改成
     "浅色块填充+统一深色文字"——浅色的莫兰迪色号直接当文字颜色用，对比度不够，
     当背景色配深色文字反而是这类柔和色板的正确用法，效果更接近教师截图里色卡本身的
     呈现方式（色块+文字标签）。
   - 每个 Unit 的主视觉色（hero/`--bar`）从 `UNIT_HERO_COLORS` 这个数组里按 Unit 顺序轮换，
     不是固定一个颜色——教师原话"每个单元颜色不同，但相近，不突兀"，所以数组里选的都是
     色板里色调相近的几个（伯爵橙/陈酒红/暮光绿/梦幻蓝/青城灰），不是任选。以后加新 Unit
     不需要手动挑颜色，`build_site.py` 会按顺序自动分配下一个。
   - 深色模式下 --bar 和 pill 颜色**不做单独适配**，直接复用亮色模式的同一批色号——
     这些浅色调的莫兰迪色本来就是"色块"逻辑（自带深色文字才能读），在深色页面背景上
     反而显得更跳，不需要额外处理。真正需要区分深浅模式的只有页面级别的 bg/surface/
     ink/muted/line 五个 token。
4. **新增"学生作品 Student Work"板块**（`09-student-work/`）——教师确认会上传往年学生的
   项目作品（去除姓名，不含照片）。**渲染这块内容的 `student_work_card()` 函数在 schema
   设计上就没有"学生姓名"这个字段**，不是留空，是从数据结构上没有这个槽位，这是刻意的
   防呆设计。如果教师上传的素材里还是带了可识别信息，接手的 Claude 应该提醒教师自己处理，
   不要擅自打码/裁剪后当没发生过（教师原话"如果你发现问题可以提醒我处理"，处理权在她）。
5. **GitHub Pages 部署已经搭好但没有上线**——`.github/workflows/deploy-mandarin-portfolio.yml`
   在 push 到 main 时会自动构建部署，但：这次的改动都在 feature 分支，没合并到 main；
   GitHub 仓库的 Settings → Pages 需要教师手动选一次 Source（Claude 没有对应的工具权限）；
   最重要的是**教师明确说现在先不要公开，等她想清楚再开**——这不是技术阻塞，是教师主动
   选择暂缓，以后被问起"网站怎么还没上线"不需要当成 bug 处理，先确认教师是否已经决定好了。
6. **讨论过但没有采纳/搁置的方向**：
   - **付费内容/订阅制**（"Unit 1 免费，之后收费"）——教师形容为"大胆的设想"，讨论后
     搁置，主要顾虑是这类课程材料可能算学校的职务作品，个人售卖前需要教师自己核实雇佣
     合同/学校政策，Claude 没有替她做这个判断的立场。如果教师以后重新提起，直接从这里
     接着聊，不需要重新讨论"能不能做""该怎么做"这两层，教师已经知道结论是"先查合同"。

## 2026-08-05 — Assessment 板块改成直接显示真实考题，不再只指向 Schoology

**决定**：教师看过 Unit 1 页面后确认这个界面不再面向学生，`assessment_card()` 里对
Diagnostic/Quiz/Summative 类"只显示 See Schoology，不渲染 Markdown 正文"这条 2026-08-04
定下的规则可以撤销——`06-assessment/*.md` 里存的完整真实考题内容现在直接渲染到页面。

**落地**：
- `assessment_card()`（`generators/student_reference.py`）非 Project 分支改成调用新的
  `render_markdown_body(body)`，同时把 `administered` 日期也显示出来（原来这两者都被
  刻意隐藏，理由是"不给学生看"，现在理由不存在了）。Project 类分支（Final Project）没变。
- 新增 `render_markdown_body()`：这些测验文件的小节标题各不相同（Listening/Reading/
  Writing/Speaking，或 词/句子/说一说），不像 Content/Culture 卡片那样有固定的
  Overview/Text-Media/Activities/Extensions 几个已知小节名可以按名字查找，所以这个函数
  通用地把 body 里所有 `## 标题` 小节依次渲染出来，不需要预先知道小节叫什么。
- 踩过的坑：body 开头的 `# 标题` 那一行前面通常还有一个空行（frontmatter 结束的 `---`
  后面紧跟一个空行再是 `# 标题`），`re.sub(r"^#\s+.*\n", ...)` 不加 `re.M` 且不吃掉前导
  空白的话匹配不到，标题行会原样露在页面正文里——要用 `r"^\s*#\s+.*\n"` 才行。
- 另一个坑：本来想把 `1. xxx` 这种数字开头的行也解析成 `<ol>`，但
  `diagnostic-test.md` 的 Listening 部分是"1. 昨天　2. 姐姐　3. 中国..."这种一行塞好几个
  编号的flowing enumeration，不是每行一个 item 的真列表，用同一套启发式解析会把编号和
  内容拆得乱七八糟。**结论：数字编号行不特殊处理，就当普通段落渲染**——两种格式都能
  完整、正确地显示文字，只是不会被拆成好看的 `<li>`，这个取舍比"解析对一半、拆错一半"好。
- `06-assessment/README.md` 和三份测验文件（`diagnostic-test.md` 保持原样，
  `summative-test.md`/`wo-tai-lei-le-quiz.md` 的 `source` 字段）已同步更新，去掉了
  "assessment_card() 不渲染这些内容"的过时说明。

## 待补充的观察类型（模板，供未来使用）
- 哪些活动最成功
- 学生最容易犯的错误 / Vocabulary 难点
- 每年修改建议
- Student Feedback
