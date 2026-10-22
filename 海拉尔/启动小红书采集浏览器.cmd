@echo off
setlocal
start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9223 --remote-debugging-address=127.0.0.1 "--user-data-dir=%~dp0xhs-cdp-profile" --no-first-run "https://www.xiaohongshu.com/explore"
endlocal
