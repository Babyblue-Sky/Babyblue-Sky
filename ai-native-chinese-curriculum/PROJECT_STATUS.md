---
last_updated: 2026-08-05
branch: claude/ai-native-chinese-curriculum-lozz7k
---

# Project Status — 给下一次接手这个项目的 Claude 看

> 如果你是一个新对话里的 Claude，第一次看到这个项目：**先读这个文件**，
> 再按需读下面链接的文件，不要从零开始猜项目在做什么。这个仓库本身就是
> 唯一的记忆载体——没有别的地方存着之前对话的上下文。

## 项目是什么

把 Tian（Mandarin 老师）的 Middle School Mandarin 课程从 SMART Notebook 迁移到一套
Markdown+YAML 的 **AI Native Curriculum Database**，作为所有教学产出（课堂 Slides、
Assessment、个人作品集网站等）的唯一数据源。架构本身详见
[`blueprint-v1.0.md`](./blueprint-v1.0.md)，不受下面这条定位调整影响。

**2026-08-04 项目定位调整**：这套系统最初设计成"面向学生/家长的检索工具"，但教师对比
学校实际在用的 Schoology 后发现，Schoology 本身就能做多格式、可交互的资源分发，这套系统
再做一个更简陋的静态检索页是重复造轮子。**新定位：教师个人的 curriculum 设计归档 + 求职/
职业发展作品集**，服务于教师的 EdTech Explorer / leadership 职业路径叙事，受众是教师自己、
未来的雇主/同行、以及未来可能的学生（不是当前在读学生的日常检索工具）。这个转向不影响
Content Layer（Markdown+YAML）本身的价值——恰恰相反，教案设计过程中的决策记录
（`08-curriculum-intelligence.md`）在新定位下从"给下一个 Claude 看的内部笔记"变成了
**最有含金量的展示内容**。`import-pipeline/notebook_to_pptx.py`（SMART → Google Slides）
这条线完全不受影响，教师仍在用它准备课堂教学。`generators/student_reference.py` 这个渲染器
不会被删除（技术上仍然是"从 Content Layer 生成一个静态页面"这个模式的第一个实现，双语、
锚点链接等设计仍然有效），但它的产出物现在的角色是**作品集网站的一部分**，不是学生日常
检索入口——面向的读者假设从"当前在读的学生和家长"变成"浏览作品集的访客"。

## 目前进度（做到哪一步）

1. **Blueprint v1.0** — 完成。架构层设计：九条公理、四层模型、Department 级泛化。
2. **Pilot Unit** — 进行中。`mandarin-1.2/unit-01-a-day-in-my-life/` 已经有
   Cycle 1-7 全部教学内容、Diagnostic Test、Student Survey、生词表、Culture 模块
   （中秋节的故事 + 笔画书法）。**2026-08-04 教师上传了一大批材料，已经整理进 Content
   Layer**：中秋节的故事正文（16 行，Cold Character Reading）、熊猫的故事正文（9 行，
   完整标题「很饿的熊猫的故事」）、我的一天太累了正文（书信体，6 段）+ 专属生词表、
   `05-resources/vocabulary-my-day.md` 的拼音（用两份 ArchChinese 练字表确认）、
   Final Project 完整细节（`daily-routine-final-project.md`：Driving Question/
   Instructions/Rubric/Resources/教师范文，教师明确说这份可以直接引用）、四份真实
   quiz/考试（熊猫的故事、我太累了、Diagnostic、Listening & Writing Assessment——这四份
   文件从一开始就存了完整真实内容；**2026-08-05 教师明确这个页面不再面向学生，`assessment_card()`
   已改成把 Diagnostic/Quiz/Summative 的正文直接渲染出来，不再只显示 "See Schoology"**，
   详见下面第 5 条和 `06-assessment/README.md`）、**Cycle 3-7 教学内容**
   （用 `.notebook` 源文件重新抽取文字，见下面第 6 条——这条路径之前只喂了 Slides pptx，
   没喂 Content Layer，这次补上了）。**Cycle 1-7 的格式也全部按教师反馈重做**：每节课只
   保留 Do-Now / Objective / Main Activities 三项，删掉了课堂常规模板说明、逐条语法点、
   Cycle 级生词汇总、备注段落——教师原话"太长了，学生们不会看的，太多信息等于无效信息"，
   这条格式规则以后编辑任何 Cycle 文件都要延续，见 08-curriculum-intelligence.md
   2026-08-04 的记录。
   **还缺**：笔画书法的真实 YouTube 视频链接、中秋节的故事的教师朗读音频链接（熊猫的故事
   和我太累了两个已经拿到 Drive 链接并补进对应 Markdown 的 Text/Media，中秋节的故事这个
   还没有）、Cycle 6 教的"可怕的故事/女人的故事"（鬼故事）还没有对应的 03-content 正文
   文件（源材料不完整，只有零散练习句，需要教师上传更完整的材料）。
   **教师明确说她会在一个新对话里上传更多 Unit 1 材料**——接手的 Claude 应该按
   Blueprint 的 Import Pipeline（Extractor 抽取 → AI Classifier 归类 → Human Review）
   把新材料整理进对应模块的 Markdown，然后重新跑 `generators/student_reference.py`
   生成新版页面。整理新内容时要延续这次对话定下的规则（见下面"别再问一遍的事"
   和"关键设计决策"两节，以及 08-curriculum-intelligence.md 2026-08-04 的最新记录），
   不要每次都重新讨论一遍。
