import os
import shutil

def batch_rename_files(source_path, rename_rule, rule_params, file_filter=""):
    """
    批量重命名文件核心函数
    :param source_path: 源文件夹路径
    :param rename_rule: 重命名规则（add_prefix/add_suffix/replace_text/add_sequence）
    :param rule_params: 规则参数（对应不同规则）
    :param file_filter: 文件类型筛选（如 ".txt,.pdf"）
    :return: 执行报告（字典）
    """
    # 初始化返回结果
    result = {
        "success_count": 0,
        "failed_files": [],
        "rename_map": {},  # 原文件名: 新文件名
        "error_msg": ""
    }

    # 1. 校验源路径
    if not os.path.exists(source_path):
        result["error_msg"] = f"源路径不存在：{source_path}"
        return result
    if not os.access(source_path, os.W_OK):
        result["error_msg"] = f"无写入权限：{source_path}"
        return result

    # 2. 解析文件筛选规则
    allowed_extensions = [ext.lower() for ext in file_filter.split(",") if ext.strip()] if file_filter else []

    # 3. 遍历文件
    file_list = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
    sequence = rule_params if rename_rule == "add_sequence" else 1  # 序号起始值

    for filename in file_list:
        # 筛选文件类型
        file_ext = os.path.splitext(filename)[1].lower()
        if allowed_extensions and file_ext not in allowed_extensions:
            continue

        # 跳过隐藏文件（macOS/Linux）
        if filename.startswith("."):
            continue

        # 生成新文件名
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

            # 处理重复文件名
            new_file_path = os.path.join(source_path, new_filename)
            counter = 1
            while os.path.exists(new_file_path):
                new_filename = f"{name}_{sequence}_{counter}{ext}" if rename_rule == "add_sequence" else f"{name}_{counter}{ext}"
                new_file_path = os.path.join(source_path, new_filename)
                counter += 1

            # 执行重命名
            old_file_path = os.path.join(source_path, filename)
            os.rename(old_file_path, new_file_path)
            result["success_count"] += 1
            result["rename_map"][filename] = new_filename

        except Exception as e:
            result["failed_files"].append({
                "file": filename,
                "reason": str(e)
            })

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