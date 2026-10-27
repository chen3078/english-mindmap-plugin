---
name: english-mindmap-lite-setup
description: Set up or check the English mind-map three-image plugin after installation or migration. Locate its actual installed copy, check dependencies and reference images, and help a new user start; setup itself does not generate images.
---

# 中文首次使用与迁移引导

本文件的 `parents[2]` 是插件根目录；主skill位于同级 `../english-mindmap/`。先读取根目录 `INSTALL.zh-CN.md`，再读主skill的 `MIGRATION.md`。本插件标识是 `english-mindmap-lite`，主skill名为 `english-mindmap`，不要误用原完整版的 `xhs-english-mindmap-series`。

1. 从当前技能实际位置定位安装副本，读取插件和skill版本。不要依赖作者路径、原聊天、另一版本或系统已有参考图。
2. 检查Python与Pillow，推荐Python3.11和包内requirements。需要准备依赖且用户已要求初始化时，在其工作目录建立虚拟环境，安装主skill的requirements；不要更改全局环境或写入插件缓存。后续脚本使用同一解释器。
3. 运行根目录 `scripts/check_plugin.py`，检查两个插件manifest、来源、版本、主skill清单哈希、16张PNG和本地依赖。失败就指出缺失项并修复；不修改清单以掩盖丢文件。
4. 实际打开包内Key/Cup、Dog原图；当前是家居主题时加看Window。脚本可解码不代表已经做视觉查看。
5. 根据当前聊天实际工具检查生图、图片编辑和实际图片参考输入能力。缺失时说明当前只能规划内容，不能声称可完整生成，不要求粘贴账号秘密，也不临时改用无关绘图库替代。Python、插件和图像工具分别报告，避免把安装成功当作生图成功。
6. 说明默认成品只有完整版、无字练习版和完整中英双语问答图片，均1086×1448；三类不等于三张。原版质量标准保留，先确认内容再制图，继承本聊天已有确认，不重复询问。
7. 若两版并存，后续本次任务明确读取本插件内 `english-mindmap/SKILL.md`。用户只要求初始化时完成检查后结束；已给出主题时继续该主题的内容规划，不另问主题。只有用户授权制作才调用生图。

简明报告已通过、缺少的能力与具体下一步。新使用者电脑/账号没有实际生成过主题时，标为尚待首次生图验收。
