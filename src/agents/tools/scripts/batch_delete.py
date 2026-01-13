import os

from src.utils.tool_utils import add_failed_file, init_batch_result, validate_path


def batch_delete_files(
    target_path,
    file_filter="",
    delete_subfolders=False,
    dry_run=True,
    max_delete=200,
):
    result = init_batch_result()
    result["deleted_files"] = []
    result["would_delete_files"] = []
    result["would_delete_count"] = 0

    if not validate_path(target_path, result):
        return result
    if not os.path.isdir(target_path):
        result["error_msg"] = f"目标路径不是文件夹：{target_path}"
        return result
    if not os.access(target_path, os.W_OK):
        result["error_msg"] = f"无写入权限：{target_path}"
        return result

    if not isinstance(max_delete, int) or max_delete <= 0:
        result["error_msg"] = "max_delete 必须为正整数"
        return result

    filter_parts = (
        [f.strip().lower() for f in file_filter.split(",") if f.strip()]
        if file_filter
        else []
    )

    def walk_root(path: str):
        return [(path, [], os.listdir(path))]

    walk_func = os.walk if delete_subfolders else walk_root
    delete_candidates = []

    for root, _, files in walk_func(target_path):
        if not delete_subfolders and root != target_path:
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

            delete_candidates.append(os.path.join(root, filename))

    if len(delete_candidates) > max_delete:
        delete_candidates = delete_candidates[:max_delete]

    result["would_delete_count"] = len(delete_candidates)
    if dry_run:
        result["would_delete_files"] = delete_candidates
        return result

    for file_path in delete_candidates:
        try:
            os.remove(file_path)
            result["success_count"] += 1
            result["deleted_files"].append(file_path)
        except Exception as e:
            add_failed_file(result, os.path.basename(file_path), str(e))

    return result


def run(
    target_path: str,
    file_filter: str = "",
    delete_subfolders: bool = False,
    dry_run: bool = True,
    max_delete: int = 200,
):
    return batch_delete_files(
        target_path=target_path,
        file_filter=file_filter,
        delete_subfolders=delete_subfolders,
        dry_run=dry_run,
        max_delete=max_delete,
    )

