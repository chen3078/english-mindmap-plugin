# 中文安装与首次使用指南

## 1. 准备环境

- 使用支持插件的Codex桌面版／CLI。旧版本没有插件命令时先更新客户端。
- 完整生图需要图片生成工具，以及把参考原图实际传给工具的能力。
- 连线、排版及检查需要Python 3.10或以上和Pillow。
- 免费领取的是插件与说明；账号权限和生图额度由所用服务提供。无需向作者提供密码或密钥。

## 2. 在线安装，推荐

在安装了Codex的终端逐条执行：

```text
codex plugin marketplace add chen3078/english-mindmap-plugin
codex plugin add english-mindmap@english-mindmap
```

添加来源和安装插件是两步。成功后新建聊天；看不到插件时重启桌面应用，在插件选择器查找“英语口语思维导图”。CLI用户可用 `codex plugin list --marketplace english-mindmap --json` 查看状态。

也可以把下面这句话发给Codex：

> 请从 https://github.com/chen3078/english-mindmap-plugin 安装英语口语思维导图插件，先读取中文安装指南并检查依赖。安装后帮我执行首次使用检查。

## 3. 依赖与初始化

选择首次使用引导 `english-mindmap-setup`。它会定位当前安装副本、检查Python/Pillow及参考图，不会自动生成图片。

缺少Pillow时，让Codex在你的工作目录建虚拟环境，按安装副本的 `skills/xhs-english-mindmap-series/requirements.txt` 安装。不要把作者电脑路径照搬到你的机器。

开发者也可在下载的仓库根目录执行：

```text
python -m venv .venv
```

Windows：

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\skills\xhs-english-mindmap-series\requirements.txt
.\.venv\Scripts\python.exe -X utf8 .\skills\xhs-english-mindmap-series\scripts\verify_bundle.py
```

macOS/Linux：

```sh
.venv/bin/python -m pip install -r skills/xhs-english-mindmap-series/requirements.txt
.venv/bin/python -X utf8 skills/xhs-english-mindmap-series/scripts/verify_bundle.py
```

实际生产时让Codex使用已配置依赖的解释器。完整性检查通过后，仍需确认实际生图工具和参考图输入能力。

## 4. 第一个主题

新建聊天，选择“英语口语思维导图”，发送：

> 主题：镜子。面向成人英语初学者，家居篇手绘风格。先按内容规划标准给我完整双语问答，包含材料、部件及制作过程。等我确认后，再制作完整版导图、无提示练习图和问答页。按模板逐图检查，不符合就修改。

亲子用途可把受众改为children，并说明孩子年龄或现有程度。只做导图或视频素材时直接说明；输出格式可缩减，主题的重要知识不能因页数擅自删除。

自己练：先看导图，再读懂问答，最后看无提示图尝试回答。亲子练：家长选一题，孩子看图作答，按能力从词语逐步练到句子。材料需要配合实际开口使用。

## 5. 备用ZIP安装

从 Releases 下载完整插件ZIP并解压到准备保留的位置。目录应同时包含 `plugin.json`、`.codex-plugin`、`.agents/plugins/marketplace.json` 和 `skills`，不要只复制SKILL.md。

```text
codex plugin marketplace add <解压后的插件根目录>
codex plugin add english-mindmap@english-mindmap
```

含空格的路径加引号。本地文件安装不代表生图服务可以离线运行。

## 6. 更新和常见问题

刷新插件来源后更新插件，再重新开启聊天：

```text
codex plugin marketplace upgrade english-mindmap
codex plugin add english-mindmap@english-mindmap
```

- 找不到来源：检查命令、Git和网络；可用本地ZIP安装。
- 同名技能重复：确认当前使用插件内版本，不让助手擅自删除旧作品。
- 图里没线／连线乱：成品不通过；要求按连线标准绘制、保存绑定并重新验收。
- 没生成图片：检查实际生图及图片参考输入能力。
- 网页聊天不能运行本地脚本：先在具备本地工具的Codex环境使用。

## 7. 验证范围

发布包验证完整性、插件发现和安装、30项主skill程序回归及包装检查。机器可检查记录、计划和像素绑定，不能独立保证所有事实和美观。另一位使用者账号下的新主题真实生图仍需按样张与逐图检查流程执行。
