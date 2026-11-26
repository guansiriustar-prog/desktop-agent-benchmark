-- 桌面壁纸轮换：读取图片清单，到点就切到下一张
-- 由 launchd 每 5 分钟调用一次；成功后 1 小时内不再动作，失败则下次继续重试
-- 清单由 refresh-wallpaper-list.sh 生成（需要“桌面”读权限，故不在本脚本中扫描目录）

set libFolder to POSIX path of (path to library folder from user domain)
set manifestPath to libFolder & "Scripts/wallpaper-rotate.list"
set statePath to libFolder & "Scripts/.wallpaper-rotate.state"
set logPath to libFolder & "Logs/wallpaper-rotate.log"

-- 读状态：第 1 行是图片索引，第 2 行是下次可切换的时间戳
set prev to -1
set dueAt to 0
try
	set stateTxt to (read (POSIX file statePath) as «class utf8»)
	set AppleScript's text item delimiters to linefeed
	set stItems to text items of stateTxt
	set AppleScript's text item delimiters to ""
	if (count of stItems) ≥ 1 then
		try
			set prev to ((item 1 of stItems) as integer)
		end try
	end if
	if (count of stItems) ≥ 2 then
		try
			set dueAt to ((item 2 of stItems) as integer)
		end try
	end if
end try

set nowEpoch to (do shell script "date +%s") as integer
if nowEpoch < dueAt then return "not due yet"

-- 读清单
try
	set manifestText to (read (POSIX file manifestPath) as «class utf8»)
on error
	my logLine(logPath, "读不到图片清单")
	return "no manifest"
end try

set AppleScript's text item delimiters to linefeed
set rawItems to text items of manifestText
set AppleScript's text item delimiters to ""
set thePaths to {}
repeat with p in rawItems
	set t to (contents of p) as text
	if t is not "" then set end of thePaths to t
end repeat

set total to (count of thePaths)
if total is 0 then
	my logLine(logPath, "清单为空")
	return "empty manifest"
end if

set idx to ((prev + 1) mod total)
set targetPath to (item (idx + 1) of thePaths) as text
set shortName to my baseName(targetPath)

try
	tell application "System Events"
		with timeout of 20 seconds
			set picture of every desktop to targetPath
		end timeout
	end tell
on error errMsg number errNum
	my logLine(logPath, shortName & " 切换失败(" & errNum & ")，下次重试：" & errMsg)
	return "failed"
end try

-- 成功后记录索引与下次时间
try
	set fs to open for access (POSIX file statePath) with write permission
	set eof fs to 0
	write ((idx as text) & linefeed & ((nowEpoch + 3300) as text)) to fs
	close access fs
end try

my logLine(logPath, shortName & " 已切换 idx=" & idx & "/" & total)
return shortName

on baseName(p)
	set AppleScript's text item delimiters to "/"
	set segs to text items of p
	set AppleScript's text item delimiters to ""
	return (contents of last item of segs) as text
end baseName

on logLine(logPath, msg)
	try
		set stamp to do shell script "date '+%Y-%m-%d %H:%M:%S'"
		do shell script "printf '%s\\n' " & (quoted form of (stamp & " " & msg)) & " >> " & (quoted form of logPath)
	end try
end logLine
