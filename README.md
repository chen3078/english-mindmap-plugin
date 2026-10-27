# 英语口语思维导图 · Codex 插件

**现有两个独立版本，可并存：** 原完整版 `english-mindmap`；新增 [三类图片精简版 `english-mindmap-lite`](plugins/english-mindmap-lite/README.md)，只生成完整版导图、无字练习图和中英双语问答图片。精简版基于 English-mindmap-2026.10.27，原完整版代码和参考图保持不变。

安装精简版：

```text
codex plugin marketplace add chen3078/english-mindmap-plugin
codex plugin add english-mindmap-lite@english-mindmap
```

已经添加过来源时先执行 `codex plugin marketplace upgrade english-mindmap`。迁移到其他电脑请看[精简版中文教程](plugins/english-mindmap-lite/INSTALL.zh-CN.md)，下载[精简版插件迁移包](https://github.com/chen3078/english-mindmap-plugin/releases/tag/lite-v1.0.0)。下文为原完整版说明。

选一个生活主题，制作配套的**完整思维导图、无提示练习图、双语问答**：用图片找到表达角度，理解完整回答，再看图尝试自己说。适合成人英语初学者和想陪孩子练英语的家长。

插件 **v1.0.0**，内置 skill **v2026.10.26.3**。免费领取插件；Codex及生图服务的账号权限、额度和费用按所用服务规则。

[中文安装指南](INSTALL.zh-CN.md) · [下载原完整版插件包](https://github.com/chen3078/english-mindmap-plugin/releases/tag/v1.0.0)

下图是包内已认可的家居篇风格参考，供了解整页效果；新主题会按自身内容重新规划。

![已认可的家居篇思维导图参考](skills/xhs-english-mindmap-series/assets/approved-window/cover.png)

## 安装

需要支持插件的Codex，以及实际图片生成、图片参考输入和本地Python运行能力。[查看中文安装指南](INSTALL.zh-CN.md)。

```text
codex plugin marketplace add chen3078/english-mindmap-plugin
codex plugin add english-mindmap@english-mindmap
```

安装后新建聊天，在插件选择器中选择“英语口语思维导图”，运行首次使用引导，或输入：

> 主题：镜子。先按照skill规划完整双语问答供我确认，再制作配套图片。

从确认内容、生成完整样张、检查修正到制作其余页面逐步进行。脚本通过不等于图像美观通过。

## 一套主题包含什么

| 材料 | 怎样使用 |
| --- | --- |
| 完整导图 | 找到外观、材质、用途、制作等适合该主题的表达角度 |
| 无提示练习图 | 看图片回忆表达，卡住时回问答页核对 |
| 双语问答 | 理解并尝试完整回答，再换成自己的真实情况 |
| 英文问答稿 | 阅读练习，或作为制作配音的文字素材 |
| 每题视频静态图 | 剪视频时添加自己的字幕与声音 |

也可只请求某种材料。家居物品沿用柔软、舒适、可爱的手绘处理。本插件提供学习材料制作流程，不提供独立的发音评分服务，也不直接输出剪辑完成的视频。

## 质量标准

- 18张认可参考图，分别承担画风、构图、主体比例、家居处理和视频构图职责。
- 新主题考虑来源、特征、材料／部件、用途、过程等；完整人工制品需要独立制作题。
- 导图要有真实连线，检查绘制记录、最终像素与几何；整齐美观另按模板逐图验收。
- 先完成完整样张，再制作其余页面；逐页核对文字、插画和布局。

这些标准和程序检查降低遗漏风险，不保证一次生成成功或学习进度。[完整skill说明](skills/xhs-english-mindmap-series/SKILL.md)。

## 分享给朋友

发送仓库地址和[中文安装指南](INSTALL.zh-CN.md)。备用插件ZIP在 Releases；下载后按指南添加本地插件来源。仓库分发不等于已上架官方公共插件目录。

## 验证

```text
python scripts/check_plugin.py
python -X utf8 skills/xhs-english-mindmap-series/scripts/test_regressions.py
```

部署方式依据[官方插件说明](https://developers.openai.com/plugins/build/plugins)。字体许可保存在skill的 assets/fonts 中；本包没有额外授予参考图内第三方角色或商标的权利。
