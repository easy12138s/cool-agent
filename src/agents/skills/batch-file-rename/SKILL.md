---
name: batch-file-rename
description: 批量重命名指定文件夹内的文件，支持添加前缀/后缀、文本替换、序号命名等规则，自动处理重复文件名，适用于文件整理、归档场景。
parameters:
  type: object
  properties:
    source_path:
      type: string
      description: 目标文件夹路径
    rename_rule:
      type: string
      enum: ["add_prefix", "add_suffix", "replace_text", "add_sequence"]
      description: 重命名规则
    rule_params:
      type: string
      description: 规则参数（前缀/后缀字符串，或替换规则如 "old:new"，或起始序号）
    file_filter:
      type: string
      description: 文件类型筛选（如 ".jpg,.png"）
  required:
    - source_path
    - rename_rule
    - rule_params
compatibility: 支持 Windows/macOS/Linux，依赖 Python 3.6+，需文件系统读写权限。
metadata:
  version: "1.1"
  author: "Cool Agent"
  update_time: "2025-12-23"
---

# 批量重命名文件技能
## 适用场景
- **照片整理**：添加日期前缀（"IMG_001.jpg" -> "2024_IMG_001.jpg"）
- **格式修正**：统一替换错误字符（"文档-最终版.doc" -> "文档_v1.doc"）
- **序列化**：将乱序文件重命名为有序列表（"file_a.txt", "file_b.txt" -> "doc_1.txt", "doc_2.txt"）

## 核心参数
1. `source_path` (string, required): 目标文件夹
2. `rename_rule` (enum, required):
   - "add_prefix": 加前缀
   - "add_suffix": 加后缀
   - "replace_text": 文本替换
   - "add_sequence": 序号命名
3. `rule_params` (any, required):
   - 前/后缀: 字符串
   - 替换: [旧词, 新词]
   - 序号: 起始数字 (int)
4. `file_filter` (string, optional): 文件类型筛选

## 示例
**用户指令**: "给这个文件夹里的所有图片加个前缀 'Holiday_'"
**对应参数**:
- source_path: "Photos"
- rename_rule: "add_prefix"
- rule_params: "Holiday_"
- file_filter: ".jpg,.png"