3. **存储载体已定案** — git 里的 Markdown + YAML，不用 Notion/Airtable/Sheets。
4. **Unit Template 结构（当前 8 个模块，随时可能因为新发现再调整，以
   `mandarin-1.2/unit-01-a-day-in-my-life/` 里实际的资料夹为准，不要相信这里的
   文字描述会一直准确）**：
   `01-overview / 02-teaching / 03-content / 04-culture / 05-resources / 06-assessment / 07-ai-workspace / 08-curriculum-intelligence / 09-student-work`
   （**09-student-work 是 2026-08-04 项目定位调整后新增的**，展示往年学生作品，schema 里
   刻意没有"学生姓名"字段，见该模块的 README.md）
5. **Generation Layer（渲染器）** — 2026-08-04 跟着定位调整做了一轮大改，历史设计教训
   （英文化、锚点链接、日期颗粒度等规则）详见
   [08-curriculum-intelligence.md](./mandarin-1.2/unit-01-a-day-in-my-life/08-curriculum-intelligence.md)，
   这里只记当前状态：
   - `generators/student_reference.py` — 单个 Unit 的"Curriculum Archive 课程归档"页面
     （标题/eyebrow 已从"Student Reference 学生检索页面"改名，见 2026-08-04 定位调整）。
     **Teaching Flow 板块现在是"一段 Overview 摘要 + 嵌入的真实课堂 Slides"**，不再是
     Do-Now/Objective/Main Activities 逐日列表——那份逐日细节没删，挪进每个
     `cycle-N.md` 里渲染器不读的"逐日细节"小节，源码里还在。Slides 嵌入读 Cycle
     frontmatter 的 `slides_embed_url`（Google Slides "Publish to web" 生成的嵌入链接，
     不是普通分享链接），没填的 Cycle 显示占位提示，不是报错。**新增"学生作品 Student
     Work"板块**，读 `09-student-work/*.md`，目前是空的（教师还没上传作品）。
     **配色改用教师指定的莫兰迪色板**：pill 徽章从描边文字改成柔和色块+深色文字，
     每个 Unit 用 `UNIT_HERO_COLORS` 数组里不同但相近的一个色号做主视觉色（轮换机制，
     不是写死一个）。**2026-08-05**：教师明确这个页面是她的个人作品集，不是学生工具，
     所以 Diagnostic/Quiz/Summative 类 Assessment 不用再只显示"See Schoology"——
     `assessment_card()` 改成通用渲染任意 `## 小节`（新增 `render_markdown_body()`，
     因为这些测验文件的小节标题各不相同，不像 Content/Culture 卡片那样是固定的
     Overview/Text-Media/Activities/Extensions 几个名字）。**同一天教师看过页面后又
     提了两条修改**（详见 08-curriculum-intelligence.md 同日期第二条记录）：
     ① `administered` 日期最终**不显示**（最初这条改动顺手加了，被教师叫停撤销，
     和 Cycle 日期的"不展示具体日期"是同一条原则）；
     ② `06-assessment/*.md` 和 `01-overview.md` 之外这几份文件里的 `MS.WL.N`/`HAL.N`
     这类学校专属标准代码——**HAL（Habits of Learning）整条删除**，**WL（语言交流模式）
     保留但去掉编号前缀，只留 Interpretive/Interpersonal/Presentational Communication
     这几个通用名称**；③ 同一天教师又指出 `grading_scale`（EE/ME/AE/BE 四级评定）**也是
     这所学校的评分制度，同样不通用，已删除**（frontmatter `grading_scale` 字段 + 正文里
     "按 EE/ME/AE/BE 四级评定"这类句子全部去掉，详见 08-curriculum-intelligence.md
     同日期第三条记录）——不要理解成"标准代码删了、评分等级保留"，两个都删。
     Project 类（Final Project）渲染逻辑本身没变，只是同步改了它的 Rubric 内容。
   - `generators/build_site.py`（**新增**）——把 `student_reference.py` 的单 Unit 页面
     包一层完整 HTML5 文档壳，加一个作品集首页（index.html，列出所有已发布的 Unit，
     每个 Unit 卡片左边框用它自己的主视觉色），输出到 `site/`，供 GitHub Pages 部署。
     以后加新 Unit 页面，在这个文件的 `UNITS` 列表里加一条即可。
   - `.github/workflows/deploy-mandarin-portfolio.yml`（**新增**）——push 到 `main` 时
     自动跑 `build_site.py` 并部署到 GitHub Pages。**目前还没真正上线**：①这次的改动都在
     `claude/ai-native-chinese-curriculum-vlnr10` 分支，没合并到 main；②GitHub 仓库
     Settings → Pages 的 Source 需要教师手动选一次"GitHub Actions"（这一步 Claude 做不了）；
     ③**教师 2026-08-04 明确说先不公开，等她想清楚再开**，不要主动建议开启或去改这个决定。
   - **`generators/family_overview.py`（面向家长的独立渲染器）已于 2026-08-04 停用并从仓库删除**——不要重新创建这个文件。它当年 4 轮设计迭代的教训仍然记在 08-curriculum-intelligence.md 里。
