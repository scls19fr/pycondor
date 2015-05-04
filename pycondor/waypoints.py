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
Read Condor Soaring - Flight Plan

NaviCon.dll is necessary
"""
from constants import supported_input_extensions, \
    supported_versions, supported_output_formats

from constants_windows import paths_default

import click

import os
import glob
import traceback
import logging
import logging.config

import numpy as np
import pandas as pd
import decimal

#import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt

from task import create_task_dataframe, output_task_from_df, add_distance_bearing
from task_settings import SettingsTask, add_observation_zone

from enum import Enum # enum34

WaypointStyle = Enum("WaypointStyle", "Normal AirfieldGrass Outlanding GliderSite AirfieldSolid MtPass MtTop Sender Vor Ndb CoolTower Dam Tunnel Bridge PowerPlant Castle Intersection")

def task_to_kml_with_yattag(df_waypoints, outdir, filename_base):
    from yattag import Doc, indent
    from lxml import etree
    from pykml.parser import Schema

    doc, tag, text = Doc().tagtext()

    #doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('kml'):
        doc.attr(
            ("xmlns:gx", "http://www.google.com/kml/ext/2.2"),
            ("xmlns:atom", "http://www.w3.org/2005/Atom"),
            ("xmlns", "http://www.opengis.net/kml/2.2")
        )
        with tag('Document'):
            with tag('name'):
                text('Waypoints')
            for i, wpt in df_waypoints.iterrows():
                id = i + 1
                with tag('Placemark'):
                    with tag('name'):
                        text(wpt.Name)
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
""".format(lat=wpt.Lat, lon=wpt.Lon, alt=wpt.Altitude, name=wpt.Name))

                    with tag('Point'):
                        with tag('coordinates'):
                            text("%.5f,%.5f,%.1f" % (wpt.Lon, wpt.Lat, wpt.Altitude))

    result = indent(
        doc.getvalue(),
        indentation = ' '*4,
        newline = '\r\n'
    )

    filename_out = os.path.join(outdir, "wpt_" + filename_base + '.kml')
    print("Output '%s'" % filename_out)
    outfile = file(filename_out,'w')
    outfile.write(result)

    doc = etree.fromstring(result)
    assert Schema('kml22gx.xsd').validate(doc)

def latlon2decimal(s):
    try:
        dd = decimal.Decimal(s[0:2])
        mm = decimal.Decimal(s[2:-1])
        x = dd + mm/decimal.Decimal('60')
        direction = s[-1]
        if direction in ['N', 'W']:
            return(x)
        elif direction in ['S', 'E']:
            return(-x)
        else:
            raise(NotImplementedError("Can't convert %s" % s))
    except:
        print("Can't convert %s" % s)
        return(np.nan)

def dist2decimal(s):
    try:
        x = decimal.Decimal(s[:-1])
        unit = s[-1]
        if unit != 'm':
            raise(NotImplementedError("Unit is %s" % s))
            #ToDo: use ft, nm, ml
            #use Pint?
        return(x)
    except:
        print("Can't convert %s" % s)
        return(np.nan)

@click.command()
@click.option('--debug/--no-debug', default=False, help="debug mode")
@click.argument('waypoints_filename')
@click.option('--output', default='xls',
        help="Output type in %s" % supported_output_formats)
@click.option('--outdir', default='',
        help="Output directory - default is 'script_directory\out'")
@click.option('--disp/--no-disp', default=True)
def main(debug, waypoints_filename, output, outdir, disp):
    basepath = os.path.dirname(__file__)
    
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    
    # Translate path like {Condor} using paths_default
    d_name = paths_default.copy()
    d_name['output'] = output
    waypoints_filename = waypoints_filename.format(**d_name)
    outdir = outdir.format(**d_name)
    
    if not os.path.exists(outdir):
        print("Create directory %s" % outdir)
        os.makedirs(outdir)
    
    lst_errors = []
    filenames = glob.glob(waypoints_filename)
    N_filenames = len(filenames)

    print("")
    print("="*20)
    print("")    
    
    for i, filename in enumerate(filenames):
        try:
            logging.info("Read file %03d/%03d '%s'" % (i+1, N_filenames, filename))

            filename_base, filename_ext = os.path.splitext(os.path.basename(filename))
            if debug:        
                assert filename_ext in supported_input_extensions, \
                "File extension of '%s' is '%s' but supported extension must be in %s" \
                % (filename, filename_ext, supported_input_extensions)

            cols = ['Name', 'Code', 'Country', 'Latitude', 'Longitude', 'Elevation',
                    'Waypoint style', 'Runway direction', 'Runway length',
                    'Airport Frequency', 'Description']
            df_waypoints = pd.read_csv(filename, names=cols)

            df_waypoints = df_waypoints.rename(columns={
                'Latitude': 'Lat',
                'Longitude': 'Lon',
                'Elevation': 'Altitude',
            })
            #print(df_waypoints)
            # ToDo: rename columns
            # ToDo: map columns (at least Lat, Lon)
            # ToDo: create kml file
            df_waypoints['Waypoint style'] = df_waypoints['Waypoint style'].map(WaypointStyle)
            df_waypoints['Lat'] = df_waypoints['Lat'].map(latlon2decimal)
            df_waypoints['Lon'] = df_waypoints['Lon'].map(latlon2decimal)
            df_waypoints['Altitude'] = df_waypoints['Altitude'].map(dist2decimal)
            df_waypoints['Runway length'] = df_waypoints['Runway length'].map(dist2decimal)
            print(df_waypoints)
            print("Creating KML file (please wait)")
            task_to_kml_with_yattag(df_waypoints, outdir, filename_base)
            # Too many markers!!!
            # Use Google Maps instead
            # see https://developers.google.com/maps/articles/toomanymarkers

        except:
            logging.error(traceback.format_exc())
            lst_errors.append(filename)

        print("")
        print("="*20)
        print("")
        
    N_error = len(lst_errors)
    print("Convert %d files - %d errors" % (N_filenames, N_error))
    for i, filename_error in enumerate(lst_errors):
        print(" * %03d / %03d: %s" % (i+1, N_error, filename_error))
        
if __name__ == '__main__':
    basepath = os.path.dirname(__file__)
    logging.config.fileConfig(os.path.join(basepath, "logging.conf"))
    #logger = logging.getLogger("simpleExample")
    main()
