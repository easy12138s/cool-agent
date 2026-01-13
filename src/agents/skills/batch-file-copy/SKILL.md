---
name: batch-file-copy
description: 批量复制指定文件夹内的文件到目标路径，支持按文件类型/名称筛选，可选择是否包含子文件夹，并提供重复文件处理策略，适用于备份与归档场景。
parameters:
  type: object
  properties:
    source_path:
      type: string
      description: 源文件夹路径
    target_path:
      type: string
      description: 目标文件夹路径
    file_filter:
      type: string
      description: 筛选规则（后缀如 ".jpg" 或名称关键词）
    copy_subfolders:
      type: boolean
      description: 是否包含子文件夹
      default: false
    duplicate_strategy:
      type: string
      enum: ["rename", "overwrite", "skip"]
      description: 重复处理策略
      default: "rename"
  required:
    - source_path
    - target_path
compatibility: 支持 Windows/macOS/Linux，依赖 Python 3.6+，需文件系统读写权限。
metadata:
  version: "1.0"
  author: "Cool Agent"
  update_time: "2026-01-13"
---

# 批量复制文件技能

## 适用场景

- **备份文件**：将项目目录中的配置文件复制到备份目录
- **归档资料**：把下载目录中的 PDF 复制到归档目录（保留原文件）
- **按规则复制**：将包含关键词的文件复制到指定文件夹

## 示例

**用户指令**: "把下载目录中的所有 PDF 复制到 D 盘的 Archive 文件夹"

**对应参数**:

- source_path: "Downloads"
- target_path: "D:/Archive"
- file_filter: ".pdf"