6. **课堂 presentation 决定和 Content Layer 彻底解耦** — 教师原本以为课堂上播放的 slides 也会是这套系统生成的 HTML，讨论后确认这是个坏主意（现场需要秒改，HTML 生成流程做不到）。教师决定停用 SMART Notebook，改用 Google Slides 作为课堂工具，和这个 git 项目的更新节奏没有关系。为了把旧 SMART 内容迁过去，新增了 `import-pipeline/notebook_to_pptx.py`（Extractor 的一个具体实现，但走的是"直接产出 pptx"这条路，不经过 AI Classifier/Human Review 那条喂 Content Layer 的路）。已经用 Unit 1 Cycle 1 的 42 页 `.notebook` 文件验证过整个流程，教师确认横版布局/透明背景/楷体字体的效果可以接受。**2026-08-04 又处理了 Cycle 2-7**（教师上传了 5 个 + 中途追加 1 个 `.notebook` 文件：Cycle 2/24 页、Cycle 3/24 页、Cycle 4/45 页、Cycle 5/69 页、Cycle 6/18 页、Cycle 7/23 页，全部转换无报错，已通过 SendUserFile 发给教师），加上之前的 Cycle 1，Unit 1 全部 7 个 Cycle 的课堂 Slides 现在都已产出。字体决定已定案见下一段。**下一步**：等教师这一轮 review 反馈（横版布局/字体/图片清晰度是否都还满意）；如果教师手上还有其他 Unit 的 `.notebook` 文件，需要她上传到对话里才能处理（这个仓库里没有存任何原始 `.notebook`/`.docx` 文件，也不应该存——这些是几十 MB 的二进制文件，不适合进 git）。

   **Google Slides 里把中文字体调对的实际操作流程**（教师已经走通一遍，细节踩过的坑都在这）：
   1. 生成的 `.pptx` 上传到 Drive 后默认以"Office 兼容模式"打开（文件名旁边有黄色 `.PPTX` 标签），**这个模式下没有"扩展程序"菜单**，Apps Script 用不了——必须先 File > "Save as Google Slides" 存一份真正的 Google 原生格式，扩展程序菜单才会出现。
   2. pptx 里中文字体写的是 `"Kaiti SC"`（macOS 本地字体），Google Slides 跑在浏览器里读不到本地字体，会显示成别的字体——这不是 bug，是浏览器应用的天然限制。
   3. **Google Fonts 里没有真正的"华文楷体"/STKaiti**（那是苹果/微软的专有字体，不在开源的 Google Fonts 库里，Slides 的"更多字体"也不支持上传自定义字体文件）。目前用的是 `LXGW WenKai TC`——Google 官方描述它"带来楷体风格的韵味"，是 Google Fonts 里唯一定位为楷体风格的字体，但笔画细节和苹果系统楷体不完全一样。备选是 `Noto Serif SC`（宋体印刷风格，不是楷体，但清晰可靠）。还有几款书法体（Ma Shan Zheng / Zhi Mang Xing / Long Cang / Liu Jian Mao Cao）过于潦草，只适合一两个字的标题，不适合大段教学正文。**2026-08-04 教师已最终确定用 `LXGW WenKai TC`**——不用再讨论 `Noto Serif SC` 或重新调研字体选项，`apps-script-fix-cjk-font.gs` 第一行的字体名保持 `LXGW WenKai TC` 即可。
   4. 批量改字体（只改中文，英文/拼音保留原样）用的是 `import-pipeline/apps-script-fix-cjk-font.gs`——粘贴进 Slides 文件自己的 Apps Script 编辑器（必须从 Slides 里"扩展程序 > Apps Script"进入，不能是 script.google.com 单独建的空项目，否则 `SlidesApp.getActivePresentation()` 拿不到上下文），改第一行的字体名后保存运行。首次运行需要走一遍 OAuth 授权（选账号 > 高级 > 转到项目(不安全) > 允许），页面会提示"需要授权，请再试一次"，这是正常流程，再点一次 Run 就行，不是报错。

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
- 家长概览渲染器（`family_overview.py`）已经**删除**，不是"待改进"——教师 2026-08-04
  明确说单人维护两份渲染器工作量不现实，改成学生检索页面身兼两职。不要建议恢复、
  重建或"顺便"再造一个家长专属版本，除非教师自己重新提出
