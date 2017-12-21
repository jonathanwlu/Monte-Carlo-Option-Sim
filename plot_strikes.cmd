@ECHO OFF
setlocal
set PYTHONPATH=%PYTHONPATH%;%CD%\src
python src\runners\iv_strike_runner.py
endlocal