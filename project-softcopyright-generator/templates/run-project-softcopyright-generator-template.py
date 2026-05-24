#!/usr/bin/env python3
"""
软著资料总入口模板

用途：
- 串联代码候选选择、申请表信息、系统说明文档、源代码文档的生成流程
- 在需要人工确认的阶段自动停止并给出下一步提示

主要配置字段：
- system_name
- short_name
- version
- project_root
- workdir
- draft_dir_name
- final_dir_name
"""

import importlib.util
import json
from pathlib import Path


WORKFLOW_CONFIG = {
    "system_name": "{system_name}",
    "short_name": "{system_short_name}",
    "version": "V1.0",
    "project_root": "D:/your-project",
    "workdir": None,
    "draft_dir_name": "草稿",
    "final_dir_name": "正式资料",
}


def load_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载模块: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_selection_config(config):
    workdir = resolve_workdir(config)
    draft_dir = workdir / config["draft_dir_name"]
    return {
        "system_name": config["system_name"],
        "project_root": config["project_root"],
        "workdir": str(workdir),
        "draft_dir_name": config["draft_dir_name"],
        "selection_output_path": str(draft_dir / "代码文件选择.json"),
        "candidate_output_path": str(draft_dir / "代码文件候选清单.md"),
    }


def build_application_config(config):
    workdir = resolve_workdir(config)
    return {
        "system_name": config["system_name"],
        "short_name": config["short_name"],
        "version": config["version"],
        "workdir": str(workdir),
        "draft_dir_name": config["draft_dir_name"],
        "final_dir_name": config["final_dir_name"],
        "draft_output_path": None,
        "final_output_path": None,
    }


def build_document_config(config):
    workdir = resolve_workdir(config)
    return {
        "system_name": config["system_name"],
        "short_name": config["short_name"],
        "version": config["version"],
        "workdir": str(workdir),
        "draft_dir_name": config["draft_dir_name"],
        "final_dir_name": config["final_dir_name"],
        "screenshot_placeholder_text": "【图片预留截图位置】",
        "completion_date": "待用户确认",
        "software_type": "待根据项目分析结果填写",
        "application_field": "待根据项目业务理解确认",
        "development_purpose": "待根据项目业务理解确认",
        "target_users": "待根据项目业务理解确认",
        "running_environment": ["待用户确认"],
        "development_tools": ["待用户确认"],
        "programming_languages": ["待根据项目分析结果填写"],
        "architecture_description": "待根据项目分析结果填写",
        "technical_features": ["待根据项目业务理解确认"],
        "modules": [],
        "business_flows": ["待根据项目业务理解确认"],
        "data_design": ["待根据项目分析结果填写"],
        "summary": "待根据项目分析结果填写",
        "draft_output_path": None,
    }


def build_source_config(config):
    workdir = resolve_workdir(config)
    draft_dir = workdir / config["draft_dir_name"]
    return {
        "system_name": config["system_name"],
        "version": config["version"],
        "workdir": str(workdir),
        "draft_dir_name": config["draft_dir_name"],
        "final_dir_name": config["final_dir_name"],
        "selection_file": str(draft_dir / "代码文件选择.json"),
        "draft_output_path": None,
    }


def build_print_docx_config(config):
    workdir = resolve_workdir(config)
    return {
        "system_name": config["system_name"],
        "workdir": str(workdir),
        "draft_dir_name": config["draft_dir_name"],
        "final_dir_name": config["final_dir_name"],
        "system_md_path": None,
        "source_md_path": None,
    }


def selection_is_confirmed(selection_file: Path):
    if not selection_file.exists():
        return False
    data = json.loads(selection_file.read_text(encoding="utf-8"))
    return bool(data.get("user_confirmed"))


def resolve_workdir(config):
    return Path(config["workdir"]) if config.get("workdir") else Path(config["project_root"]) / "软著资料"


def cleanup_final_dir(config):
    final_dir = resolve_workdir(config) / config["final_dir_name"]
    final_dir.mkdir(parents=True, exist_ok=True)
    removable_patterns = [
        "*.md",
        "*_软著申请信息.docx",
        "生成报告.md",
    ]
    for pattern in removable_patterns:
        for path in final_dir.glob(pattern):
            if path.is_file():
                path.unlink()


def run_workflow(config=None):
    settings = config or WORKFLOW_CONFIG
    template_dir = Path(__file__).resolve().parent

    selection_module = load_module(
        template_dir / "propose-code-selection-template.py",
        "project_softcopyright_generator_code_selection",
    )
    application_module = load_module(
        template_dir / "generate-application-info-template.py",
        "project_softcopyright_generator_application_info",
    )
    doc_module = load_module(
        template_dir / "generate-doc-template.py",
        "project_softcopyright_generator_document",
    )
    source_module = load_module(
        template_dir / "generate-source-template.py",
        "project_softcopyright_generator_source",
    )
    print_module = load_module(
        template_dir / "render-print-docx-template.py",
        "project_softcopyright_generator_print_docx",
    )

    selection_config = build_selection_config(settings)
    application_config = build_application_config(settings)
    document_config = build_document_config(settings)
    source_config = build_source_config(settings)
    print_docx_config = build_print_docx_config(settings)

    selection_file = Path(selection_config["selection_output_path"])

    if not selection_file.exists():
        selection_module.main(selection_config)
        print("⏸ 已生成代码候选清单与选择文件，请先填写并确认 `代码文件选择.json` 后再次运行。")
        return

    if not selection_is_confirmed(selection_file):
        print("⏸ 检测到 `代码文件选择.json` 尚未确认。")
        print("请在确认代码清单后再执行“继续生成正式资料”，系统才会生成申请表 TXT 与正式 DOCX。")
        return

    cleanup_final_dir(settings)
    application_module.create_application_info(application_config)
    doc_module.create_doc(document_config)
    source_module.create_source_doc(source_config)
    print_module.render_print_docx(print_docx_config)
    print("✅ 软著资料流程已完成。")


if __name__ == "__main__":
    run_workflow()
