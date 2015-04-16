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

import jinja2

from enum import Enum # enum34 for Python 2.x

PointType = Enum('PointType', 'Undef Start Finish Area Turn')

class SettingsTask(object):
    AATEnabled = False

    start_min_height = 0
    start_min_height_ref = "AGL"
    start_max_height = 0
    start_max_height_ref = "AGL"
    start_max_speed = 0

    def __init__(self):
        pass

class ObservationZone(object):
    Radius = 1000
    Type = 'Cylinder'

def main():
    filename = "out/default.xls"
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
    df_task["ObservationZone"] = ObservationZone()

    #df_task["Type"] = PointType.Undef
    for i, tp in df_task.iterrows():
        if i==0:
            df_task.loc[i,'Type'] = PointType.Start
        elif i==df_task.index[-1]:
            df_task.loc[i,'Type'] = PointType.Finish
        elif settings_task.AATEnabled:
            df_task.loc[i,'Type'] = PointType.Area
        else:
            df_task.loc[i,'Type'] = PointType.Turn

    print(df_task)
    print(df_task.dtypes)
    
    template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('xcsoar6.tpl')
    d = {
        'settings_task': settings_task,
        'df_task': df_task
    }
    rendered = template.render(**d)
    #rendered = template.render(settings_task=settings_task)

    print(rendered)


if __name__ == '__main__':
    main()
