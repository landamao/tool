import sys
import os
import subprocess
from pathlib import Path

def main():
    print("========================================")
    print("   批量视频压缩工具")
    print("   压缩参数: CRF25 + 音量x10")
    print("========================================")
    print()

    # 检查是否传入了文件参数
    if len(sys.argv) <= 1:
        print("请将视频文件拖放到此脚本上（支持多个文件）")
        print()
        print("或者将文件拖到文件夹上，然后运行：")
        print(f'  "{Path(sys.argv[0]).name}" "视频1.mp4" "视频 2.mp4"')
        print()
        input("按任意键继续...")
        sys.exit(1)

    # 获取所有文件参数
    文件列表 = sys.argv[1:]
    文件数 = len(文件列表)
    
    print(f"找到 {文件数} 个文件")
    print()

    成功数 = 0
    失败文件列表 = []
    
    # 用于存储单个文件处理时的信息
    单文件信息 = None

    # 处理每个文件
    for 索引, 文件路径 in enumerate(文件列表):
        文件路径 = 文件路径.strip('"')  # 去除可能的引号
        if not os.path.exists(文件路径):
            print(f"[{索引}] 文件不存在: {文件路径}")
            失败文件列表.append((文件路径, "文件不存在"))
            continue

        print(f"[{索引}] 正在处理: {文件路径}")
        
        # 构建输出文件名
        文件dir = os.path.dirname(文件路径)
        文件名 = os.path.basename(文件路径)
        前缀, 后缀名 = os.path.splitext(文件名)
        输出文件 = os.path.join(文件dir, f"{前缀}_压缩{后缀名}")
        
        print(f"     输出为: {输出文件}")
        print()
        print("-" * 50)

        # 构建ffmpeg命令
        命令 = [
            "ffmpeg",
            "-i", 文件路径,
            "-c:v", "libx264",
            "-crf", "25",
            "-preset", "fast",
            "-c:a", "aac",
            "-af", "volume=10.0",
            输出文件
        ]

        try:
            # 执行ffmpeg命令，实时显示输出
            执行结果 = subprocess.run(
                命令,
                stdout=sys.stdout,      # 将ffmpeg的标准输出重定向到当前脚本的标准输出
                stderr=sys.stderr,      # 将ffmpeg的错误输出重定向到当前脚本的错误输出
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            print("-" * 50)
            
            if 执行结果.returncode == 0:
                print("     [✓] 完成")
                
                # 如果是单个文件且处理成功，记录信息以便后续询问是否覆盖
                if 文件数 == 1:
                    单文件信息 = {
                        '输入文件': 文件路径,
                        '输出文件': 输出文件,
                        '输入文件大小': os.path.getsize(文件路径) if os.path.exists(文件路径) else 0,
                        '输出文件大小': os.path.getsize(输出文件) if os.path.exists(输出文件) else 0
                    }
                
                成功数 += 1
            else:
                print("     [✗] 失败")
                失败文件列表.append((文件路径, f"FFmpeg返回码: {执行结果.returncode}"))

        except FileNotFoundError:
            print("     [✗] 失败: 未找到ffmpeg，请确保已安装并添加到系统路径")
            失败文件列表.append((文件路径, "未找到ffmpeg"))
        except KeyboardInterrupt:
            print("\n     [!] 处理被用户中断")
            失败文件列表.append((文件路径, "用户中断"))
            break
        except Exception as e:
            print(f"     [✗] 失败: {str(e)}")
            失败文件列表.append((文件路径, str(e)))
        
        print()

    # 如果是单个文件且处理成功，询问是否覆盖原文件
    if 文件数 == 1 and 成功数 == 1:
        输入文件 = 单文件信息['输入文件']
        输出文件 = 单文件信息['输出文件']
        
        if os.path.exists(输入文件) and os.path.exists(输出文件):
            输入文件大小 = 单文件信息['输入文件大小'] / (1024 * 1024)  # 转换为MB
            输出文件大小 = 单文件信息['输出文件大小'] / (1024 * 1024)  # 转换为MB
            压缩率 = (1 - 输出文件大小 / 输入文件大小) * 100 if 输入文件大小 > 0 else 0
            
            print("=" * 50)
            print(f"文件压缩完成:")
            print(f"  原文件: {输入文件} ({输入文件大小:.2f} MB)")
            print(f"  压缩文件: {输出文件} ({输出文件大小:.2f} MB)")
            print(f"  压缩率: {压缩率:.1f}%")
            print("=" * 50)
            print()
            print()
            # 询问是否覆盖原文件，默认是(Y)
            while True:
                选择 = input(f"是否覆盖原文件? [Y/n]: ").strip().lower()

                print()
                if not 选择 or 选择 == 'y' or 选择 == 'yes':
                    try:
                        # 删除原文件
                        os.remove(输入文件)
                        # 将压缩文件重命名为原文件名
                        os.rename(输出文件, 输入文件)
                        print("  已覆盖原文件")
                    except Exception as e:
                        print(f"  覆盖文件时出错: {e}")
                        print(f"  压缩文件保存在: {输出文件}")
                    break
                elif 选择 == 'n' or 选择 == 'no':
                    print(f"  保留原文件，压缩文件保存在: {输出文件}")
                    break
                else:
                    print("  请输入 Y 或 N (默认Y): ")
            print()
            print()

    print("========================================")
    print("批量处理完成！")
    print(f"处理成功: {成功数} 个文件")
    print(f"处理失败: {len(失败文件列表)} 个文件")
    print("========================================")
    
    if 失败文件列表:
        print("失败文件列表:")
        for 文件路径, 错误信息 in 失败文件列表:
            print()
            print(f"  - {文件路径}: {错误信息}")
        print()
    
    input("按任意键继续...")

if __name__ == "__main__":
    main()