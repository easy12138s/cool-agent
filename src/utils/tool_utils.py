import os
import re
from typing import List, Dict, Any, Optional, Callable

def init_batch_result() -> Dict[str, Any]:
    """初始化批量操作的标准结果字典"""
    return {
        "success_count": 0,
        "skipped_count": 0,
        "overwritten_count": 0,
        "failed_files": [],
        "error_msg": ""
    }

def validate_path(path: str, result_dict: Dict[str, Any]) -> bool:
    """验证路径是否存在，若不存在则填充错误信息"""
    if not os.path.exists(path):
        result_dict["error_msg"] = f"路径不存在：{path}"
        return False
    return True

def ensure_dir(path: str, result_dict: Dict[str, Any]) -> bool:
    """确保目录存在，不存在则创建"""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            result_dict["error_msg"] = f"创建文件夹失败：{str(e)}"
            return False
    return True

def get_allowed_exts(file_filter: str) -> List[str]:
    """解析逗号分隔的文件过滤器"""
    return [e.lower() for e in file_filter.split(",") if e.strip()] if file_filter else []

def compile_regex(keyword: str, case_sensitive: bool, result_dict: Dict[str, Any]) -> Optional[re.Pattern]:
    """编译正则表达式，处理异常"""
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        return re.compile(keyword, flags)
    except re.error as e:
        result_dict["error_msg"] = f"无效的正则表达式：{e}"
        return None

def read_file_safe(file_path: str) -> Optional[str]:
    """安全读取文件，支持多种编码"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return None
    except Exception:
        return None

def walk_files(
    search_path: str, 
    allowed_exts: List[str], 
    callback: Callable[[str, str], None]
):
    """遍历文件并应用回调"""
    for root, _, files in os.walk(search_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if allowed_exts and ext not in allowed_exts:
                continue
            
            file_path = os.path.join(root, file)
            callback(file_path, file)

def add_failed_file(result_dict: Dict[str, Any], filename: str, reason: str):
    """添加失败文件记录"""
    result_dict["failed_files"].append({
        "file": filename,
        "reason": reason
    })

def init_search_replace_result(search_path: str, file_filter: str) -> Optional[tuple[Dict[str, Any], List[str]]]:
    """初始化搜索/替换操作的结果和过滤器，并执行路径验证"""
    result = {
        "processed_count": 0,
        "matched_count": 0,
        "modified_count": 0,
        "failed_files": [],
        "error_msg": ""
    }
    
    if not validate_path(search_path, result):
        return result, None
        
    allowed_exts = get_allowed_exts(file_filter)
    return result, allowed_exts
