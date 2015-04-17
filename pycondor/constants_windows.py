#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

program_files = os.environ["ProgramFiles"] #"ProgramFiles(x86)" "ProgramW6432"
condor_path_default = os.path.join(program_files, "Condor")
