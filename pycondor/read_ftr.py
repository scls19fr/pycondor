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
"""
from constants import supported_input_extensions, \
    supported_versions, supported_output_formats

import click

import os
import traceback

import numpy as np
#import pandas as pd

import struct
import pprint


def to_hex_str(d):
    s = hex(d)[2:].upper()
    s = str("0" * (2 - len(s)) + s)
    return(s)


@click.command()
@click.argument('ftr_filename')
@click.option('--offset', default=0, help="Offset") # 1895
@click.option('--cols', default=10, help="Nb of columns")
@click.option('--rows', default=4, help="Nb of rows")
def main(ftr_filename, offset, cols, rows):
    basepath = os.path.dirname(__file__)
    pp = pprint.PrettyPrinter(indent=4)
    print("Reading '%s'" % ftr_filename)
    marker_length = 4 # bytes
    #np.set_printoptions(threshold=2)
    a_bytes = np.fromfile(ftr_filename, dtype=np.dtype('u1')) # Read file in a Numpy Array
    for i in range(50):
        a_bytes_slice = a_bytes[offset+i*(32+marker_length):]
        #print(a_bytes)
        vfunc = np.vectorize(to_hex_str)
        a_str_hex = vfunc(a_bytes_slice)
        #print(a_str_hex)
        #print("".join(a_str_hex[:32+marker_length]))
        print("".join(a_str_hex[marker_length:32+marker_length]))
    #a_str_hex_slice = a_str_hex[offset:(offset+cols*rows)]
    #pp.pprint(a_str_hex_slice.reshape(rows,cols)) #.tolist())

    #print("".join(a_str_hex_slice))
        
if __name__ == '__main__':
    main()
