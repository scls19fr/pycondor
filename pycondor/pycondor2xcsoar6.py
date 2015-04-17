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

from aerofiles.xcsoar import Writer, TaskType, PointType, ObservationZoneType, AltitudeReference

from lxml import etree
from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX

# see https://github.com/Turbo87/aerofiles/blob/master/aerofiles/xcsoar/constants.py
class ObservationZone:
    def __init__(self, **kw):
        assert 'type' in kw

        self.type = kw['type']

        if kw['type'] == ObservationZoneType.LINE:
            assert 'length' in kw
            self.length = kw['length']

        elif kw['type'] == ObservationZoneType.CYLINDER:
            assert 'radius' in kw
            self.radius = kw['radius']

        elif kw['type'] == ObservationZoneType.SECTOR:
            assert 'radius' in kw
            assert 'start_radial' in kw
            assert 'end_radial' in kw
            self.radius = kw['radius']
            self.start_radial = kw['start_radial']
            self.end_radial = kw['end_radial']

        elif kw['type'] == ObservationZoneType.SYMMETRIC_QUADRANT:
            assert 'radius' in kw
            self.radius = kw['radius']

        elif kw['type'] == ObservationZoneType.CUSTOM_KEYHOLE:
            assert 'radius' in kw
            assert 'inner_radius' in kw
            assert 'angle' in kw
            self.radius = kw['radius']
            self.inner_radius = kw['inner_radius']
            self.angle = kw['angle']

    def __str__(self):
        s = self.type + " "
        for key, val in self.__dict__.items():
            if key!="type":
                s += "%s: %s" % (key, val)
        return(s)

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

def task_to_xcsoar(df_task, outdir, filename_base):
    filename_out = os.path.join(outdir, filename_base + '.tsk')
    print("Output '%s'" % filename_out)

    with open(filename_out, 'w') as fp:
        writer = Writer(fp)

        with writer.write_task(type=TaskType.RACING):
            for i, tp in df_task.iterrows():
                with writer.write_point(type=tp.Type):
                    writer.write_waypoint(
                        name=tp.Name,
                        latitude=tp.Lat,
                        longitude=tp.Lon
                    )
                    
                    # ToDo: ENHANCEMENT #writer.write_observation_zone(tp.ObservationZone)

                    # ToDo: Add a aerofiles.xcsoar.ObservationZone object
                    #https://github.com/Turbo87/aerofiles/blob/master/aerofiles/xcsoar/writer.py

                    d = {}
                    for key, val in tp.ObservationZone.__dict__.items():
                        d[key] = val

                    writer.write_observation_zone(**d)

def task_to_kml(df_task, outdir, filename_base):
    lst = df_task[['Lon', 'Lat']].values
    s_coords = " ".join(map(lambda coord: "%s,%s" % (coord[0], coord[1]), lst))
    doc = KML.kml(
        KML.Placemark(
            KML.name("gx:altitudeMode Example"),
            KML.LookAt(
                KML.longitude(df_task['Lon'].mean()),
                KML.latitude(df_task['Lat'].mean()),
                KML.heading(0),
                KML.tilt(0),
                KML.range(100000),
                GX.altitudeMode("relativeToSeaFloor"),
            ),
            KML.LineString(
                KML.extrude(1),
                GX.altitudeMode("relativeToSeaFloor"),
                KML.coordinates(s_coords)
            )
        )
    )
    print(etree.tostring(doc, pretty_print=True))
    # output a KML file (named based on the Python script)
    filename_out = os.path.join(outdir, filename_base + '.kml')
    print("Output '%s'" % filename_out)
    outfile = file(filename_out,'w')
    outfile.write(etree.tostring(doc, pretty_print=True))

    assert Schema('kml22gx.xsd').validate(doc)
    # This validates:
    # xmllint --noout --schema ../../pykml/schemas/kml22gx.xsd altitudemode_reference.kml


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

    for i, tp in df_task.iterrows():
        if i==0:
            df_task.loc[i,'Type'] = PointType.START
            df_task.loc[i, 'ObservationZone'] = ObservationZone(type=ObservationZoneType.CYLINDER, radius=500)
        elif i==df_task.index[-1]:
            df_task.loc[i,'Type'] = PointType.FINISH
            df_task.loc[i, 'ObservationZone'] = ObservationZone(type=ObservationZoneType.LINE, length=500)
        elif settings_task.AATEnabled:
            df_task.loc[i,'Type'] = PointType.AREA
            df_task.loc[i, 'ObservationZone'] = ObservationZone(type=ObservationZoneType.CYLINDER, radius=1000)
        else:
            df_task.loc[i,'Type'] = PointType.TURN
            df_task.loc[i, 'ObservationZone'] = ObservationZone(type=ObservationZoneType.CYLINDER, radius=1000)

    print(df_task)
    print(df_task.dtypes)

    task_to_xcsoar(df_task, outdir, filename_base)

    task_to_kml(df_task, outdir, filename_base)


if __name__ == '__main__':
    main()
