---
last_updated: 2026-08-04
branch: claude/ai-native-chinese-curriculum-vlnr10
---

# Project Status — 给下一次接手这个项目的 Claude 看

> 如果你是一个新对话里的 Claude，第一次看到这个项目：**先读这个文件**，
> 再按需读下面链接的文件，不要从零开始猜项目在做什么。这个仓库本身就是
> 唯一的记忆载体——没有别的地方存着之前对话的上下文。

## 项目是什么

把 Tian（Mandarin 老师）的 Middle School Mandarin 课程从 SMART Notebook 迁移到一套
Markdown+YAML 的 **AI Native Curriculum Database**，作为所有教学产出（学生检索页面、
Slides、Assessment 等）的唯一数据源。详见 [`blueprint-v1.0.md`](./blueprint-v1.0.md)。

## 目前进度（做到哪一步）

1. **Blueprint v1.0** — 完成。架构层设计：九条公理、四层模型、Department 级泛化。
2. **Pilot Unit** — 进行中。`mandarin-1.2/unit-01-a-day-in-my-life/` 已经有
   Cycle 1/2 教学内容、Diagnostic Test、Student Survey、生词表、Culture 模块
   （中秋节的故事 + 笔画书法）。**还缺**：Cycle 3-6、「我的一天太累了」和
   「中秋节的故事」的正文、Final Project 细节、笔画书法的真实 YouTube 视频链接、
   「我的一天太累了」生词表的英文释义（详见下面"下次对话，别再问一遍的事"）。
   **教师明确说她会在一个新对话里上传更多 Unit 1 材料**——接手的 Claude 应该按
   Blueprint 的 Import Pipeline（Extractor 抽取 → AI Classifier 归类 → Human Review）
   把新材料整理进对应模块的 Markdown，然后重新跑 `generators/student_reference.py`
   生成新版页面。整理新内容时要延续这次对话定下的规则（见下面"别再问一遍的事"
   和"关键设计决策"两节），不要每次都重新讨论一遍。
3. **存储载体已定案** — git 里的 Markdown + YAML，不用 Notion/Airtable/Sheets。
4. **Unit Template 结构（当前 7 个模块，随时可能因为新发现再调整，以
   `mandarin-1.2/unit-01-a-day-in-my-life/` 里实际的资料夹为准，不要相信这里的
   文字描述会一直准确）**：
   `01-overview / 02-teaching / 03-content / 04-culture / 05-resources / 06-assessment / 07-ai-workspace / 08-curriculum-intelligence`
5. **Generation Layer（渲染器）**：
   - `generators/student_reference.py` — 面向学生的"Unit 检索页面"，**已完成多轮教师反馈修订，2026-08-04 起同时作为发给家长的版本**。定位是纯静态检索/参考工具，不做设备同步、进度追踪、登录；**不是实时系统**，是"当前 Content Layer 数据的一次快照"，教师上完新课后要先把内容整理进 Markdown，再重新跑脚本才会更新——这一点已经跟教师明确同步过。内容包括：故事/文化正文（数据里有多少显示多少，缺失的标注"内容整理中"）、页面全程可搜索（sticky 导航条里也有一份同步的搜索框）。测验类 Assessment 不暴露考题内容，Performance Task/Project 类完整显示任务说明。顶部的整表生词表已删除（和 Content/Culture 卡片重复）——生词现在只在各自卡片里，但仍可搜索。**Teaching Flow 板块已从"逐日期+活动"降级为"Cycle 级别的大致顺序"**（不再展示具体日期/星期），因为教师明确说逐日同步维护成本不现实——这是本项目目前为止最重要的一条"渲染器颗粒度要服务于维护成本"的经验，详见 [08-curriculum-intelligence.md](./mandarin-1.2/unit-01-a-day-in-my-life/08-curriculum-intelligence.md) 最新几条记录。Quizlet/YouTube 等链接目前渲染不出来——不是渲染器的问题，是 Content Layer 里还没有真实 URL。**Culture 与 Teaching Flow 板块的正文（除生词表和语法/句型列表外）已全部译成英文**——学生是非母语者，纯中文说明用不上，这条规则以后每次往这两个板块加新内容时都要遵守。Culture 板块的 Overview 正文里也不应该再出现具体日期（教师 2026-08-04 反馈发现两处漏网的日期，已清掉）。**站内交叉引用链接（`[...](../06-assessment/xxx.md)` 这种指向仓库里另一个 Markdown 文件的链接）已经改成指向同页面内对应卡片的锚点**（每张卡片现在都有 `id="item-<文件名去掉扩展名>"`，`inline_md()` 里的链接改写逻辑会自动把认得的 `.md` 链接换成 `#item-...`，认不出来的直接退化成纯文字，不留死链接）——原来这类链接会原样渲染成指向仓库里 `.md` 源文件的相对路径，页面本身是单个静态 HTML，不管在哪里打开都点不开，这是教师 2026-08-04 反馈发现的。以后往 Content Layer 里写"见 XXX.md"这种交叉引用时，不用改渲染器逻辑，脚本会自动处理。
   - **`generators/family_overview.py`（面向家长的独立渲染器）已于 2026-08-04 停用并从仓库删除**——教师明确说这项工程量太大，没法为每个 Unit 同时维护两份渲染器、过两轮教师 review，决定只用学生检索页面这一份，同时发给学生和家长看。**不要重新创建这个文件或建议"要不要恢复家长版"**——这是教师明确做过的取舍，原因是工作量，不是渲染效果问题。它当年 4 轮设计迭代的教训（配色、日期颗粒度、双语原则等）仍然记在 08-curriculum-intelligence.md 里，不因为文件删除而失效，往学生页面加东西时仍可参考。
   - **下一步**：教师会在新对话里上传更多 Unit 1 材料——把新材料整理进 Content Layer 后
     重新跑这个脚本、重新发页面即可，渲染器本身（英文化、无日期、锚点链接这几条规则）
     暂时不需要再改，除非教师明确提出新的板块级别反馈。
