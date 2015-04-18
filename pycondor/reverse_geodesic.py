#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Script to output some (X, Y) -> (Lat, Lon) points
"""

import os
import json
import pandas as pd
import numpy as np

path = ""

filename = os.path.join(path, "out/condor.json")
with open(filename) as json_data:
    d = json.load(json_data)

landcape = "Provence-Oisans2"

filename = os.path.join(path, "out/condor.json")
with open(filename) as json_data:
    d = json.load(json_data)

landcape = "Provence-Oisans2"

#print(d)
#print(json.dumps(d["Landscapes"][landcape], indent=4))

(max_x, max_y) = d["Landscapes"][landcape]["max"]
P0 = d["Landscapes"]["Provence-Oisans2"]["points"]["0"]
P1 = d["Landscapes"]["Provence-Oisans2"]["points"]["1"]
P2 = d["Landscapes"]["Provence-Oisans2"]["points"]["2"]
P3 = d["Landscapes"]["Provence-Oisans2"]["points"]["3"]

d["points_xy"] = {}
d["points_xy"][0] = (0, 0)
d["points_xy"][1] = (max_x, 0)
d["points_xy"][2] = (max_x, max_y)
d["points_xy"][3] = (0, max_y)


df = pd.DataFrame(index=np.arange(4), columns=["PosX", "PosY", "Lat", "Lon"])
print(df)
df[0]=1

Nx = 100
Ny = 100

(max_x, max_y) = (100.0, 100.0)

a_x = np.linspace(0, max_x, Nx)
a_y = np.linspace(0, max_y, Ny)

#print(a_x, a_y)