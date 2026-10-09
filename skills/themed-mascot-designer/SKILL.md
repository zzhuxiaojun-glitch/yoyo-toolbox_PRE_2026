---
name: themed-mascot-designer
description: >-
  Design a themed SET of mascot / character sprites for a project — each
  character gets a personality profile and a visually DISTINCT form, then a
  ready-to-run image-generation prompt document. Use when the user wants to
  create or refine a group of characters/mascots (animals, creatures, etc.)
  for an app/game/brand, especially when they say things like 「做一套某主题
  的吉祥物/角色」「设计一组动物角色」「给项目做组像素猫/狗角色」「这几只角色
  长得太像了，区别做大一点」「把性格写成档案再交给 Codex 生图」「themed
  mascot set」「character set design」. The workflow: (1) write one
  personality profile per character (with signature self-intro + species-fact
  voice lines), (2) research Claude Code / Codex
  character-design skills, (3) translate each personality into a distinct
  body type / silhouette / eyes / pose, (4) produce a gen-prompt document to
  hand to an image model (Codex imagegen, Nano Banana, etc.).
---

# Themed Mascot Designer

把「一组主题角色」从性格设定做到可生图的成品。产出两类文档:**一角一份性格档案** + **一份生图 prompt 文档**。

## 何时用

用户要为某个项目做**一整组**吉祥物 / 角色 / 动物精灵,并最终交给生图模型出图。
典型场景:从零设计一套角色;或已有一版图但「N 只角色长得太像」要把区别做大。
单个角色、或纯写文案不涉及视觉,不需要本 skill。

## 核心理念(贯穿全程,不可妥协)

> **角色之间靠「剪影」区分,但所有角色守住同一个「核心魅力」。**

- 区别由**性格**驱动 —— 精明→瘦长、馋嘴→圆胖、胆小→缩小蜷缩、慵懒→塌软、元气→敦实动感。
- 区别落在**六要素**:体型 / 剪影 / 眼神 / 表情 / 五官标志 / 招牌姿态。绝不能只换配色。
- 但核心魅力(可爱 / 帅 / 萌,按主题定)是**全员恒定的框** —— 差异在框内做,瘦长的角色靠
  chibi 头身比拉回可爱,畏缩的角色靠水汪大眼拉回可爱。

## 工作流 · 4 阶段

### Phase 1 — 角色档案

为**每个角色单独写一份** `profiles/<slug>.md`。模板见 [assets/profile-template.md](assets/profile-template.md)。
每份要扩写到「个性鲜明」:性格底色 + 习惯 + 怪癖 + 喜欢/讨厌的食物和事 + 日常与角色间关系 + 两条招牌台词。

- 关系网很重要 —— 让一组角色像「群像」而非 N 个孤立角色(谁是搭档 / 天敌 / 崇拜对象)。
- 怪癖要**具体**,因为它们之后会变成视觉细节和姿态。
- **每个角色补两条招牌台词**:一条「自我介绍」+ 一条「品种知识科普」(用角色口吻科普它所属
  物种 / 品种的真实趣味知识,**所选事实要呼应该角色性格**)—— 台词让吉祥物能开口,品种科普
  顺带把它变成知识彩蛋。语言跟随项目台词约定。详见 profile-template 的「🗣️ 台词」节。
- 若项目已有「台词 / 行为」权威文档,**不要覆盖它** —— 先 Glob/Grep 查有没有既存角色设定文件,
  有就以它为基底扩写;**台词写进该权威文档,没有独立文档则写进 profile 的「🗣️ 台词」节**。
  视觉 / 性格细节始终写 profile,两边互相注明分工与链接。
- **养成系统**:若项目给角色配了好感度 / 升级系统,招牌台词要扩成分类台词集 + 配音色 —— 见下方「可选模块」。

### Phase 2 — skill 调研

按 [references/skill-research.md](references/skill-research.md) 找角色 / 剪影 / 像素 / 动物设计相关 skills。

- 先查本机 `~/.claude/skills/` 与 `~/.codex/skills/`,再查 marketplace / Codex 官方目录。
- 已验证基线:**hatch-pet**(Codex 官方,值得装)、**game-character-sprites**、**character-design-sheet**
  —— 详见参考文件,含安装命令和「为何不装某些」的判断。
- 安装**合适的**;对不便安装但含通用原则的(尤其 Claude Code 专用 skill),把**原则提炼**出来即可。
- 调研结论要在 Phase 4 写进生图文档,让生图执行方看到准则来源。

### Phase 3 — 形态设计(性格 → 差异化形态)

读 [references/design-principles.md](references/design-principles.md),为每个角色填档案里的「🎨 视觉设计要点」。

- 用「体型轴 / 眼神轴 / 姿态轴」词库,把每个角色钉到**不同的档位** —— 一组角色要在各轴上铺开。
- 两个性格相近的角色,必须用**不同解法**拉开(例:两个都「精明」→ 一个瘦长威严竖塔、
  一个瘦长优雅曲线;并在档案里写清两者的区分对照)。
