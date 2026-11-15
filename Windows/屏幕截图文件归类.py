import os
import shutil
from datetime import datetime

def organize_screenshots_by_month(source_dir, target_dir):
    """
    将源目录中的截图文件按月份归类到目标目录
    
    Args:
        source_dir: 源目录路径（包含截图文件的目录）
        target_dir: 目标目录路径（归类后的目录）
    """
    # 检查源目录是否存在
    if not os.path.isdir(source_dir):
        print(f"源目录不存在: {source_dir}")
        return
    
    # 创建目标目录（如果不存在）
    os.makedirs(target_dir, exist_ok=True)
    
    # 遍历源目录中的所有文件
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        
        # 仅处理文件，跳过子目录
        if os.path.isfile(file_path):
            try:
                # 获取文件的修改时间
                mtime = os.path.getmtime(file_path)
                mtime_dt = datetime.fromtimestamp(mtime)
                year_month = mtime_dt.strftime('%Y-%m')
                
                # 在目标目录下创建月份文件夹
                month_dir = os.path.join(target_dir, year_month)
                os.makedirs(month_dir, exist_ok=True)
                
                # 移动文件到目标目录下的对应月份文件夹
                target_path = os.path.join(month_dir, filename)
                
                # 检查目标文件是否已存在，避免覆盖
                if os.path.exists(target_path):
                    # 如果文件已存在，添加时间戳作为后缀
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    new_filename = f"{name}_{timestamp}{ext}"
                    target_path = os.path.join(month_dir, new_filename)
                
                shutil.move(file_path, target_path)
                print(f"已移动: {filename} 到 {target_path}")
                
            except Exception as e:
                print(f"处理文件 {filename} 失败: {e}")

if __name__ == "__main__":
    # 设置源目录和目标目录路径
    source_directory = r"E:\LanDaMao\Pictures\屏幕截图"
    target_directory = r"E:\LanDaMao\Pictures\屏幕截图集"
    
    organize_screenshots_by_month(source_directory, target_directory)