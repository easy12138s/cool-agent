import os
import shutil

from src.utils.tool_utils import (
    add_failed_file,
    ensure_dir,
    init_batch_result,
    validate_path,
)


def batch_copy_files(
    source_path,
    target_path,
    file_filter="",
    copy_subfolders=False,
    duplicate_strategy="rename",
):
    result = init_batch_result()
    result["copied_files"] = []

    if not validate_path(source_path, result):
        return result
    if not os.access(source_path, os.R_OK):
        result["error_msg"] = f"无读取源路径权限：{source_path}"
        return result

    if not ensure_dir(target_path, result):
        return result

    filter_parts = (
        [f.strip().lower() for f in file_filter.split(",") if f.strip()]
        if file_filter
        else []
    )

    def walk_root(path: str):
        return [(path, [], os.listdir(path))]

    walk_func = os.walk if copy_subfolders else walk_root
    for root, _, files in walk_func(source_path):
        if not copy_subfolders and root != source_path:
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
            rel_path = os.path.relpath(source_file, source_path)
            target_file = os.path.join(target_path, rel_path)

            try:
                target_dir = os.path.dirname(target_file)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)

                if os.path.exists(target_file):
                    if duplicate_strategy == "skip":
                        result["skipped_count"] += 1
                        continue
                    if duplicate_strategy == "overwrite":
                        os.remove(target_file)
                        result["overwritten_count"] += 1
                    elif duplicate_strategy == "rename":
                        base_dir = os.path.dirname(target_file)
                        name, ext = os.path.splitext(os.path.basename(target_file))
                        counter = 1
                        while os.path.exists(target_file):
                            target_file = os.path.join(
                                base_dir, f"{name}-副本{counter}{ext}"
                            )
                            counter += 1

                shutil.copy2(source_file, target_file)
                result["success_count"] += 1
                result["copied_files"].append(f"{source_file} → {target_file}")

            except Exception as e:
                add_failed_file(result, filename, str(e))

    return result


def run(
    source_path: str,
    target_path: str,
    file_filter: str = "",
    copy_subfolders: bool = False,
    duplicate_strategy: str = "rename",
):
    return batch_copy_files(
        source_path=source_path,
        target_path=target_path,
        file_filter=file_filter,
        copy_subfolders=copy_subfolders,
        duplicate_strategy=duplicate_strategy,
    )

