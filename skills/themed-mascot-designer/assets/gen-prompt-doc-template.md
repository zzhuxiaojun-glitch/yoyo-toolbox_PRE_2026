# 生图任务 · <主题名> 素材

> 本文件可直接交给生图执行方(Codex / Nano Banana / 其它)。共 **<N> 张素材**:<分类计数>。
> 生图说明用中文,**喂给图像模型的 prompt 用英文**(模型对英文风格描述理解更准)。
> 角色完整设定见一角一档的 [`profiles/`](profiles/)。

---

## 0. 执行须知

1. **每个角色任务的最终 prompt = `[STYLE]` 风格块 + 该角色 `[ID]` 身份锚点 + 该任务 `Subject:` 行**。三段逐字粘贴。
2. **两步生成**:大画布生成(如 1024²)→ 最近邻降采样到最终尺寸:
   `magick gen.png -filter point -resize <W>x<H> final.png`(像素风必须最近邻;非像素风可跳过)。
3. **透明背景**:除场景图外全部透明,不要白底/白边/投影。
4. **目录命名**:严格按 §1,大小写一致。
5. **先定调再批量**:先做 §3 定调图 → 人工确认「风格 OK + 角色剪影确实拉开 + 核心魅力没丢」→ 再批量。
6. **参考风格**:<若有参考图,说明;能 image-to-image 就把参考图喂模型>。
7. **表情精灵集两步走**:每个角色除常规视图外**必出**「表情精灵集」—— 先整张生成 `-expressions` 合集表(4×3 共 12 态),
   再用 `magick … -crop 4x3@` 切成 12 张独立表情精灵;合集表与 12 张切片都入库。详见 §4.5。

---

## 1. 素材清单与目录

```
<输出根目录>/
├── <列出每个角色的常规视图文件名>
└── expressions/                 # 表情精灵集:每角色 1 张 4×3 合集表 + 12 张切片
```

| 素材 | 生成尺寸 | 最终尺寸 | 透明 |
|---|---|---|---|
| <类型> | <W×H> | <W×H> | 是/否 |
| <角色>-expressions 合集表(每角色 1 张,4×3) | 1024² | 单格最终尺寸 × 4 列 × 3 行 | 是 |
| <角色>-expr-<情绪> 切片(每角色 12 张,从合集表切) | — | 单格最终尺寸 | 是 |

---

## 2. `[STYLE]` 全局风格块(逐字粘贴在每个 prompt 开头)

```
<英文风格块。包含:画风(如 pixel-art / flat illustration)、描边、抗锯齿/渐变取舍、
调色板基调、透明背景与「NO white box / NO drop shadow / NO glow」、
恒定的核心魅力比例(如 chibi 大头大眼)。注意:身体胖瘦高矮交给 §4 每个角色,STYLE 里不要写死。>
```

**配色基调**:<主调色>。**禁区**:<要避免的颜色/质感>。

---

## 2.5 设计准则(从角色设计 skills 提炼)

> 调研结论 + 4 条准则。来源见 skill-research.md / design-principles.md。

| skill | 来源 | 取用 |
|---|---|---|
| <skill> | <平台> | <装了/没装/为何 + 提炼出什么> |

1. **剪影测试** — 每个角色纯黑剪影可辨;一组剪影不雷同。
2. **身份锚点** — 每角色一段锁死 `[ID]`,所有视图 prompt 全带。
3. **姿态 > 特效** — 个性靠体型/姿势/表情/眼神,禁投影/光晕/飘浮装饰。
4. **小尺寸先行** — 设计在最终尺寸下可读,调色板克制。
5. **表情 / 眼神拉满** — 每个角色的表情和眼神**夸张化**、N 个之间**互不重复**;不要全画成
   「睁圆大眼的可爱默认脸」。眼睛在形状 / 开合度 / 视线 / 高光上各不同。*(最常翻车点,必写)*
   **落地为素材**:每个角色必出一套「表情精灵集」—— 一张 12 态 4×3 合集表 + 切分出的 12 张独立表情精灵,见 §4.5。

---

## 3. 第一步:全员合集定调图(先做,交用户确认)

