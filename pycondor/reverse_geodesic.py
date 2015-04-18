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

landscape = "Provence-Oisans2"

#print(d)
print(json.dumps(d["Landscapes"][landscape], indent=4))

(max_x, max_y) = d["Landscapes"][landscape]["max"]

Pxy = {}
P_LatLon = {}
for i in range(4):
    Pxy[i] = d["Landscapes"][landscape]["points"]["xy"][str(i)]
    P_LatLon[i] = d["Landscapes"][landscape]["points"]["LatLon"][str(i)]

df_xy = pd.DataFrame(Pxy, index=["PosX", "PosY"])
df_LatLon = pd.DataFrame(P_LatLon, index=["Lat", "Lon"])
df_ref = df_xy.append(df_LatLon).transpose()

print(df_ref)

df_measures = pd.DataFrame(index=np.arange(4), columns=df_ref.columns)
print(df_measures)

Nx = 20
Ny = 20

(max_x, max_y) = (100.0, 100.0)

filename_out = "out/%s.xlsx" % landcape
print("Output '%s'" % filename_out)
with pd.ExcelWriter(filename_out) as writer:
    df_ref.to_excel(writer, sheet_name='Ref')
    df_measures.to_excel(writer, sheet_name='Measures')

a_x = np.linspace(0, max_x, Nx)
a_y = np.linspace(0, max_y, Ny)

#print(a_x, a_y)
#http://stackoverflow.com/questions/29714771/combinatoric-cartesian-product-of-numpy-arrays-without-iterators-and-or-loops