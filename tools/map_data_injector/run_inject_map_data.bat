@echo off
setlocal
set SCRIPT_DIR=%~dp0
set PYTHON_EXE=C:\Users\zacha\AppData\Local\Programs\Python\Python314\python.exe
set PYTHONDONTWRITEBYTECODE=1

"%PYTHON_EXE%" -B "%SCRIPT_DIR%src\inject_map_data.py"
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Injector failed with exit code %EXIT_CODE%.
)

if "%EXIT_CODE%"=="0" (
    echo.
    echo Injector completed successfully.
)

pause

exit /b %EXIT_CODE%
