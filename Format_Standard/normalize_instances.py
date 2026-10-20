#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALBP 案例文件格式统一脚本
==========================
适用：本仓库 12 个 Instances_* 项目（ALBP 问题族）。
排除：Instances_RALSP（不同问题族）。

按用户决策执行的最小化改动：
  1. 优先关系写法（i,j / i j 1）【不处理】，原样保留。
  2. 标签（<tag>）全部小写；同义字段统一：
       <number of mated-station> / <mated-station number> / <number of mated station> ...
         -> <number of mated-stations>
     <number of stations>（单侧）保持不变。
  3. 文件结尾统一为一个 <end>（去除尾部空行；内部的空行保留）。
  4. 作业时间的列数语义【不处理】，原样保留。

原文件零修改，输出到镜像目录。

用法：
  python normalize_instances.py                 # 全部 12 个项目 -> normalized_output/
  python normalize_instances.py --sample         # 仅代表性样本 -> normalized_sample/
  python normalize_instances.py --project Instances_SALBP1
"""

import os
import re
import sys

ROOT = r"D:/GitHubInstances"
OUT_ROOT = r"D:/GitHubInstances/Instances_Format_Standard/normalized_output"
SAMPLE_OUT = r"D:/GitHubInstances/Instances_Format_Standard/normalized_sample"

# ALBP 族项目（RALSP 故意排除）
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

# 标签别名映射（规范化为“小写 + 空格分词”之后再去查表）。
# 注意：norm_tag 会先把连字符 '-' 转成空格再做查表，因此下列键用空格形式；
#       目标值在返回时原样写出（可保留连字符，如 number of mated-stations）。
TAG_ALIASES = {
    "number of mated station": "number of mated-stations",
    "mated station number": "number of mated-stations",
    "number of mated-station": "number of mated-stations",
    "number of matedstations": "number of mated-stations",
    # 其余同义/单复数归一（保留，不影响用户明确指定的项）
    "task direction": "task directions",
    "precedence relation": "precedence relations",
    "sequence dependency": "sequence dependencies",
}

TAG_RE = re.compile(r"^\s*<(.+?)>\s*$")


def norm_tag(raw: str) -> str:
    """把任意 <...> 标签规范为小写、统一写法（不改动连字符的词义）。"""
    t = raw.strip()
    if t.startswith("<"):
        t = t[1:]
    if t.endswith(">"):
        t = t[:-1]
    t = t.strip().lower()
    # 仅把连字符视为词分隔；下划线保留（如 z_alpha 不应被拆成 z alpha）
    t = t.replace("-", " ")
    t = re.sub(r"\s+", " ", t)
    return TAG_ALIASES.get(t, t)


def process_text(text: str):
    """返回 (规范化后的行列表, 改动摘要)。

    改动范围（最小化）：
      - 标签行：小写 + 别名归一
      - 数据行：仅去除行尾空白（含 CRLF 归一为 LF），内容原样
      - 结尾：确保唯一 <end>、去除尾部空行（内部空行保留）
    优先关系（precedence relations）与作业时间（task times）均【不处理】。
    """
    lines = text.split("\n")
    out = []
    changes = {"tags": 0, "end_added": False, "end_cleaned": False}

    for raw in lines:
        s = raw.strip()
        if s == "":
            out.append("")  # 内部空行保留
            continue
        m = TAG_RE.match(raw)
        if m:
            inner = m.group(1)
            normalized_inner = norm_tag(inner)
            if normalized_inner != inner:
                changes["tags"] += 1
            out.append(f"<{normalized_inner}>")
        else:
            # 数据行（任务时间、优先关系等）原样保留，仅去行尾空白
            out.append(raw.rstrip())

    # 去除尾部空行
    while out and out[-1] == "":
        out.pop()
        changes["end_cleaned"] = True

    # 确保唯一且位于末尾的 <end>；若原文件在中间已有 <end>，视为重复并移除
    had_end_inside = any(l == "<end>" for l in out)
    if had_end_inside:
        changes["end_cleaned"] = True
    out = [l for l in out if l != "<end>"]
    if not out or out[-1] != "<end>":
        out.append("<end>")
        changes["end_added"] = True

    return out, changes


def iter_target_files(project_filter=None, sample=False):
    projects = PROJECTS
    if project_filter:
        projects = [p for p in PROJECTS if p == project_filter]
        if not projects:
            print(f"[WARN] 项目未找到或不在 ALBP 族内: {project_filter}")
            return
    for proj in projects:
        base = os.path.join(ROOT, proj)
        if not os.path.isdir(base):
            print(f"[WARN] 目录不存在: {base}")
            continue
        for dirpath, _, fnames in os.walk(base):
            for fn in sorted(fnames):
                if not fn.lower().endswith(".txt"):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
                if sample and rel not in SAMPLE_FILES:
                    continue
                yield proj, rel, full


# 代表性样本（覆盖各格式变体），用于冒烟测试审阅
SAMPLE_FILES = {
    "Instances_SALBP1/Instances/instance_n=1000_1.txt",                       # 逗号优先关系 + order strength
    "Instances_DLBP1_with_OR_Predecessor/Instances_MO_SDLBP1/P10-40.txt",     # 三元组优先关系 + sequence dependencies + hazardous/demand
    "Instances_Cobot_ALBP2/Instances_Cycle_Ergonomics/P111_14.txt",           # 逗号优先关系 + 多机器人 + posture/energy/rigidity
    "Instances_Two_sided_DLBP1/Instances/P10_36.txt",                         # 三元组优先关系 + task directions
    "Instances_Robotic_ALB2/Instances/P111_13.txt",                           # 逗号优先关系 + limit of robots 块
    "Instances_Stochastic_ALBP1/Instances/instance_n=100_180_5.txt",          # 逗号优先关系 + mean/var
    "Instances_SALBP2/Instances_by_Scholl/P111_10_ARC.txt",                   # 无 <end> 块（测试补 <end>）
    "Instances_Robotic_Two_sided_ALBP2/Instances_with_Low_Setup/P12_4_1.txt", # <number of mated-station> 测试别名归一
}


def main():
    args = sys.argv[1:]
    sample = "--sample" in args
    project_filter = None
    for a in args:
        if a.startswith("--project="):
            project_filter = a.split("=", 1)[1]

    out_root = SAMPLE_OUT if sample else OUT_ROOT
    os.makedirs(out_root, exist_ok=True)

    total = 0
    changed = 0
    print(f"模式: {'sample' if sample else 'full'} | 输出根: {out_root}")
    print("-" * 80)
    for proj, rel, full in iter_target_files(project_filter, sample):
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        out_lines, ch = process_text(text)
        out_path = os.path.join(out_root, rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines) + "\n")
        total += 1
        did_change = ch["tags"] or ch["end_added"] or ch["end_cleaned"]
        if did_change:
            changed += 1
            print(f"[改] {rel}  | tags={ch['tags']} end_added={ch['end_added']} end_cleaned={ch['end_cleaned']}")
    print("-" * 80)
    print(f"完成：共处理 {total} 个文件，其中 {changed} 个被规范化。原文件未改动。")


if __name__ == "__main__":
    main()
