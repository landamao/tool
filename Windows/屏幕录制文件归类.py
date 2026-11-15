import os
import shutil
from datetime import datetime

def organize_files_by_month(source_dir):
    if not os.path.isdir(source_dir):
        print(f"源目录不存在: {source_dir}")
        return
    
    # 定义常见的视频文件扩展名
    video_extensions = {
        '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg',
        '.3gp', '.webm', '.ts', '.m2ts', '.vob', '.ogv', '.rm', '.rmvb', '.asf',
        '.swf', '.f4v', '.mts', '.qt', '.divx', '.xvid'
    }
    
    # 遍历源目录中的所有文件和子目录
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        
        # 仅处理文件，跳过子目录
        if os.path.isfile(file_path):
            # 获取文件扩展名并转换为小写
            file_ext = os.path.splitext(filename)[1].lower()
            
            # 跳过非视频文件
            if file_ext not in video_extensions:
                print(f"跳过非视频文件: {filename}")
                continue
            
            # 获取文件的修改时间
            mtime = os.path.getmtime(file_path)
            mtime_dt = datetime.fromtimestamp(mtime)
            year_month = mtime_dt.strftime('%Y-%m')
            month_dir = os.path.join(source_dir, year_month)
            
            # 创建月份文件夹（如果不存在）
            os.makedirs(month_dir, exist_ok=True)
            
            # 移动文件到对应的月份文件夹
            try:
                shutil.move(file_path, os.path.join(month_dir, filename))
                print(f"已移动: {filename} 到 {year_month}")
            except Exception as e:
                print(f"移动文件 {filename} 失败: {e}")

if __name__ == "__main__":
    # 设置要整理的源目录路径
    source_directory = r"E:\LanDaMao\Videos\屏幕录制"  # 修改后的路径

    organize_files_by_month(source_directory)