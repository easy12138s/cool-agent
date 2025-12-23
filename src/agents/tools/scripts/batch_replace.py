import os
import re

def batch_replace_text(search_path, old_text, new_text, file_filter="", is_regex=False):
    """
    批量替换文件内容核心函数
    :param search_path: 搜索根目录
    :param old_text: 旧文本
    :param new_text: 新文本
    :param file_filter: 文件筛选
    :param is_regex: 是否正则
    :return: 执行报告
    """
    result = {
        "processed_count": 0,
        "modified_count": 0,
        "failed_files": [],
        "error_msg": ""
    }

    if not os.path.exists(search_path):
        result["error_msg"] = f"路径不存在：{search_path}"
        return result

    allowed_exts = [e.lower() for e in file_filter.split(",") if e.strip()] if file_filter else []
    
    # 预编译正则
    pattern = None
    if is_regex:
        try:
            pattern = re.compile(old_text)
        except re.error as e:
            result["error_msg"] = f"无效的正则表达式：{e}"
            return result

    for root, _, files in os.walk(search_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if allowed_exts and ext not in allowed_exts:
                continue

            file_path = os.path.join(root, file)
            result["processed_count"] += 1

            try:
                # 读取内容
                content = ""
                encoding = 'utf-8'
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        encoding = 'latin-1'
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except:
                        continue

                # 检查并替换
                new_content = content
                modified = False
                
                if is_regex:
                    if pattern.search(content):
                        new_content = pattern.sub(new_text, content)
                        modified = new_content != content
                else:
                    if old_text in content:
                        new_content = content.replace(old_text, new_text)
                        modified = True

                if modified:
                    # 写入回文件
                    with open(file_path, 'w', encoding=encoding) as f:
                        f.write(new_content)
                    result["modified_count"] += 1

            except Exception as e:
                result["failed_files"].append({
                    "path": file_path,
                    "reason": str(e)
                })

    return result

if __name__ == "__main__":
    # Test
    pass
