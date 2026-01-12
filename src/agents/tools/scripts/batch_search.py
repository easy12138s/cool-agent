from src.utils.tool_utils import (
    compile_regex,
    init_search_replace_result,
    read_file_safe,
    walk_files,
)


def batch_search_files(
    search_path, keyword, is_regex=False, file_filter="", case_sensitive=False
):
    """
    批量搜索文件内容核心函数
    """
    result, allowed_exts = init_search_replace_result(search_path, file_filter)
    if result.get("error_msg"):
        return result

    pattern = None
    if is_regex:
        pattern = compile_regex(keyword, case_sensitive, result)
        if result["error_msg"]:
            return result

    def search_callback(file_path, filename):
        content = read_file_safe(file_path)
        if content is None:
            return

        matches = []
        if is_regex:
            matches = pattern.findall(content)
        else:
            if not case_sensitive:
                if keyword.lower() in content.lower():
                    matches = [keyword]
            else:
                if keyword in content:
                    matches = [keyword]

        if matches:
            result["matched_count"] += 1
            result["matched_files"].append(
                {"path": file_path, "match_preview": f"Found {len(matches)} matches"}
            )

    walk_files(search_path, allowed_exts, search_callback)

    # 限制返回数量
    if len(result["matched_files"]) > 100:
        result["matched_files"] = result["matched_files"][:100]

    return result


if __name__ == "__main__":
    # Test
    print(batch_search_files(".", "TODO", file_filter=".py"))
