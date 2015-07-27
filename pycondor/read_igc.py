#!/usr/bin/env python
#-*- coding:utf-8 -*-


from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

__author__ = "Sébastien Celles"
__copyright__ = "Copyright 2015, www.celles.net"
__credits__ = ["Sébastien Celles"]
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Sébastien Celles"
__email__ = "s.celles@gmail.com"
__status__ = "Development"

"""
Read IGC file

"""

import click

import os
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import pytz
import decimal
from tools import haversine_distance

def latlon2decimal(s):
    try:
        dd = decimal.Decimal(s[0:3])
        mm = decimal.Decimal(s[3:5] + '.' + s[5:-1])
        x = dd + mm / decimal.Decimal('60')
        direction = s[-1]
        if direction in ['N', 'E']:
            return(x)
        elif direction in ['S', 'W']:
            return(-x)
        else:
            raise(NotImplementedError("Can't convert %s" % s))
    except:
        print("Can't convert %s" % s)
        print(traceback.format_exc())
        return(np.nan)

def igc_b_line_to_tuple(s):
    #s='B1301104728192N01041482EA0085500855'
    dat = [s[1:6+1], '0'+s[7:7+8], s[7+8:15+9], s[15+9:]]
    dat[0] = datetime.time(
        hour=int(dat[0][0:2]),
        minute=int(dat[0][2:4]),
        second=int(dat[0][4:6]))
    dat[1] = latlon2decimal(dat[1]) # Lat
    dat[2] = latlon2decimal(dat[2]) # Lon
    dat[3] = (dat[3][0], int(dat[3][1:6]), int(dat[3][6:11])) # Elevation ('A'|'V', z_baro, z_gps)  
    return(dat)

def igc_c_line_to_tuple(s):
    #s='C4627617N01119600EBOLZANO'
    dat = ['0'+s[1:1+8], s[1+8:1+8+9], s[1+8+9:]]
    dat[0] = latlon2decimal(dat[0]) # Lat
    dat[1] = latlon2decimal(dat[1]) # Lon
    if dat[0] is np.nan or dat[1] is np.nan:
        return(np.nan)
    return(dat)

from task import task_to_string, calculate_center

