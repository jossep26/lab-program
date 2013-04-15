:: ver. 1.0b, last update 2011 Oct 9
:: author zby

:: This script is intended for usage with batchBlast.cmd only.
@echo off

echo ^<tr^> >> %2
echo ^<th^> >> %2
REM echo ^<h3^> >> %2
echo %1 >> %2
REM echo ^<^/h3^> >> %2
echo ^<^/th^> >> %2
echo ^<^/tr^> >> %2

echo ^<tr^> >> %2
echo ^<td style="background-color:#ccccff;"^> >> %2
echo ^<pre^> >> %2
type %1 >> %2
echo ^<^/pre^> >> %2
echo ^<^/td^> >> %2
echo ^<^/tr^> >> %2

