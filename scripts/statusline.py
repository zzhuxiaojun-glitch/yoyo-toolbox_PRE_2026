#!/usr/bin/env python3
"""Claude Code 三行分层状态栏。

从 stdin 读取 Claude Code 传入的会话 JSON，输出 1~3 行 ANSI 状态栏。
行数随终端宽度自动收敛：>=120 列三行，>=90 列两行，更窄一行。

安装（写进 ~/.claude/settings.json 或项目 .claude/settings.json）：

    "statusLine": {
      "type": "command",
      "command": "python3 /path/to/statusline.py"
    }
"""

import json
import os
import shutil
import subprocess
import sys

# ---------------------------------------------------------------- 配置

SHOW_KEYS = False   # 快捷键提示；Claude Code 本身已提示，默认关
MAX_BRANCH = 28     # 分支名截断宽度
GIT_TIMEOUT = 0.8   # git 子进程超时（秒），超时即放弃该单元而不是卡住状态栏

# 测试结果可选缓存：由你的测试钩子写入，形如
#   {"passed": 18, "failed": 0}
# 不存在就不显示「测试」单元 —— 宁可留空，不编数字。
TEST_CACHE = ".claude/statusline-tests.json"

# ---------------------------------------------------------------- 调色板
# 256 色近似图稿 token，兼容绝大多数终端；真彩终端自动升级为精确值。

TRUECOLOR = os.environ.get("COLORTERM", "") in ("truecolor", "24bit")


def _c(idx, rgb):
    if TRUECOLOR:
        r, g, b = rgb
        return f"\x1b[38;2;{r};{g};{b}m"
    return f"\x1b[38;5;{idx}m"


ACCENT = _c(173, (0xD0, 0x8A, 0x4E))   # 黏土橙 · 唯一强调色
OK     = _c(108, (0x7F, 0xA3, 0x7A))   # 鼠尾草绿 · 健康
WARN   = _c(179, (0xC9, 0xA2, 0x4D))   # 沙黄 · 注意
CRIT   = _c(167, (0xC4, 0x69, 0x5E))   # 陶红 · 阻断
FG1    = _c(253, (0xED, 0xE8, 0xE2))   # 主行数值
FG2    = _c(245, (0xA2, 0x9A, 0x92))   # 次行数值
FG3    = _c(240, (0x6B, 0x64, 0x5E))   # 标签 / 微行
BOLD   = "\x1b[1m"
DIM    = "\x1b[2m"
R      = "\x1b[0m"

SEP = f"{FG3} │ {R}"


def cell(label, value, vcolor=FG1, icon=None):
    """一个单元：暗标签 + 亮数值。终端里字号层级换成明度层级。"""
    head = f"{FG3}{icon} {R}" if icon else ""
    lab = f"{FG3}{label} {R}" if label else ""
    return f"{head}{lab}{vcolor}{value}{R}"


def meter(pct, width=10):
    """上下文水位条。低位鼠尾草绿，高位转强调色再转陶红。"""
    pct = max(0, min(100, int(pct)))
    filled = round(width * pct / 100)
    color = OK if pct < 60 else (ACCENT if pct < 85 else CRIT)
    bar = f"{color}{'━' * filled}{R}{FG3}{'━' * (width - filled)}{R}"
    return f"{bar} {color}{pct}%{R}"


# ---------------------------------------------------------------- 数据采集

def run(args, cwd):
    try:
        out = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=GIT_TIMEOUT
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def git_state(cwd):
    """返回 (分支名, 是否有未提交改动, 改动文件数)；非 git 仓库返回 None。"""
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if branch is None:
        return None
    if branch == "HEAD":  # detached
        short = run(["git", "rev-parse", "--short", "HEAD"], cwd)
        branch = f"detached@{short}" if short else "detached"
    status = run(["git", "status", "--porcelain"], cwd)
    files = [l for l in (status or "").splitlines() if l.strip()]
    return branch, bool(files), len(files)


def env_label():
    """WSL / 发行版 / macOS 标签。"""
    if sys.platform == "darwin":
        return "macOS"
    distro = None
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            for line in f:
                if line.startswith("NAME="):
                    distro = line.split("=", 1)[1].strip().strip('"')
                    break
    except OSError:
        pass
    is_wsl = False
    try:
        with open("/proc/version", encoding="utf-8") as f:
            is_wsl = "microsoft" in f.read().lower()
    except OSError:
        pass
    if distro and is_wsl:
        return f"WSL {distro.split()[0]}"
    return distro or sys.platform


