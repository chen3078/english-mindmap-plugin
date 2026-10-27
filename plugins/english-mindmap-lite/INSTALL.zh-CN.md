# English-mindmap 三类图片版｜中文迁移与使用教程

适用版本：独立插件 `english-mindmap-lite` v1.0.0，内置 skill `english-mindmap` 2026.10.27.1。适用对象：拿到仓库链接或迁移ZIP、没有原聊天背景的新使用者。

## 一、迁移的是什么

迁移的是继续制作新主题的能力，不只是警察等主题的现成图片。本版与原完整版插件独立安装，可以并存。

| 项目 | 本版规则 |
| --- | --- |
| 学习成品 | 完整版导图、无字练习图、中英双语问答图片 |
| 尺寸 | 每张1086×1448，3:4 PNG |
| 问答 | 每题都有英文问题、英文回答、中文问题、中文回答；按文字长度分页 |
| 画风 | 沿用Key/Cup手绘和适用的Dog、Carrot、Window等参考职责 |
| 质量 | 完整内容规划、参考图实际输入、受控连线、样张与逐页视觉检查 |
| 移除内容 | 视频静态图、独立英文稿、社交文案等额外学习成品 |

三类内容不等于三张图片。例如9组问答分3页时，一套通常是2张导图加3张问答，共5张。

## 二、先准备使用环境

1. 使用支持插件与本地工具的Codex桌面环境；终端需要能运行 `codex plugin --help`。没有该命令时先更新或安装支持插件的客户端/CLI。不要假定普通网页上传ZIP就完成了插件安装。
2. 当前账号与聊天必须有**真实图片生成、图片编辑、实际图片参考输入**能力；插件不会自带或解锁生图服务。仅能输出文字的模型不足以完成全部图片。
3. 推荐Python **3.11**，并安装包内固定依赖 `Pillow==10.1.0`。主skill要求Python≥3.10；为减少旧版Pillow在较新Python上的安装兼容问题，首次迁移优先用3.11。
4. 网络用于获取依赖和生图。ZIP可以在本地解压、安装，生图服务仍需要网络和相应账号权限。
5. 新电脑只用自己的账号。不要拷贝作者的登录状态、密钥、浏览器资料或整份Codex配置。

## 三、方法A：从GitHub安装（推荐）

在能运行Codex的终端逐条执行：

```text
codex plugin marketplace add chen3078/english-mindmap-plugin
codex plugin add english-mindmap-lite@english-mindmap
```

如果原完整版已装过，先刷新来源，再安装精简版：

```text
codex plugin marketplace upgrade english-mindmap
codex plugin add english-mindmap-lite@english-mindmap
```

两者名称不同：`english-mindmap@english-mindmap` 是原完整版，`english-mindmap-lite@english-mindmap` 才是本次精简版。不要因为看到相同的“思维导图”字样就混用。

安装后重启应用、新建聊天，在插件选择器里选择“英语口语思维导图·三类图片版”。首次使用先运行它的设置引导。

也可以将这句话连同仓库地址发给目标电脑的Codex：

> 请从 https://github.com/chen3078/english-mindmap-plugin 安装 english-mindmap-lite 三类图片版，保留已有完整版。读取新版的 INSTALL.zh-CN.md，运行 english-mindmap-lite-setup，检查本机Python、Pillow、完整参考图及实际生图能力。不要复制作者路径，不要先生成图片。

## 四、方法B：用ZIP迁移到另一台电脑

