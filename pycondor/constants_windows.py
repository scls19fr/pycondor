#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import traceback

try:
    program_files = os.environ["ProgramFiles"]
    # "ProgramFiles" "ProgramFiles(x86)" "ProgramW6432"
    print(program_files)
except:
    print(traceback.format_exc())
    program_files = "C:\\Program Files"

paths_default = {
    "ProgramFiles": program_files,
    "Condor": os.path.join(program_files, "Condor"),
    "CondorLandscapes": os.path.join(program_files, "Condor", "Landscapes"),
}
