import os

def batch_create_files(target_path, file_template, create_count, file_content="", overwrite=False):
    """
    批量新建文件核心函数
    :param target_path: 目标文件夹路径
    :param file_template: 文件名模板（含{num}占位符）
    :param create_count: 新建数量
    :param file_content: 文件初始内容
    :param overwrite: 是否覆盖已有文件
    :return: 执行报告（字典）
    """
    # 初始化返回结果
    result = {
        "success_count": 0,
        "skipped_count": 0,
        "overwritten_count": 0,
        "failed_files": [],
        "created_files": [],
        "error_msg": ""
    }

    # 1. 校验参数
    if not isinstance(create_count, int) or create_count <= 0:
        result["error_msg"] = "创建数量必须为正整数"
        return result

    # 2. 确保目标文件夹存在
    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except Exception as e:
            result["error_msg"] = f"创建目标文件夹失败：{str(e)}"
            return result

    # 3. 批量创建文件
    for i in range(1, create_count + 1):
        # 生成文件名
        filename = file_template.replace("{num}", str(i))
        # 校验文件名合法性（简化版，仅过滤非法字符）
        illegal_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        for char in illegal_chars:
            filename = filename.replace(char, "_")
        
        file_path = os.path.join(target_path, filename)

        try:
            # 处理重复文件
            if os.path.exists(file_path):
                if not overwrite:
                    result["skipped_count"] += 1
                    continue
                else:
                    # 备份原有文件
                    bak_path = f"{file_path}.bak"
                    os.rename(file_path, bak_path)
                    result["overwritten_count"] += 1

            # 创建文件并写入内容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            
            result["success_count"] += 1
            result["created_files"].append(filename)

        except Exception as e:
            result["failed_files"].append({
                "file": filename,
                "reason": str(e)
            })

    return result

if __name__ == "__main__":
    test_result = batch_create_files(
        target_path="/Users/yourname/Desktop/test",
        file_template="week_{num}.md",
        create_count=3,
        file_content="# 周报模板\n## 本周完成：\n## 下周计划："
    )
    print("执行结果：", test_result)