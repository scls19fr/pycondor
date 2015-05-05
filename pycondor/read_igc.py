#!/usr/bin/env python
#-*- coding:utf-8 -*-


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
Read IGC file

"""

import click

import os
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import pytz
import decimal

def latlon2decimal(s):
    try:
        dd = decimal.Decimal(s[0:3])
        mm = decimal.Decimal(s[3:5] + '.' + s[5:-1])
        x = dd + mm / decimal.Decimal('60')
        direction = s[-1]
        if direction in ['N', 'E']:
            return(x)
        elif direction in ['S', 'W']:
            return(-x)
        else:
            raise(NotImplementedError("Can't convert %s" % s))
    except:
        print("Can't convert %s" % s)
        print(traceback.format_exc())
        return(np.nan)

def igc_b_line_to_tuple(s):
    dat = [s[1:6+1], '0'+s[7:7+8], s[7+8:15+9], s[15+9:]]
    dat[0] = datetime.time(
        hour=int(dat[0][0:2]),
        minute=int(dat[0][2:4]),
        second=int(dat[0][4:6]))
    dat[1] = latlon2decimal(dat[1]) # Lat
    dat[2] = latlon2decimal(dat[2]) # Lon
    dat[3] = (dat[3][0], int(dat[3][1:6]), int(dat[3][6:11])) # Elevation ('A'|'V', z_baro, z_gps)  
    return(dat)

@click.command()
@click.argument('igc_filename')
def main(igc_filename):
    basepath = os.path.dirname(__file__)
    print("Reading '%s'" % igc_filename)

    df = pd.read_csv(igc_filename, header=None)
    df['FirstChar'] = df[0].map(lambda s: s[0])
    df = df[df['FirstChar']=='B']
    #print(df)

    #s = 'B1005364607690N00610358EA0000001265'
    #print(s)
    #dat = igc_b_line_to_tuple(s)
    #print(dat)

    s_tuple = df[0].map(igc_b_line_to_tuple)

    df['Time'] = s_tuple.map(lambda t: t[0])
    df['Lat'] = s_tuple.map(lambda t: t[1])
    df['Lon'] = s_tuple.map(lambda t: t[2])
    df['Z_mode'] = s_tuple.map(lambda t: t[3][0])
    df['Z_baro'] = s_tuple.map(lambda t: t[3][1])
    df['Z_gps'] = s_tuple.map(lambda t: t[3][2])

    df = df.set_index('Time')
    print(df)

    df['Z_gps'].plot()
    plt.show()
        
if __name__ == '__main__':
    main()