6. **课堂 presentation 决定和 Content Layer 彻底解耦** — 教师原本以为课堂上播放的 slides 也会是这套系统生成的 HTML，讨论后确认这是个坏主意（现场需要秒改，HTML 生成流程做不到）。教师决定停用 SMART Notebook，改用 Google Slides 作为课堂工具，和这个 git 项目的更新节奏没有关系。为了把旧 SMART 内容迁过去，新增了 `import-pipeline/notebook_to_pptx.py`（Extractor 的一个具体实现，但走的是"直接产出 pptx"这条路，不经过 AI Classifier/Human Review 那条喂 Content Layer 的路）。已经用 Unit 1 Cycle 1 的 42 页 `.notebook` 文件验证过整个流程，教师确认横版布局/透明背景/楷体字体的效果可以接受。**下一步**：如果教师认可这份完整版，继续处理 Cycle 2 及后续；教师手上其他 Unit/Cycle 的 `.notebook` 文件需要她上传到对话里才能处理（这个仓库里没有存任何原始 `.notebook`/`.docx` 文件，也不应该存——这些是几十 MB 的二进制文件，不适合进 git）。

   **Google Slides 里把中文字体调对的实际操作流程**（教师已经走通一遍，细节踩过的坑都在这）：
   1. 生成的 `.pptx` 上传到 Drive 后默认以"Office 兼容模式"打开（文件名旁边有黄色 `.PPTX` 标签），**这个模式下没有"扩展程序"菜单**，Apps Script 用不了——必须先 File > "Save as Google Slides" 存一份真正的 Google 原生格式，扩展程序菜单才会出现。
   2. pptx 里中文字体写的是 `"Kaiti SC"`（macOS 本地字体），Google Slides 跑在浏览器里读不到本地字体，会显示成别的字体——这不是 bug，是浏览器应用的天然限制。
   3. **Google Fonts 里没有真正的"华文楷体"/STKaiti**（那是苹果/微软的专有字体，不在开源的 Google Fonts 库里，Slides 的"更多字体"也不支持上传自定义字体文件）。目前用的是 `LXGW WenKai TC`——Google 官方描述它"带来楷体风格的韵味"，是 Google Fonts 里唯一定位为楷体风格的字体，但笔画细节和苹果系统楷体不完全一样。备选是 `Noto Serif SC`（宋体印刷风格，不是楷体，但清晰可靠）。还有几款书法体（Ma Shan Zheng / Zhi Mang Xing / Long Cang / Liu Jian Mao Cao）过于潦草，只适合一两个字的标题，不适合大段教学正文。**教师目前还没最终决定用 LXGW WenKai TC 还是 Noto Serif SC**，下次对话如果她提起，从这里接着聊，不用重新调研一遍字体选项。
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
- Culture / Teaching Flow 板块的正文用英文，只有生词表和语法/句型列表可以留中文——
  这条规则已经落实到 `student_reference.py` 读取的 Content Layer 文件里，以后往这两个
  模块加新内容（新 Cycle、新 Culture 条目）时要延续，不要又写一长串中文叙述回去。
  具体到"生词/语法"的豁免范围：短词/短语（2-4 字，如"这个/那个"）可以留中文，
  完整句型模板（带"___"填空、带句号的整句）一律不要嵌进 Teaching Flow 叙述里——
  写英文描述就够了，句型本身的中文原文属于该 Cycle 独立的"涉及的核心词汇/句型"
  小节，不需要在叙述句子里重复一遍
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
  搜不到。能用的楷体风格替代是 `LXGW WenKai TC`，或者放弃楷体风格改用 `Noto Serif SC`，
  见"目前进度"第 6 条的完整记录
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
