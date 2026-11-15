import os
import sys

def batch_rename_files():
    """
    批量重命名当前目录下的文件
    """
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    print(f"当前工作目录: {current_dir}")
    print("=" * 50)
    
    # 获取用户输入
    try:
        search_str = input("请输入需要查找的字符: ").strip()
        if not search_str:
            print("错误：查找字符不能为空！")
            return
        
        replace_str = input("请输入需要替换的字符（直接回车表示删除）: ").strip()
        
        # 获取当前目录下的所有文件（不包括子目录）
        files = [f for f in os.listdir(current_dir) 
                if os.path.isfile(os.path.join(current_dir, f))]
        
        if not files:
            print("当前目录下没有文件！")
            return
        
        # 筛选出包含查找字符的文件
        matched_files = []
        rename_plan = []
        
        for filename in files:
            if search_str in filename:
                new_filename = filename.replace(search_str, replace_str)
                matched_files.append(filename)
                rename_plan.append((filename, new_filename))
        
        if not matched_files:
            print(f"没有找到包含 '{search_str}' 的文件！")
            return
        
        # 显示预览
        print("\n" + "=" * 50)
        print("重命名预览:")
        print("=" * 50)
        
        for old_name, new_name in rename_plan:
            if old_name == new_name:
                print(f"无变化: {old_name}")
            else:
                print(f"原文件: {old_name}")
                print(f"新文件: {new_name}")
                print("-" * 40)
        
        # 检查是否有重复的新文件名
        new_filenames = [new_name for _, new_name in rename_plan]
        if len(new_filenames) != len(set(new_filenames)):
            print("\n警告：重命名后会出现重复文件名！")
            print("建议修改替换字符以避免冲突。")
        
        # 确认操作
        print(f"\n总共 {len(rename_plan)} 个文件将被重命名")
        confirm = input("确认执行重命名？(y/N): ").strip().lower()
        
        if confirm == 'y':
            # 执行重命名
            success_count = 0
            error_count = 0
            
            for old_name, new_name in rename_plan:
                if old_name != new_name:
                    try:
                        old_path = os.path.join(current_dir, old_name)
                        new_path = os.path.join(current_dir, new_name)
                        
                        # 检查新文件名是否已存在
                        if os.path.exists(new_path) and old_name != new_name:
                            print(f"错误：文件 '{new_name}' 已存在，跳过 '{old_name}'")
                            error_count += 1
                            continue
                        
                        os.rename(old_path, new_path)
                        print(f"重命名成功: {old_name} -> {new_name}")
                        success_count += 1
                        
                    except Exception as e:
                        print(f"重命名失败 '{old_name}': {str(e)}")
                        error_count += 1
            
            print(f"\n重命名完成！")
            print(f"成功: {success_count} 个文件")
            print(f"失败: {error_count} 个文件")
            
        else:
            print("操作已取消")
    
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"发生错误: {str(e)}")

def show_current_files():
    """
    显示当前目录下的文件列表
    """
    current_dir = os.getcwd()
    files = [f for f in os.listdir(current_dir) 
            if os.path.isfile(os.path.join(current_dir, f))]
    
    print("\n当前目录文件列表:")
    print("-" * 30)
    for i, filename in enumerate(files, 1):
        print(f"{i:2d}. {filename}")
    print("-" * 30)

if __name__ == "__main__":
    print("文件批量重命名工具")
    print("=" * 50)
    
    # 显示当前文件列表
    show_current_files()
    
    # 执行重命名
    batch_rename_files()
    
    # 显示重命名后的文件列表
    print("\n" + "=" * 50)
    show_current_files()
    
    input("\n按回车键退出...")