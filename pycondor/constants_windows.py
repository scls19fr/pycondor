#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import traceback

try:
    program_files = os.environ["ProgramFiles"]
    # "ProgramFiles" "ProgramFiles(x86)" "ProgramW6432"
    print(program_files)
except:
    #print(traceback.format_exc())
    program_files = "C:\\Program Files (x86)"
    print("Can't find environment variable for Program Files directory")
    print("Maybe you are not running this script under Windows")
    print("Using '%s'" % program_files)

condor_path_default = os.path.join(program_files, "Condor")
home_path = os.path.expanduser("~")
  
paths_default = {
    "ProgramFiles": program_files,
    "Condor": condor_path_default,
    "CondorLandscapes": os.path.join(condor_path_default, "Landscapes"),
    "CondorFlightPlansDefault": os.path.join(condor_path_default, "FlightPlans", "Default"),
    "CondorFlightPlansUser": os.path.join(condor_path_default, "FlightPlans", "User"),
    "CondorFlightTracks": os.path.join(condor_path_default, "FlightTracks"),
    "XCSoar": os.path.join(program_files, "XCSoar"),
    "XCSoarData": os.path.join(home_path, "Documents", "XCSoarData"),
}
