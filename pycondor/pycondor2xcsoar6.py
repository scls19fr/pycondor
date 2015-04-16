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

PointType = Enum('PointType', 'Start Finish Area Turn')

class SettingsTask(object):
    AATEnabled = False

    start_min_height = 0
    start_min_height_ref = "AGL"
    start_max_height = 0
    start_max_height_ref = "AGL"
    start_max_speed = 0

    def __init__(self):
        pass

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
    print(df_task)
    print(df_task.dtypes)
    #df_task["Type"] = PointType.Turn
    #for i, tp in df_task.iterrows():
    #    pos_x, pos_y = df_task['PosX'], df_task['PosY']
    #    df_task.loc[i,'Lat'] = mydll.XYToLat(pos_x, pos_y)

    settings_task = SettingsTask()

    

    template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('xcsoar6.tpl')
    d = {
        'variable': 'Hello template',
        'settings_task': settings_task
    }
    rendered = template.render(**d)
    #rendered = template.render(settings_task=settings_task)

    print(rendered)


if __name__ == '__main__':
    main()
