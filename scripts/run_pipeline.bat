@echo off
REM run_pipeline.bat
REM Triggers the pipeline for Windows Task Scheduler.
REM
REM Set up in Task Scheduler:
REM   1. Open Task Scheduler -> Create Basic Task
REM   2. Trigger: choose your schedule (e.g. Daily)
REM   3. Action: "Start a program"
REM      Program/script:  the full path to this .bat file
REM      Start in:        the project's src\ folder (important --
REM                        pipeline.py resolves paths relative to it)

cd /d "%~dp0..\src"
"C:\Program Files\Python312\python.exe" pipeline.py
