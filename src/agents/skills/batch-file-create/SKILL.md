---
name: batch-file-create
description: 批量新建指定格式的文件，支持自定义文件名模板、数量、文件类型，自动避免覆盖已有文件，适用于批量创建文档、模板文件等场景。
parameters:
  type: object
  properties:
    target_path:
      type: string
      description: 目标文件夹路径
    file_template:
      type: string
      description: 文件名模板，必须包含 {num} 占位符（如 "Report_{num}.txt"）
    create_count:
      type: integer
      description: 创建数量
    file_content:
      type: string
      description: 文件初始内容
    overwrite:
      type: boolean
      description: 是否覆盖同名文件
      default: false
  required:
    - target_path
    - file_template
    - create_count
compatibility: 支持 Windows/macOS/Linux，依赖 Python 3.6+，需文件系统读写权限。
metadata:
  version: "1.1"
  author: "Cool Agent"
  update_time: "2025-12-23"
---

# 批量新建文件技能

## 适用场景

- **周报/日志模板**：生成 `week_1.md` ~ `week_52.md`
- **配置文件初始化**：生成 `server_1.conf` ~ `server_10.conf`
- **测试数据生成**：生成一批带固定内容的测试文本

## 核心参数

1. `target_path` (string, required): 目标文件夹路径（如 "D:/Docs/Weekly"）
2. `file_template` (string, required): 文件名模板，必须包含 `{num}` 占位符（如 "Report\_{num}.txt"）
3. `create_count` (integer, required): 创建数量（如 5）
4. `file_content` (string, optional): 文件初始内容（默认空）
5. `overwrite` (boolean, optional): 是否覆盖同名文件（默认 False，跳过）

## 示例

**用户指令**: "帮我在桌面的 logs 文件夹下创建 10 个空的 log 文件，名字叫 test_1.log 到 test_10.log"
**对应参数**:

- target_path: "Desktop/logs"
- file*template: "test*{num}.log"
- create_count: 10
