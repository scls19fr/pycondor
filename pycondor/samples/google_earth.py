#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

import pandas as pd

from yattag import Doc, indent

from lxml import etree

from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX


def calculate_center(df_task):
    """
    Returns tuple (Lat, Lon) of center of task
    """
    center = ((df_task['Lat'].max() + df_task['Lat'].min()) / 2,
        (df_task['Lon'].max() + df_task['Lon'].min()) / 2)
    return(center)

def task_to_string(df_task):
    """
    Returns a string from a task DataFrame like:
    '5.9840002060,44.0549011230,1500.0 6.0107221603,44.0150871277,1500.0 6.3285999298,44.0536003113,1600.0 6.5361166000,44.2888832092,2700.0 6.3811173439,44.4144477844,2200.0 5.9840002060,44.0549011230,1500.0'

    'lon1,lat1,alt1 lon2,lat2,alt2'
    """
    return(" ".join(
        df_task.apply(lambda tp: "%.10f,%.10f,%.1f" %
         (tp.Lon, tp.Lat, tp.Altitude), axis=1)))

def main():
    disp = True
    outdir = '.'
    filename_base = 'default'

    df_task = pd.DataFrame({
        "Name": ["Saint Auban", "Go", "Coupe S", "3 Eveches", "DORMILLOUSE FORT", "Saint Auban"],
        "Lat": [44.054901123046875, 44.015087127685547, 44.053600311279297, 44.288883209228516, 44.414447784423828, 44.054901123046875],
        "Lon": [5.9840002059936523, 6.0107221603393555, 6.3285999298095703, 6.5361166000366211, 6.3811173439025879, 5.9840002059936523],
        "Altitude": [1500, 1500, 1600, 2700, 2200, 1500]
    })

    task_to_kml_with_yattag(df_task, outdir, filename_base+"_yattag", disp)

    task_to_kml_with_pykml(df_task, outdir, filename_base+"_pykml", disp)

def task_to_kml_with_yattag(df_task, outdir, filename_base, disp):
    doc, tag, text = Doc().tagtext()

    s_coords = task_to_string(df_task)    
    (lat, lon) = calculate_center(df_task)

    #doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('kml'):
        doc.attr(
            ("xmlns:gx", "http://www.google.com/kml/ext/2.2"),
            ("xmlns:atom", "http://www.w3.org/2005/Atom"),
            ("xmlns", "http://www.opengis.net/kml/2.2")
        )
        with tag('Placemark'):
            with tag('name'):
                text('Condor task default')
            with tag('LookAt'):
                with tag('longitude'):
                    text("%f" % lon)
                with tag('latitude'):
                    text("%f" % lat)
                with tag('heading'):
                    text("%d" % 0)
                with tag('tilt'):
                    text("%d" % 60)
                with tag('range'):
                    text("%d" % 80000)
                with tag('gx:altitudeMode'):
                    text('relativeToSeaFloor')
            with tag('LineString'):
                with tag('extrude'):
                    text("%d" % 1)
                with tag('gx:altitudeMode'):
                    text('relativeToSeaFloor')
                with tag('coordinates'):
                    text(s_coords)

    result = indent(
        doc.getvalue(),
        indentation = ' '*4,
        newline = '\r\n'
    )

    if disp:
        print(result)

    filename_out = os.path.join(outdir, filename_base + '.kml')
    print("Output '%s'" % filename_out)
    outfile = file(filename_out,'w')
    outfile.write(result)

    doc = etree.fromstring(result)
    assert Schema('kml22gx.xsd').validate(doc)


def task_to_kml_with_pykml(df_task, outdir, filename_base, disp):

    s_coords = task_to_string(df_task)    
    (lat, lon) = calculate_center(df_task)

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