- 逐一过「区别六要素」与「剪影测试」:把每个角色想成纯黑剪影,确认彼此能分辨。
- 每个角色写明「魅力锚点」—— 守住核心魅力的那一手。
- 每个角色填一份「😀 表情 / 眼神 12 态变化谱」(平静 / 开心 / 沮丧 / 惊讶 / 得意 / 困倦 / 加油 /
  思考 / 害羞 / 不满 / 大哭 / 欢呼),逐态写眼 / 眉 / 嘴 / 招牌小动作 —— 这是 Phase 4「表情精灵集」的设计依据。

### Phase 4 — 生图文档 + 交接

按 [assets/gen-prompt-doc-template.md](assets/gen-prompt-doc-template.md) 产出一份生图 prompt 文档。

- **`[STYLE]` 全局风格块**:画风 / 描边 / 调色板 / 透明背景 / 恒定的核心魅力比例。
  身体胖瘦高矮**不写进 STYLE**,交给每个角色。
- **`[ID]` 身份锚点**:每个角色一段锁死的英文身份串,该角色所有视图的 prompt 全部带上(准则 2)。
- **per-视图 `Subject:` 行**:从档案的「视图差异」翻成英文,姿态/表情各不同,标注 `subject fills ~XX%`。
- **设计准则节**:放 Phase 2 的调研结论 + 5 条准则;**准则 5「表情 / 眼神拉满」是生图最常翻车点**
  (模型爱把 N 只画成同一张可爱默认脸)—— 务必在文档里单列强制要求 + 写进 QA。
- **表情精灵集(每角色必出)**:准则 5 要落成**可直接用的素材** —— 每个角色除常规视图外,必出一张
  「12 态表情合集表」(4×3 排列),**再切分成 12 张独立表情精灵**(平静 / 开心 / 沮丧 / 惊讶 / 得意 /
  困倦 / 加油 / 思考 / 害羞 / 不满 / 大哭 / 欢呼);合集表整张生成保 12 态风格一致,切片切好即用
  (App 内情绪切换、好感度立绘档)。详见 gen-prompt-doc-template §4.5。
- **定调图**:文档第一步永远是「全员合集定调图」,交用户确认「风格 OK + 剪影拉开 + 魅力没丢」**再批量**。
- 喂给图像模型的 prompt 用**英文**;文档说明用中文。
- 交接:文档可直接给 Codex(`imagegen` / `hatch-pet`)或 `nano-banana-pro` skill 执行。
  生图由用户/Codex 跑,本 skill 只负责把文档做到「拿了就能出图」。
- **养成系统**:若项目有好感度奖励,文档要多一类「分档立绘」素材(每角 N 档)—— 见下方「可选模块」。

## 可选模块 · 养成 / 好感度奖励

> **启用条件**:项目给这组角色配了「养成 / 好感度 / 升级」系统(撸宠、好感度升级解锁奖励)。
> 普通吉祥物 / 图标集 / 一次性角色,不需要本模块 —— 跳过。

养成系统让「角色设计」多出两条**随好感度等级递进**的产出,都是性格设计工作,由本 skill 完成:

- **分档立绘** —— 每角色 N 档(典型 3 档:初遇 / 熟络 / 羁绊)正式立绘,随好感度逐档解锁;
  立绘是养成详情页的大尺寸展示图,与小 idle sprite 区分。
- **分类音声台词集 + 音色** —— 把 Phase 1 的 2 条招牌台词扩成按用途分类、按等级解锁的台词集
  (问候 / 鼓励 / 升级 / 专属),并为每个角色匹配一种声线(性格 → 音色)。

**核心准则**:递进必须**忠于性格** —— 高冷角色到最高档也只是「以它克制的方式」流露亲昵,
不要让 N 个角色走同一条「挥手→微笑→拥抱」弧线。

衔接:启用时 Phase 1 档案多填「🎁 养成奖励」节,Phase 4 生图文档多一类「分档立绘」素材。
本 skill 只做**设计**;解锁推导 / 建表 / 语音合成等**功能工程**交配套的 `pixel-mascot-theme`。
完整指引见 [references/affinity-rewards.md](references/affinity-rewards.md)。

## 产出物结构(建议)

```
<项目>/<主题目录>/
├── profiles/
│   ├── README.md           # 索引 + 体型/剪影对比总表
│   └── <slug>.md           # 一角一档
└── <主题>_ASSET_PROMPTS.md # 生图 prompt 文档(Phase 4)
```

profiles/README.md 里放一张「体型 / 剪影差异总表」—— 一眼看出全组是否拉开了,是最有用的自查工具。

## 参考文件

- [references/design-principles.md](references/design-principles.md) — 4 条核心准则 + 性格→形态映射词库 + 六要素检查。Phase 3 必读。
- [references/skill-research.md](references/skill-research.md) — 已验证的设计 skills、安装命令、复查方法。Phase 2 读。
- [assets/profile-template.md](assets/profile-template.md) — 单角色档案模板。Phase 1 用。
- [assets/gen-prompt-doc-template.md](assets/gen-prompt-doc-template.md) — 生图 prompt 文档模板。Phase 4 用。
- [references/affinity-rewards.md](references/affinity-rewards.md) — 养成 / 好感度奖励的设计指引(分档立绘 + 音声台词集 + 音色)。可选模块用。

> 真实范例:JLPTsimu 项目的「像素猫咪」8 猫主题 —— `doc_jlptsimu/pixel-cats/`(profiles/ + CODEX_ASSET_PROMPTS.md)。
