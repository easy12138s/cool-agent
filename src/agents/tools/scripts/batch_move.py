import os
import shutil
from src.utils.tool_utils import init_batch_result, validate_path, ensure_dir, add_failed_file

def batch_move_files(source_path, target_path, file_filter="", move_subfolders=False, duplicate_strategy="rename"):
    """
    批量移动文件核心函数
    """
    result = init_batch_result()
    result["moved_files"] = []

    if not validate_path(source_path, result):
        return result
    if not os.access(source_path, os.R_OK):
        result["error_msg"] = f"无读取源路径权限：{source_path}"
        return result

    if not ensure_dir(target_path, result):
        return result

    filter_parts = [f.strip().lower() for f in file_filter.split(",") if f.strip()] if file_filter else []

    walk_func = os.walk if move_subfolders else lambda p: [(p, [], os.listdir(p))]
    for root, dirs, files in walk_func(source_path):
        if not move_subfolders and root != source_path:
            continue

        for filename in files:
            file_lower = filename.lower()
            if filter_parts:
                match = False
                for f in filter_parts:
                    if f.startswith("."):
                        if file_lower.endswith(f):
                            match = True
                            break
                    else:
                        if f in file_lower:
                            match = True
                            break
                if not match:
                    continue

            source_file = os.path.join(root, filename)
            target_file = os.path.join(target_path, filename)

            try:
                if os.path.exists(target_file):
                    if duplicate_strategy == "skip":
                        result["skipped_count"] += 1
                        continue
                    elif duplicate_strategy == "overwrite":
                        os.remove(target_file)
                        result["overwritten_count"] += 1
                    elif duplicate_strategy == "rename":
                        name, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(target_file):
                            target_file = os.path.join(target_path, f"{name}-副本{counter}{ext}")
                            counter += 1

                if os.path.splitdrive(source_file)[0] != os.path.splitdrive(target_file)[0]:
                    shutil.copy2(source_file, target_file)
                    os.remove(source_file)
                else:
                    shutil.move(source_file, target_file)

                result["success_count"] += 1
                result["moved_files"].append(f"{source_file} → {target_file}")

            except Exception as e:
                add_failed_file(result, filename, str(e))

    return result


if __name__ == "__main__":
    test_result = batch_move_files(
        source_path="/Users/yourname/Desktop/test",
        target_path="/Users/yourname/Desktop/pdf_files",
        file_filter=".pdf",
        duplicate_strategy="rename"
    )
    print("执行结果：", test_result)