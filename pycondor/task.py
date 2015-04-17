#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from aerofiles.xcsoar import Writer, TaskType, PointType, ObservationZoneType, AltitudeReference

from lxml import etree
from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX

def turn_point(config, id):
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
        "Width": decimal.Decimal,
        "Height": decimal.Decimal,
        "Azimuth": decimal.Decimal,
    }
    d_turn_point = {}
    for property in TP_properties:
        property_name = "TP%s%d" % (property, id)
        data = config.get("Task", property_name)
        if property in d_convert:
            convert = d_convert[property]
            data = convert(data)
        d_turn_point[property] = data
    return(d_turn_point)

def create_task_dataframe(config):
    task_version = config.get('Task', 'TaskVersion')
    task_count = int(config.get('Task', 'Count'))
    lst_task = []
    for id in range(task_count):
        task = turn_point(config, id)
        #print("Task %d: %s" % (id, task))
        lst_task.append(task)
    df_task = pd.DataFrame(lst_task)

    return(df_task)


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
    #(lon, lat) = (df_task.loc[0, 'Lon'], df_task.loc[0, 'Lat'])
    (lon, lat) = ((df_task['Lon'].max()+df_task['Lon'].min()) / 2,
                (df_task['Lat'].max()+df_task['Lat'].min()) / 2)
    doc = KML.kml(
        KML.Placemark(
            KML.name("gx:altitudeMode Example"),
            KML.LookAt(
                KML.longitude(lon),
                KML.latitude(lat),
                KML.heading(0),
                KML.tilt(60),
                KML.range(80000),
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


def output_task_from_df(df_task, filename_base, output, outdir):
    output = output.lower()

    if output not in supported_output_formats:
        raise(NotImplementedError("'%s' task format not supported - must be in %s"
            % (output, supported_output_formats)))

    if output in ['xls', 'excel']:
        filename_out = os.path.join(outdir, filename_base + '.xls')
        print("Output '%s'" % filename_out)
        df_task.to_excel(filename_out)
    elif output in ['xlsx', 'excelx']:
        filename_out = os.path.join(outdir, filename_base + '.xlsx')
        print("Output '%s'" % filename_out)
        df_task.to_excel(filename_out)
    elif output in ['csv']:
        filename_out = os.path.join(outdir, filename_base + '.csv')
        print("Output '%s'" % filename_out)
        df_task.to_csv(filename_out)
    elif output.lower() in ['tsk', 'xcsoar']:
        template_dir = os.path.join(os.path.dirname(__file__), 'templates') 
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        template = env.get_template('xcsoar6.tpl')
        d = {'variable': 'Hello template'}
        rendered = template.render(**d)
        filename_out = os.path.join(outdir, filename_base + '.tsk')
        print("Output '%s'" % filename_out)
        with open(filename_out, "wb") as fd:
            fd.write(rendered)
        raise(NotImplementedError("XCSoar task format is not yet supported (WIP)"))
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
             ax.annotate(i, xy=(tp['Lon']+delta_Lon/40, tp['Lat']+delta_Lat/40))
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
