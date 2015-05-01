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
    program_files = "C:\\Program Files"
    print("Can't find environment variable for Program Files directory")
    print("Maybe you are not running this script under Windows")
    print("Using '%s'" % program_files)

paths_default = {
    "ProgramFiles": program_files,
    "Condor": os.path.join(program_files, "Condor"),
    "CondorLandscapes": os.path.join(program_files, "Condor", "Landscapes"),
}
