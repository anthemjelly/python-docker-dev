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

    # 只处理txt文件，且过滤掉隐藏文件（可选）
    files = [f for f in os.listdir(folder) if f.endswith(".txt") and not f.startswith(".")]


    if not files:
        print("错误：文件夹里没有txt文件！")
        return

    # 2. 第一步：筛选并保留「原有带数字且前缀匹配」的文件（不参与重命名）
    reserved_files = []  # 存储无需重命名的文件
    to_rename_files = [] # 存储需要重命名的无数字文件
    for file in files:
        # 提取文件名中的数字（仅匹配前缀+_+数字的格式）
        match = re.search(rf"{prefix}_({pattern})\.txt", file)
        if match:
            reserved_files.append(file)  # 如Document_1.txt，直接保留
        else:
            to_rename_files.append(file) # 如aaa.txt，需要重命名

    # 3. 用户确认
    print("检测到：")
    print(f"- 无需重命名的文件（保留原有名称）：{reserved_files}")
    print(f"- 待重命名的文件：{to_rename_files}")
    print(f"\n即将重命名 {len(to_rename_files)} 个文件，是否继续？(y/n)")
    confirm = input().strip().lower()
    if confirm != "y":
        print("操作取消！")
        return


# 4. 为待重命名文件分配「不重复的递增序号」
    rename_mapping = {}
    used_nums = set()  # 记录已使用的序号（避免冲突）

    # 先收集原有保留文件的序号
    for res_file in reserved_files:
        num = re.search(rf"{prefix}_({pattern})\.txt", res_file).group(1)
        used_nums.add(int(num))

    # 为无数字文件分配最小可用序号
    current_num = 0
    for file in to_rename_files:
        old_path = os.path.join(folder, file)
        # 找到未被使用的最小序号
        while current_num in used_nums:
            current_num += 1
        # 生成新文件名（无重复）
        new_name = f"{prefix}_{current_num}.txt"
        new_path = os.path.join(folder, new_name)
        rename_mapping[old_path] = new_path
        # 标记该序号已使用
        used_nums.add(current_num)
        current_num += 1


    # 第四步：执行重命名（异常处理+统计）
    success = 0
    fail = 0
    for old_path, new_path in rename_mapping.items():
        old_file = os.path.basename(old_path)
        new_file = os.path.basename(new_path)
        try:
            # 跳过新旧路径相同的情况（避免无意义操作）
            if old_path == new_path:
                print(f"跳过 {old_file}：新文件名与原文件名相同")
                success += 1
                continue
            os.rename(old_path, new_path)
            print(f"成功：{old_file} → {new_file}")
            success += 1
        except Exception as e:
            print(f"失败：{old_file} → {new_file} 错误：{e}")
            fail += 1

    # 最终统计
    print("\n=== 重命名结果 ===")
    print(f"总计文件数：{len(files)}")
    print(f"成功：{success} 个")
    print(f"失败：{fail} 个")

# 用argparse支持命令行传参（比如运行时输入：python rename.py --folder 路径 --prefix 测试）
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量重命名工具")
    parser.add_argument("--folder", required=True, help="文件夹路径")
    parser.add_argument("--prefix", default="file", help="新文件名前缀")
    args = parser.parse_args()
    batch_rename(args.folder, args.prefix)
