# 角色 / 像素设计 skills 调研

> Phase 2「skill 调研」读本文件。下方是已验证的基线结论(2026-05);仍应快速复查有无更新。

## 一、已验证可用的 skills(基线)

| skill | 来源 / 平台 | 用法 | 取用建议 |
|---|---|---|---|
| **hatch-pet** | `openai/skills` 的 `.curated/hatch-pet`(Codex 官方) | Codex 原生「像素宠物」生成 skill,含 Pet-Safe Style / Transparency&Effects / QA Rubric | ✅ 值得装进 `~/.codex/skills/`。即使本项目是单图工作流不跑它的脚本管线,它的三节规范是金科玉律 → 已提炼成 design-principles 准则 3。 |
| **game-character-sprites** | `tachikomared/character-animation-creator-skill`(Codex/GPT agent) | 8 方向像素角色动画图集,核心是「剪影优先 + 分辨率层级」 | ⭐ 原则极有用(→ 准则 1、4)。本体是动画图集管线,对静态单图过重;需要动画时再装。 |
| **character-design-sheet** | `inferen-sh/skills`(Claude Code) | AI 生图角色一致性:turnaround / 表情表,核心是「description anchor」 | ⭐ 「身份锚点」技术直接采纳 → 已转化成档案里的 `[ID]` 块。skill 本体是 FLUX/LoRA 专用,一般不装。 |

**安装命令**:
```bash
# hatch-pet(从 openai/skills 稀疏检出单个 skill)
cd /tmp && git clone --depth 1 --filter=blob:none --sparse https://github.com/openai/skills oai-skills \
  && cd oai-skills && git sparse-checkout set skills/.curated/hatch-pet \
  && cp -r skills/.curated/hatch-pet ~/.codex/skills/hatch-pet

# game-character-sprites(需要动画图集时)
git clone https://github.com/tachikomared/character-animation-creator-skill ~/.codex/skills/game-character-sprites
```

## 二、不适用 / 已排除

| skill | 原因 |
|---|---|
| pixel-plugin (willibrandon) | Aseprite 程序化逐像素绘制,不是文生图工作流。 |
| pixel-art-professional | 要求 light-source-aware 3D 光影,和「flat / NO shading」可爱像素风冲突。 |

## 三、本机已有的相关 skills(可直接用,先查)

- `browse-skills-marketplace` — 搜 skills.sh / skills.pub / SkillsMP。
- `nano-banana-pro` — 用 Nano Banana Pro(Gemini 3 Pro Image)生图,支持 image-to-image,可作 Codex 之外的生图后端。
- `ui-ux-pro-max` / `frontend-design` / `web-design-guidelines` — 通用视觉设计,非角色专用。

## 四、复查方法(skill 生态会变,每次开新主题快速扫一遍)

1. **本机优先**:先看 `~/.claude/skills/` 与 `~/.codex/skills/` 有没有现成的。
2. **marketplace**:调用 `browse-skills-marketplace` skill,或 WebSearch:
   `character design / silhouette / pixel art / sprite / animal design + claude code skill / codex skill`。
3. **Codex 官方目录**:`gh api 'repos/openai/skills/git/trees/main?recursive=1' --jq '.tree[].path'`
   过滤 `charact|pixel|art|image|sprite|design`。
4. **判 verdict**:对每个候选问三个问题 ——
   (a) 是文生图工作流,还是程序化绘图 / 动画管线?(b) 风格要求和本主题冲突吗(如强制 3D 光影)?
   (c) 它的「设计原则」能不能脱离 skill 本体单独提炼进生图文档?
5. **可转化项**:Claude Code 专用 skill 若含通用设计原则(如 description-anchor),
   把**原则**提炼写进生图文档即可,不必为 Codex 强行安装该 skill。

## 五、写进生图文档的「skill 取用结论」

Phase 4 的生图文档里要放一节「设计准则(从 skills 提炼)」,内容 =
本文件第一节的表格(哪些装了/没装/为何) + design-principles.md 的 4 条准则。
让 Codex(或其它生图执行方)看到准则来源、可信、可直接照做。
