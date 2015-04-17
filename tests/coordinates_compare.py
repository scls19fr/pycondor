#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import json
import pandas as pd

path = "../pycondor"
filename = os.path.join(path, "out/default.xls")
df = pd.read_excel(filename)
print(df)

filename = os.path.join(path, "out/condor.json")
with open(filename) as json_data:
    d = json.load(json_data)

landcape = "Provence-Oisans2"

#print(d)
print(json.dumps(d["Landscapes"][landcape], indent=4))

(max_x, max_y) = d["Landscapes"][landcape]["max"]
P0 = d["Landscapes"]["Provence-Oisans2"]["points"]["0"]
P1 = d["Landscapes"]["Provence-Oisans2"]["points"]["1"]
P2 = d["Landscapes"]["Provence-Oisans2"]["points"]["2"]
P3 = d["Landscapes"]["Provence-Oisans2"]["points"]["3"]

print("(max_x, max_y): (%s, %s)" % (max_x, max_y))
print("(P0x, P0y): (%s, %s)" % (P0[0], P0[1]))
print("(P1x, P1y): (%s, %s)" % (P1[0], P1[1]))
print("(P2x, P2y): (%s, %s)" % (P2[0], P2[1]))
print("(P3x, P3y): (%s, %s)" % (P3[0], P3[1]))

from pyproj import Proj

# ToFix

pnyc = Proj(
    proj='lcc',
    datum='NAD83',
    lat_1=P1[0],
    lat_2=P2[0],
    lat_0=P0[0],
    lon_0=P0[1],
    x_0=max_x,
    y_0=max_y)

#x = [0]
#y = [0]
(x, y) = (0, 0)
lon, lat = pnyc(x, y, inverse=True)
#print lat, lon
