#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Script to output some (X, Y) -> (Lat, Lon) points
"""

import click

import os
#import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from constants import supported_versions, supported_output_formats

from constants_windows import condor_path_default

from condor_dll import init_navicon_dll, iter_landscapes

from geodesic import plot_geodesic
  
def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out

def reverse_proj_from_dll(outdir, condor_path, landscape, nx, ny, flag_show):
    navicon_dll = init_navicon_dll(condor_path, landscape)
    max_x, max_y = navicon_dll.GetMaxX(), navicon_dll.GetMaxY()

    P = {}
    P[0] = (0, 0)
    P[1] = (max_x, 0)
    P[2] = (0, max_y)
    P[3] = (max_x, max_y)
    
    d_df = {}

    s = "ref"
    
    d_df[s] = pd.DataFrame(index=np.arange(4), columns=["PosX", "PosY", "Lat", "Lon"])
    
    for i in d_df[s].index:
        x,y = P[i][0], P[i][1]
        d_df[s]["PosX"][i] = x
        d_df[s]["PosY"][i] = y
        d_df[s]["Lat"][i] = navicon_dll.XYToLat(x, y)
        d_df[s]["Lon"][i] = navicon_dll.XYToLon(x, y)
    
    a_x = np.linspace(0, max_x, nx)
    a_y = np.linspace(0, max_y, ny)
    values = cartesian([a_x, a_y])
    
    s = "measures"
    d_df[s] = pd.DataFrame(values, columns=["PosX", "PosY"])
    d_df[s]["Lat"] = np.nan
    d_df[s]["Lon"] = np.nan
    
    for i in d_df[s].index:
        x = d_df[s]["PosX"][i]
        y = d_df[s]["PosY"][i]
        d_df[s]["Lat"][i] = navicon_dll.XYToLat(x, y)
        d_df[s]["Lon"][i] = navicon_dll.XYToLon(x, y)

    #print(d_df["ref"])
    #print(d_df["measures"])

    print("""ref:
%s

measures:
%s""" % (d_df["ref"], d_df["measures"]))
    
    filename_out = os.path.join(outdir, "geodesic_%s.xlsx" % landscape)
    print("Output '%s'" % filename_out)
    with pd.ExcelWriter(filename_out) as writer:
        key = "ref"
        d_df[key].to_excel(writer, sheet_name=key)
        key = "measures"
        d_df[key].to_excel(writer, sheet_name=key)
        
    plot_geodesic(outdir, landscape, d_df["measures"])
    if flag_show:
        plt.show()

@click.command()
@click.option('--outdir', default='', help="Output directory - default is 'script_directory\out'")
@click.option('--condor_path', default='', help="Condor Soaring installation path - default is %s" % condor_path_default)
@click.option('--landscape', default='', help="Landscape name - should be inside 'Condor\Landscapes' directory (it's also the name of a .trn file)")
@click.option('--Nx', default=20, help="Number of intervals on x axis")
@click.option('--Ny', default=20, help="Number of intervals on y axis")
def main(outdir, condor_path, landscape, nx, ny):
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    if condor_path=='':
        condor_path = condor_path_default

    landscapes = landscape
    landscapes = landscapes.split(',')

    if landscapes!=['']:
        for i, landscape in enumerate(landscapes):
            if i==1:
                flag_show = True
            else:
                flag_show = False
            reverse_proj_from_dll(outdir, condor_path, landscape, nx, ny, flag_show)
    else:
        for landscape in iter_landscapes(condor_path):
            print("Landscape '%s'" % landscape)
            flag_show = False
            reverse_proj_from_dll(outdir, condor_path, landscape, nx, ny, flag_show)

if __name__ == "__main__":
    main()
