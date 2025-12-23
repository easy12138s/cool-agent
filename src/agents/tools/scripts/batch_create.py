import os
from .utils import init_batch_result, ensure_dir, add_failed_file

def batch_create_files(target_path, file_template, create_count, file_content="", overwrite=False):
    """
    批量新建文件核心函数
    """
    result = init_batch_result()
    result["created_files"] = []

    if not isinstance(create_count, int) or create_count <= 0:
        result["error_msg"] = "创建数量必须为正整数"
        return result

    if not ensure_dir(target_path, result):
        return result

    for i in range(1, create_count + 1):
        filename = file_template.replace("{num}", str(i))
        illegal_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        for char in illegal_chars:
            filename = filename.replace(char, "_")
        
        file_path = os.path.join(target_path, filename)

        try:
            if os.path.exists(file_path):
                if not overwrite:
                    result["skipped_count"] += 1
                    continue
                else:
                    bak_path = f"{file_path}.bak"
                    if os.path.exists(bak_path):
                        os.remove(bak_path)
                    os.rename(file_path, bak_path)
                    result["overwritten_count"] += 1

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            
            result["success_count"] += 1
            result["created_files"].append(filename)

        except Exception as e:
            add_failed_file(result, filename, str(e))

    return result

if __name__ == "__main__":
    test_result = batch_create_files(
        target_path="/Users/yourname/Desktop/test",
        file_template="week_{num}.md",
        create_count=3,
        file_content="# 周报模板\n## 本周完成：\n## 下周计划："
    )
    print("执行结果：", test_result)