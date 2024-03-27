@echo off
set "ndkpath=%1"
echo SetupEnvironment - Android Platform
echo Before Modification: NDKROOT:  %NDKROOT%
echo Before Modification: NDK_ROOT:  %NDK_ROOT%
setx NDKROOT "%ndkpath%"
setx NDK_ROOT "%ndkpath%"
echo Cur NDKROOT:  %NDKROOT%
echo Cur NDK_ROOT:  %NDK_ROOT%