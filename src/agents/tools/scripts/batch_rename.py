import os
from .utils import validate_path, get_allowed_exts, add_failed_file

def batch_rename_files(source_path, rename_rule, rule_params, file_filter=""):
    """
    批量重命名文件核心函数
    """
    result = {
        "success_count": 0,
        "failed_files": [],
        "rename_map": {},  # 原文件名: 新文件名
        "error_msg": ""
    }

    if not validate_path(source_path, result):
        return result
    if not os.access(source_path, os.W_OK):
        result["error_msg"] = f"无写入权限：{source_path}"
        return result

    allowed_extensions = get_allowed_exts(file_filter)

    file_list = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
    sequence = rule_params if rename_rule == "add_sequence" else 1

    for filename in file_list:
        file_ext = os.path.splitext(filename)[1].lower()
        if allowed_extensions and file_ext not in allowed_extensions:
            continue

        if filename.startswith("."):
            continue

        name, ext = os.path.splitext(filename)
        new_filename = filename

        try:
            if rename_rule == "add_prefix":
                new_filename = f"{rule_params}{filename}"
            elif rename_rule == "add_suffix":
                new_filename = f"{name}{rule_params}{ext}"
            elif rename_rule == "replace_text":
                old_text, new_text = rule_params
                new_filename = filename.replace(old_text, new_text)
            elif rename_rule == "add_sequence":
                new_filename = f"{name}_{sequence}{ext}"
                sequence += 1

            new_file_path = os.path.join(source_path, new_filename)
            counter = 1
            while os.path.exists(new_file_path):
                # 避免死循环，如果新旧路径一致则跳过
                if os.path.join(source_path, filename) == new_file_path:
                    break
                new_filename = f"{name}_{sequence}_{counter}{ext}" if rename_rule == "add_sequence" else f"{name}_{counter}{ext}"
                new_file_path = os.path.join(source_path, new_filename)
                counter += 1

            if new_filename != filename:
                old_file_path = os.path.join(source_path, filename)
                os.rename(old_file_path, new_file_path)
                result["success_count"] += 1
                result["rename_map"][filename] = new_filename

        except Exception as e:
            add_failed_file(result, filename, str(e))

    return result

if __name__ == "__main__":
    # 测试：给桌面test文件夹的txt文件添加前缀
    test_result = batch_rename_files(
        source_path="/Users/yourname/Desktop/test",
        rename_rule="add_prefix",
        rule_params="20240520_",
        file_filter=".txt"
    )
    print("执行结果：", test_result)