- Culture 板块的正文用英文，只有生词表和语法/句型列表可以留中文——这条规则已经落实到
  `student_reference.py` 读取的 Content Layer 文件里，以后往这个模块加新内容时要延续。
  **Teaching Flow 这条规则已经被 2026-08-04 的格式改动取代**：Cycle 现在只渲染一段
  英文 Overview 摘要 + 嵌入的 Slides，不再有逐日中文叙述需要顾虑双语问题；每个
  `cycle-N.md` 里那份"逐日细节"小节不会被渲染，中英文怎么写都不影响页面，不用再纠结
  这条豁免规则怎么套用到 Teaching Flow 上
- **2026-08-04 项目定位从"学生/家长检索工具"改成"教师个人 curriculum 归档 + 求职作品集"，
  已经定案，不要重新讨论"要不要转型"这个问题**——完整背景见上面"项目是什么"一节和
  08-curriculum-intelligence.md 同日期的记录。跟着这次转型定下的、同样不用重新讨论的：
  - GitHub Pages 部署代码已经搭好（`build_site.py` + `.github/workflows/deploy-mandarin-portfolio.yml`），
    但**教师明确说先不公开**，不要主动建议开启或催促上线，除非她自己重新提起
  - "Unit 1 免费、后面收费"的付费设想讨论后**搁置**，原因是可能涉及职务作品归属，
    教师需要先自己查雇佣合同——不要重新讨论"能不能做"，如果教师重新提起，直接从
    "先查合同"这个结论接着聊
  - Cycle 页面配色用教师指定的莫兰迪色板（`UNIT_HERO_COLORS` 数组），已经定案；
    她说了"更多细节以后再慢慢调整"，指的是微调，不是推翻整个方案重来
  - Cycle 的 Teaching Flow 板块改成"一段摘要 + 嵌入课堂 Slides"，不是"以后再改回逐日
    列表"——除非教师明确要求，不要主动建议恢复 Do-Now/Objective/Main Activities 格式
  - `09-student-work/` 模块的 `student_work_card()` **不要加"学生姓名"字段**——这是
    2026-08-04 刻意的防呆设计，不是疏漏
  - **2026-08-05**：既然页面不面向学生，`06-assessment/*.md` 里的 Diagnostic/Quiz/
    Summative 真实考题内容现在会直接渲染到页面上（`assessment_card()` 已改，见上面
    第 5 条）——不要再假设这些文件只是"内部存档，页面上看不到"，也不要主动把这条
    显示行为改回"See Schoology"，除非教师自己重新提出
