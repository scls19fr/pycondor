#!/usr/bin/env python
#-*- coding:utf-8 -*-

import click

import os
import json
import pandas as pd
import numpy as np
import pyproj
import matplotlib.pyplot as plt

@click.command()
@click.argument('xls_filename')
@click.option('--outdir', default='', help="Output directory - default is 'script_directory\out'")
def main(xls_filename, outdir):
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    
    #xls_filename = os.path.join(outdir, "Provence-Oisans2.xlsx")

    filename_base, filename_ext = os.path.splitext(os.path.basename(xls_filename))

    d_df = {}
    d_df = pd.read_excel(xls_filename, sheetname=None)

    max_x, max_y = d_df['ref']['PosX'].max(), d_df['ref']['PosY'].max()
    print "max_x=%s, max_y=%s" % (max_x, max_y)

    p = pyproj.Proj(
        proj='utm',
        zone=32,
        ellps='WGS84'
    )

    d_df['measures']['PosX2'] = np.nan
    d_df['measures']['PosY2'] = np.nan

    for i, point in d_df['measures'].iterrows():
        xy2 = p(point['Lat'], point['Lon'])
        d_df['measures']['PosX2'][i] = xy2[0]
        d_df['measures']['PosY2'][i] = xy2[1]
        #print(xy2)

    d_df['measures']['Eps'] = np.sqrt(
        (d_df['measures']['PosX2'] - d_df['measures']['PosX'])**2 + \
        (d_df['measures']['PosY2'] - d_df['measures']['PosY'])**2
    )

    print(d_df)
    print(d_df['measures']['Eps'].mean())

    fig, axarr = plt.subplots(2, 2)
    for i, val_i in enumerate(["PosX", "PosY"]):
        for j, val_j in enumerate(["Lat", "Lon"]):
            #d_df['measures'].plot(x=val_i, y=val_j, ax=axarr[i,j])
            axarr[i,j].plot(d_df['measures'][val_j], d_df['measures'][val_i])
            axarr[i,j].set_xlabel(val_j)
            axarr[i,j].set_ylabel(val_i)

    filename_out = os.path.join(outdir, "%s_geodesic.png" % (filename_base))
    print("Output '%s'" % filename_out)
    plt.savefig(filename_out)
    plt.show()


if __name__ == "__main__":
    main()
