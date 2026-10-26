---
name: english-mindmap-setup
description: Set up or check the English mind-map plugin after installation. Use for verifying dependencies and references or helping a new user start; setup itself does not start a lesson or generate images.
---

# 中文首次使用引导

用中文完成安装检查。插件根目录为本文件的 parents[2]；主skill位于同级 `../xhs-english-mindmap-series/`。先读取插件根目录 INSTALL.zh-CN.md，再读取主skill MIGRATION.md。

1. 定位当前安装副本中的主skill，不依赖作者电脑绝对路径，不修改其他技能。
2. 检查Python >=3.10、Pillow及参考图读取能力。生图工具必须支持实际图片参考；缺失时说明可先规划内容，不能声称具备完整生图能力。不要求用户粘贴密码或密钥。
3. 在主skill目录运行 `python -X utf8 scripts/verify_bundle.py`。依赖缺失且用户要求完成初始化时，在用户工作目录建虚拟环境，按该skill requirements.txt 安装，避免全局环境改动。
4. 实际打开Key/Cup、Dog及家居篇适用的Window原图。文件检查通过不代表新主题视觉通过。
5. 说明支持导图、无提示练习、双语问答、英文稿和每题视频素材；不宣传发音评分或互动纠音。遵循主skill原有的内容确认、制作、连线与逐图验收流程。
6. 输出目录按用户工作区约定选择。用户尚未给主题时才询问；已给出的主题或确认不重复询问。

简明报告已验证项目、缺少能力和下一步。未经真实生成和检查，不称首次生图已通过。
