#!/usr/bin/env python
#-*- coding:utf-8 -*-

from constants import supported_output_formats

import os
import codecs

import decimal

import numpy as np
import pandas as pd
#import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt

from tools import haversine_bearing, haversine_distance

from aerofiles.xcsoar import Writer, TaskType, PointType, AltitudeReference

#import jinja2

def turn_point(config, i):
    TP_properties = ["Name", "PosX", "PosY", "PosZ", "Airport", "SectorType", "Radius",
    "Angle", "Altitude", "Width", "Height", "Azimuth"]
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
        "Azimuth": decimal.Decimal,
    }
    d_turn_point = {}
    for prop in TP_properties:
        property_name = "TP%s%d" % (prop, i)
        data = config.get("Task", property_name)
        if prop in d_convert:
            convert = d_convert[prop]
            data = convert(data)
        d_turn_point[prop] = data
    return(d_turn_point)

def create_task_dataframe(config):
    #task_version = config.get('Task', 'TaskVersion')
    
    task_count = int(config.get('Task', 'Count'))
    lst_task = []
    for i in range(task_count):
        task = turn_point(config, i)
        #print("Task %d: %s" % (i, task))
        lst_task.append(task)
    df_task = pd.DataFrame(lst_task)

    return(df_task)


def task_to_xcsoar(df_task, outdir, filename_base):
    filename_out = os.path.join(outdir, filename_base + '.tsk')
    print("Output '%s'" % filename_out)
    with open(filename_out, 'w') as fp:  # codecs.open(..., encoding='...')
        writer = Writer(fp)

        with writer.write_task(type=TaskType.RACING):  # encoding='...'
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

def task_to_kml(df_task, outdir, filename_base, disp):
    from lxml import etree
    from pykml.parser import Schema
    from pykml.factory import KML_ElementMaker as KML
    from pykml.factory import GX_ElementMaker as GX

    #lst = df_task[['Lon', 'Lat']].values
    #s_coords = " ".join(map(lambda coord: "%s,%s" % (coord[0], coord[1]), lst))
    
    lst = df_task[['Lon', 'Lat', 'Altitude']].values
    s_coords = " ".join(map(lambda coord: "%s,%s,%s" % (coord[0], coord[1], coord[2]), lst))
    #s_coords = " ".join(map(lambda coord: "%s,%s,100.0" % (coord[0], coord[1]), lst))
    
    #(lon, lat) = (df_task.loc[0, 'Lon'], df_task.loc[0, 'Lat'])
    (lon, lat) = ((df_task['Lon'].max()+df_task['Lon'].min()) / 2,
                (df_task['Lat'].max()+df_task['Lat'].min()) / 2)
    
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


        )
    )
    if disp:
        print(etree.tostring(doc, pretty_print=True))
    # output a KML file (named based on the Python script)
    filename_out = os.path.join(outdir, filename_base + '.kml')
    print("Output '%s'" % filename_out)
    outfile = file(filename_out,'w')
    outfile.write(etree.tostring(doc, pretty_print=True))

    assert Schema('kml22gx.xsd').validate(doc)
    # This validates:
    # xmllint --noout --schema ../../pykml/schemas/kml22gx.xsd altitudemode_reference.kml

def task_to_gmaps(df_task, outdir, filename_base, disp):
    #import pygmaps
    import webbrowser
    import jinja2

    center = ((df_task['Lat'].max() + df_task['Lat'].min()) / 2,
        (df_task['Lon'].max() + df_task['Lon'].min()) / 2)


    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('gmaps.tpl')
    
    map_type = 'HYBRID'  # google.maps.MapTypeId.TERRAIN ROADMAP SATELLITE HYBRID
   
    d_variables = {
        'df_task': df_task,
        'nb_wpts': len(df_task),
        'center': center,
        'title': "Condor Task %s" % filename_base,
        'map_type': map_type,
        'json_task': df_task.to_json(orient="columns"),
    }
    rendered = template.render(**d_variables)

    if disp:
        print(rendered)

    filename_out = os.path.join(outdir, filename_base + '.html')
    print("Output '%s'" % filename_out)
    with open(filename_out, "wb") as fd:
        fd.write(rendered)
        
    if disp:
        webbrowser.open_new(filename_out)

