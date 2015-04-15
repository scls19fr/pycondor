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

#import geopy

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
        ax.scatter(df_task['PosX'],df_task['PosY'])
        ax.plot(df_task['PosX'],df_task['PosY'])
        delta_PosX = df_task['PosX'].max() - df_task['PosX'].min()
        delta_PosY = df_task['PosY'].max() - df_task['PosY'].min()
        for i, tp in df_task.iterrows():
            ax.annotate(i, xy=(tp['PosX']+delta_PosX/40, tp['PosY']+delta_PosY/40))
        ax.set_xlabel('PosX')
        ax.set_ylabel('PosY')
        if output in ['matplotlib', 'mpl']:
            print("Display task")
            plt.show()
        if output in ['png', 'jpg', 'bmp']:
            filename_out = os.path.join(outdir, filename_base + '.' + output)
            print("Output '%s'" % filename_out)
            plt.savefig(filename_out)
    else:
        raise(NotImplementedError)

supported_input_extensions = ['.fpl']
supported_versions = ['1150']
supported_output_formats = ['Excel', 'xls',
    'xlsx', 'Excelx',
    'CSV', \
    'matplotlib', 'mpl', 'bmp', 'png', 'jpg',
    'tsk', 'xcsoar'
    ]

@click.command()
@click.option('--debug/--no-debug', default=False, help="debug mode")
@click.argument('filename')
@click.option('--output', default='xls')
@click.option('--outdir', default='')
def main(debug, filename, output, outdir):
    filename_base, filename_ext = os.path.splitext(os.path.basename(filename))
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    if debug:        
        assert filename_ext in supported_input_extensions, \
        "File extension of '%s' is '%s' but supported extension must be in %s" \
        % (filename, filename_ext, supported_input_extensions)
    print("Read '%s'" % filename)
    config = configparser.ConfigParser()
    config.read(filename)
    condor_version = config.get('Version', 'Condor version')
    if debug:
        assert condor_version in supported_versions, \
            "[Version] Condor version '%s' is not a supported version - must be in %s" \
            % (condor_version, supported_versions)

    print("Condor version: %s" % condor_version)

    df_task = create_task_dataframe(config)
    print(df_task)

    output_task_from_df(df_task, filename_base, output, outdir)

    plt.show()

if __name__ == '__main__':
    main()
