@echo off

REM Reference: http://stackoverflow.com/questions/8397674/windows-batch-file-looping-through-directories-to-process-files
REM Require ffmpeg installation
echo.
echo ========================================
echo About to convert ALL .avi files to .mp4
echo   including ALL subdirectories!
echo If this is NOT you what want, 
echo         CLOSE THIS WINDOW 
echo                  to end this batch.
echo If this is exactly you want,
echo          press any key to continue.
echo ========================================
echo.

pause

call :treeProcess
goto :eof

:treeProcess
REM Do whatever you want here over the files of this subdir, for example:
for %%f in (*.avi) do (
    if NOT exist new-%%~nf.mp4 (
        ffmpeg -i %%f -vcodec mpeg4 new-%%~nf.mp4
    )
)

for /D %%d in (*) do (
    cd %%d
    call :treeProcess
    cd ..
)
exit /b
