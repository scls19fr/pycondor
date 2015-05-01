REM Batch script to convert several files

REM python.exe condor2task.py samples/default.fpl --debug --output xls
python.exe condor2task.py {Condor}/FlightPlans/User/*.fpl --output tsk --outdir {XCSoarData}
REM python.exe condor2task.py {Condor}/FlightPlans/Default/*.fpl --output tsk --outdir {XCSoarData}
