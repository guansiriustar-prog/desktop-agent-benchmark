#!/bin/bash
# T16 helper: start = unmuted at 50%; check = print; restore = user's original (volume 0, muted)
case "$1" in
  start)   osascript -e 'set volume output volume 50' -e 'set volume without output muted' ;;
  restore) osascript -e 'set volume output volume 0' -e 'set volume with output muted' ;;
esac
echo "$(date +%H:%M:%S) $(osascript -e 'get volume settings')"
