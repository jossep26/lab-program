:: ver. 1.01b, last update 2011 Oct 9
:: author zby

:: DESCRIPTION Aims to offer an easy way to check multiple sequencing results 
::             against one common template sequence.
::             Each sequencing result file (*.seq) is checked using blastn as 
::             "query", the template sequence as "subject".
::             The outputs are collected and combined into one html file.

:: REQUIREMENT This windows script requires a local installation of blast+ .
::             Please refer to 
::             http://www.ncbi.nlm.nih.gov/staff/tao/URLAPI/pc_setup.html
::             for installation guides, and
::             ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ 
::             for appropriate files.

:: USAGE 1. Copy batchBlast.cmd (this file) and writeResults.cmd into 
::              sequencing results folder.
::       2. Set the full filename (with path) for the target or template 
::              sequence file.
::       3. Run this batch file, by double-clicking this file or run in a  
::              command line interface.

@echo off

setlocal

set subject="e:\zby\document\ugene.project\ple.and.flank.fa"
set outFile=result.htm

forfiles /m *.seq /c "cmd /c blastn -task megablast -query @file -subject %subject% -outfmt 0 > @fname.blastout"

echo ^<html^> > %outFile%
echo ^<head^> >> %outFile%
echo ^<title^> Results %DATE% %TIME% ^<^/title^> >> %outFile%
echo ^<^/head^> >> %outFile%
echo ^<body^> >> %outFile%

echo ^<h1^> Results for files in %CD% ^<^/h1^> >> %outFile%
echo ^<table border="0" ^> >> %outFile%

for /f %%f in ('dir /b *.blastout') do call writeResults.cmd %%f %outFile%

echo ^<^/table^> >> %outFile%
echo ^<^/body^> >> %outFile%
echo ^<^/html^> >> %outFile%

for /f %%f in ('dir /b *.blastout') do del %%f

endlocal
