from src.utils.tool_utils import (
    add_failed_file,
    compile_regex,
    init_search_replace_result,
    walk_files,
)


def batch_replace_text(search_path, old_text, new_text, file_filter="", is_regex=False):
    """
    批量替换文件内容核心函数
    """
    result, allowed_exts = init_search_replace_result(search_path, file_filter)
    if result.get("error_msg"):
        return result

    pattern = None
    if is_regex:
        pattern = compile_regex(old_text, True, result)
        if result["error_msg"]:
            return result

    def replace_callback(file_path, filename):
        result["processed_count"] += 1
        try:
            # 这里需要知道原始编码以写回，read_file_safe 不够用，我们需要带编码的读取
            content = None
            encoding = "utf-8"
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                encoding = "latin-1"
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()

            if content is None:
                return

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
                with open(file_path, "w", encoding=encoding) as f:
                    f.write(new_content)
                result["modified_count"] += 1

        except Exception as e:
            add_failed_file(result, filename, str(e))

    walk_files(search_path, allowed_exts, replace_callback)
    return result


def run(
    search_path: str,
    old_text: str,
    new_text: str,
    file_filter: str = "",
    is_regex: bool = False,
):
    return batch_replace_text(
        search_path=search_path,
        old_text=old_text,
        new_text=new_text,
        file_filter=file_filter,
        is_regex=is_regex,
    )


if __name__ == "__main__":
    # Test
    pass
