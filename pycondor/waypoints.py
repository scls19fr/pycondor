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

import pandas as pd
#import decimal
#import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt

from task import create_task_dataframe, output_task_from_df, add_distance_bearing
from task_settings import SettingsTask, add_observation_zone


#import geopy

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

            print(df_waypoints)
            # ToDo: rename columns
            # ToDo: map columns (at least Lat, Lon)
            # ToDo: create kml file

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
