import datetime
import time

def get_local_utc_offset() -> str:
    """获取本地时区相对于UTC的偏移字符串，例如 UTC+8 或 UTC-5"""
    # 获取本地时间戳和UTC时间戳的差值（秒）
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    offset_seconds = time.altzone if is_dst else time.timezone
    # time.timezone / time.altzone 返回的是 UTC 到本地时间的负偏移（秒），取反得到本地相对于UTC的偏移
    offset_seconds = -offset_seconds
    offset_hours = offset_seconds // 3600
    offset_minutes = (offset_seconds % 3600) // 60
    sign = '+' if offset_seconds >= 0 else '-'
    if offset_minutes == 0:
        return f"UTC{sign}{abs(offset_hours)}"
    else:
        return f"UTC{sign}{abs(offset_hours)}:{abs(offset_minutes):02d}"

def timestamp_to_datetime(timestamp: float) -> str:
    """将Unix时间戳转换为本地日期时间字符串（年月日格式，包含毫秒）"""
    dt = datetime.datetime.fromtimestamp(timestamp)
    base = dt.strftime("%Y年%m月%d日 %H:%M:%S")
    milliseconds = dt.microsecond // 1000
    return f"{base}.{milliseconds:03d}"

def main():
    local_tz = get_local_utc_offset()
    print(f"时间戳转换工具 - 当前使用本地时区: {local_tz}")
    print("请输入 Unix 时间戳（支持小数），输入 q 或 exit 退出\n")
    
    while True:
        user_input = input("请输入时间戳: ").strip()
        if user_input.lower() in ('q', 'exit', ''):
            print("已退出。")
            break
        
        try:
            ts = float(user_input)
            result = timestamp_to_datetime(ts)
            print(f"转换结果 ({local_tz}): {result}\n")
        except ValueError:
            print("输入无效，请输入数字格式的时间戳（例如 1775042822.0200853）\n")

if __name__ == "__main__":
    main()