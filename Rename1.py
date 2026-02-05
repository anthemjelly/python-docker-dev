import argparse
import os
import re


def get_unique_filename(folder, base_name, ext=".txt"):
    """
    生成不重复的文件名（解决覆盖问题）
    :param folder: 文件夹路径
    :param base_name: 基础文件名（如Document_0）
    :param ext: 文件扩展名
    :return: 唯一的文件名（如Document_0_1.txt）
    """
    new_name = f"{base_name}{ext}"
    new_path = os.path.join(folder, new_name)
    counter = 1
    # 若文件已存在，自动加序号（如Document_0_1.txt、Document_0_2.txt）
    while os.path.exists(new_path):
        new_name = f"{base_name}_{counter}{ext}"
        new_path = os.path.join(folder, new_name)
        counter += 1
    return new_name

def batch_rename(folder, prefix="file", pattern=r"\d+"):

    """
    批量重命名文件
    :param folder: 文件夹路径
    :param prefix: 新文件名前缀
    :param pattern: 正则表达式，提取原文件名中的特征（比如数字）
    """

    # 第一步：检查文件夹是否存在（防呆）
    if not os.path.isdir(folder):
        print(f"错误：文件夹 {folder} 不存在！")
        return

    files = [f for f in os.listdir(folder) if f.endswith(".txt")]

    if not files:
        print("错误：文件夹里没有txt文件！")
        return

    # 第二步：让用户确认（避免误操作）
    print(f"即将重命名 {len(files)} 个文件，是否继续？(y/n)")
    confirm = input().strip().lower()
    if confirm != "y":
        print("操作取消！")
        return

    # 第三步：异常处理（文件被占用时跳过）
    success = 0
    fail = 0
    for file in files:
        old_path = os.path.join(folder, file)
        # 用正则提取原文件名中的数字（比如原文件是"文档123.txt"，提取123）
        match = re.search(pattern, file)
        num = match.group() if match else "0"
        new_name = f"{prefix}_{num}.txt"
        new_path = os.path.join(folder, new_name)
        try:
            os.rename(old_path, new_path)
            success += 1
        except Exception as e:
            print(f"重命名 {file} 失败：{e}")
            fail += 1

    print(f"完成！重命名了{len(files)}个文件")

# 用argparse支持命令行传参（比如运行时输入：python rename.py --folder 路径 --prefix 测试）
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量重命名工具")
    parser.add_argument("--folder", required=True, help="文件夹路径")
    parser.add_argument("--prefix", default="file", help="新文件名前缀")
    args = parser.parse_args()
    batch_rename(args.folder, args.prefix)