def process_df_task_objects(df_task):
    for col in ['ObservationZone']: # only one object for now
        if col in df_task.columns:
            df_task[col] = df_task[col].map(str)
    return(df_task)

def output_task_from_df(df_task, filename_base, output, outdir, disp):
    output = output.lower()

    if output not in supported_output_formats:
        raise(NotImplementedError("'%s' task format not supported - must be in %s"
            % (output, supported_output_formats)))

    if output in ['xls', 'excel']:
        filename_out = os.path.join(outdir, filename_base + '.xls')
        print("Output '%s'" % filename_out)
        df_task = process_df_task_objects(df_task)
        df_task.to_excel(filename_out)
    elif output in ['xlsx', 'excelx']:
        filename_out = os.path.join(outdir, filename_base + '.xlsx')
        print("Output '%s'" % filename_out)
        df_task = process_df_task_objects(df_task)
        df_task.to_excel(filename_out)
    elif output in ['csv']:
        filename_out = os.path.join(outdir, filename_base + '.csv')
        print("Output '%s'" % filename_out)
        df_task = process_df_task_objects(df_task)
        df_task.to_csv(filename_out)
    elif output.lower() in ['tsk', 'xcsoar']:
        task_to_xcsoar(df_task, outdir, filename_base)
    elif output.lower() in ['kml', 'google earth', 'ge', 'googleearth']:
        task_to_kml(df_task, outdir, filename_base, disp)
    elif output.lower() in ['gmaps', 'google maps', 'gm']:
        task_to_gmaps(df_task, outdir, filename_base, disp)
    elif output in ['matplotlib', 'mpl', 'png', 'jpg', 'bmp']:
        fig, ax = plt.subplots(1, 1)
        #ax.scatter(df_task['PosX'],df_task['PosY'])
        #ax.plot(df_task['PosX'],df_task['PosY'])
        #delta_PosX = df_task['PosX'].max() - df_task['PosX'].min()
        #delta_PosY = df_task['PosY'].max() - df_task['PosY'].min()
        #for i, tp in df_task.iterrows():
        #    ax.annotate(i, xy=(tp['PosX']+delta_PosX/40, tp['PosY']+delta_PosY/40))
        #ax.set_xlabel('PosX')
        #ax.set_ylabel('PosY')
        ax.scatter(df_task['Lon'],df_task['Lat'])
        ax.plot(df_task['Lon'],df_task['Lat'])
        delta_Lon = df_task['Lon'].max() - df_task['Lon'].min()
        delta_Lat = df_task['Lat'].max() - df_task['Lat'].min()
        for i, tp in df_task.iterrows():
            ax.annotate(i, xy=(tp['Lon'] + delta_Lon/40, tp['Lat'] + delta_Lat/40))
        ax.set_xlabel('Lon')
        ax.set_ylabel('Lat')
        if output in ['matplotlib', 'mpl']:
            print("Display task")
            plt.show()
        if output in ['png', 'jpg', 'bmp']:
            filename_out = os.path.join(outdir, filename_base + '.' + output)
            print("Output '%s'" % filename_out)
            plt.savefig(filename_out)
    else:
        raise(NotImplementedError)

def add_distance_bearing(df_task):
    """
    Add columns for bearing and distance (and cumsum)
    """
    df_task['Bearing'] = np.nan
    df_task['DistanceToGo'] = np.nan
    for idx in df_task.index[:-1]:
        (lat1, lon1) = (df_task.loc[idx, 'Lat'], df_task.loc[idx, 'Lon'])
        (lat2, lon2) = (df_task.loc[idx + 1, 'Lat'], df_task.loc[idx + 1, 'Lon'])
        df_task.loc[idx, 'Bearing'] = haversine_bearing(lat1, lon1, lat2, lon2)
        df_task.loc[idx, 'DistanceToGo'] = haversine_distance(lat1, lon1, lat2, lon2)
    df_task['DistanceToGoSum'] = df_task['DistanceToGo'].shift(1).fillna(0).cumsum()
    df_task['DistanceToGoSumRev'] = df_task['DistanceToGo'].sum() - df_task['DistanceToGoSum']
    return(df_task)

