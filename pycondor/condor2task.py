#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import absolute_import, division, print_function

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

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

#import pandas as pd
#import decimal
#import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt

from task import create_task_dataframe, output_task_from_df, add_distance_bearing
from task_settings import SettingsTask, add_observation_zone

from condor_dll import NaviConDLL

#import geopy

@click.command()
@click.option('--debug/--no-debug', default=False, help="debug mode")
@click.argument('fpl_filename')
        # Condor Task .fpl file or *.fpl
        # {Condor}/default.fpl
@click.option('--output', default='xls',
        help="Output type in %s" % supported_output_formats)
@click.option('--outdir', default='',
        help="Output directory - default is 'script_directory\out'")
@click.option('--condor_path', default='',
        help="Condor Soaring installation path - default is %s" % paths_default['Condor'])
@click.option('--landscape', default='',
        help="Landscape name - should be inside 'Condor\Landscapes' directory (it's also the name of a .trn file)")
@click.option('--disp/--no-disp', default=True)
def main(debug, fpl_filename, output, outdir, condor_path, landscape, disp):
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    if condor_path=='':
        condor_path = paths_default['Condor']
    fpl_filename = fpl_filename.format(**paths_default)
    outdir = outdir.format(**paths_default)
    i_error = 0
    for i, filename in enumerate(glob.glob(fpl_filename)):
        try:
            logging.info("Read file %03d '%s'" % (i, filename))

            filename_base, filename_ext = os.path.splitext(os.path.basename(filename))
            if debug:        
                assert filename_ext in supported_input_extensions, \
                "File extension of '%s' is '%s' but supported extension must be in %s" \
                % (filename, filename_ext, supported_input_extensions)

            config = configparser.ConfigParser()
            #with open(filename, 'r') as fd: # fix \xef\xbb[Version]\n
            config.read(filename)
            try:
                condor_version = config.get('Version', 'Condor version')
            except:
                logging.error("Can't get 'Version/Condor version'")
                condor_version = None
            if debug:
                assert condor_version in supported_versions, \
                    "[Version] Condor version '%s' is not a supported version - must be in %s" \
                    % (condor_version, supported_versions)

            print("Condor version: %s" % condor_version)
        
            if landscape=='':
                landscape = config.get('Task', 'Landscape')

            df_task = create_task_dataframe(config)
        
            navicon_dll = NaviConDLL(condor_path)
            navicon_dll.init(landscape)

            max_x, max_y = navicon_dll.xy_max()
        
            if disp:
                print("MaxX: %f" % max_x)
                print("MaxY: %f" % max_y)

                (x, y) = (0, 0)
                (lat, lon) = navicon_dll.xy_to_lat_lon(x, y)
                print("XYToLat(%f,%f): %f" % (x, y, lat))
                print("XYToLon(%f,%f): %f" % (x, y, lon))
            
                (x, y) = (max_x, 0)
                (lat, lon) = navicon_dll.xy_to_lat_lon(x, y)
                print("XYToLat(%f,%f): %f" % (x, y, lat))
                print("XYToLon(%f,%f): %f" % (x, y, lon))

                (x, y) = (max_x, max_y)
                (lat, lon) = navicon_dll.xy_to_lat_lon(x, y)
                print("XYToLat(%f,%f): %f" % (x, y, lat))
                print("XYToLon(%f,%f): %f" % (x, y, lon))

                (x, y) = (0, max_y)
                (lat, lon) = navicon_dll.xy_to_lat_lon(x, y)
                print("XYToLat(%f,%f): %f" % (x, y, lat))
                print("XYToLon(%f,%f): %f" % (x, y, lon))

                print("")
        
            df_task["Lat"] = 0.0
            df_task["Lon"] = 0.0
        
            for j, tp in df_task.iterrows():
                pos_x, pos_y = tp['PosX'], tp['PosY']
                (lat, lon) = navicon_dll.xy_to_lat_lon(pos_x, pos_y)
                df_task.loc[j,'Lat'] = lat
                df_task.loc[j,'Lon'] = lon
            
            settings_task = SettingsTask()

            #df_task["Comment"] = ""
            #df_task["Wpt_id"] = df_task.index.map(lambda i: "_" + str(i))

            df_task = add_distance_bearing(df_task)
            df_task = add_observation_zone(settings_task, df_task)

            if disp:
                print(df_task)
                #print(df_task.dtypes)
        
            output_task_from_df(df_task, filename_base, output, outdir)

            plt.show()

        except:
            logging.error(traceback.format_exc())
            i_error += 1

        print("")
        print("="*20)
        print("")
        
    print("Convert %d files - %d errors" % (i+1, i_error))
            
if __name__ == '__main__':
    basepath = os.path.dirname(__file__)
    logging.config.fileConfig(os.path.join(basepath, "logging.conf"))
    #logger = logging.getLogger("simpleExample")
    main()
