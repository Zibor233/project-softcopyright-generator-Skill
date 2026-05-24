#!/usr/bin/env python3
"""
代码候选选择模板

用途：
- 扫描项目源码，生成代码候选清单和可编辑的代码选择文件
- 作为正式代码抽取前的候选整理与人工确认入口

主要配置字段：
- system_name
- project_root
- workdir
- draft_dir_name
- selection_output_path
- candidate_output_path
"""

import json
from pathlib import Path


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".cs",
    ".php",
    ".rb",
    ".rs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".vue",
    ".sql",
}

SKIP_DIRS = {
    "node_modules",
    "dist",
    "build",
    ".git",
    ".idea",
    ".vscode",
    ".next",
    "coverage",
    "tmp",
    "logs",
}

LINES_PER_PAGE = 60
TARGET_PAGES = 60

CODE_SELECTION_CONFIG = {
    "system_name": "{system_name}",
    "project_root": "D:/your-project",
    "workdir": "D:/your-project/软著资料",
    "draft_dir_name": "草稿",
    "selection_output_path": None,
    "candidate_output_path": None,
}


def should_skip_path(path: Path):
    return any(part in SKIP_DIRS for part in path.parts)


def read_line_count(path: Path):
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except Exception:
        return 0


def determine_priority(relative_path: str):
    normalized = relative_path.replace("\\", "/").lower()
    name = Path(relative_path).name.lower()

    if name in {"main.py", "app.py", "main.js", "main.ts", "main.tsx", "app.tsx", "server.js"}:
        return 0, "入口文件证据"
    if "/routes/" in normalized or "/router/" in normalized or "routes." in normalized:
        return 10, "路由文件证据"
    if "/pages/" in normalized or "/views/" in normalized or "/screens/" in normalized:
        return 20, "页面文件证据"
    if "/api/" in normalized or "/services/" in normalized:
        return 30, "数据交互文件证据"
    if "/store/" in normalized or "/stores/" in normalized or "/redux/" in normalized:
        return 40, "状态管理文件证据"
    if "/components/" in normalized:
        return 50, "组件文件证据"
    if "/utils/" in normalized or "/lib/" in normalized or "/hooks/" in normalized:
        return 60, "通用能力文件证据"
    if any(key in normalized for key in ["/backend/", "/server/", "/models/", "/schemas/", "/controllers/"]):
        return 70, "后端核心文件证据"
    return 80, "补充源码证据"


def build_candidates(project_root: Path):
    candidates = []
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_path(path):
            continue
        if path.suffix.lower() not in CODE_EXTENSIONS:
            continue

        relative_path = path.relative_to(project_root).as_posix()
        line_count = read_line_count(path)
        priority, evidence = determine_priority(relative_path)
        candidates.append(
            {
                "path": relative_path,
                "selected": False,
                "start_line": 1,
                "end_line": None,
                "line_count": line_count,
                "priority": priority,
                "evidence": evidence,
                "model_reason": "",
            }
        )

    candidates.sort(key=lambda item: (item["priority"], item["path"]))
    return candidates


def estimated_pages(candidates):
    total_lines = sum((item.get("line_count") or 0) + 2 for item in candidates)
    return (total_lines + LINES_PER_PAGE - 1) // LINES_PER_PAGE if total_lines else 0


def write_selection_json(output_path: Path, project_root: Path, candidates):
    data = {
        "project_root": str(project_root.resolve()),
        "selection_required": True,
        "model_selection_required": True,
        "confirmation_required": True,
        "user_confirmed": False,
        "target_pages": TARGET_PAGES,
        "lines_per_page": LINES_PER_PAGE,
        "estimated_all_candidate_pages": estimated_pages(candidates),
        "next_action": "请先由模型填写 selected/start_line/end_line/model_reason，再由用户确认。",
        "files": candidates,
    }
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_selection_md(output_path: Path, candidates):
    lines = [
        "# 代码文件候选清单",
        "",
        "本清单只列出候选源码证据，不默认决定最终抽取文件。",
        "请先由模型根据项目业务和源码职责填写 `selected`、`start_line`、`end_line`、`model_reason`，再让用户确认。",
        "",
        "## 候选文件",
        "",
        "| 文件 | 行数 | 证据类型 | 默认说明 |",
        "| --- | ---: | --- | --- |",
    ]

    for item in candidates:
        lines.append(
            f"| `{item['path']}` | {item['line_count']} | {item['evidence']} | 待模型判断是否抽取 |"
        )

    lines.extend(
        [
            "",
            "## 使用规则",
            "",
            "1. 不要默认抽取整个代码库。",
            "2. 优先选择最能体现软件真实功能和运行逻辑的源码文件。",
            "3. 如只想抽取某个文件的一部分，可填写 `start_line` 和 `end_line`。",
            "4. 代码抽取时必须以 `代码文件选择.json` 为准。",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(config=None):
    settings = config or CODE_SELECTION_CONFIG
    project_root = Path(settings["project_root"])
    workdir = Path(settings["workdir"])
    draft_dir = workdir / settings["draft_dir_name"]
    draft_dir.mkdir(parents=True, exist_ok=True)

    if not project_root.exists():
        raise SystemExit(f"项目目录不存在: {project_root}")

    selection_output_path = Path(settings["selection_output_path"]) if settings["selection_output_path"] else draft_dir / "代码文件选择.json"
    candidate_output_path = Path(settings["candidate_output_path"]) if settings["candidate_output_path"] else draft_dir / "代码文件候选清单.md"

    candidates = build_candidates(project_root)
    write_selection_json(selection_output_path, project_root, candidates)
    write_selection_md(candidate_output_path, candidates)

    print(f"✅ 已生成代码候选清单: {candidate_output_path}")
    print(f"✅ 已生成代码选择文件: {selection_output_path}")
    print("下一步：请由模型填写选择结果，再由用户确认。")


if __name__ == "__main__":
    main()
