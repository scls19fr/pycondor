#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""

This code is just for test
for now to try to output XCSoar6 file
"""


import os
import click
import pandas as pd
import decimal

#import jinja2

from task import task_to_kml, task_to_xcsoar, add_observation_zone
from aerofiles.xcsoar import Writer, TaskType, PointType, ObservationZoneType, AltitudeReference
from observationzone import ObservationZone

class SettingsTask(object):
    AATEnabled = False

    aat_min_time = 0

    start_min_height = 0
    start_min_height_ref = AltitudeReference.AGL

    start_max_height = 0
    start_max_height_ref = AltitudeReference.AGL

    start_max_speed = 0

    finish_min_height = 0
    finish_min_height_ref = AltitudeReference.AGL

    def __init__(self):
        pass

def main():
    outdir = "out"
    filename = "out/default.xls"
    filename_base, filename_ext = os.path.splitext(os.path.basename(filename))
    
    df_task = pd.read_excel(filename)
    #print(df_task)
    #print(df_task.dtypes)
    d_convert = {
        "PosX": decimal.Decimal,
        "PosY": decimal.Decimal,
        "PosZ": decimal.Decimal,
        "Airport": int,
        "SectorType": int,
        "Radius": decimal.Decimal,
        "Angle": decimal.Decimal,
        "Altitude": decimal.Decimal,
        "Width": decimal.Decimal,
        "Height": decimal.Decimal,
        "Width": decimal.Decimal,
        "Height": decimal.Decimal,
        "Azimuth": decimal.Decimal,
    }
    for col, typ in d_convert.items():
        df_task[col] = df_task[col].astype(typ)

    settings_task = SettingsTask()

    df_task["Comment"] = ""
    df_task["Wpt_id"] = df_task.index.map(lambda i: "_" + str(i))

    df_task = add_observation_zone(settings_task, df_task)

    print(df_task)
    print(df_task.dtypes)

    task_to_xcsoar(df_task, outdir, filename_base)

    task_to_kml(df_task, outdir, filename_base)


if __name__ == '__main__':
    main()
