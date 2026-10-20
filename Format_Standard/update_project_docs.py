#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 12 个 ALBP 仓库统一更新 VERSION / CHANGELOG.md / README.md，
记录本次“案例格式统一”修订。不改变任何 .txt 内容。

版本策略：在现有版本基础上提升 minor（x.y.z -> x.(y+1).0）。
"""
import os
import re

ROOT = r"D:/GitHubInstances"
DATE = "2026-10-21"

PROJECTS = [
    "Instances_Cobot_ALBP2",
    "Instances_Cobot_Two_sided_ALBP2",
    "Instances_DLBP1_with_OR_Predecessor",
    "Instances_Robotic_ALB2",
    "Instances_Robotic_Two_sided_ALBP2",
    "Instances_SALBP1",
    "Instances_SALBP2",
    "Instances_Stochastic_ALBP1",
    "Instances_TALBP2_Worker_Assignment",
    "Instances_Two_sided_ALBP1",
    "Instances_Two_sided_ALBP2",
    "Instances_Two_sided_DLBP1",
]

CHANGED_BLOCK = (
    "### Changed\n"
    "- Unified the instance file format across the entire dataset:\n"
    "  - All `<tag>` header labels are now lowercased (e.g., `Precedence relations` -> `precedence relations`).\n"
    "  - `number of mated-station` and `mated-station number` are consolidated to `number of mated-stations`; "
    "`number of stations` is left unchanged.\n"
    "  - Every file now ends with exactly one `<end>` tag; trailing blank lines are removed while internal blank lines are preserved.\n"
    "- Precedence relations (both the `i,j` and `i j 1` forms) and the task-time column layouts are "
    "intentionally left unchanged to keep downstream parsers compatible.\n"
)


def bump_version(v: str) -> str:
    parts = v.strip().split(".")
    while len(parts) < 3:
        parts.append("0")
    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return v  # 非标准版本号，原样返回
    return f"{major}.{minor + 1}.0"


def update_version(path, new_v):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    # 取首行作为版本（兼容可能的多余空行）
    lines = content.split("\n")
    # 保留文件其余部分，只改首行
    rest = lines[1:] if len(lines) > 1 else []
    new_content = new_v + ("\n" + "\n".join(rest) if rest else "\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)


def update_changelog(path, new_v):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if f"## [{new_v}]" in content:
        return  # 已插入，避免重复
    new_section = f"## [{new_v}] - {DATE}\n\n{CHANGED_BLOCK}\n"
    # 在 `## [Unreleased]` 之后插入
    m = re.search(r"^##\s*\[Unreleased\]\s*$", content, re.MULTILINE)
    if m:
        insert_at = m.end()
        # 确保段间有空行：在 Unreleased 后接一个空行，再放新段
        new_content = content[:insert_at].rstrip("\n") + "\n\n" + new_section + "\n" + content[insert_at:].lstrip("\n")
    else:
        # 退路：直接拼到文件开头
        new_content = new_section + "\n" + content
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)


def update_readme(path, new_v):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    content = re.sub(r"(\*\*Version:\*\*\s*)\S+", rf"\g<1>{new_v}", content)
    content = re.sub(r"(\*\*Last Updated:\*\*\s*)\S+", rf"\g<1>{DATE}", content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    for proj in PROJECTS:
        base = os.path.join(ROOT, proj)
        ver_path = os.path.join(base, "VERSION")
        ch_path = os.path.join(base, "CHANGELOG.md")
        rd_path = os.path.join(base, "README.md")
        if not (os.path.isfile(ver_path) and os.path.isfile(ch_path) and os.path.isfile(rd_path)):
            print(f"[跳过] 缺少文档文件: {proj}")
            continue
        with open(ver_path, "r", encoding="utf-8", errors="ignore") as f:
            old_v = f.read().strip().split("\n")[0].strip()
        new_v = bump_version(old_v)
        update_version(ver_path, new_v)
        update_changelog(ch_path, new_v)
        update_readme(rd_path, new_v)
        print(f"[更新] {proj}: {old_v} -> {new_v}")


if __name__ == "__main__":
    main()