def points_to_kml_with_yattag(df_points, df_task, outdir, filename_base, disp):
    from yattag import Doc, indent
    from lxml import etree
    from pykml.parser import Schema

    doc, tag, text = Doc().tagtext()

    s_coords = task_to_string(df_points)    
    #(lat, lon) = calculate_center(df_points)

    #doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('kml'):
        doc.attr(
            ("xmlns:gx", "http://www.google.com/kml/ext/2.2"),
            ("xmlns:atom", "http://www.w3.org/2005/Atom"),
            ("xmlns", "http://www.opengis.net/kml/2.2")
        )
        with tag('Document'):
            with tag('name'):
                text("Condor task '%s'" % filename_base)
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
""".format(lat=tp.Lat, lon=tp.Lon, alt=tp.Altitude, name=tp.Name))
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

    filename_out = os.path.join(outdir, "trace_" + filename_base + '.kml')
    print("Output '%s'" % filename_out)
    outfile = file(filename_out,'w')
    outfile.write(result)

    doc = etree.fromstring(result)
    assert Schema('kml22gx.xsd').validate(doc)

@click.command()
@click.argument('igc_filename')
@click.option('--z_mode', default='gps', help="z mode ('baro', 'gps')")
@click.option('--outdir', default='',
        help="Output directory - default is 'script_directory\out'")
@click.option('--disp/--no-disp', default=False)
@click.option('--use-c/--no-use-c', default=True)
def main(igc_filename, z_mode, outdir, disp, use_c):
    basepath = os.path.dirname(__file__)
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    z_mode = z_mode.lower()
    assert z_mode in ['baro', 'gps']
    print("Reading '%s'" % igc_filename)

    filename = igc_filename
    filename_base, filename_ext = os.path.splitext(os.path.basename(filename))
    df_all = pd.read_csv(filename, header=None, names=['Data'])
    df_all['FirstChar'] = df_all['Data'].map(lambda s: s[0])

    print(df_all['FirstChar'].value_counts())
    df_task = df_all[df_all['FirstChar']=='C'].copy()

    df_points = df_all[df_all['FirstChar']=='B'].copy()
    Npts = len(df_points)
    df_points.index = np.arange(Npts)

    #s = 'B1005364607690N00610358EA0000001265'
    #print(s)
    #dat = igc_b_line_to_tuple(s)
    #print(dat)

    s_tuple = df_points['Data'].map(igc_b_line_to_tuple)

    m = 100
    g = 9.81
    first_date = datetime.date.today() # ToFix
    df_points['Time'] = s_tuple.map(lambda t: t[0])
    df_points['TimeSup'] = (df_points['Time'] < df_points['Time'].shift(1)).astype(int).cumsum()
    df_points['Time'] = df_points['Time'].map(lambda t: datetime.datetime.combine(first_date, t))
    df_points['Time'] = df_points['Time'] + df_points['TimeSup'] * datetime.timedelta(days=1)
    df_points['Deltatime'] = df_points['Time'] - df_points['Time'].shift(1)
    #df_points['Deltatime'] = df_points['Deltatime'].fillna(np.timedelta64(0, 's'))
    df_points['Deltatime'] = df_points['Deltatime'] / np.timedelta64(1, 's')
    print(df_points['Deltatime'].value_counts())
    #df_points['Deltatime'] = 10 # seconds
    df_points['Lat'] = s_tuple.map(lambda t: t[1])
    df_points['Lon'] = s_tuple.map(lambda t: t[2])
    df_points['Lat2'] = df_points['Lat'].shift(1)
    df_points['Lon2'] = df_points['Lon'].shift(1)
    df_points['Speed'] = 1000 * df_points.apply(lambda pt: haversine_distance(pt['Lat'], pt['Lon'], pt['Lat2'], pt['Lon2']), axis=1) / df_points['Deltatime']
    df_points['Speed'] = df_points['Speed'].fillna(0.0)
    df_points['Speed_km/h'] = df_points['Speed'] * 3.6
    df_points.drop(['Lat2', 'Lon2'], axis=1, inplace=True)
    df_points['Ec'] = 0.5 * m * df_points['Speed']**2 # kinetic energy
    df_points['Z_mode'] = s_tuple.map(lambda t: t[3][0])
    df_points['Z_baro'] = s_tuple.map(lambda t: t[3][1])
    df_points['Z_gps'] = s_tuple.map(lambda t: t[3][2])
    df_points['Altitude'] = df_points["Z_%s" % z_mode]
    df_points['Vz'] = (df_points['Altitude'] - df_points['Altitude'].shift(1)) / df_points['Deltatime']
    df_points['Vz'] = df_points['Vz'].fillna(0.0)
    df_points['Ep'] = m * g * df_points['Altitude'] - m * g * df_points['Altitude'].loc[0] # potential energy
    df_points['Em'] = df_points['Ec'] + df_points['Ep']
    df_points['Vz_comp'] = (df_points['Em'] - df_points['Em'].shift(1)) / (df_points['Deltatime'] * m *g)
    df_points['Vz_comp'] = df_points['Vz_comp'].fillna(0.0)

    """
    Ep = m g z
    Ec = 1/2 m v^2
    Em = Ep + Ec

    dEm / dt = m g dz/dt + d/dt (1/2 m v^2)

    VzComp = ( dEm / dt) * 1 / (m * g)
        = dz/dt + 1/(2*g) * d/dt(v^2)
        = Vz + VzK
        with VzK = 1/(2*g) * d/dt(v^2)
    
    """

    df_points['Name'] = ""
    df_points.loc[0, "Name"] = "Start"
    df_points.loc[Npts-1, "Name"] = "Finish"

    df_points = df_points.set_index('Time')
    print("Points:\n%s" % df_points)

    print("Max speed: %f km/h" % df_points['Speed_km/h'].max())
    print("Max Vz: %f" % df_points['Vz'].max())
    print("Min Vz: %f" % df_points['Vz'].min())
    print("Max Vz_comp: %f" % df_points['Vz_comp'].max())
    print("Min Vz_comp: %f" % df_points['Vz_comp'].min())


    if len(df_task)==0 or not use_c:
        print("No C record - using first and last point")
        df_task = df_points[df_points['Name'] != ""].copy()
        df_task = df_task.reset_index()
    else:
        df_task['Data'] = df_task['Data'].map(igc_c_line_to_tuple)
        df_task = df_task[df_task['Data'].notnull()].copy()
        df_task.index = np.arange(len(df_task))
        df_task['Lat'] = df_task['Data'].map(lambda t: t[0])
        df_task['Lon'] = df_task['Data'].map(lambda t: t[1])
        df_task['Name'] = df_task['Data'].map(lambda t: t[2])
        df_task['Altitude'] = 0

    print("Task:\n%s" % df_task)

    points_to_kml_with_yattag(df_points, df_task, outdir, filename_base, disp)

    #df['Z_gps'].plot()
    #plt.show()
        
if __name__ == '__main__':
    main()
