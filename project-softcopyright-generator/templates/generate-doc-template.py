#!/usr/bin/env python3
"""
系统说明文档模板

用途：
- 根据已确认的软著口径和项目分析结果生成系统说明文档草稿 markdown
- 正式 docx 由内置打印模板统一转换生成

主要配置字段：
- system_name
- short_name
- version
- workdir
- draft_dir_name
- final_dir_name
- screenshot_placeholder_text
- draft_output_path
"""

from pathlib import Path


DOCUMENT_CONFIG = {
    "system_name": "{system_name}",
    "short_name": "{system_short_name}",
    "version": "V1.0",
    "workdir": "D:/your-project/软著资料",
    "draft_dir_name": "草稿",
    "final_dir_name": "正式资料",
    "screenshot_placeholder_text": "【图片预留截图位置】",
    "completion_date": "2026年05月24日",
    "software_type": "业务管理系统",
    "application_field": "企业信息化管理",
    "development_purpose": (
        "本系统用于提升业务流程的数字化、标准化与可追溯能力，"
        "帮助用户实现核心数据的统一管理、业务处理与结果分析。"
    ),
    "target_users": "管理员、业务人员、审核人员",
    "running_environment": [
        "操作系统：Windows 10/11 或 Linux",
        "运行环境：Python 3.11 / Node.js 20 / MySQL 8.0",
        "浏览器环境：Chrome、Edge",
    ],
    "development_tools": [
        "开发工具：Trae / Cursor / VS Code",
        "数据库工具：Navicat / DBeaver",
        "版本管理：Git",
    ],
    "programming_languages": ["Python", "JavaScript", "TypeScript", "SQL"],
    "architecture_description": (
        "系统采用分层架构设计，按照入口层、接口层、服务层、数据层和前端展示层进行组织。"
        "各模块职责清晰，通过统一配置、数据模型和业务服务协同完成系统功能。"
    ),
    "technical_features": [
        "基于真实项目代码生成软著资料，内容与源码保持一致。",
        "支持自动识别项目入口文件、核心模块与关键业务链路。",
        "支持在正式生成前先输出软著建议稿并等待用户确认。",
        "支持按前30页、后30页、每页60行的规则生成源代码文档。",
    ],
    "modules": [
        {
            "name": "系统管理模块",
            "description": "负责系统参数配置、账号管理、角色权限维护与基础信息管理。",
            "functions": [
                "维护系统基础配置和参数项",
                "管理用户账号、角色与权限分配",
                "记录关键操作日志，便于审计追踪",
            ],
        },
        {
            "name": "业务处理模块",
            "description": "负责核心业务数据的录入、校验、处理和状态流转。",
            "functions": [
                "支持业务数据新增、编辑、查询与状态变更",
                "通过服务层封装业务规则和处理逻辑",
                "对关键流程进行统一校验和异常处理",
            ],
        },
        {
            "name": "统计分析模块",
            "description": "负责对业务数据进行统计、汇总、展示和结果分析。",
            "functions": [
                "按条件生成数据汇总结果",
                "支持报表展示和趋势分析",
                "为管理决策提供数据依据",
            ],
        },
    ],
    "business_flows": [
        "用户登录系统后进入主页，根据角色权限访问对应功能模块。",
        "用户在业务模块中录入或维护数据，系统完成参数校验和业务处理。",
        "处理结果写入数据库后，由统计分析模块进行汇总、展示和查询。",
    ],
    "data_design": [
        "系统围绕用户、角色、业务对象、业务记录、日志记录等核心实体组织数据结构。",
        "数据层通过模型或数据访问层统一封装，保证读写逻辑的一致性。",
        "关键表之间通过主键、外键或业务标识进行关联，满足查询与追溯要求。",
    ],
    "summary": (
        "本系统基于真实项目代码整理生成系统说明资料，能够较为完整地反映软件的"
        "业务目标、功能结构、技术架构和实现特点，适合用于软件著作权登记材料编制。"
    ),
    "draft_output_path": None,
}


def append_report(report_path, lines):
    existing = report_path.read_text(encoding="utf-8") if report_path.exists() else "# 生成报告\n\n"
    if not existing.endswith("\n"):
        existing += "\n"
    report_path.write_text(existing + "\n".join(lines) + "\n", encoding="utf-8")


def add_bullet_lines(lines, items, ordered=False):
    for index, item in enumerate(items, start=1):
        prefix = f"{index}. " if ordered else "- "
        lines.append(f"{prefix}{item}")


def create_doc(project_info=None):
    info = project_info or DOCUMENT_CONFIG
    screenshot_placeholder_text = info.get("screenshot_placeholder_text", "【图片预留截图位置】")
    workdir = Path(info["workdir"])
    draft_dir = workdir / info["draft_dir_name"]
    draft_dir.mkdir(parents=True, exist_ok=True)

    output_path = Path(info["draft_output_path"]) if info.get("draft_output_path") else draft_dir / f"{info['system_name']}_系统说明文档.md"
    report_path = draft_dir / "生成报告.md"

    lines = [
        f"# {info['system_name']}系统说明文档",
        "",
        f"软件名称：{info['system_name']}",
        "",
        f"版本号：{info['version']}",
        "",
        "## 第一章 软件概述",
        "",
        "### 1.1 软件简介",
        f"{info['system_name']}是一套{info['software_type']}，主要面向{info['application_field']}场景。",
        "",
        "### 1.2 开发背景",
        info["development_purpose"],
        "",
        "### 1.3 开发目的",
        info["development_purpose"],
        "",
        "## 第二章 运行环境与开发环境",
        "",
        "### 2.1 运行环境",
    ]
    add_bullet_lines(lines, info["running_environment"])
    lines.extend(
        [
            "",
            "### 2.2 开发环境",
        ]
    )
    add_bullet_lines(lines, info["development_tools"])
    lines.extend(
        [
            "",
            f"编程语言：{'、'.join(info['programming_languages'])}",
            "",
            "## 第三章 系统总体架构",
            "",
            "### 3.1 架构组成",
            info["architecture_description"],
            "",
            "## 第四章 功能模块说明",
            "",
        ]
    )

    for index, module in enumerate(info["modules"], start=1):
        lines.extend(
            [
                f"### 4.{index} {module['name']}",
                module["description"],
                "",
                "#### 界面截图位置",
                screenshot_placeholder_text,
                "",
                "#### 主要功能",
            ]
        )
        add_bullet_lines(lines, module["functions"], ordered=True)
        lines.append("")

    lines.extend(
        [
            "## 第五章 关键业务流程说明",
            "",
        ]
    )
    add_bullet_lines(lines, info["business_flows"], ordered=True)
    lines.extend(
        [
            "",
            "## 第六章 数据设计说明",
            "",
        ]
    )
    add_bullet_lines(lines, info["data_design"])
    lines.extend(
        [
            "",
            "## 第七章 主要技术特点",
            "",
        ]
    )
    add_bullet_lines(lines, info["technical_features"], ordered=True)
    lines.extend(
        [
            "",
            "## 第八章 总结",
            "",
            info["summary"],
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    append_report(
        report_path,
        [
            "## 系统说明文档草稿",
            "",
            f"- 软件名称：{info['system_name']}",
            f"- 版本号：{info['version']}",
            f"- 草稿文件：`{output_path.name}`",
            "",
        ],
    )
    print(f"✅ 系统说明文档草稿已生成: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    create_doc()