- 文件名:`_styleboard.png`(临时,不入库) ｜ 生成尺寸:<大尺寸>
- **验收点**:画风统一 ✓ + N 个角色的体型/剪影/姿态拉开 ✓ + **表情/眼神明显不同且夸张** ✓ + 全员仍守核心魅力 ✓。

```
[STYLE]
Subject: a contact sheet of <N> DISTINCT <主题角色>, each in its own cell,
same art style and one shared palette — but each has a CLEARLY DIFFERENT
body type, silhouette, pose, EXPRESSION and EYE STYLE driven by its
personality. They must NOT look like one character recolored. CRITICAL:
each character's facial expression and eye shape must be exaggerated and
all <N> clearly different — do NOT give them the same neutral wide-eyed
cute face. The <N> characters:
(1) <角色> — <体型 + 剪影 + 姿态 + 眼神 + 表情 一句>;
(2) ...
Consistent outline weight; <N> visibly distinct silhouettes.
```

✅ 用户确认后再做 §4 / §5。

---

## 4. 角色素材(<N> 角色 × <每角视图数> 视图)

每个角色:`[STYLE]` + 该角 `[ID]` + 各视图 `Subject:` 行。完整设定见 `profiles/<slug>.md`。

### 角色 N · <中文名> `<slug>` — <派系>

> **体型/剪影**:<一句>。**眼神**:<一句>。**表情**:<一句>。

```
[ID] <英文身份锚点 —— 锁死种类、配色/斑纹、体型、专属辨识特征、眼神。所有视图复用。>
```

- **<slug>-<视图>** — `Subject: <该视图的具体姿态/表情描述,含 subject fills ~XX% of canvas>`
- ...(每个视图一行)

> (其余角色重复本结构)

---

## 4.5 表情精灵集(每个角色必出 —— 落实准则 5)

> 准则 5「表情 / 眼神拉满」必须落成**可直接用的素材**,不能只停在 prompt 措辞。
> 每个角色除 §4 常规视图外,**必出一套「表情精灵集」**:一张 4×3 共 12 态合集表 + 切分出的 12 张独立表情精灵。

**12 态标准集**(4×3 行优先;覆盖学习 / 养成 App 的全部情绪场景):

| # | 态 | English(prompt 用) | # | 态 | English |
|---|---|---|---|---|---|
| 0 | 平静专注 | calm focused | 6 | 加油 / 鼓励 | cheering / encouraging |
| 1 | 开心 / 灿烂 | bright delighted | 7 | 思考 / 疑惑 | thinking / puzzled |
| 2 | 沮丧 / 失落 | dejected / downcast | 8 | 害羞 / 脸红 | shy / blushing |
| 3 | 惊讶 | shocked / surprised | 9 | 不满 / 鼓腮 | pouty / sulking |
| 4 | 得意 / 自豪 | smug / proud | 10 | 大哭 | crying / teary |
| 5 | 困倦 | sleepy / drowsy | 11 | 欢呼 / 庆祝 | joyful celebration |

**第一步 · 生成合集表** `<slug>-expressions.png` —— 整张一次生成(保证 12 格风格 / 角色一致):

```
[STYLE]
[ID](该角色)
Subject: a 4x3 expression sheet — the SAME character (<slug>) repeated in 12
head-and-shoulders portrait crops on one canvas, each crop a DRAMATICALLY
different emotion with a clearly different EYE shape, brow and mouth, in this
row-major order: (1) calm focused; (2) bright delighted; (3) dejected/downcast;
(4) shocked/surprised; (5) smug/proud; (6) sleepy/drowsy; (7) cheering/
encouraging; (8) thinking/puzzled; (9) shy/blushing; (10) pouty/sulking;
(11) crying/teary; (12) joyful celebration. Keep the [ID] markings identical
across all 12 so they are unmistakably ONE character, but make the 12
expressions and eyes exaggerated and obviously different — NOT one face
recolored. <一句:该角色如何演这 12 态,从档案「😀 表情 / 眼神 12 态变化谱」翻译>.
```

生成 1024² → 最近邻降采样到「合集表最终尺寸」(= 单格最终尺寸 × 4 列 × 3 行)。

