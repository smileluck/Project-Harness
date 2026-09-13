#!/usr/bin/env python3
"""harness_common.py — 脚本层公共工具（零依赖，stdlib only）。

脚本间共享的确定性小工具唯一维护点；各脚本不得再各自复制这些实现。
"""

from __future__ import annotations

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
