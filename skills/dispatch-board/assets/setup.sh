#!/usr/bin/env bash
# Bootstrap a new dispatch-board in current dir.
# Usage:  bash ~/.claude/skills/dispatch-board/assets/setup.sh [root_dir]
#         default root_dir = "tasks"

set -euo pipefail

ROOT_DIR="${1:-tasks}"
SKILL_ASSETS="$(dirname "$(readlink -f "$0")")"

if [ -d "$ROOT_DIR" ]; then
  echo "❌ $ROOT_DIR/ already exists; aborting (won't overwrite)"
  exit 1
fi

mkdir -p "$ROOT_DIR/status" "$ROOT_DIR/dispatches"
touch "$ROOT_DIR/status/.gitkeep"

# 复制 dashboard 脚本（生成器）
cp "$SKILL_ASSETS/build_dashboard.py" "$ROOT_DIR/build_dashboard.py"
chmod +x "$ROOT_DIR/build_dashboard.py"

# 复制 README / pitfalls 模板
cp "$SKILL_ASSETS/README.md.template"  "$ROOT_DIR/README.md"
cp "$SKILL_ASSETS/pitfalls.md.template" "$ROOT_DIR/pitfalls.md"

# 把 README 里的占位换成真实项目名
PROJECT_NAME="$(basename "$(pwd)")"
sed -i "s/<PROJECT_NAME>/${PROJECT_NAME}/g" "$ROOT_DIR/README.md"

# 跑首版 dashboard（空 categories，但产出空表 OK）
( cd "$ROOT_DIR" && python3 build_dashboard.py )

cat <<EOF

✅ Dispatch board bootstrapped at: $ROOT_DIR/

下一步：
  1. 加你的第一个 dispatch 类别：
     mkdir -p $ROOT_DIR/dispatches/<category>
     cp $SKILL_ASSETS/dispatch_TEMPLATE.md.template $ROOT_DIR/dispatches/<category>/TEMPLATE.md
     cp $SKILL_ASSETS/manifest.json.template $ROOT_DIR/dispatches/<category>/manifest.json
     # 编辑 TEMPLATE.md 写该类别的标准操作
     # 编辑 manifest.json 写 entries

  2. 重生 dashboard 看效果：
     cd $ROOT_DIR && python3 build_dashboard.py

  3. 浏览器打开：
     file://\$(pwd)/MASTER_PROGRESS.html

  4. 用户在新会话里说「执行 dispatch <category>/001」即可触发。
EOF
