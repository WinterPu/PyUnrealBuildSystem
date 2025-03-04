@echo off
setlocal enabledelayedexpansion

:: Check if a parameter is provided
if "%~1"=="" (
    echo Error: Please provide Java installation path as a parameter
    echo Usage: %0 [Java installation path]
    exit /b 1
)

:: Check if the provided path exists
if not exist "%~1" (
    echo Error: Path "%~1" does not exist
    exit /b 1
)

:: Check if the provided path contains java.exe
if not exist "%~1\bin\java.exe" (
    echo Warning: java.exe not found in "%~1\bin", please confirm this is the correct Java installation path
    choice /c YN /m "Do you still want to set JAVA_HOME?"
    if errorlevel 2 exit /b 1
)

:: Set JAVA_HOME environment variable (permanent)
echo Setting JAVA_HOME=%~1
setx JAVA_HOME "%~1" /m

@REM :: Add Java path to PATH for the current session
@REM set "JAVA_HOME=%~1"
@REM set "PATH=%JAVA_HOME%\bin;%PATH%"

echo.
echo JAVA_HOME has been successfully set to: %JAVA_HOME%
echo Please reopen command prompt for environment variables to take effect.
echo.
echo You can verify the settings by running:
echo java -version

endlocal