- **往 `02-teaching/cycle-N.md` 或任何会被 `render_blocks()` 处理的正文加内容时，
  每个列表项（`- `开头）和每个引用块（`> `开头）的整句必须写在同一物理行，不要为了
  编辑器里好看手动换行折成两行**——`render_blocks()` 是按"每一行的行首标记"分组的，
  续行如果没有重复 `-`/`>` 前缀，会被当成独立段落，把一个列表项拆成"列表项 + 孤立
  悬空段落"两块，肉眼在源码里可能看不出问题，必须重新生成 HTML 并截图看才会发现。
  这个坑 2026-08-04 这次对话踩过两次（cycle-1.md 和 zhongqiujie-de-gushi.md 里都出现过）
- 站内交叉引用统一写 `[人话标题](../对应模块/文件名.md)`（比如 `[the Diagnostic
  Test](../06-assessment/diagnostic-test.md)`），不要把文件路径本身当链接文字——
  `student_reference.py` 的 `inline_md()` 会自动把这类链接换成页面内锚点（如果目标
  文件确实渲染成了一张卡片）或者退化成纯文字（如果目标没有渲染出来，比如
  05-resources 底下的文件目前完全不上这个页面），不需要手动判断该不该加链接
- 课堂上实际播放的 presentation 和这个 git 项目（Content Layer / Generation Layer）**故意解耦**，
  不要提议把它做成"从数据库生成的 HTML"——这条已经讨论过，会重新引入"现场没法秒改"的问题
- 生成的文件（.pptx 等）**没法通过 Google Drive API 直接上传**——试过，编码后的体积让单次
  工具调用不现实，哪怕文件本身只有一两百 KB。正确流程是生成后用 SendUserFile 直接发给教师，
  由她自己上传 Drive、用 "Open with Google Slides" 转换，不要重新尝试 API 直传
- pptx 里的中文字体统一用 `"Kaiti SC"`，教师已经确认接受"转到 Slides 后手动整体调一次字体"
  这个额外步骤，不需要为了找 Slides 能自动识别的字体名而改生成逻辑
- Google Fonts 里没有真正的"华文楷体"/STKaiti，别再建议教师去"更多字体"里搜这个名字——
  搜不到。**教师 2026-08-04 已最终定下用 `LXGW WenKai TC`**，不是 `Noto Serif SC`，
  别再重新讨论这两个选项，见"目前进度"第 6 条的完整记录
- 原始 `.notebook`/`.docx` 等源文件不进这个 git 仓库——都是几十 MB 的二进制文件，教师需要时
  会直接上传到对话里，处理完不必也不应该把原始文件存进仓库

## 我（未来的 Claude）应该怎么"更新记忆"

我没有跨对话的记忆。每次都要靠读这个仓库重新获得上下文。所以规则是：
1. **重大决策、设计教训 → 写进 `08-curriculum-intelligence.md`**（针对某个 Unit 的具体决策）
   或这个文件（针对整个项目的进度/状态）。
2. **每次做完一段有意义的工作，都要 commit + push**，不要攒着不提交——
   下一个对话（不管是不是我）只能看到已经 push 的内容。
3. **这份 `PROJECT_STATUS.md` 要随进度更新**，尤其是"目前进度"和"下一步"这两节，
   避免下次对话花时间重新梳理一遍现状。
