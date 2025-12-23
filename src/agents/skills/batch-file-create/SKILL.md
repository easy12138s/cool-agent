---
name: batch-file-create
description: 批量新建指定格式的文件，支持自定义文件名模板、数量、文件类型，自动避免覆盖已有文件，适用于批量创建文档、模板文件等场景。
compatibility: 支持 Windows/macOS/Linux，依赖 Python 3.6+，需文件系统读写权限。
metadata:
  version: "1.0"
  author: "Custom AI Agent"
  update_time: "2025-12-23"
---

# 批量新建文件技能
## 适用场景
当需要快速创建多个格式统一的文件时使用，例如：
- 批量创建10个空白的周报模板（week_1.md ~ week_10.md）；
- 创建多个分类的txt文档（分类A.txt、分类B.txt）；
- 生成带固定内容的配置文件（config_1.ini ~ config_5.ini）。

## 核心参数（用户需提供）
1. `target_path`：必填，新建文件的目标文件夹路径（绝对路径/相对路径均可）；
2. `file_template`：必填，文件名模板（支持 {num} 占位符表示序号，如 "week_{num}.md"）；
3. `create_count`：必填，新建文件数量（正整数，如 10）；
4. `file_content`：可选，文件初始内容（留空则创建空白文件）；
5. `overwrite`：可选，是否覆盖已有文件（默认 False，避免误操作）。

## 执行步骤
1. 校验用户输入：确认 `target_path` 存在且有读写权限，`create_count` 为正整数；
2. 生成待创建的文件名列表：
   - 替换模板中的 {num} 为连续序号（从1开始）；
   - 例如模板 "week_{num}.md" + 数量3 → week_1.md、week_2.md、week_3.md；
3. 校验文件名合法性：跳过含非法字符（如 /、\、:、*）的文件名；
4. 处理重复文件：
   - 若 `overwrite=False`：跳过已存在的文件，记录为“已跳过”；
   - 若 `overwrite=True`：先备份原有文件（添加 .bak 后缀），再覆盖；
5. 逐个创建文件：写入 `file_content`（若有），确保文件编码为 UTF-8；
6. 返回执行报告：成功创建数量、跳过/覆盖数量、失败文件（含原因）、文件列表。

## 注意事项
1. 文件名模板仅支持 {num} 一个占位符（简化逻辑）；
2. 支持的文件类型：txt、md、ini、csv、json 等文本文件（暂不支持二进制文件）；
3. 若目标文件夹不存在，自动创建（需用户确认）；
4. 单个文件内容大小限制为 10MB（避免内存溢出）。