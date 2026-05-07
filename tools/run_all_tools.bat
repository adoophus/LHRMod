@echo off
setlocal
set TOOLS_DIR=%~dp0
set PYTHON_EXE=C:\Users\zacha\AppData\Local\Programs\Python\Python314\python.exe
set PYTHONDONTWRITEBYTECODE=1

echo ============================================================
echo  map_data_injector
echo ============================================================
"%PYTHON_EXE%" -B "%TOOLS_DIR%map_data_injector\src\inject_map_data.py"
set INJECT_EXIT=%ERRORLEVEL%
if "%INJECT_EXIT%"=="0" (
    echo map_data_injector: OK
) else (
    echo map_data_injector: FAILED ^(exit code %INJECT_EXIT%^)
)

echo.
echo ============================================================
echo  population_adjuster
echo ============================================================
"%PYTHON_EXE%" -B "%TOOLS_DIR%population_adjuster\src\population_adjuster.py"
set POPS_EXIT=%ERRORLEVEL%
if "%POPS_EXIT%"=="0" (
    echo population_adjuster: OK
) else (
    echo population_adjuster: FAILED ^(exit code %POPS_EXIT%^)
)

echo.
if "%INJECT_EXIT%"=="0" if "%POPS_EXIT%"=="0" (
    echo All tools completed successfully.
) else (
    echo One or more tools failed.
)

pause
