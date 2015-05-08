#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
ToDo: trying to read a .ftr file

python read_ftr.py ~/Downloads/50km.ftr

"""

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
Read Condor Soaring - Flight Track Record .ftr


0x00: Heure, float32
0x04: X, float32 // Coordonnées internes à Condor 
0x08: Y, float32 // Coordonnées internes à Condor 
0x0C: Altitude, float32
0x10: float32*4 = Quaternion (x,y,z axis and w scalar)
0x20: Distance parcourue, float32 (non utilisé)


offset=1859
F3 2E 00 00 -> unsigned int little -> 12019
number of points

t=pd.Series([12.00001, 12.000151, 12.000290, 12.000429, 12.000572])

In [14]: (t-t.shift())*3600
Out[14]:
0       NaN
1    0.5076
2    0.5004
3    0.5004
4    0.5148
dtype: float64

import datetime
timestamp_offset = 0
(t*3600.0).map(lambda s: datetime.datetime.utcfromtimestamp(s+timestamp_offset))

50km.ftr
Bex (GMaps: 46.2566682,6.9868854,410)
6.9868854 -> (float) 0x40df9491 -> (double) 0x401bf291fb3fa6df
TPPosX0=93037.734375 -> (float) 0x47b5b6de ->  (double) 0x40f6b6dbc0000000
    0E66B547 (floats little) -> 92876
TPPosY0=47881.1484375 -> 0x473b0926 -> 0x40e76124c0000000
    C6D23947 (floats little) -> 47570
TPPosZ0=399 -> 0x43c78000 -> 0x4078f00000000000
    AF5BC843 (floats little) -> 400.7

lon = 6.9868854
lat = 46.2566682
PosX = 93037.734375
PosY = 47881.1484375
PosZ = 399.0

...

Raron
Coordonnées : 46.18.221N / 7.49.404E => 46.30368333333333336 / 7.8234
TPPosX2=28706.744140625 -> 0x46e0457d -> 0x40dc08afa0000000
TPPosY2=52222.98046875 -> 0x474bfefb -> 0x40e97fdf60000000
TPPosZ2=637 -> 0x441f4000 -> 0x4083e80000000000

"""

import click

import os
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import struct
import pprint

def to_hex_str(d, len_tot=2):
    s = hex(d)[2:].upper()
    s = str("0" * (len_tot - len(s)) + s)
    return(s)

def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

def double_to_hex(f):
    return hex(struct.unpack('<Q', struct.pack('<d', f))[0])

def print_line(offset, s_hex):
    print("%08d: %s" % (offset, s_hex))

def hexify(df):
    return(df.applymap(to_hex_str))

def reverse_bytes(df):
    return(df[::-1])

@click.command()
@click.argument('ftr_filename')
def main(ftr_filename):
    basepath = os.path.dirname(__file__)

    ftr_filename = "/Users/scls/Downloads/50km.ftr"

    #pp = pprint.PrettyPrinter(indent=4)
    print("Reading '%s'" % ftr_filename)
    #ftr_dtype = np.dtype([
    #    ("time", np.float32),
    #    ("PosX", np.float32),
    #    ("PosY", np.float32),
    #    ("Alt", np.float32),
    #    ("Qx", np.float32),
    #    ("Qy", np.float32),
    #    ("Qz", np.float32),
    #    ("Qw", np.float32),
    #    ("dist", np.float32),
    #])

    ftr_dtype = np.dtype([
        ("Datetime", "<f32"),
        ("PosX", "<f32"),
        ("PosY", "<f32"),
        ("Alt", "<f32"),
        ("Qx", "<f32"),
        ("Qy", "<f32"),
        ("Qz", "<f32"),
        ("Qw", "<f32"),
        ("dist", "<f32"),
    ])

    offset_size = 1859
    N = 12019
    offset_array = 1863

    a_bytes = np.memmap(ftr_filename, dtype=ftr_dtype, mode='r', offset=offset_array, shape=N)
    df_ftr = pd.DataFrame(a_bytes)

    df_ftr['Datetime'] = pd.to_datetime(df_ftr['Datetime'] * 3600.0, unit='s')
    df_ftr = df_ftr.set_index('Datetime')

    
    df_ftr['Alt'].plot()
    plt.show()
        
if __name__ == '__main__':
    main()
