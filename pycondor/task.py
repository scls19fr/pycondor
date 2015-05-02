#!/usr/bin/env python
#-*- coding:utf-8 -*-

from constants import supported_output_formats

import os
import codecs
import json

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

def task_to_kml_with_yattag(df_task, outdir, filename_base, disp):
    from yattag import Doc, indent
    from lxml import etree
    from pykml.parser import Schema

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
        with tag('Document'):
            with tag('name'):
                text('Condor task default')
            for i, tp in df_task.iterrows():
                id = i + 1
                with tag('Placemark'):
                    with tag('name'):
                        text("%d: %s" % (id, tp.Name))
                    with tag('description'):
                        text("""

        <dl>
            <dt>Lat: </dt><dd>{lat}</dd>
            <dt>Lon: </dt><dd>{lon}</dd>
            <dt>Alt: </dt><dd>{alt}</dd>
        </dl>
        <dl>            
            <dt>Google search: </dt><dd><a href="https://www.google.fr/?#safe=off&q={name}">{name}</a></dd>
        </dl>
""".format(id=id, lat=tp.Lat, lon=tp.Lon, alt=tp.Altitude, name=tp.Name))
                    with tag('Point'):
                        with tag('coordinates'):
                            text("%.5f,%.5f,%.1f" % (tp.Lon, tp.Lat, tp.Altitude))
        
            with tag('Placemark'):
                #with tag('LookAt'):
                #    with tag('longitude'):
                #        text("%.5f" % lon)
                #    with tag('latitude'):
                #        text("%.5f" % lat)
                #    with tag('heading'):
                #        text("%d" % 0)
                #    with tag('tilt'):
                #        text("%d" % 60)
                #    with tag('range'):
                #        text("%d" % 80000)
                #    with tag('gx:altitudeMode'):
                #        text('relativeToSeaFloor')
                with tag('LineString'):
                #    with tag('extrude'):
                #        text("%d" % 1)
                #    with tag('gx:altitudeMode'):
                #        text('relativeToSeaFloor')
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
    from lxml import etree
    from pykml.parser import Schema
    from pykml.factory import KML_ElementMaker as KML
    from pykml.factory import GX_ElementMaker as GX

    s_coords = task_to_string(df_task)    
    (lat, lon) = calculate_center(df_task)
    
    #def turn_point_to_placemark(tp):
    #    placemark = KML.Placemark(
    #        KML.name(tp['Name']),
    #        KML.description(tp['Name']),
    #        KML.Point(
    #            KML.coordinates(tp['Lon'], tp['Lat'], tp['Altitude'])
    #        ),
    #    )
    #    return(placemark)
    #placemarks = [turn_point_to_placemark(tp) for i, tp in df_task.iterrows()]

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
    # This validates:
    # xmllint --noout --schema ../../pykml/schemas/kml22gx.xsd altitudemode_reference.kml

def task_to_gmaps(df_task, outdir, filename_base, disp):
    #import pygmaps
    import webbrowser
    import jinja2

    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('gmaps.tpl')
    
    map_type = 'HYBRID'  # google.maps.MapTypeId.TERRAIN ROADMAP SATELLITE HYBRID
   
    d_variables = {
        'df_task': df_task,
        'nb_wpts': len(df_task),
        'title': "Condor Task %s" % filename_base,
        'map_type': map_type,
        'json_task': task_to_json(df_task, ["Airport", "Name", "Lat", "Lon", "Altitude", "Bearing", "DistanceToGo"]),
    }
    rendered = template.render(**d_variables)

    print(task_tp_to_dict(df_task))

    if disp:
        print(rendered)

    filename_out = os.path.join(outdir, filename_base + '.html')
    print("Output '%s'" % filename_out)
    with open(filename_out, "wb") as fd:
        fd.write(rendered)

    if disp:
        webbrowser.open_new(filename_out)

def task_to_json(df_task, cols=None):
    if cols is None:
        cols = ["Name", "Lat", "Lon"]
    #s_json = "{" + "\n"
    #for i, col in enumerate(cols):
    #    s_json = s_json + '    "' + col + '"' + ": " + json.dumps(list(df_task[col])) + "," + "\n"
    #s_json = s_json[:-2] + "\n" # Removes last comma
    #s_json = s_json + "}"
    #return(s_json)
    return(task_to_json_dict_of_list(df_task[cols]))

def task_to_json_dict_of_list(df_task):
    """
    Returns a dict of list like:

    {
        "Lat": [44.054901123046875, 44.01508712768555, 44.0536003112793,
                44.288883209228516, 44.41444778442383, 44.054901123046875],
        "Lon": [5.984000205993652, 6.0107221603393555, 6.32859992980957, 
                6.536116600036621, 6.381117343902588, 5.984000205993652],
        "Name": ["SaintAuban", "Go", "CoupeS", 
                "3Eveches", "DORMILLOUSEFORT", "SaintAuban"]
    }

    """
    return(json.dumps(df_task.to_dict(orient='list')))

def task_to_json_list_of_list(df_task):
    """
    Returns a list of list (without columns name) like:

    [['Saint Auban', 'Go', 'Coupe S', 
      '3 Eveches', 'DORMILLOUSE FORT', 'Saint Auban'],
     [44.054901123046875, 44.01508712768555, 44.0536003112793, 
      44.288883209228516, 44.41444778442383, 44.054901123046875],
     [5.984000205993652, 6.0107221603393555, 6.32859992980957, 
      6.536116600036621, 6.381117343902588, 5.984000205993652]]

    """
    return(map(lambda callable: callable(), list(df_task.apply(lambda tp: tp.to_dict()))))

def task_to_json_list_of_dict(df_task):
    """
    Returns a list of dict like

    [{'Lat': 44.054901123046875, 'Lon': 5.984000205993652, 'Name': 'Saint Auban'},
     {'Lat': 44.01508712768555, 'Lon': 6.0107221603393555, 'Name': 'Go'},
     {'Lat': 44.0536003112793, 'Lon': 6.32859992980957, 'Name': 'Coupe S'},
     {'Lat': 44.288883209228516, 'Lon': 6.536116600036621, 'Name': '3 Eveches'},
     {'Lat': 44.41444778442383, 'Lon': 6.381117343902588, 'Name': 'DORMILLOUSE FORT'},
     {'Lat': 44.054901123046875, 'Lon': 5.984000205993652, 'Name': 'Saint Auban'}]

    """
    return(df_task.to_dict(orient='records'))

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
        #task_to_kml_with_pykml(df_task, outdir, filename_base, disp)
        task_to_kml_with_yattag(df_task, outdir, filename_base, disp)
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
    elif output in ['json']:
        s_json = task_to_json(df_task)
        #filename_out = os.path.join(outdir, filename_base + '.xls')
        #print("Output '%s'" % filename_out)
        if disp:
            print(s_json)
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

def is_closed(df_task):
    """
    Returns boolean (True / False)
    * True if last point == first point
    * False if last point != first point
    """
    closed = (df_task['Lat'].iloc[0] == df_task['Lat'].iloc[-1]) \
        and (df_task['Lon'].iloc[0] == df_task['Lon'].iloc[-1])
    return(closed)

def task_tp_to_dict(df_task):
    """
    Returns a dict
    * keys: (lat, lon) tuple
    * values: nb of times this point is being used in this task
    This can be use for Google Maps to add only 1 marker for a given point
    """
    d_points = {}
    s_points = df_task[['Lat', 'Lon']].apply(lambda tp: (tp['Lat'], tp['Lon']), axis=1)
    d_points = s_points.value_counts().to_dict()
    return(d_points)