def context_usage(transcript_path, limit):
    """从 transcript 末尾回扫最近一次 usage，估算上下文占用。

    只读文件尾部若干 KB，避免长会话下状态栏变慢。
    """
    if not transcript_path or not os.path.isfile(transcript_path):
        return None
    try:
        size = os.path.getsize(transcript_path)
        with open(transcript_path, "rb") as f:
            f.seek(max(0, size - 256 * 1024))
            tail = f.read().decode("utf-8", "ignore")
    except OSError:
        return None

    for line in reversed(tail.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        usage = (rec.get("message") or {}).get("usage")
        if not isinstance(usage, dict):
            continue
        used = (
            usage.get("input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
            + usage.get("output_tokens", 0)
        )
        if used:
            return used, min(100, round(used * 100 / limit))
    return None


def test_state(project_dir):
    path = os.path.join(project_dir, TEST_CACHE)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    passed = int(data.get("passed", 0))
    failed = int(data.get("failed", 0))
    return passed, failed


def gsd_update():
    """GSD 更新提醒。直接读 gsd-check-update 写的缓存，不拉起 node 进程。

    返回已着色的片段，或 None。
    """
    home = os.path.expanduser("~")
    for path in (
        os.path.join(home, ".cache", "gsd", "gsd-update-check.json"),
        os.path.join(home, ".claude", "cache", "gsd-update-check.json"),
    ):
        try:
            with open(path, encoding="utf-8") as f:
                cache = json.load(f)
            break
        except (OSError, ValueError):
            continue
    else:
        return None

    def parse_v(v):
        try:
            return tuple(int(x) for x in str(v).split(".")[:3])
        except ValueError:
            return None

    installed, latest = parse_v(cache.get("installed")), parse_v(cache.get("latest"))
    dev_install = bool(installed and latest and installed > latest)

    if cache.get("stale_hooks") and not dev_install:
        return f"{CRIT}⚠ hooks 过期 · /gsd-update{R}"
    if cache.get("update_available") and not dev_install:
        tag = f" {cache['latest']}" if cache.get("latest") else ""
        return f"{WARN}⬆ /gsd-update{tag}{R}"
    return None


def human_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n // 1000}k"
    return str(n)


def human_time(ms):
    s = int((ms or 0) / 1000)
    if s >= 3600:
        return f"{s // 3600}h{(s % 3600) // 60:02d}m"
    if s >= 60:
        return f"{s // 60}m{s % 60:02d}s"
    return f"{s}s"


# ---------------------------------------------------------------- 组装

def build(data):
    cwd = data.get("workspace", {}).get("current_dir") or data.get("cwd") or os.getcwd()
    project_dir = data.get("workspace", {}).get("project_dir") or cwd
    model = data.get("model", {}) or {}
    model_name = model.get("display_name") or model.get("id") or "claude"
    model_id = model.get("id", "")
    mode = (data.get("output_style", {}) or {}).get("name") or ""
    cost = data.get("cost", {}) or {}

    limit = 1_000_000 if "[1m]" in model_id or "1m" in model_id.lower() else 200_000
    git = git_state(cwd)
    ctx = context_usage(data.get("transcript_path"), limit)
    tests = test_state(project_dir)

    # ---- 第一行 · 身份：我在哪、用什么在干活
    row1 = [cell(None, os.path.basename(cwd.rstrip("/")) or "/", BOLD + FG1)]
    if git:
        branch, dirty, _ = git
        if len(branch) > MAX_BRANCH:
            branch = branch[: MAX_BRANCH - 1] + "…"
        mark = f" {WARN}✗{R}" if dirty else f" {OK}✓{R}"
        row1.append(f"{FG3}⑂ {R}{FG1}{branch}{R}{mark}")
    row1.append(f"{ACCENT}◆ {model_name}{R}")
    if mode and mode != "default":
        row1.append(f"{FG2}{mode}{R}")

    # ---- 第二行 · 状态：这次改动的健康度
    # 左缘竖条编码整体健康：全绿 / 有改动转黄 / 测试失败转红
    health = OK
    row2 = []
    if git:
        _, _, nfiles = git
        if nfiles:
            health = WARN
            row2.append(cell("改动", f"{nfiles} files", FG2))
        else:
            row2.append(cell("改动", "干净", FG3))
    added = cost.get("total_lines_added")
    removed = cost.get("total_lines_removed")
    if added or removed:
        row2.append(f"{OK}+{added or 0}{R}{FG3}/{R}{CRIT}-{removed or 0}{R}")
    if tests:
        passed, failed = tests
        if failed:
            health = CRIT
            row2.append(cell("测试", f"{failed} 失败 · {passed} 通过", CRIT))
        else:
            row2.append(cell("测试", f"{passed} 通过", OK))
    row2.append(cell("环境", env_label(), FG2))
    if ctx:
        row2.append(f"{FG3}上下文 {R}{meter(ctx[1])}")

    # ---- 第三行 · 代谢：偶尔一瞥的数字
    row3 = []
    if ctx:
        row3.append(cell("tokens", f"{human_tokens(ctx[0])} / {human_tokens(limit)}", FG3))
    if cost.get("total_cost_usd") is not None:
        row3.append(cell("花费", f"${cost['total_cost_usd']:.2f}", FG3))
    if cost.get("total_api_duration_ms"):
        row3.append(cell("API", human_time(cost["total_api_duration_ms"]), FG3))
    if cost.get("total_duration_ms"):
        row3.append(cell("会话", human_time(cost["total_duration_ms"]), FG3))
    if SHOW_KEYS:
        row3.append(f"{FG3}esc 取消 · ⌃k 命令 · ⏎ 执行{R}")
    gsd = gsd_update()
    if gsd:
        row3.append(gsd)

    # 左缘竖条贴住首个单元，不参与分隔线；空行直接丢弃
    stripes = (ACCENT, health, FG3)
    rows = []
    for stripe, cells in zip(stripes, (row1, row2, row3)):
        if not cells:
            continue
        rows.append(f"{stripe}▎{R}" + SEP.join(cells))
    return rows


def columns():
    env = os.environ.get("COLUMNS")
    if env and env.isdigit():
        return int(env)
    return shutil.get_terminal_size(fallback=(120, 24)).columns


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        data = {}

    rows = build(data)
    width = columns()

    # 窄宽收敛：宽度不够时按「代谢 → 状态」的顺序丢弃，身份行永远保留
    if width < 90:
        rows = rows[:1]
    elif width < 120:
        rows = rows[:2]

    sys.stdout.write("\n".join(rows))


if __name__ == "__main__":
    main()
