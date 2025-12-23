---
name: batch-file-move
description: 批量移动指定文件夹内的文件到目标路径，支持按文件类型/名称筛选，自动处理重复文件，适用于文件分类、归档场景。
compatibility: 支持 Windows/macOS/Linux，依赖 Python 3.6+，需文件系统读写权限。
metadata:
  version: "1.1"
  author: "Cool Agent"
  update_time: "2025-12-23"
---

# 批量移动文件技能
## 适用场景
- **文件归档**：将下载文件夹中的所有 PDF 移动到 "文档/PDF"
- **清理桌面**：将桌面上的截图（.png）移动到 "图片/截图"
- **项目整理**：将包含 "v1" 的旧版本文件移入 "Archive" 文件夹

## 核心参数
1. `source_path` (string, required): 源文件夹路径
2. `target_path` (string, required): 目标文件夹路径
3. `file_filter` (string, optional): 筛选规则
   - 按后缀: ".jpg,.png"
   - 按名称: "report_"
   - 留空: 所有文件
4. `move_subfolders` (boolean, optional): 是否包含子文件夹（默认 False）
5. `duplicate_strategy` (enum, optional): 重复处理 ("rename", "overwrite", "skip")，默认 "rename"

## 示例
**用户指令**: "把下载目录里的所有压缩包（zip, rar）移动到 D 盘的 Software 文件夹"
**对应参数**:
- source_path: "Downloads"
- target_path: "D:/Software"
- file_filter: ".zip,.rar"
