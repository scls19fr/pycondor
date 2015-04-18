#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Script to output some (X, Y) -> (Lat, Lon) points
"""

import click

import os
import json
import pandas as pd
import numpy as np

from constants import supported_input_extensions, \
    supported_versions, supported_output_formats

from constants_windows import program_files, \
    condor_path_default

from condor_dll import init_navicon_dll
    
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

@click.command()
@click.option('--outdir', default='', help="Output directory - default is 'script_directory\out'")
@click.option('--condor_path', default='', help="Condor Soaring installation path - default is %s" % condor_path_default)
@click.option('--landscape', default='Provence-Oisans2', help="Landscape name - should be inside 'Condor\Landscapes' directory (it's also the name of a .trn file)")
def main(outdir, condor_path, landscape):
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    if condor_path=='':
        condor_path = condor_path_default

    navicon_dll = init_navicon_dll(condor_path, landscape)
    max_x, max_y = navicon_dll.GetMaxX(), navicon_dll.GetMaxY()
        
    #filename = os.path.join(basepath, "out/condor.json")
    #with open(filename) as json_data:
    #    d = json.load(json_data)

    #print(d)
    #print(json.dumps(d["Landscapes"][landscape], indent=4))

    #(max_x, max_y) = d["Landscapes"][landscape]["max"]

    Pxy = {}
    P_LatLon = {}
    for i in range(4):
        Pxy[i] = d["Landscapes"][landscape]["points"]["xy"][str(i)]
        P_LatLon[i] = d["Landscapes"][landscape]["points"]["LatLon"][str(i)]

    df_xy = pd.DataFrame(Pxy, index=["PosX", "PosY"])
    df_LatLon = pd.DataFrame(P_LatLon, index=["Lat", "Lon"])
    df_ref = df_xy.append(df_LatLon).transpose()

    print(df_ref)

    Nx = 20
    Ny = 20

    a_x = np.linspace(0, max_x, Nx)
    a_y = np.linspace(0, max_y, Ny)
    values = cartesian([a_x, a_y])

    df_measures = pd.DataFrame(values, columns=["PosX", "PosY"])
    df_measures["Lat"] = np.nan
    df_measures["Lon"] = np.nan

    print(df_measures)

    filename_out = os.path.join(outdir, "%s.xlsx" % landcape)
    print("Output '%s'" % filename_out)
    with pd.ExcelWriter(filename_out) as writer:
        df_ref.to_excel(writer, sheet_name='Ref')
        df_measures.to_excel(writer, sheet_name='Measures')

if __name__ == "__main__":
    main()