#!/bin/bash
# 每小时轮换桌面壁纸：红->绿->蓝，由当前小时数 mod 3 决定，确保每小时切换且循环稳定
DIR="$HOME/Desktop/横评/测试图片"
H=$(date +%H)
idx=$(( 10#$H % 3 ))
case $idx in
  0) F="红.png" ;;
  1) F="绿.png" ;;
  2) F="蓝.png" ;;
esac
PIC="$DIR/$F"
if [ -f "$PIC" ]; then
  osascript -e "tell application \"System Events\" to tell every desktop to set picture to \"$PIC\""
fi
