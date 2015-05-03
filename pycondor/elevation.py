#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Script to output XCSoar, Google Earth, Google Maps
from spreadsheet file (Excel xls or xlsx)
"""

from constants import supported_output_formats
from constants_windows import paths_default

import os
import glob
import click
import numpy as np
import pandas as pd
import json

import requests
import requests_cache

import matplotlib.pylab as plt

from task import task_to_string, add_distance_bearing

@click.command()
@click.argument('input_filename')
# use out/default.xls but also wildcard filename like out/*.xls
#@click.option('--output', default='kml',
#        help="Output type in %s" % supported_output_formats)
@click.option('--outdir', default='',
        help="Output directory - default is 'script_directory\out'")
@click.option('--disp/--no-disp', default=True)
@click.option('--expire_after', default='00:15:00.0', help=u"Cache expiration (0: no cache, -1: no expiration, d: d seconds expiration cache)")
@click.option('--samples', default=100, help=u"Point samples")
@click.option('--api_key', default='', help=u"Google API key")
#def main(input_filename, output, outdir, disp):
def main(input_filename, outdir, disp, expire_after, samples, api_key):
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')

    filename_cache = os.path.join(outdir, "requests_cache")
    if expire_after == '0':
        expire_after = None
        print("expire_after==0 no cache")
    else:
        if expire_after == '-1':
            expire_after = 0
            print("Installing cache '%s.sqlite' without expiration" % filename_cache)
        else:
            expire_after = pd.to_timedelta(expire_after, unit='s')
            print("Installing cache '%s.sqlite' with expire_after=%s (d days hh:mm:ss)" % (filename_cache, expire_after))
        requests_cache.install_cache(filename_cache, backend='sqlite', expire_after=expire_after) # expiration seconds

    input_filename = input_filename.format(**paths_default)
    outdir = outdir.format(**paths_default)
    for filename in glob.glob(input_filename):
        print("Read '%s'" % filename)

        filename_base, filename_ext = os.path.splitext(os.path.basename(filename))
    
        if filename_ext in ['.xls', '.xlsx']:
            df_task = pd.read_excel(filename)
        elif filename_ext in ['.fpl']:
            raise(NotImplementedError("ToDo: File format '%s' not YET supported" % filename_ext))
            # see condor2task code
        else:
            raise(NotImplementedError("File format '%s' not supported" % filename_ext))

        df_task = add_distance_bearing(df_task)
        dist_tot = df_task['DistanceToGo'].sum()
    
        if disp:
            print(df_task)
            #print(df_task.dtypes)

        s_coords = "|".join(
            df_task.apply(lambda tp: "%.10f%s%.10f" %
            (tp.Lat, ",", tp.Lon), axis=1))

        params = {
            'path': s_coords,
            'samples': samples,
            'key': api_key
        }

        #url = "https://maps.googleapis.com/maps/api/elevation/json?path=36.578581,-118.291994|36.23998,-116.83171&samples=3"
        url = "https://maps.googleapis.com/maps/api/elevation/json"

        print("Request to '%s' with\n%s" % (url, params))
        response = requests.get(url, params=params)

        dat = response.json()
        df_elevation = pd.DataFrame(dat['results'])
        df_elevation = df_elevation.rename(columns={
            "elevation": "Elevation",
            "resolution": "Resolution"
        })
        df_elevation['Lat'] = df_elevation['location'].map(lambda location: location['lat'])
        df_elevation['Lon'] = df_elevation['location'].map(lambda location: location['lng'])
        df_elevation.drop('location', axis=1, inplace=True)
        #df_elevation = add_distance_bearing(df_elevation)
        df_elevation['Distance'] = np.linspace(0, dist_tot, samples)

        if disp:
            print(df_elevation)

        #def forceAspect(ax,aspect=1):
        #    im = ax.get_images()
        #    extent =  im[0].get_extent()
        #    ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)

        dist_max = df_elevation['Distance'].max()
        elev_max = df_elevation['Elevation'].max()

        fig = plt.figure()
        ax = fig.add_subplot(111, adjustable='box', aspect=dist_max / (elev_max * 4.0))
        ax.plot(df_elevation['Distance'], df_elevation['Elevation'])
        ax.set_title("Ground elevation for '%s'" % filename_base)
        ax.set_xlabel('Distance (km)')
        ax.set_ylabel('Elevation (m)')
        ax.grid(True)
        #forceAspect(ax,aspect=2.0)

        filename_out = os.path.join(outdir, "elevation_%s.%s" % (filename_base, "png"))
        print("Output '%s'" % filename_out)
        plt.savefig(filename_out)

        if disp:
            plt.show()

if __name__ == '__main__':
    main()
