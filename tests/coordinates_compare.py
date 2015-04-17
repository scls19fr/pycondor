#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import json
import pandas as pd

path = "../pycondor"
filename = os.path.join(path, "out/default.xls")
df = pd.read_excel(filename)

filename = os.path.join(path, "out/condor.json")
with open(filename) as json_data:
    d = json.load(json_data)

print(d)

print(d["Landscapes"][""]