#!/usr/bin/env python3
"""
源代码文档模板

用途：
- 根据已确认的代码选择结果生成源代码文档草稿 markdown
- 正式 docx 由内置打印模板统一转换生成

主要配置字段：
- system_name
- version
- workdir
- draft_dir_name
- final_dir_name
- selection_file
- draft_output_path
"""

import json
from pathlib import Path


LINES_PER_PAGE = 60
PAGES_PER_SECTION = 30
TARGET_LINES_PER_SECTION = LINES_PER_PAGE * PAGES_PER_SECTION

SOURCE_CONFIG = {
    "system_name": "{system_name}",
    "version": "V1.0",
    "workdir": "D:/your-project/软著资料",
    "draft_dir_name": "草稿",
    "final_dir_name": "正式资料",
    "selection_file": "D:/your-project/软著资料/草稿/代码文件选择.json",
    "draft_output_path": None,
}


def append_report(report_path, lines):
    existing = report_path.read_text(encoding="utf-8") if report_path.exists() else "# 生成报告\n\n"
    if not existing.endswith("\n"):
        existing += "\n"
    report_path.write_text(existing + "\n".join(lines) + "\n", encoding="utf-8")


def read_lines(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def read_selection_config(selection_file):
    path = Path(selection_file)
    if not path.exists():
        raise FileNotFoundError(f"代码选择文件不存在: {selection_file}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("代码选择文件格式错误，顶层必须为 JSON 对象。")
    project_root = data.get("project_root")
    files = data.get("files")
    if not project_root or not isinstance(files, list):
        raise ValueError("代码选择文件缺少 project_root 或 files 字段。")
    if data.get("confirmation_required") and not data.get("user_confirmed"):
        raise ValueError("代码选择文件尚未确认，请先完成人工确认再生成源代码文档。")
    return Path(project_root), files


def collect_selected_chunks(project_root, selection_items, target_lines=TARGET_LINES_PER_SECTION * 2):
    collected = []
    total_lines = 0

    for file_info in selection_items:
        if not isinstance(file_info, dict) or not file_info.get("selected"):
            continue

        relative_path = file_info.get("path")
        if not relative_path:
            continue

        file_path = project_root / relative_path
        start_line = max(int(file_info.get("start_line", 1) or 1), 1)
        end_line = file_info.get("end_line")

        lines = read_lines(file_path)
        actual_end_line = end_line if end_line else len(lines)
        selected = lines[start_line - 1 : actual_end_line]

        if not selected:
            continue

        remaining = target_lines - total_lines
        if remaining <= 0:
            break

        taken = selected[:remaining]
        taken_end = start_line + len(taken) - 1

        collected.append(
            {
                "path": Path(relative_path).as_posix(),
                "start_line": start_line,
                "end_line": taken_end,
                "lines": taken,
            }
        )
        total_lines += len(taken)

    return collected, total_lines


def split_chunks_for_sections(chunks):
    first_section = []
    second_section = []
    first_total = 0
    second_total = 0

    for chunk in chunks:
        first_lines = []
        remaining_first = TARGET_LINES_PER_SECTION - first_total
        if remaining_first > 0:
            first_lines = chunk["lines"][:remaining_first]
            if first_lines:
                first_section.append(
                    {
                        "path": chunk["path"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["start_line"] + len(first_lines) - 1,
                        "lines": first_lines,
                    }
                )
                first_total += len(first_lines)

        remaining_second = TARGET_LINES_PER_SECTION - second_total
        second_start_index = len(first_lines)
        second_lines = chunk["lines"][second_start_index : second_start_index + remaining_second]
        if second_lines:
            second_section.append(
                {
                    "path": chunk["path"],
                    "start_line": chunk["start_line"] + second_start_index,
                    "end_line": chunk["start_line"] + second_start_index + len(second_lines) - 1,
                    "lines": second_lines,
                }
            )
            second_total += len(second_lines)

        if first_total >= TARGET_LINES_PER_SECTION and second_total >= TARGET_LINES_PER_SECTION:
            break

    return first_section, first_total, second_section, second_total


def append_chunk_pages(lines, chunks, start_page_number):
    page_number = start_page_number
    for chunk in chunks:
        page_line_count = 0
        current_page_lines = []
        current_start_line = chunk["start_line"]

        for offset, line in enumerate(chunk["lines"]):
            current_page_lines.append(line)
            page_line_count += 1
            if page_line_count >= LINES_PER_PAGE:
                lines.extend(
                    [
                        f"#### 第 {page_number} 页",
                        f"### 文件：{chunk['path']} ({current_start_line}-{current_start_line + len(current_page_lines) - 1})",
                        "```",
                        *current_page_lines,
                        "```",
                        "",
                    ]
                )
                page_number += 1
                current_start_line = chunk["start_line"] + offset + 1
                page_line_count = 0
                current_page_lines = []

        if current_page_lines:
            lines.extend(
                [
                    f"#### 第 {page_number} 页",
                    f"### 文件：{chunk['path']} ({current_start_line}-{current_start_line + len(current_page_lines) - 1})",
                    "```",
                    *current_page_lines,
                    "```",
                    "",
                ]
            )
            page_number += 1

    return page_number


def create_source_doc(plan=None):
    config = plan or SOURCE_CONFIG
    workdir = Path(config["workdir"])
    draft_dir = workdir / config["draft_dir_name"]
    draft_dir.mkdir(parents=True, exist_ok=True)
    draft_output_path = Path(config["draft_output_path"]) if config.get("draft_output_path") else draft_dir / f"{config['system_name']}_源代码文档.md"
    report_path = draft_dir / "生成报告.md"
    project_root, selection_items = read_selection_config(config["selection_file"])
    selected_chunks, selected_total = collect_selected_chunks(project_root, selection_items)
    if not selected_chunks:
        raise ValueError("代码选择文件中没有已选中的源码，无法生成源代码文档。")
    first_chunks, first_total, second_chunks, second_total = split_chunks_for_sections(selected_chunks)
    lines = [f"# {config['system_name']}源代码文档", ""]
    next_page = append_chunk_pages(lines, first_chunks, 1)
    append_chunk_pages(lines, second_chunks, next_page)

    draft_output_path.write_text("\n".join(lines), encoding="utf-8")
    append_report(
        report_path,
        [
            "## 源代码文档草稿",
            "",
            f"- 软件名称：{config['system_name']}",
            f"- 版本号：{config['version']}",
            f"- 代码选择文件：`{Path(config['selection_file']).name}`",
            f"- 项目根目录：`{project_root}`",
            f"- 已选源码总行数：{selected_total}",
            f"- 前30页代码行数：{first_total}",
            f"- 后30页代码行数：{second_total}",
            f"- 草稿文件：`{draft_output_path.name}`",
            "",
        ],
    )
    print(f"✅ 源代码文档草稿已生成: {draft_output_path}")

    if first_total < TARGET_LINES_PER_SECTION or second_total < TARGET_LINES_PER_SECTION:
        print("⚠️ 提示：当前配置的连续代码不足目标行数，请补充文件或调整起止行范围。")

    return str(draft_output_path)


if __name__ == "__main__":
    create_source_doc()
