import os
import shutil

def batch_move_files(source_path, target_path, file_filter="", move_subfolders=False, duplicate_strategy="rename"):
    """
    批量移动文件核心函数
    :param source_path: 源文件夹路径
    :param target_path: 目标文件夹路径
    :param file_filter: 文件筛选规则（类型/名称）
    :param move_subfolders: 是否移动子文件夹
    :param duplicate_strategy: 重复文件处理策略（rename/overwrite/skip）
    :return: 执行报告（字典）
    """
    # 初始化返回结果
    result = {
        "success_count": 0,
        "skipped_count": 0,
        "overwritten_count": 0,
        "failed_files": [],
        "moved_files": [],
        "error_msg": ""
    }

    # 1. 校验源路径
    if not os.path.exists(source_path):
        result["error_msg"] = f"源路径不存在：{source_path}"
        return result
    if not os.access(source_path, os.R_OK):
        result["error_msg"] = f"无读取源路径权限：{source_path}"
        return result

    # 2. 确保目标路径存在
    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except Exception as e:
            result["error_msg"] = f"创建目标文件夹失败：{str(e)}"
            return result

    # 3. 解析筛选规则
    filter_parts = [f.strip().lower() for f in file_filter.split(",") if f.strip()] if file_filter else []

    # 4. 遍历文件（递归/非递归）
    walk_func = os.walk if move_subfolders else lambda p: [(p, [], os.listdir(p))]
    for root, dirs, files in walk_func(source_path):
        # 跳过子文件夹（若不允许移动）
        if not move_subfolders and root != source_path:
            continue

        for filename in files:
            # 筛选文件
            file_lower = filename.lower()
            if filter_parts:
                # 按类型/名称筛选
                match = False
                for f in filter_parts:
                    if f.startswith("."):  # 按类型
                        if file_lower.endswith(f):
                            match = True
                            break
                    else:  # 按名称
                        if f in file_lower:
                            match = True
                            break
                if not match:
                    continue

            # 拼接路径
            source_file = os.path.join(root, filename)
            target_file = os.path.join(target_path, filename)

            try:
                # 处理重复文件
                if os.path.exists(target_file):
                    if duplicate_strategy == "skip":
                        result["skipped_count"] += 1
                        continue
                    elif duplicate_strategy == "overwrite":
                        os.remove(target_file)
                        result["overwritten_count"] += 1
                    elif duplicate_strategy == "rename":
                        # 生成新文件名（添加-副本）
                        name, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(target_file):
                            target_file = os.path.join(target_path, f"{name}-副本{counter}{ext}")
                            counter += 1

                # 执行移动（跨磁盘用copy+delete，同磁盘用rename）
                if os.path.splitdrive(source_file)[0] != os.path.splitdrive(target_file)[0]:
                    shutil.copy2(source_file, target_file)
                    os.remove(source_file)
                else:
                    shutil.move(source_file, target_file)

                result["success_count"] += 1
                result["moved_files"].append(f"{source_file} → {target_file}")

            except Exception as e:
                result["failed_files"].append({
                    "file": source_file,
                    "reason": str(e)
                })

    return result


if __name__ == "__main__":
    test_result = batch_move_files(
        source_path="/Users/yourname/Desktop/test",
        target_path="/Users/yourname/Desktop/pdf_files",
        file_filter=".pdf",
        duplicate_strategy="rename"
    )
    print("执行结果：", test_result)