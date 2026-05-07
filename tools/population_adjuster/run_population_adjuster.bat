@echo off
setlocal
set SCRIPT_DIR=%~dp0
set PYTHON_EXE=C:\Users\zacha\AppData\Local\Programs\Python\Python314\python.exe
set PYTHONDONTWRITEBYTECODE=1

"%PYTHON_EXE%" -B "%SCRIPT_DIR%src\population_adjuster.py"
set EXIT_CODE=%ERRORLEVEL%

if "%EXIT_CODE%"=="0" (
    echo.
    echo population_adjuster completed.
) else (
    echo.
    echo population_adjuster failed with exit code %EXIT_CODE%.
)

pause
exit /b %EXIT_CODE%
