@echo off
REM Weekly fleet codebase-audit wrapper, fired by the app-launcher Jobs tab
REM (job id "codebase-audit-fleet", weekly THU 22:00, visible console).
REM Runs the /audit-fleet skill headless on the local Claude subscription.
REM Opus 4.7 + high effort; bypassPermissions because a scheduled run has
REM no human to answer permission prompts.
cd /d E:\automation
claude -p "/audit-fleet" --model claude-opus-4-7 --effort high --permission-mode bypassPermissions
