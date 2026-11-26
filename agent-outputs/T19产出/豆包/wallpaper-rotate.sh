#!/bin/bash
# 桌面壁纸轮换：每次运行切换到「横评/测试图片」里的下一张
DIR="/Users/<user>/Desktop/横评/测试图片"
MANIFEST="$HOME/Library/Scripts/wallpaper-rotate.list"
STATE="$HOME/Library/Scripts/.wallpaper-rotate.state"
LOG="$HOME/Library/Logs/wallpaper-rotate.log"

# 只在有读权限时刷新图片清单（launchd 环境读不到“桌面”目录，走清单）
tmp=$(mktemp)
if find "$DIR" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.heic' -o -iname '*.gif' -o -iname '*.bmp' -o -iname '*.tif' -o -iname '*.tiff' \) 2>/dev/null | LC_ALL=C sort > "$tmp" && [ -s "$tmp" ]; then
    mv "$tmp" "$MANIFEST"
else
    rm -f "$tmp"
fi

[ -s "$MANIFEST" ] || { echo "$(date '+%F %T') 找不到图片清单" >> "$LOG"; exit 0; }

files=()
while IFS= read -r f; do
    [ -n "$f" ] && files+=("$f")
done < "$MANIFEST"

count=${#files[@]}
[ "$count" -eq 0 ] && exit 0

idx=0
if [ -f "$STATE" ]; then
    prev=$(cat "$STATE" 2>/dev/null)
    case "$prev" in
        ''|*[!0-9]*) idx=0 ;;
        *) idx=$(( (prev + 1) % count )) ;;
    esac
fi

file="${files[$idx]}"
echo "$idx" > "$STATE"

/usr/bin/osascript <<EOF >> "$LOG" 2>&1
tell application "System Events" to set picture of every desktop to "$file"
EOF
rc=$?
echo "$(date '+%F %T') [$(basename "$file")] idx=$idx/$count rc=$rc" >> "$LOG"
exit $rc
