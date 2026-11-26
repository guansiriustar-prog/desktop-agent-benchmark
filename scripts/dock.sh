#!/bin/bash
# T17 helper: check = print the Dock keys that matter; restore = back to the original (orientation key absent = bottom)
if [ "$1" = restore ]; then defaults delete com.apple.dock orientation 2>/dev/null; killall Dock; sleep 2; fi
printf "%s" "$(date +%H:%M:%S)"
for k in orientation autohide autohide-delay tilesize magnification largesize mineffect show-recents static-only minimize-to-application launchanim; do
  v=$(defaults read com.apple.dock $k 2>/dev/null) || v="(unset)"; printf " %s=%s" "$k" "$v"; done; echo
