#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import pandas as pd
from yattag import Doc, indent
from lxml import etree
from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX

def main():
    df_task = pd.DataFrame({
        "Name": ["Saint Auban", "Go", "Coupe S", "3 Eveches", "DORMILLOUSE FORT", "Saint Auban"],
        "Lat": [44.054901123046875, 44.015087127685547, 44.053600311279297, 44.288883209228516, 44.414447784423828, 44.054901123046875],
        "Lon": [5.9840002059936523, 6.0107221603393555, 6.3285999298095703, 6.5361166000366211, 6.3811173439025879, 5.9840002059936523],
        "Altitude": [1500, 1500, 1600, 2700, 2200, 1500]
    })
    task_to_kml(df_task, '.', 'default', True)

def task_to_kml(df_task, outdir, filename_base, disp):
    doc, tag, text = Doc().tagtext()

    with tag('kml',
        ("xmlns:gx", "http://www.google.com/kml/ext/2.2"),
        ("xmlns:atom", "http://www.w3.org/2005/Atom"),
        ("xmlns", "http://www.opengis.net/kml/2.2")
            ):
        with tag('Placemark'):
            with tag('name'):
                text('Condor task default')
        with tag('LookAt'):
            with tag('longitude'):
                text("6.26005840302")
            with tag('latitude'):
                text("44.2147674561")
            with tag('heading'):
                text("0")
            with tag('tilt'):
                text("60")
            with tag('range'):
                text("80000")
            with tag('gx:altitudeMode'):
                text('relativeToSeaFloor')
        with tag('LineString'):
            with tag('extrude'):
                text("1")
            with tag('gx:altitudeMode'):
                text('relativeToSeaFloor')
            with tag('coordinates'):
                text("5.98400020599,44.054901123,1500.0 6.01072216034,44.0150871277,1500.0 6.32859992981,44.0536003113,1600.0 6.53611660004,44.2888832092,2700.0 6.3811173439,44.4144477844,2200.0 5.98400020599,44.054901123,1500.0")

    result = indent(
        doc.getvalue(),
        indentation = ' '*4,
        newline = '\r\n'
    )

    print(result)



def task_to_kml_with_pykml(df_task, outdir, filename_base, disp):

    #lst = df_task[['Lon', 'Lat']].values
    #s_coords = " ".join(map(lambda coord: "%s,%s" % (coord[0], coord[1]), lst))
    
    lst = df_task[['Lon', 'Lat', 'Altitude']].values
    s_coords = " ".join(map(lambda coord: "%s,%s,%s" % (coord[0], coord[1], coord[2]), lst))
    #s_coords = " ".join(map(lambda coord: "%s,%s,100.0" % (coord[0], coord[1]), lst))
    
    #(lon, lat) = (df_task.loc[0, 'Lon'], df_task.loc[0, 'Lat'])
    (lon, lat) = ((df_task['Lon'].max()+df_task['Lon'].min()) / 2,
                (df_task['Lat'].max()+df_task['Lat'].min()) / 2)
    
    def turn_point_to_placemark(tp):
        placemark = KML.Placemark(
            KML.name(tp['Name']),
            KML.description(tp['Name']),
            KML.Point(
                KML.coordinates(tp['Lon'], tp['Lat'], tp['Altitude'])
            ),
        )
        return(placemark)

    placemarks = [KML.Placemark(
        KML.name(tp.Name),
        KML.description(tp.Name),
        KML.Point(KML.coordinates(tp.Lon, tp.Lat, tp.Altitude))
    ) for i, tp in df_task.iterrows()]

    print placemarks

    doc = KML.kml(
        KML.Placemark(
            KML.name("Condor Task %s" % filename_base),
            KML.LookAt(
                KML.longitude(lon),
                KML.latitude(lat),
                KML.heading(0),
                KML.tilt(60),
                KML.range(80000),
                GX.altitudeMode("relativeToSeaFloor"),
                #GX.altitudeMode("absolute"),
            ),
            KML.LineString(
                KML.extrude(1),
                GX.altitudeMode("relativeToSeaFloor"),
                #GX.altitudeMode("absolute"),
                KML.coordinates(s_coords),
            ),
        ),
        #*placemarks
    )
    if disp:
        print(etree.tostring(doc, pretty_print=True))
    # output a KML file (named based on the Python script)
    filename_out = os.path.join(outdir, filename_base + '.kml')
    print("Output '%s'" % filename_out)
    outfile = file(filename_out,'w')
    outfile.write(etree.tostring(doc, pretty_print=True))

    assert Schema('kml22gx.xsd').validate(doc)



if __name__ == "__main__":
    main()