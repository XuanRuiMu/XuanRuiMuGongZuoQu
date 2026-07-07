@echo off
chcp 65001 >nul
set PYTHON="C:\Users\27606\AppData\Local\uv\cache\archive-v0\x-4NBu9_OAB_87_f\Scripts\python.exe"
%PYTHON% "%~dp0run_all.py"
exit /b %errorlevel%