从 [lite-v1.0.0发布页](https://github.com/chen3078/english-mindmap-plugin/releases/tag/lite-v1.0.0) 下载 **English-mindmap-2026.10.27-plugin-portable.zip**。`English-mindmap-2026.10.27.zip` 是原始skill包，不是带安装外壳的插件包；初次迁移请选择带 `plugin-portable` 的文件。

将插件ZIP整个解压到准备长期保留的位置。打开解压后的 `english-mindmap-lite` 文件夹，应同时看到：

```text
english-mindmap-lite/
├── plugin.json
├── .codex-plugin/plugin.json
├── .agents/plugins/marketplace.json
├── INSTALL.zh-CN.md
├── scripts/
└── skills/
    ├── english-mindmap/SKILL.md
    └── english-mindmap-lite-setup/SKILL.md
```

隐藏目录也必须保留。不要只复制SKILL.md、参考缩略图或教程。下载和解压完毕后，可对照发布页 `SHA256SUMS.txt` 检查文件；Windows执行 `Get-FileHash -Algorithm SHA256 '你的ZIP路径'`，macOS执行 `shasum -a 256 '你的ZIP路径'`。

终端中执行下面两步，第一行路径替换成实际解压根目录（包含plugin.json的目录），有空格时保留引号：

```text
codex plugin marketplace add "实际解压目录/english-mindmap-lite"
codex plugin add english-mindmap-lite@english-mindmap-lite-local
```

本地包来源名是 `english-mindmap-lite-local`，GitHub来源名是 `english-mindmap`。两种安装方法任选一种，避免同一精简版从两个来源重复启用。原完整版可以继续保留。

## 五、首次初始化：先检查，再制作

选择本插件的首次使用引导，或发送：

> 使用 $english-mindmap-lite-setup 检查当前安装副本；为我的工作目录准备Python虚拟环境，核验16张参考图与字体，并实际打开相关参考图。分别报告插件安装、本地脚本、参考图和图片生成工具是否可用。先不生成新主题。

引导会定位**当前安装副本**，不依赖作者的D盘路径。依赖安装放在用户工作目录的虚拟环境中，避免改动系统Python。安装前按宿主权限规则执行；不会索取密码或密钥。

也可手动初始化。先在终端进入解压后的插件根目录。Windows执行（`python`不是3.11时，改用 `py -3.11`）：

```text
python -m venv .venv
```

Windows继续：

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\skills\english-mindmap\requirements.txt
.\.venv\Scripts\python.exe -X utf8 .\scripts\check_plugin.py
```

macOS/Linux（先确认Python3.11可用）：

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r skills/english-mindmap/requirements.txt
.venv/bin/python -X utf8 scripts/check_plugin.py
```

将这个虚拟环境解释器告诉Codex，后续生成和检查使用它。手工创建环境可在解压目录；如果是在插件安装缓存中操作，改在自己的工作目录建虚拟环境，主skill路径使用当前安装副本的绝对路径。

验证通过应看到主skill `BUNDLE PASS` 和插件 `LITE PLUGIN PASS`。这证明文件与脚本检查通过，实际生图权限仍由首次引导单独核实。不要用Python绘图或图标拼贴悄悄替代本系列的真实生图流程。

## 六、生成第一个主题

新建聊天，只选择三类图片版，发送：

> 使用三类图片版插件的 $english-mindmap。主题：警察，类别：职业篇，受众：英语初学者。请先规划适合该主题的完整中英双语问答供我确认，再生成完整版导图、无字练习图和全部双语问答图片。画风、参考图、连线和验收要求全部沿用本版标准。

需要成人自练可改为“成人英语初学者”；亲子练习可提供孩子的年龄和水平。主题换成面包、番茄、海豚、镜子等即可，内容按主题规划，不机械复制警察的9个分支。

看到完整问答后，确认或一次性指出需要修改的内容。确认后发送：

> 内容确认，请继续生成全部图片，不要停在文案。先完成样张并按参考检查，通过后制作其余页面。最后按完整版、练习版、双语问答顺序展示成品，并给我纯图片ZIP。

成品自己也检查这几项：

- 完整版：英文主题、短分支标题和对应图片清楚，连线每组一条、无漏线、交叉和穿字。
- 练习版：与完整版对应，保留连线和动作关系，不残留文字、数字、署名或空编号圈。
- 问答页：每题四项双语文字齐全，顺序连续，无漏题、错译、错图和裁字；手机宽度也可读。
- 全套：3:4尺寸一致，人物/物品与画风连续。学习成品ZIP只有正式PNG；制作记录留在工作目录中供后续修改。

使用方式：先看完整版梳理表达角度，再读问答理解句子，最后看练习版口头复述。卡住时返回问答，不必一次背完全部内容。

## 七、更新、并存与常见问题

| 现象 | 处理方法 |
| --- | --- |
| 找不到精简版 | 刷新GitHub来源，确认选择的是 `english-mindmap-lite`，重启应用并新建聊天 |
| 旧版也在，结果多了英文稿/视频图 | 本次只选择精简版，并明确使用插件内 `english-mindmap`，不要让两版同时接管当前任务 |
| 安装了但没出图 | 先完成问答确认；再核实当前聊天确有生图和参考图输入工具；缺工具时不得称图片已完成 |
| `codex` 命令不存在 | 使用支持插件的客户端/CLI；让目标电脑Codex协助定位本机CLI，不能照抄作者安装路径 |
| 缺Pillow/安装编译失败 | 用Python3.11新建虚拟环境，再装包内requirements，不擅自改成未知依赖版本 |
| 找不到字体或参考图 | 重新下载并完整解压，运行check_plugin，不能只补一张缩略图后宣称迁移完成 |
| 图片少线、乱码或文字被挡 | 该图未通过；要求按对应标准修正并重新验收，不能只修改记录中的状态 |
| 本地目录移动后不能更新 | 重新添加移动后的本地来源，再安装；不要手改缓存内部路径 |
| 要移除精简版 | 在线安装用 `codex plugin remove english-mindmap-lite@english-mindmap`；本地安装将来源名改为 `english-mindmap-lite-local`。不影响原版和学习作品 |

在线更新先刷新来源，再安装新版并重启聊天；本地ZIP更新先按新版本说明替换迁移目录、核验并重新安装。不要覆盖自己的主题作品。

## 八、迁移验收与边界

把下面清单交给接收者逐项确认：插件可发现并安装；引导定位了本机副本；依赖与包检查通过；16张原始参考可打开；当前聊天具备真实生图及图片参考能力；一个新主题实际完成并逐图检查。最后一项需要接收者在自己的电脑、账号与环境完成。

发布前的同机新目录、隔离Codex配置安装与脚本测试范围见 [交付记录](DELIVERY.zh-CN.md)。同机测试不冒称另一位使用者已验收。本插件提供原标准及检查流程，图片质量依赖实际生成与修正，不保证任意模型一次成功。

插件结构、仓库与本地来源、引导技能依据[官方插件打包说明](https://developers.openai.com/plugins/build/plugins)；本包需要本地执行环境，参见[官方桌面插件说明](https://developers.openai.com/plugins/deploy/desktop-only)。这是GitHub分发，不等于已上架官方公共插件目录。
