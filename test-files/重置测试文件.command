#!/bin/bash
# 双击运行：在桌面放一个干净的「横评」文件夹。
# 桌面上已有的「横评」先打包存进本文件夹的「重置前的旧文件」，再删掉换成干净的。
cd "$(dirname "$0")" || exit 1
[ -n "$HOME" ] || exit 1
ZIP="$PWD/原件.zip"
DST="$HOME/Desktop/横评"
OLD="$PWD/重置前的旧文件"
if [ ! -f "$ZIP" ]; then
  echo "找不到 原件.zip：$ZIP"
  exit 1
fi
if [ -e "$DST" ]; then
  mkdir -p "$OLD" || exit 1
  SAVE="$OLD/横评-$(date +%Y%m%d-%H%M%S).zip"
  if ditto -c -k --keepParent "$DST" "$SAVE"; then
    rm -rf "$DST"
    echo "旧的「横评」已打包：$SAVE"
  else
    echo "旧的「横评」没打包成功，先不动它。"
    exit 1
  fi
fi
ditto -x -k "$ZIP" "$DST" || exit 1
echo "已恢复：$DST"
