import os
import shutil
import time  # 新增导入，用于获取当前时间戳

def 整理下载文件夹(源目录路径):
    if not os.path.isdir(源目录路径):
        print(f"源目录不存在: {源目录路径}")
        return

    # 定义压缩包文件扩展名集合（包含常见格式）
    压缩包扩展名集合 = {'.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz',
                       '.bz2', '.tar.bz2', '.xz', '.tar.xz', '.iso'}

    # 遍历源目录中的所有条目
    for 文件名 in os.listdir(源目录路径):
        文件完整路径 = os.path.join(源目录路径, 文件名)
        
        # 仅处理文件，跳过子目录
        if os.path.isfile(文件完整路径):
            # 处理复合扩展名（如.tar.gz）
            文件扩展名 = ""
            if 文件名.endswith(('.tar.gz', '.tar.bz2', '.tar.xz')):
                if 文件名.endswith('.tar.gz'):
                    文件扩展名 = '.tar.gz'
                elif 文件名.endswith('.tar.bz2'):
                    文件扩展名 = '.tar.bz2'
                else:
                    文件扩展名 = '.tar.xz'
            else:
                # 获取普通扩展名并转为小写
                文件扩展名 = os.path.splitext(文件名)[1].lower()

            # 确定目标文件夹
            目标子目录名称 = None
            if 文件扩展名 == '.exe':
                目标子目录名称 = '应用程序'
            elif 文件扩展名 == '.py':
                目标子目录名称 = 'Python文件'
            elif 文件扩展名 == '.apk':
                目标子目录名称 = 'APK文件'
            elif 文件扩展名 == '.torrent':
                目标子目录名称 = '种子文件'
            elif 文件扩展名 in 压缩包扩展名集合:
                目标子目录名称 = '压缩包'

            # 移动文件到对应目录
            if 目标子目录名称:
                目标目录完整路径 = os.path.join(源目录路径, 目标子目录名称)
                os.makedirs(目标目录完整路径, exist_ok=True)  # 确保目标目录存在
                try:
                    shutil.move(文件完整路径, os.path.join(目标目录完整路径, 文件名))
                    print(f"已移动: {文件名} -> {目标子目录名称}")

                    # 刷新目标文件夹的修改日期为当前时间
                    当前时间戳 = time.time()  # 获取当前时间戳
                    os.utime(目标目录完整路径, (当前时间戳, 当前时间戳))  # 同时更新访问时间和修改时间
                    # 可选：打印更新信息（如需调试可取消注释）
                    # print(f"已更新目录修改时间: {目标子目录名称}")

                except Exception as 异常信息:
                    print(f"移动失败 {文件名}: {str(异常信息)}")
            # else: 不处理其他类型文件

if __name__ == "__main__":
    待整理的源目录 = r"E:\Downloads"
    整理下载文件夹(待整理的源目录)