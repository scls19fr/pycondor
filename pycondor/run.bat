REM Batch script to convert several files

REM Create json / yaml file for Landscapes installed
REM python.exe condor2data.py

REM Create one xls file from one Condor flight plan file (.fpl)
REM python.exe condor2task.py samples\default.fpl --debug --output xls
REM python.exe condor2task.py samples\default.fpl --debug --output png

REM Create one XCSoar task file from one Condor flight plan file (.fpl)
REM python.exe condor2task.py samples\default.fpl --debug --output tsk
REM python.exe condor2task.py "{Condor}\FlightPlans\User\Partial Gold badge examination EAlps2.0_CC.fpl" --debug --output tsk

REM Create several XCSoar task file for several Condor flight plan file (.fpl)
REM python.exe condor2task.py "{Condor}\FlightPlans\Default\*.fpl" --output tsk --outdir "{XCSoarData}"  --no-disp --fixencoding
REM python.exe condor2task.py "{Condor}\FlightPlans\User\*.fpl" --output tsk --outdir "{XCSoarData}" --no-disp --fixencoding

REM python.exe condor2task.py "{Condor}\FlightPlans\User\*.fpl" --output xls --outdir "{XCSoarData}\xls" --no-disp

REM python.exe condor2task.py "{Condor}\FlightPlans\User\*.fpl" --output ge --outdir "{XCSoarData}\ge" --no-disp

REM python.exe condor2task.py "{Condor}\FlightPlans\User\*.fpl" --output gmaps --outdir "{XCSoarData}\gmaps" --no-disp

REM python.exe condor2task.py "{Condor}\FlightPlans\User\*.fpl" --output xls --outdir "{XCSoarData}\{output}" --no-disp
python.exe condor2task.py "{Condor}\FlightPlans\User\*.fpl" --output gmaps --outdir "{XCSoarData}\{output}" --no-disp