**第二步 · 切分成 12 张独立表情精灵** —— 把合集表均匀切成 12 格,每格导出独立透明 PNG,
**切好即可直接用**(App 内随情绪切换立绘、好感度立绘档位):

```
magick <slug>-expressions.png -crop 4x3@ +repage <slug>-expr-%d.png
# 产出 <slug>-expr-0.png … <slug>-expr-11.png(行优先);按 12 态顺序重命名:
# 0=calm 1=happy 2=sad 3=surprised 4=proud 5=sleepy
# 6=cheer 7=thinking 8=shy 9=pouty 10=crying 11=celebrate
```

**交付物**:每个角色 = 1 张合集表 `<slug>-expressions.png` + 12 张切片 `<slug>-expr-<情绪>.png`,
**两者都入库**(切片放 §1 目录树的 `expressions/` 子目录)。

> 态命名可按主题微调(暗调主题可把「开心」改成「难得的微光浅笑」),数量也可按 App 需求增减,
> 但「先出整张合集表、再切分成独立精灵」这个两步流程不变。新增 6 态(加油~欢呼)要延续每个
> 角色「克制 ↔ 外放」的幅度基调,别和前 6 态脱节。

---

## 4.6 分档立绘(可选 —— 仅养成 / 好感度系统)

> 无养成系统**删除本节**。立绘 = 养成详情页大尺寸展示图,与小 idle sprite 区分。
> 每角色 N 档(典型 3 档),随好感度解锁,一档比一档亲近。设计要领见 [references/affinity-rewards.md]。

每档:`[STYLE]` + 该角 `[ID]` + 该档 `Subject:` 行。**N 档共用同一 `[ID]`**,确保是同一角色。

### 角色 N · <中文名> `<slug>` 立绘 N 档

- **<slug>-portrait-t1**(初遇)— `Subject: <拘谨、有距离的姿态/表情/场景,subject fills ~XX%>`
- **<slug>-portrait-t2**(熟络)— `Subject: <放松、主动一些>`
- **<slug>-portrait-tN**(羁绊)— `Subject: <最亲昵,但忠于该角色性格>`

> **递进准则**:亲近度的表达方式因角色性格而异 —— 不要 N 个角色用同一条递进弧线。
> N 档都守剪影 / 体型 / 核心魅力,变的是姿态 / 表情 / 距离。

---

## 5. UI / 场景素材(如有)

<边框、图标、背景、底纹等非角色素材;每项给 [STYLE] + Subject。>

---

## 6. 交付前 QA 自查

**画风基础**:透明真透明 / 无糊边 / 配色守基调 / 文件名尺寸目录对。
**角色「区别」**:
- [ ] 剪影测试:任取两角填黑能区分。
- [ ] 体型拉开:能指出谁最 X、谁最 Y。
- [ ] 招牌姿态各不同,不是换配色。
- [ ] **眼神 N 种、互不重复且夸张**(准则 5):形状 / 开合度 / 视线 / 高光都不同。
- [ ] **表情 N 种、互不重复且夸张**(准则 5):不是「同一张可爱默认脸」。
**表情精灵集**(准则 5 落地,§4.5):
- [ ] 每个角色都出了「1 张 4×3 合集表 + 12 张切片」,合集表与切片都入库。
- [ ] 合集表 12 态眼形 / 表情夸张且互不重复,不是「一张脸复制 12 次」。
- [ ] 12 张切片是独立透明 PNG、尺寸一致、切口干净无错位,拿了即用。
- [ ] 同角色 12 张切片一眼是同一个角色(`[ID]` 特征一致)。
- [ ] 新增 6 态(加油 / 思考 / 害羞 / 不满 / 大哭 / 欢呼)幅度与前 6 态一致,未脱节。
**核心魅力**:体型差异再大,全员仍守住可爱/帅/萌。
**一致性**:同角色各视图一眼是同一个(身份锚点生效);无投影/光晕/飘浮装饰。
**养成立绘(如有)**:N 档是同一角色(同 `[ID]`)· 档间亲近度肉眼可见递进 · 递进忠于性格不崩设 · 每档都守核心魅力。
