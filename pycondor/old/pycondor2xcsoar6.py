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

# constants from
#https://github.com/Turbo87/aerofiles/blob/master/aerofiles/xcsoar/constants.py
#and from http://git.xcsoar.org/cgit/jmw/xcsoar.git/plain/src/Task/TypeStrings.cpp

class MyEnum(Enum):
    def __str__(self):
        return(self.name)

class TaskType(MyEnum):
    AAT = 1
    FAIGeneral = 2
    FAIGoal = 3
    FAIOR = 4
    FAITriangle = 5
    MAT = 6
    Mixed = 7
    RT = 8 # Racing
    Touring = 9

class PointType(MyEnum):
    Start = 1
    OptionalStart = 2
    Area = 3
    Turn = 4
    Finish = 5

class ObservationZoneType(MyEnum):
    BGAStartSector = 1
    BGAFixedCourse = 2
    BGAEnhancedOption = 3
    CustomKeyhole = 4
    Cylinder = 5
    FAISector = 6
    Keyhole = 7
    Line = 8 # (length)
    MatCylinder = 9
    Sector = 10
    SymmetricQuadrant = 11 #(radius, angle)

class AltitudeReference(MyEnum):
    AGL = 1
    MSL = 2

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

class ObservationZone(object):
    Radius = None # 1000
    Type = None #ObservationZoneType.Cylinder
    Length = None
    Angle = None

    #def __str__(self):
    #    s="%s %d" % (self.Type, self.Radius)
    #    return(s)

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

    #df_task["Type"] = PointType.Undef
    for i, tp in df_task.iterrows():
        df_task.loc[i, 'ObservationZone'] = ObservationZone()
        if i==0:
            df_task.loc[i,'Type'] = PointType.Start
            df_task.loc[i, 'ObservationZone'].Type = ObservationZoneType.Cylinder
            df_task.loc[i, 'ObservationZone'].Radius = 500
        elif i==df_task.index[-1]:
            df_task.loc[i,'Type'] = PointType.Finish
            df_task.loc[i, 'ObservationZone'].Type = ObservationZoneType.Line
            df_task.loc[i, 'ObservationZone'].Length = 1000
        elif settings_task.AATEnabled:
            df_task.loc[i,'Type'] = PointType.Area
            df_task.loc[i, 'ObservationZone'].Type = ObservationZoneType.Cylinder
            df_task.loc[i, 'ObservationZone'].Radius = 1000
        else:
            df_task.loc[i,'Type'] = PointType.Turn
            df_task.loc[i, 'ObservationZone'].Type = ObservationZoneType.Cylinder
            df_task.loc[i, 'ObservationZone'].Radius = 1000

    print(df_task)
    print(df_task.dtypes)
    
    template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('xcsoar6.tpl')
    d_variables = {
        'settings_task': settings_task,
        'df_task': df_task,
        'nb_wpts': len(df_task)
    }
    rendered = template.render(**d_variables)

    print(rendered)

    filename_out = os.path.join(outdir, filename_base + '.tsk')
    print("Output '%s'" % filename_out)
    with open(filename_out, "wb") as fd:
        fd.write(rendered)


if __name__ == '__main__':
    main()
