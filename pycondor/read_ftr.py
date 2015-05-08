#!/usr/bin/env python
#-*- coding:utf-8 -*-

import click

import os
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from construct import Struct, Bytes, ULInt32, LFloat32, Array, CString, String

def read_ftr(filename, delete_keys=None):
    offset_size = 1859

    ftr_record_struct = Struct("record",
        LFloat32("Datetime"),
        LFloat32("PosX"),
        LFloat32("PosY"),
        LFloat32("Alt"),
        LFloat32("Qx"),
        LFloat32("Qy"),
        LFloat32("Qz"),
        LFloat32("Qw"),
        LFloat32("Dist"),
    )

    ftr_struct = Struct("ftr_header",
        String("filetype", 4),
        Bytes("unknown00", 136),
        String("FirstName", 17),
        String("FamilyName", 17),
        String("Country", 17),
        Bytes("unknown01", offset_size - 4 - 136 - 17 - 17 - 17),
        ULInt32("length"), # uint32 (4 bytes) @ 1859
        Array(lambda ctx: ctx.length, ftr_record_struct),
    )

    with open(filename, "rb") as fd:
        dat = ftr_struct.parse_stream(fd)

    df_ftr = pd.DataFrame(dat['record'])

    df_ftr['Datetime'] = pd.to_datetime(df_ftr['Datetime'] * 3600.0, unit='s')
    df_ftr['Timedelta'] = df_ftr['Datetime'] - df_ftr['Datetime'].shift(1)
    df_ftr['Timedelta'] = df_ftr['Timedelta'] / np.timedelta64(1, 's') # Timedelta as seconds
    df_ftr['Vz'] = ((df_ftr['Alt'] - df_ftr['Alt'].shift(1)).fillna(0) / df_ftr['Timedelta']).fillna(0)
    df_ftr = df_ftr.set_index('Datetime')

    dat['record'] = df_ftr

    if delete_keys is not None:
        for key in delete_keys:
            if key in dat.keys():
                del dat[key]

    for key in ['FirstName', 'FamilyName', 'Country']:
        dat[key] = dat[key].replace('\x06', '').replace('\x00', '')

    return(dat)

def drawdown_forloop(s_altitude, alt_diff):
    local_max = s_altitude.irow(0)
    for dt, h in s_altitude.iteritems():
        if h > local_max:
            local_max = h
        if h < local_max - alt_diff:
            return(dt)
    return

def drawdown(s_altitude, alt_diff):
    flag_down = s_altitude <= np.maximum.accumulate(s_altitude) - alt_diff
    try:
        return(s_altitude[flag_down].index[0])
    except:
        return

@click.command()
@click.argument('ftr_filename')
def main(ftr_filename):
    dat = read_ftr(ftr_filename, delete_keys=['unknown00', 'unknown011'])
    df_ftr = dat['record']
    del dat['record']
    print(dat)
    assert dat['length'] == 12019 # with 50km.ftr

    alt_diff = 100.0
    dt_dd = drawdown(df_ftr['Alt'], alt_diff)
    if dt_dd is not None:
        h_dd = df_ftr['Alt'][dt_dd]
        print("Drawdown found at %s %s" % (dt_dd, h_dd))

    fig, ax = plt.subplots(1, 1)
    df_ftr['Alt'].plot(ax=ax)
    ax.scatter(dt_dd, h_dd, c='r')
    ax.annotate("%d m loss" % alt_diff, xy=(dt_dd, h_dd - 0.5 * alt_diff),
        xytext=(dt_dd, h_dd - 4*alt_diff),
        arrowprops=dict(facecolor='black', shrink=0.005),
        horizontalalignment='center', verticalalignment='top'
    )
    plt.show()

if __name__ == '__main__':
    main()