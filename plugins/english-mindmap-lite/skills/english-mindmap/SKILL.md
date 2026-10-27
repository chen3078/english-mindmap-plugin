---
name: english-mindmap
description: "Generate Key/Cup-style English learning images for a beginner topic: a labeled mind map, a matching picture-only practice map, and complete bilingual Q&A image pages. Use for the English-mindmap three-image edition; excludes video stills, standalone English transcripts and social captions."
metadata:
  version: "2026.10.27.1"
---

# English-mindmap · 三类图片精简版

本版基于 xhs-english-mindmap-series 2026.10.26.3，保留内容规划、认可画风、参考职责、连线最终像素校验及逐页视觉验收。默认只制作以下三类 **1086 × 1448、3:4 PNG**：

1. **思维导图完整版** `01-cover.png`：英文主题、短分支标题、英文关键词、对应插画及小号品牌署名。
2. **思维导图练习版** `02-picture-practice.png`：与完整版相同主题、分组顺序和图片关系，保留有效连线与动作箭头；去掉所有文字、数字、品牌及空编号圈。
3. **中英双语问答图片** `03-qa-01-04.png` 等：每题包含英文问题、英文回答、中文问题、中文回答及相应插画。按实际文字长度分页，保持题目完整有序；三类不等于三张图。

不生成逐题视频图片、视频、纯英文问答文本、小红书文案、知识总结页或额外封面。用户只要求其中一类时仅做指定子集；不要为满足检查擅自扩大范围。其他任务应交给用户另行选择的流程。

## 内容与范围

- 接受主题、类别、儿童或成人初学者受众以及用户事实；沿用已有确认，不重复询问已知信息。日常词保持日常范围，不把 cat 扩为狮虎。
- 品牌署名沿用 `新陈代谢（英语版）`，放在完整版及双语页，练习版无署名。
- 先读 [内容规划](references/content-planning.md)、[类别框架](references/content-frameworks.md)、[内容清单结构](references/manifest-schema.md)。按实际主题建立完整知识路径，通常6—9个分支，题数由内容决定，不能机械复制其他主题。
- 新主题清单含 `topic_en`、`topic_zh`、`category`、`audience`、`brand`、`visual_family`、`content_plan`、`groups`、`qa_items`。`visual_family` 明确为 `general` 或 `home`。`groups` 是分支，`qa_items` 是问题；一分支可以多题，两者编号独立。
- 第一分支标题严格为 `What`，位置分支为 `Where`，植物生长需要分支为 `Needs`；其余用简短自然的栏目名。完整自然问句只放问答中。历史参考控制视觉，不是新主题用词模板。
- 按类别覆盖来源、外观、材料/部件、种类、用途、取得/照护、过程及有价值的扩展，并写明不适用或省略理由。完整人工制品需独立制作题；材料、使用或清洁不能替代制作。食物遵循 Milk 的问题规划逻辑并适配实际食物。动物不强制声音题。数字、寿命、技术过程等事实需可靠来源。
- 先展示完整双语问答进行内容确认，已有明确批准直接沿用；冻结清单后再生图。运行 `python -X utf8 scripts/check_manifest.py <主题目录>/manifest.json`，机器结构通过后仍需人工审阅语义。

## 视觉参考与生产

先读 [生产流程](references/production-workflow.md)、[视觉系统](references/visual-system.md)、[完整版艺术指导](references/cover-art-direction.md)、[参考职责](references/reference-roles.md)。家居篇加读 [家居标准](references/home-series.md)，保留 Window 的柔软舒适处理。

- 完整版：Key/Cup 控制手绘线条与水彩铅笔纸感；指定 Cat/Dog 控制整页节奏；Carrot 控制紧凑左侧主体比例。普通8分支主体约占页高40—45%、页宽左侧约三分之一，右侧分点保持可读尺寸。家居篇加用认可 Window 完整版。
- 练习版：参考 Dog/Lion 成品及 Carrot 比例；家居篇再加 Window 练习版。必须由本主题已通过完整版的视觉方案派生，不能另做无关拼贴。
- 问答页：Dog 两张认可整页是主要排版标准；Rabbit 两张三题页为补充；家居篇再加 Window 两张双语页。实际打开原图并按职责传入，不能只在提示词中写路径。所有参考只传递指定视觉职责，不能把原动物、图案和事实带到新主题。
- 每次实际生图前运行参考计划预检；调用后按 [生图证据](references/generation-evidence.md) 记录真实提示词、实际参考输入和返回图片。未知工具信息留空，不补造旧调用。后续问答页实际输入本主题已通过样张，统一主体身份和制作方法。

## 三类图片的执行要求

**完整版与练习版：** 按 [连线规则](references/branch-topology.md) 先准备无珊瑚色分支线的内部底稿，再用 `scripts/render_connectors.py` 绘制每组一条受控曲线并保存底稿/计划/成品绑定。完整版终点对应标题/编号圈；练习版对应图片群，不能停在空白处。每张分别检查实际像素、交叉、拥挤、绕行、穿字、漏线、多线和整齐度。几何通过不等于美观通过。无连线底稿只是内部素材，不能当练习成品交付。

**双语问答：** 先读 [问答排版](references/qa-layout.md)，在冻结内容时规划全部页码。常见6—9题用2—3页，每页约3—4题；文字长则合理拆分，不能缩成难读小字。先做一张包含真实四项文字的完整样张，在300—400px等宽整页对照下检查 Dog/Window 家族效果，通过后继续后续页。工具支持参考图和双语文字时优先完整页面生成；出现难解决文字问题或用户要可编辑文本时使用独立插画加精确排字，仍须通过同一整页样张标准。

无文字要求仅用于导图练习版。绝不能向会自动展示结果的生图工具请求整页空白问答卡片底图，再把补字当作未来步骤。每张问答成品都必须实际显示该页每题的四项原文。有多个部件的答案需分别清楚表现全部部件。

## 检查与交付

每张新图或修改图按 [逐图检查](references/image-review.md) 和 [质量门槛](references/quality-gates.md) 打开真实全尺寸PNG、手机宽度整页对照并记录具体观察。保留内容检查、结构通过、视觉通过与用户批准的区别；失败先修正，不能编造观察让脚本通过。

工作目录内部保存 manifest、真实生产记录、连线计划和验收图库；这些是制作依据，不是额外学习成品。最后重建图库/绑定，再运行：

```text
python -X utf8 scripts/build_review_gallery.py <主题目录>
python -X utf8 scripts/check_release.py <主题目录>
python -X utf8 scripts/package_images.py <主题目录> <主题图片.zip>
```

`check_release.py` 的默认 `full` 只表示 `cover,practice,qa`；子集可写 `--scope cover`、`--scope practice`、`--scope qa`。缺图、问题范围不完整、文字关联错误、旧验收、无效证据、连线不合格或图库断链均不能发布。脚本不能自动证明文字像素准确或审美达标，必须人工核对。

`package_images.py` 通过完整检查后，仅将完整版、练习版与全部问答PNG打入主题图片包。不要把 manifest、提示词、检查图库、参考图、底稿或记录当作第四类成品交付。只链接正式图片或纯图片包，按完整版、练习版、问答页顺序交付。

迁移安装与本版验证范围见 [MIGRATION.md](MIGRATION.md)。字体许可证保存在 `assets/fonts/`。
