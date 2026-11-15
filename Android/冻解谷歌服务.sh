#!/system/bin/sh

# 检查是否具有root权限
if [ $(id -u) -ne 0 ]; then
    echo "错误：此脚本需要root权限。"
    exit 1
fi

PACKAGE_VENDING="com.android.vending"
PACKAGE_GMS="com.google.android.gms"
ACTIVITY="com.android.vending/com.google.android.finsky.activities.MainActivity"

# 检查com.android.vending是否处于冻结（禁用）状态
if pm list packages -d | grep -q "$PACKAGE_VENDING"; then
    echo "$PACKAGE_VENDING 已冻结，正在解冻并启动..."

    # 解冻两个应用
    if pm enable "$PACKAGE_VENDING"; then
        echo "$PACKAGE_VENDING 已启用"
    else
        echo "启用 $PACKAGE_VENDING 失败"
    fi

    if pm enable "$PACKAGE_GMS"; then
        echo "$PACKAGE_GMS 已启用"
    else
        echo "启用 $PACKAGE_GMS 失败"
    fi

    # 启动Google Play商店主界面
    echo "启动 Google Play 商店..."
    sleep 0.2
    am start -n "$ACTIVITY"
else
    echo "$PACKAGE_VENDING 未冻结，正在冻结..."

    # 冻结两个应用
    if pm disable "$PACKAGE_VENDING"; then
        echo "$PACKAGE_VENDING 已禁用"
    else
        echo "禁用 $PACKAGE_VENDING 失败"
    fi

    if pm disable "$PACKAGE_GMS"; then
        echo "$PACKAGE_GMS 已禁用"
    else
        echo "禁用 $PACKAGE_GMS 失败"
    fi
fi

echo "操作完成。"