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
   - `generators/student_reference.py` — 面向学生的"Unit 检索页面"，**已完成两轮教师反馈修订**。定位是纯静态检索/参考工具，不做设备同步、进度追踪、登录；**不是实时系统**，是"当前 Content Layer 数据的一次快照"，教师上完新课后要先把内容整理进 Markdown，再重新跑脚本才会更新——这一点已经跟教师明确同步过。比家长版丰富：故事/文化正文（数据里有多少显示多少，缺失的标注"内容整理中"）、页面全程可搜索（sticky 导航条里也有一份同步的搜索框）。测验类 Assessment 不暴露考题内容，Performance Task/Project 类完整显示任务说明。顶部的整表生词表已删除（和 Content/Culture 卡片重复）——生词现在只在各自卡片里，但仍可搜索。配色用暖棕色（`--bar: #8A5A3B`）区别于家长版的蓝绿色。**Teaching Flow 板块已从"逐日期+活动"降级为"Cycle 级别的大致顺序"**（不再展示具体日期/星期），因为教师明确说逐日同步维护成本不现实——这是本项目目前为止最重要的一条"渲染器颗粒度要服务于维护成本"的经验，详见 [08-curriculum-intelligence.md](./mandarin-1.2/unit-01-a-day-in-my-life/08-curriculum-intelligence.md) 最新几条记录。Quizlet/YouTube 等链接目前渲染不出来——不是渲染器的问题，是 Content Layer 里还没有真实 URL。
   - **2026-08-04 更新**：核对过 `family_overview.py` 的源码——它压根不读 `02-teaching/`
     目录，从没展示过逐日期的 Teaching Flow，所以不存在"同样的维护成本问题"，这一条
     可以不用再回头确认了。已重新跑了两个渲染器（数据没变化，输出内容和上一版一致），
     把最新的 `student_reference.html`（Teaching Flow 已是 Cycle 级别颗粒度）和
     `family_overview.html` 发给教师看，等她确认 Teaching Flow 这版颗粒度是否满意。
   - **下一步**：等教师对这版学生检索页面的反馈；没有新反馈之前不用再改这两个渲染器。
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
- 家长页面的字体/配色/翻译：已经定稿（见 `generators/family_overview.py` 的
  docstring 和历史 commit message），除非教师主动要求再改，不要自己重新设计一遍
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
