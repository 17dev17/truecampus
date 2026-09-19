@echo off
title TrueCampus Server
echo ========================================================
echo Starting TrueCampus B2B2C Verification Platform...
echo ========================================================
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
