import hashlib
import os
import sys


def calculate_file_md5(file_path):
    """计算单个文件的MD5值"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"计算文件 {file_path} 的MD5时出错: {str(e)}")
        return None


def build_md5_dict(folder_path):
    """构建MD5字典，键为MD5值，值为文件绝对路径列表"""
    md5_dict = {}
    folder_abs_path = os.path.abspath(folder_path)

    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return None, folder_abs_path

    print(f"正在计算文件夹 '{folder_abs_path}' 中文件的MD5值...")

    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            md5_hash = calculate_file_md5(file_path)

            if md5_hash:
                # 使用绝对路径作为文件名
                abs_file_path = os.path.abspath(file_path)

                # 如果MD5值已存在，添加到列表；否则创建新列表
                if md5_hash in md5_dict:
                    md5_dict[md5_hash].append(abs_file_path)
                else:
                    md5_dict[md5_hash] = [abs_file_path]

                file_count += 1

    print(f"已完成 {file_count} 个文件的MD5计算")
    return md5_dict, folder_abs_path


def compare_folders_md5(folder1_path, folder2_path):
    """比较两个文件夹的MD5值"""
    # 构建两个文件夹的MD5字典
    dict1, folder1_abs = build_md5_dict(folder1_path)
    if dict1 is None:
        return

    dict2, folder2_abs = build_md5_dict(folder2_path)
    if dict2 is None:
        return

    # 存储比较结果
    success_files = []  # 校验成功的文件
    fail_files_dict1 = []  # 在文件夹1中校验失败的文件
    fail_files_dict2 = []  # 在文件夹2中校验失败的文件

    print("\n" + "=" * 60)
    print("校验开始")
    print("=" * 60)

    # 校验文件夹1的文件
    print(f"\n校验{folder1_abs}的md5值:")
    for md5_value, file_list in dict1.items():
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            if md5_value in dict2:
                print(f"\t✅  {file_name}  |  {md5_value}  校验成功")
                success_files.append({
                    'file': file_path,
                    'md5': md5_value,
                    'folder': folder1_abs
                })
            else:
                print(f"\t❌  {file_name}  |  {md5_value}  校验失败")
                fail_files_dict1.append({
                    'file': file_path,
                    'md5': md5_value
                })

    # 校验文件夹2的文件
    print(f"\n校验{folder2_abs}的md5值:")
    for md5_value, file_list in dict2.items():
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            if md5_value in dict1:
                print(f"\t✅  {file_name}  |  {md5_value}  校验成功")
                success_files.append({
                    'file': file_path,
                    'md5': md5_value,
                    'folder': folder2_abs
                })
            else:
                print(f"\t❌  {file_name}  |  {md5_value}  校验失败")
                fail_files_dict2.append({
                    'file': file_path,
                    'md5': md5_value
                })

    # 输出总计
    print("\n" + "=" * 60)
    print("总计")
    print("=" * 60)

    # 计算唯一的成功文件数（按MD5值去重）
    unique_success_md5 = set()
    for item in success_files:
        unique_success_md5.add(item['md5'])

    print(f"文件夹1和2中校验成功的文件数量为{len(unique_success_md5)}个")

    # 输出校验失败的文件
    if fail_files_dict1 or fail_files_dict2:
        print("\n校验失败的有:")

        if fail_files_dict1:
            print(f"在{folder1_abs}中:")
            for item in fail_files_dict1:
                file_name = os.path.basename(item['file'])
                print(f"\t❌   文件名： {file_name}  |  md5值： {item['md5']}  校验失败\n")

        if fail_files_dict2:
            print(f"在{folder2_abs}中:")
            for item in fail_files_dict2:
                file_name = os.path.basename(item['file'])
                print(f"\t❌   文件名： {file_name}  |  md5值： {item['md5']}  校验失败\n")

    # 保存详细结果到文件
    save_detailed_results(folder1_abs, folder2_abs, success_files, fail_files_dict1, fail_files_dict2,
                          unique_success_md5)

    return {
        'folder1_abs': folder1_abs,
        'folder2_abs': folder2_abs,
        'success_count': len(unique_success_md5),
        'fail_files_dict1': fail_files_dict1,
        'fail_files_dict2': fail_files_dict2
    }


def save_detailed_results(folder1_abs, folder2_abs, success_files, fail_files_dict1, fail_files_dict2,
                          unique_success_md5):
    """保存详细结果到文件"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"md5_comparison_{timestamp}.txt"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("MD5比较详细报告\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"文件夹1: {folder1_abs}\n")
            f.write(f"文件夹2: {folder2_abs}\n\n")

            f.write("校验开始\n")
            f.write("=" * 60 + "\n\n")

            # 文件夹1的校验结果
            f.write(f"校验{folder1_abs}的md5值:\n")
            folder1_files = [item for item in success_files if item['folder'] == folder1_abs]
            for item in folder1_files:
                file_name = os.path.basename(item['file'])
                f.write(f"\t✅   文件名： {file_name}  |  md5值：{item['md5']}  校验成功\n")

            for item in fail_files_dict1:
                file_name = os.path.basename(item['file'])
                f.write(f"\t❌   文件名： {file_name}  |  md5值： {item['md5']}  校验失败\n")

            # 文件夹2的校验结果
            f.write(f"\n校验{folder2_abs}的md5值:\n")
            folder2_files = [item for item in success_files if item['folder'] == item['folder'] == folder2_abs]
            for item in folder2_files:
                file_name = os.path.basename(item['file'])
                f.write(f"\t✅   文件名： {file_name}  |  md5值：{item['md5']}  校验成功\n")

            for item in fail_files_dict2:
                file_name = os.path.basename(item['file'])
                f.write(f"\t❌   文件名： {file_name}  |  md5值： {item['md5']}  校验失败\n")

            # 总计
            f.write("\n" + "=" * 60 + "\n")
            f.write("总计\n")
            f.write("=" * 60 + "\n")

            f.write(f"文件夹1和2中校验成功的文件数量为{len(unique_success_md5)}个\n")

            if fail_files_dict1 or fail_files_dict2:
                f.write("\n校验失败的有:\n")

                if fail_files_dict1:
                    f.write(f"在{folder1_abs}中:\n")
                    for item in fail_files_dict1:
                        file_name = os.path.basename(item['file'])
                        f.write(f"\t❌   文件名： {file_name}  |  md5值： {item['md5']}  校验失败\n")

                if fail_files_dict2:
                    f.write(f"在{folder2_abs}中:\n")
                    for item in fail_files_dict2:
                        file_name = os.path.basename(item['file'])
                        f.write(f"\t❌   文件名： {file_name}  |  md5值： {item['md5']}  校验失败\n")

        print(f"\n详细报告已保存到: {filename}")
    except Exception as e:
        print(f"保存详细报告时出错: {str(e)}")


def main():
    # 获取文件夹路径
    if len(sys.argv) == 3:
        folder1 = sys.argv[1]
        folder2 = sys.argv[2]
    else:
        print("请输入两个文件夹路径进行MD5比较")
        folder1 = input("第一个文件夹路径: ").strip().strip('"')
        folder2 = input("第二个文件夹路径: ").strip().strip('"')

    # 比较文件夹
    results = compare_folders_md5(folder1, folder2)

    if results:
        print(f"\n比较完成!")
        print(f"成功匹配的MD5值: {results['success_count']}个")
        print(f"文件夹1中未匹配的文件: {len(results['fail_files_dict1'])}个")
        print(f"文件夹2中未匹配的文件: {len(results['fail_files_dict2'])}个")


if __name__ == "__main__":
    main()

input()