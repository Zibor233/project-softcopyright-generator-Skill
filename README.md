# Project SoftCopyright Generator

一个面向真实项目代码的软著资料生成 Skill。

`Project SoftCopyright Generator` 用于读取本地项目代码，分析项目结构、功能模块、技术栈与关键源码，并生成适合软件著作权登记使用的申请信息、系统说明文档和源代码文档。

本项目重点解决以下问题：

- 已有真实项目代码，但整理软著资料耗时且容易漏项
- 文档口径不统一，申请信息、系统说明、代码文档经常需要反复修改
- 代码文档抽取规则复杂，前 30 页、后 30 页、每页 60 行不易手工控制
- 正式资料排版繁琐，容易在最终导出阶段再次返工

## 项目特点

- 基于本地真实项目代码生成软著资料，而不是依赖虚构示例
- 支持先分析项目、先给建议、先确认，再进入正式资料生成
- 支持代码候选清单与选择 JSON，便于人工审核代码抽取范围
- 支持系统说明文档中的 `【图片预留截图位置】`
- 支持源代码文档按前 30 页、后 30 页、每页 60 行的规则组织
- 支持正式资料目录与草稿目录分离，便于实际交付
- 内置 markdown / txt 到 docx 的排版转换模板，不依赖临时脚本

## 适用场景

- 已完成开发的本地项目，需要整理软件著作权登记资料
- 企业项目、外包项目、SaaS 项目、内部管理系统等已有代码仓库的场景
- 希望把软著资料整理流程标准化、模板化、可复用化的团队

## 仓库结构

```text
.
├─ project-softcopyright-generator/
│  ├─ SKILL.md
│  ├─ references/
│  │  ├─ application-fields.md
│  │  └─ design-spec.md
│  └─ templates/
│     ├─ generate-application-info-template.py
│     ├─ generate-doc-template.py
│     ├─ generate-source-template.py
│     ├─ propose-code-selection-template.py
│     ├─ render-print-docx-template.py
│     └─ run-project-softcopyright-generator-template.py
└─ README.md
```

## 工作流程

`Project SoftCopyright Generator` 的核心流程如下：

1. 读取本地项目代码
2. 分析目录结构、入口文件、核心模块、技术栈
3. 输出软著建议稿
4. 等待用户确认软件名称、版本号、功能描述等信息
5. 生成代码文件候选清单与代码文件选择 JSON
6. 等待用户确认代码抽取方案
7. 用户明确回复“确认，继续生成正式资料”
8. 生成正式资料

## 输出目录规范

推荐在项目根目录下创建 `软著资料` 目录，结构如下：

```text
<项目根目录>/
└─ 软著资料/
   ├─ 草稿/
   │  ├─ 软著建议稿.md
   │  ├─ 申请表信息.md
   │  ├─ 代码文件候选清单.md
   │  ├─ 代码文件选择.json
   │  ├─ xxx_系统说明文档.md
   │  ├─ xxx_源代码文档.md
   │  └─ 生成报告.md
   └─ 正式资料/
      ├─ xxx_系统说明文档.docx
      ├─ xxx_源代码文档.docx
      └─ xxx_软著申请信息.txt
```

说明：

- `草稿/` 目录用于保留建议稿、中间稿、代码清单和生成报告
- `正式资料/` 目录只保留最终提交所需正式文件
- 系统说明文档和源代码文档先生成 markdown 草稿，再转换为 docx
- 申请表正式稿只保留 `.txt`，不额外生成 `.docx`

## 模板文件说明

### 1. `run-project-softcopyright-generator-template.py`

总入口脚本，用于串联整套流程：

- 首次运行时生成 `代码文件候选清单.md` 和 `代码文件选择.json`
- 当选择文件已确认后，再继续生成申请表、系统说明草稿、源代码草稿和正式 docx

### 2. `propose-code-selection-template.py`

用于扫描项目源码并生成代码候选文件清单。

### 3. `generate-application-info-template.py`

用于生成：

- `草稿/申请表信息.md`
- `正式资料/xxx_软著申请信息.txt`

### 4. `generate-doc-template.py`

用于生成：

- `草稿/xxx_系统说明文档.md`

并在功能模块中保留：

- `【图片预留截图位置】`

### 5. `generate-source-template.py`

用于根据已确认的代码选择结果生成：

- `草稿/xxx_源代码文档.md`

内容按前 30 页、后 30 页、每页 60 行组织。

### 6. `render-print-docx-template.py`

用于将草稿目录中的：

- `xxx_系统说明文档.md`
- `xxx_源代码文档.md`

转换为正式资料目录中的：

- `xxx_系统说明文档.docx`
- `xxx_源代码文档.docx`

## 使用方式

### 方式一：通过总入口模板执行

使用：

- `templates/run-project-softcopyright-generator-template.py`

推荐流程：

1. 提供本地项目目录
2. 生成代码候选清单
3. 确认代码抽取方案
4. 回复“确认，继续生成正式资料”
5. 输出正式资料

### 方式二：拆分模板执行

如果需要更细粒度控制，也可以分步骤使用模板：

1. `propose-code-selection-template.py`
2. `generate-application-info-template.py`
3. `generate-doc-template.py`
4. `generate-source-template.py`
5. `render-print-docx-template.py`

## 设计原则

- 先读项目，后写资料
- 先给建议，后做确认
- 以真实源码为准，不虚构内容
- 正式资料与草稿分层管理
- 正式排版必须复用内置模板，不临时生成额外脚本

## 当前版本能力

- 项目分析与建议稿输出
- 代码候选清单生成
- 申请表信息生成
- 系统说明文档草稿生成
- 源代码文档草稿生成
- docx 正式排版输出

## 后续优化方向

- 更严格的申请表字段校验
- 更智能的代码区段推荐
- 更多提交场景下的 docx 排版细节优化
- 更完整的真实项目实测样例

## 开源说明

本项目适合发布到 GitHub 和 Gitee，建议搭配以下内容一起维护：

- `README.md`
- 开源许可证文件
- 示例截图或演示文档
- 版本更新记录

如果你准备对外发布，建议后续再补充：

- `LICENSE`
- `CHANGELOG.md`
- 示例输入输出截图
- 常见问题说明

## License

当前 `SKILL.md` 中声明为 `MIT`，如正式开源，建议在仓库根目录补充标准 `MIT LICENSE` 文件。
