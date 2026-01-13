---
name: batch-file-delete
description: 批量删除指定文件夹内的文件，支持按文件类型/名称筛选，可选择是否包含子文件夹，支持 dry_run 预演，适用于清理临时文件与无用文件场景。
parameters:
  type: object
  properties:
    target_path:
      type: string
      description: 目标文件夹路径
    file_filter:
      type: string
      description: 筛选规则（后缀如 ".log" 或名称关键词）
    delete_subfolders:
      type: boolean
      description: 是否包含子文件夹
      default: false
    dry_run:
      type: boolean
      description: 是否仅预演不实际删除
      default: true
    max_delete:
      type: integer
      description: 最多删除数量限制
      default: 200
  required:
    - target_path
compatibility: 支持 Windows/macOS/Linux，依赖 Python 3.6+，需文件系统读写权限。
metadata:
  version: "1.0"
  author: "Cool Agent"
  update_time: "2026-01-13"
---

# 批量删除文件技能

## 适用场景

- **清理日志**：删除某目录下的 .log 文件
- **清理临时文件**：删除包含 "~"、"tmp" 的文件
- **清理重复下载**：删除包含 "副本" 关键词的文件（需谨慎）

## 示例

**用户指令**: "先看看桌面目录里有哪些 .log 文件会被删除"

**对应参数**:

- target_path: "Desktop"
- file_filter: ".log"
- dry_run: true
