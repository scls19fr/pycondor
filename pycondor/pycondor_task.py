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

Dependencies
 - Python 2.7 or Python 3.4
 - Pandas (Numpy, ...)
 - matplotlib
 - xlwt-future (for Excel .xls output with Python 3)
"""

import click

import os
import sys

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import decimal
import pandas as pd
import decimal
import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt

import jinja2

from ctypes import WinDLL, c_char_p, c_int, c_float

def init_navicon_dll(condor_path, landscape):
    dll_filename = os.path.join(condor_path, 'NaviCon.dll')
    print("Using functions from '%s'" % dll_filename)
    print("With landscape '%s'" % landscape)
    print("")
    trn_path = os.path.join(condor_path, "Landscapes", landscape, landscape + ".trn")

    navicon_dll = WinDLL(dll_filename)

    navicon_dll.NaviConInit.argtypes = [c_char_p]
    navicon_dll.NaviConInit.restype = c_int

    navicon_dll.GetMaxX.argtypes = []
    navicon_dll.GetMaxX.restype = c_float

    navicon_dll.GetMaxY.argtypes = []
    navicon_dll.GetMaxY.restype = c_float

    navicon_dll.XYToLon.argtypes = [c_float, c_float]
    navicon_dll.XYToLon.restype = c_float

    navicon_dll.XYToLat.argtypes = [c_float, c_float]
    navicon_dll.XYToLat.restype = c_float

    navicon_dll.NaviConInit(trn_path)

    return(navicon_dll)

#import geopy

supported_input_extensions = ['.fpl']
supported_versions = ['1150']
supported_output_formats = ['Excel', 'xls',
    'xlsx', 'Excelx',
    'CSV', \
    'matplotlib', 'mpl', 'bmp', 'png', 'jpg',
    'tsk', 'xcsoar'
    ]
program_files = os.environ["ProgramFiles"] #"ProgramFiles(x86)" "ProgramW6432"
condor_path_default = os.path.join(program_files, "Condor")

@click.command()
@click.option('--debug/--no-debug', default=False, help="debug mode")
@click.argument('filename')
@click.option('--output', default='xls', help="Output type in %s" % supported_output_formats)
@click.option('--outdir', default='', help="Output directory - default is 'script_directory\out'")
@click.option('--condor_path', default='', help="Condor Soaring installation path - default is %s" % condor_path_default)
@click.option('--landscape', default='', help="Landscape name - should be inside 'Condor\Landscapes' directory (it's also the name of a .trn file)")
def main(debug, filename, output, outdir, condor_path, landscape):
    filename_base, filename_ext = os.path.splitext(os.path.basename(filename))
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    if debug:        
        assert filename_ext in supported_input_extensions, \
        "File extension of '%s' is '%s' but supported extension must be in %s" \
        % (filename, filename_ext, supported_input_extensions)
    if condor_path=='':
        condor_path = condor_path_default
        
    print("Read '%s'" % filename)
    config = configparser.ConfigParser()
    config.read(filename)
    condor_version = config.get('Version', 'Condor version')
    if debug:
        assert condor_version in supported_versions, \
            "[Version] Condor version '%s' is not a supported version - must be in %s" \
            % (condor_version, supported_versions)

    print("Condor version: %s" % condor_version)
    
    if landscape=='':
        landscape = config.get('Task', 'Landscape')

    df_task = create_task_dataframe(config)
    
    navicon_dll = init_navicon_dll(condor_path, landscape)

    max_x, max_y = navicon_dll.GetMaxX(), navicon_dll.GetMaxY()
    print("MaxX: %f" % max_x)
    print("MaxY: %f" % max_y)

    (x, y) = (0, 0)
    print("XYToLat(%f,%f): %f" % (x,y, navicon_dll.XYToLat(x,y)))
    print("XYToLon(%f,%f): %f" % (x,y, navicon_dll.XYToLon(x,y)))
    
    (x, y) = (max_x, 0)
    print("XYToLat(%f,%f): %f" % (x,y, navicon_dll.XYToLat(x,y)))
    print("XYToLon(%f,%f): %f" % (x,y, navicon_dll.XYToLon(x,y)))

    (x, y) = (max_x, max_y)
    print("XYToLat(%f,%f): %f" % (x,y, navicon_dll.XYToLat(x,y)))
    print("XYToLon(%f,%f): %f" % (x,y, navicon_dll.XYToLon(x,y)))

    (x, y) = (0, max_y)
    print("XYToLat(%f,%f): %f" % (x,y, navicon_dll.XYToLat(x,y)))
    print("XYToLon(%f,%f): %f" % (x,y, navicon_dll.XYToLon(x,y)))

    print("")
    
    df_task["Lat"] = 0.0
    df_task["Lon"] = 0.0
    
    for i, tp in df_task.iterrows():
        pos_x, pos_y = tp['PosX'], tp['PosY']
        df_task.loc[i,'Lat'] = navicon_dll.XYToLat(pos_x, pos_y)
        df_task.loc[i,'Lon'] = navicon_dll.XYToLon(pos_x, pos_y)
        
    print(df_task)

    output_task_from_df(df_task, filename_base, output, outdir)

    plt.show()

if __name__ == '__main__':
    main()
