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
@click.option('--offset', default=0, help="Offset") # 1895
@click.option('--cols', default=10, help="Nb of columns")
@click.option('--rows', default=4, help="Nb of rows")
def main(ftr_filename, offset, cols, rows):
    basepath = os.path.dirname(__file__)
    pp = pprint.PrettyPrinter(indent=4)
    print("Reading '%s'" % ftr_filename)
    #marker_length = 4 # bytes
    #frame_length = 32 # bytes
    #length = marker_length + frame_length # 36 bytes
    length = 36
    #alphabet = "".join(map(lambda x: str(x), range(10))) # 0123456789
    #header ="".join([" "+ alphabet[i % 10] for i in range(frame_length)])
    #print_line(0, header)
    #np.set_printoptions(threshold=2)
    #print [i+"a" for i in range(frame_length+marker_length)]
    a_bytes = np.fromfile(ftr_filename, dtype=np.dtype('u1')) # Read file in a Numpy Array
    a_bytes_slice = a_bytes[offset:]
    N = len(a_bytes_slice)
    assert (N % length) == 0, "len==%d is not a multiple of %d" % (N, length)
    #a_bytes_slice.resize(N/length, length)
    # reshape != resize
    a_bytes_slice = a_bytes_slice.reshape(N/length, length)
    #a_bytes_slice = a_bytes_slice.reshape(N)
    pd.set_option('display.max_columns', 40)
    df_bytes = pd.DataFrame(a_bytes_slice)
    vfunc = np.vectorize(to_hex_str)

    print(df_bytes)
    print(hexify(df_bytes))
    #for i in range(50):
    #    #print(a_bytes)
    #    a_str_hex = vfunc(a_bytes_slice)
    #    #print(a_str_hex)
    #    #print("".join(a_str_hex[:frame_length+marker_length]))
    #    s_hex = "".join(a_str_hex[marker_length:frame_length+marker_length])
    #    print_line(offset, s_hex)
    #    #print("%08d: %s r" % (offset, s_hex[::-1]))
    #    offset = offset + frame_length + marker_length
    #    #print("")
    #a_str_hex_slice = a_str_hex[offset:(offset+cols*rows)]
    #pp.pprint(a_str_hex_slice.reshape(rows,cols)) #.tolist())

    #print("".join(a_str_hex_slice))
        
if __name__ == '__main__':
    main()
