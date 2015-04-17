#!/usr/bin/env python
#-*- coding:utf-8 -*-

supported_input_extensions = ['.fpl']
supported_versions = ['1150']
supported_output_formats = ['Excel', 'xls',
    'xlsx', 'Excelx',
    'CSV', \
    'matplotlib', 'mpl', 'bmp', 'png', 'jpg',
    'tsk', 'xcsoar'
    ]
program_files = os.environ["ProgramFiles"] #"ProgramFiles(x86)" "ProgramW6432"
condor_path_default = os.path.join(program_files, "Condor")
