#!/usr/bin/env python3
"""
申请表信息模板

用途：
- 根据已确认的软著口径生成申请表信息草稿
- 输出草稿版 `申请表信息.md` 和正式版 `软著申请信息.txt`

主要配置字段：
- system_name
- short_name
- version
- workdir
- draft_dir_name
- final_dir_name
- draft_output_path
- final_output_path
"""

from pathlib import Path


APPLICATION_CONFIG = {
    "system_name": "{system_name}",
    "short_name": "{system_short_name}",
    "version": "V1.0",
    "workdir": "D:/your-project/软著资料",
    "draft_dir_name": "草稿",
    "final_dir_name": "正式资料",
    "draft_output_path": None,
    "final_output_path": None,
    "fields": [
        ("软件全称", "{system_name}"),
        ("软件简称", "{system_short_name}"),
        ("版本号", "V1.0"),
        ("著作权人", "待用户确认"),
        ("开发完成日期", "待用户确认"),
        ("首次发表日期", "待用户确认"),
        ("开发的硬件环境", "待用户确认"),
        ("运行的硬件环境", "待用户确认"),
        ("开发该软件的操作系统", "待用户确认"),
        ("软件开发环境 / 开发工具", "Visual Studio Code / Cursor"),
        ("该软件的运行平台 / 操作系统", "Windows 10/11 或 Linux"),
        ("软件运行支撑环境 / 支持软件", "Node.js / Python / 数据库 / 浏览器"),
        ("编程语言", "Python、JavaScript、TypeScript、SQL"),
        ("源程序量", "待根据项目分析结果填写"),
        ("开发目的", "待根据项目业务理解确认"),
        ("面向领域 / 行业", "待根据项目业务理解确认"),
        ("软件的主要功能", "待根据项目业务理解确认"),
        ("技术特点", "待根据项目业务理解确认"),
        ("页数", "60 页代码文档"),
        ("软件分类", "应用软件"),
    ],
}


def append_report(report_path, lines):
    existing = report_path.read_text(encoding="utf-8") if report_path.exists() else "# 生成报告\n\n"
    if not existing.endswith("\n"):
        existing += "\n"
    report_path.write_text(existing + "\n".join(lines) + "\n", encoding="utf-8")


def normalize_fields(config):
    normalized = []
    for key, value in config["fields"]:
        if value == "{system_name}":
            value = config["system_name"]
        elif value == "{system_short_name}":
            value = config["short_name"]
        normalized.append((key, value))
    return normalized


def write_markdown(draft_output_path, fields):
    lines = ["# 申请表信息", ""]
    for key, value in fields:
        lines.append(f"- {key}：{value}")
    lines.append("")
    draft_output_path.write_text("\n".join(lines), encoding="utf-8")


def write_text(final_output_path, fields):
    lines = []
    for key, value in fields:
        lines.append(f"{key}：{value}")
    lines.append("")
    final_output_path.write_text("\n".join(lines), encoding="utf-8")


def create_application_info(config=None):
    settings = config or APPLICATION_CONFIG
    workdir = Path(settings["workdir"])
    draft_dir = workdir / settings["draft_dir_name"]
    final_dir = workdir / settings["final_dir_name"]
    draft_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    draft_output_path = (
        Path(settings["draft_output_path"])
        if settings["draft_output_path"]
        else draft_dir / "申请表信息.md"
    )
    final_output_path = (
        Path(settings["final_output_path"])
        if settings["final_output_path"]
        else final_dir / f"{settings['system_name']}_软著申请信息.txt"
    )

    fields = normalize_fields(settings)
    pending_fields = [key for key, value in fields if "待用户确认" in str(value)]

    write_markdown(draft_output_path, fields)
    write_text(final_output_path, fields)

    append_report(
        draft_dir / "生成报告.md",
        [
            "## 申请表信息",
            "",
            f"- 软件名称：{settings['system_name']}",
            f"- 版本号：{settings['version']}",
            f"- 草稿文件：`{draft_output_path.name}`",
            f"- 正式文件：`{final_output_path.name}`",
            f"- 待确认字段数：{len(pending_fields)}",
            "",
        ],
    )

    if pending_fields:
        print("⚠️ 提示：以下字段仍待用户确认：")
        for field in pending_fields:
            print(f"- {field}")

    print(f"✅ 已生成申请表草稿: {draft_output_path}")
    print(f"✅ 已生成申请表文本: {final_output_path}")
    return str(draft_output_path), str(final_output_path)


if __name__ == "__main__":
    create_application_info()
