import argparse
import os
import re


# ===================== 独立函数1：基础校验（复用场景：所有文件操作前的校验） =====================
# 🚨 功能：检查文件夹是否存在、筛选txt文件，返回「有效文件列表」或提示错误
def validate_folder_and_files(folder):
    """
    驗證文件夾有效性，並篩選出待處理的txt文件
    :param folder: 文件夾路徑
    :return: 有效txt文件列表（失敗返回None）
    """
    # 🚨 檢查文件夾是否存在
    if not os.path.isdir(folder):
        print(f"錯誤：文件夾 {folder} 不存在！")
        return None
    # 🚨 篩選txt文件，排除隱藏文件（如 .DS_Store）
    files = [f for f in os.listdir(folder) if f.endswith(".txt") and not f.startswith(".")]
    if not files:
        print("錯誤：文件夾里沒有txt文件！")
        return None
    return files

# ===================== 独立函数2：分类文件（复用场景：按规则拆分「保留/待重命名」文件） =====================
# 🚨 核心修改：精准区分「保留文件」和「待重命名文件」，避免误改原有带数字文件
def classify_files(files, prefix, pattern=r"\d+"):
    """
    分類文件：保留「前綴+數字.txt」的文件，其餘為待重命名文件
    :param files: 所有txt文件列表
    :param prefix: 新文件名前綴（如Document）
    :param pattern: 匹配數字的正則表達式
    :return: (reserved_files, to_rename_files) 保留文件列表、待重命名文件列表
    """
    reserved_files = []  # 无需重命名的文件（如Document_1.txt）
    to_rename_files = [] # 需要重命名的文件（如K.txt、哈.txt）

    # 🚨 遍歷所有文件，按「前綴+_+數字.txt」規則分類
    for file in files:
        # 🚨 正則匹配：嚴格匹配「前綴_數字.txt」格式（如Document_1.txt）
        match = re.search(rf"{prefix}_({pattern})\.txt", file)
        if match:
            reserved_files.append(file)  # 符合規則 → 保留
        else:
            to_rename_files.append(file) # 不符合 → 待重命名
    return reserved_files, to_rename_files

# ===================== 独立函数3：收集已用序号（复用场景：避免序号重复） =====================
# 🚨 功能：从「保留文件」中提取已用序号，生成「序号池」，避免新文件名重复
def collect_used_numbers(reserved_files, prefix, pattern=r"\d+"):
    """
    收集保留文件中已使用的數字序號，避免重命名時衝突
    :param reserved_files: 保留文件列表
    :param prefix: 文件名前綴
    :param pattern: 匹配數字的正則表達式
    :return: 已使用的序號集合（如{0,1}）
    """
    used_nums = set()
    for res_file in reserved_files:
        # 🚨 提取保留文件中的數字（如Document_1.txt → 1）
        num = re.search(rf"{prefix}_({pattern})\.txt", res_file).group(1)
        used_nums.add(int(num))
    return used_nums

# ===================== 独立函数4：生成重命名映射（复用场景：批量生成新旧文件名对应关系） =====================
# 🚨 核心修改：为待重命名文件分配「最小未使用序号」，避免重复
def generate_rename_mapping(folder, to_rename_files, prefix, used_nums):
    """
    生成「舊路徑→新路徑」的映射表，分配不重複的序號
    :param folder: 文件夾路徑
    :param to_rename_files: 待重命名文件列表
    :param prefix: 新文件名前綴
    :param used_nums: 已使用的序號集合
    :return: 重命名映射字典 {old_path: new_path}
    """
    rename_mapping = {}
    current_num = 0  # 從0開始分配序號

    for file in to_rename_files:
        old_path = os.path.join(folder, file)
        # 🚨 找到最小的未使用序號（如已用0、1 → 下一個用2）
        while current_num in used_nums:
            current_num += 1
        # 🚨 生成新文件名（如Document_2.txt）
        new_name = f"{prefix}_{current_num}.txt"
        new_path = os.path.join(folder, new_name)
        rename_mapping[old_path] = new_path
        # 🚨 標記該序號已使用，避免重複
        used_nums.add(current_num)
        current_num += 1
    return rename_mapping

# ===================== 独立函数5：执行重命名（复用场景：所有批量重命名操作） =====================
# 🚨 功能：执行重命名，带异常处理和详细日志，可单独复用
def execute_rename(rename_mapping):
    """
    執行重命名操作，返回成功/失敗數量
    :param rename_mapping: 重命名映射字典 {old_path: new_path}
    :return: (success, fail) 成功數量、失敗數量
    """
    success = 0
    fail = 0
    for old_path, new_path in rename_mapping.items():
        old_file = os.path.basename(old_path)
        new_file = os.path.basename(new_path)
        try:
            os.rename(old_path, new_path)
            print(f"成功：{old_file} → {new_file}")
            success += 1
        except Exception as e:
            print(f"失敗：{old_file} → {new_file} 錯誤：{e}")
            fail += 1
    return success, fail

# ===================== 独立函数6：主逻辑（复用场景：整合所有步骤，可直接调用） =====================
def batch_rename(folder, prefix="file", pattern=r"\d+"):
    """
    批量重命名主函數（整合所有獨立函數）
    :param folder: 文件夾路徑
    :param prefix: 新文件名前綴
    :param pattern: 匹配數字的正則表達式
    """
    # 步驟1：基礎校驗
    files = validate_folder_and_files(folder)
    if not files:
        return

    # 步驟2：分類文件（保留/待重命名）
    reserved_files, to_rename_files = classify_files(files, prefix, pattern)
    # 🚨 列印分類結果，讓用戶確認
    print("檢測到：")
    print(f"- 無需重命名的文件（保留原有名稱）：{reserved_files}")
    print(f"- 待重命名的文件：{to_rename_files}")
    print(f"\n即將重命名 {len(to_rename_files)} 個文件，是否繼續？(y/n)")
    confirm = input().strip().lower()
    if confirm != "y":
        print("操作取消！")
        return

    # 步驟3：收集已用序號
    used_nums = collect_used_numbers(reserved_files, prefix, pattern)

    # 步驟4：生成重命名映射
    rename_mapping = generate_rename_mapping(folder, to_rename_files, prefix, used_nums)

    # 步驟5：執行重命名
    success, fail = execute_rename(rename_mapping)

    # 步驟6：列印統計結果
    print("\n=== 重命名結果 ===")
    print(f"保留原有文件數：{len(reserved_files)}")
    print(f"待重命名文件數：{len(to_rename_files)}")
    print(f"重命名成功：{success} 個")
    print(f"重命名失敗：{fail} 個")

# ===================== 命令行入口（复用场景：直接运行脚本/其他脚本调用） =====================
if __name__ == "__main__":
    # 🚨 命令行參數解析（可單獨复用於其他命令行工具）
    parser = argparse.ArgumentParser(description="批量重命名工具（獨立函數版）")
    parser.add_argument("--folder", required=True, help="文件夾路徑")
    parser.add_argument("--prefix", default="file", help="新文件名前綴")
    args = parser.parse_args()
    # 調用主函數
    batch_rename(args.folder, args.prefix)
