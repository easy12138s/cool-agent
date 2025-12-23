import os
import re

def batch_search_files(search_path, keyword, is_regex=False, file_filter="", case_sensitive=False):
    """
    批量搜索文件内容核心函数
    :param search_path: 搜索根目录
    :param keyword: 搜索关键词
    :param is_regex: 是否正则
    :param file_filter: 文件筛选
    :param case_sensitive: 是否区分大小写
    :return: 执行报告
    """
    result = {
        "matched_count": 0,
        "matched_files": [],
        "error_msg": ""
    }

    if not os.path.exists(search_path):
        result["error_msg"] = f"路径不存在：{search_path}"
        return result

    # 预处理筛选条件
    allowed_exts = [e.lower() for e in file_filter.split(",") if e.strip()] if file_filter else []
    
    # 预编译正则（如果需要）
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = None
    if is_regex:
        try:
            pattern = re.compile(keyword, flags)
        except re.error as e:
            result["error_msg"] = f"无效的正则表达式：{e}"
            return result

    for root, _, files in os.walk(search_path):
        for file in files:
            # 筛选扩展名
            ext = os.path.splitext(file)[1].lower()
            if allowed_exts and ext not in allowed_exts:
                continue

            file_path = os.path.join(root, file)
            
            try:
                # 读取文件（尝试 UTF-8，回退到 Latin-1）
                content = ""
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except:
                        continue # 无法读取，跳过

                matches = []
                if is_regex:
                    matches = pattern.findall(content)
                else:
                    if not case_sensitive:
                        if keyword.lower() in content.lower():
                            matches = [keyword] # 简单标记匹配
                    else:
                        if keyword in content:
                            matches = [keyword]

                if matches:
                    result["matched_count"] += 1
                    result["matched_files"].append({
                        "path": file_path,
                        "match_preview": f"Found {len(matches)} matches"
                    })
                    
                    if len(result["matched_files"]) >= 100: # 限制返回数量
                        return result

            except Exception as e:
                continue

    return result

if __name__ == "__main__":
    # Test
    print(batch_search_files(".", "TODO", file_filter=".py"))
