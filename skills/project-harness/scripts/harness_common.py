#!/usr/bin/env python3
"""harness_common.py — 脚本层公共工具（零依赖，stdlib only）。

脚本间共享的确定性小工具唯一维护点；各脚本不得再各自复制这些实现。
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def find_git_root(path: Path) -> Path | None:
    """向上查找包含 .git 的目录（.git 可以是目录或 worktree 文件）。"""
    for cand in (path, *path.parents):
        if (cand / ".git").exists():
            return cand
    return None


def read_text_relaxed(path: Path) -> str | None:
    """容错读取文本（utf-8 + errors=replace）；OSError/解码失败返回 None。"""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def git_version(root: Path) -> str:
    """harness 版本：git describe --tags --always --dirty，回退 short HEAD / unknown。"""
    for git_args in (("describe", "--tags", "--always", "--dirty"),
                     ("rev-parse", "--short", "HEAD")):
        try:
            r = subprocess.run(["git", "-C", str(root), *git_args],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            break
    return "unknown"


def detect_doc_lang(repo: Path) -> str:
    """探测目标仓库既有文档的主语言：CJK 字符占比 >30% 判 zh，否则 en。

    读取 AGENTS.md / README 系列文件（各截前 20000 字符）；无既有文档或
    全空时回退 zh（2026-09-13 用户确认的阈值与回退）。
    """
    texts: list[str] = []
    for name in ("AGENTS.md", "README.md", "README.zh-CN.md", "README.rst"):
        f = repo / name
        if f.is_file():
            content = read_text_relaxed(f)
            if content:
                texts.append(content[:20000])
    if not texts:
        return "zh"
    text = "".join(texts)
    if not text.strip():
        return "zh"
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return "zh" if cjk / len(text) > 0.30 else "en"
