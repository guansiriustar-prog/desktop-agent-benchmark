#!/bin/bash
# 刷新壁纸清单（把「横评/测试图片」里的图片写进清单），需要在有“桌面”读权限的环境下运行
DIR="/Users/<user>/Desktop/横评/测试图片"
MANIFEST="$HOME/Library/Scripts/wallpaper-rotate.list"

tmp=$(mktemp)
find "$DIR" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.heic' -o -iname '*.gif' -o -iname '*.bmp' -o -iname '*.tif' -o -iname '*.tiff' \) 2>/dev/null | LC_ALL=C sort > "$tmp"
if [ -s "$tmp" ]; then
    mv "$tmp" "$MANIFEST"
    echo "已更新清单，共 $(wc -l < "$MANIFEST" | tr -d ' ') 张图："
    cat "$MANIFEST"
else
    rm -f "$tmp"
    echo "读取失败：目录为空或没有读权限（$DIR）" >&2
    exit 1
fi
