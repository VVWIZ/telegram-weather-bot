@echo off
set PYTHONIOENCODING=utf-8
:restart
echo [%date% %time%] Zapusk bota...
"C:\Users\Arys\AppData\Local\Python\pythoncore-3.14-64\python.exe" "C:\claude\teleg_bot\bot.py"
echo [%date% %time%] Bot ostanovitsya, perezapusk cherez 5 sekund...
timeout /t 5 /nobreak
goto restart
