#!/usr/bin/env python
#-*- coding:utf-8 -*-

import click

import os
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from construct import Struct, Bytes, UBInt8, ULInt32, LFloat32, Array, CString, String, PascalString

from constants_windows import paths_default

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
        #Bytes("unknown00", 136),
        #String("FirstName", 17),
        Bytes("unknown00", 135),
        String("FirstName", 17),
        String("FamilyName", 17),
        String("Country", 17),
        String("RN", 8),
        String("CN", 4),
        Bytes("unknown02", 5),
        String("Landscape", 17),
        Bytes("unknown03", offset_size - 4 - 135 - 17 - 17 - 17 - 17 - 17),
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

    for key in ['FirstName', 'FamilyName', 'Country', 'Landscape', 'RN', 'CN']:
        length = ord(dat[key][0])
        s = dat[key][1:]
        dat[key] = s.replace('\x00', '')
        assert len(dat[key])==length, "Length error with %s len=%d should be %d" % (s, len(s), length)

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

def convert_coordinates(condor_path, dat):
    from condor_dll import NaviConDLL
    landscape = dat["Landscape"]
    navicon_dll = NaviConDLL(condor_path)
    navicon_dll.init(landscape)
    df = dat['record']
    t_ser = df.apply(lambda pt: navicon_dll.xy_to_lat_lon(pt['PosX', pt['PosY']]), axis=1)
    df['Lat'] = t_ser.map(lambda t: t[0])
    df['Lon'] = t_ser.map(lambda t: t[1])
    return(df)

@click.command()
@click.argument('ftr_filename')
@click.option("--outdir", default="", help="Output directory - default is 'script_directory\out'")
@click.option("--condor_path", default="", help="Condor Soaring installation path - default is %s" % paths_default['Condor'])
def main(ftr_filename, outdir, condor_path):
    dat = read_ftr(ftr_filename, delete_keys=['unknown00', 'unknown011'])
    df_ftr = dat['record']
    del dat['record']
    for key, val in dat.items():
        if 'unknow' in key:
            del dat[key]
    print(dat)
    assert dat['length'] == 12019 # with 50km.ftr

    df_ftr = convert_coordinates(condor_path, dat)
    df_ftr.to_excel(os.path.join(outdir, "out.xls"))


    alt_diff = 100.0
    dt_dd = drawdown(df_ftr['Alt'], alt_diff)
    if dt_dd is not None:
        h_dd = df_ftr['Alt'][dt_dd]
        print("Drawdown found at %s %s" % (dt_dd, h_dd))

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)
    ax1.plot(-df_ftr['PosX'], df_ftr['PosY'])
    df_ftr['Alt'].plot(ax=ax2)
    ax2.scatter(dt_dd, h_dd, c='r')
    ax2.annotate("%d m loss" % alt_diff, xy=(dt_dd, h_dd - 0.5 * alt_diff),
        xytext=(dt_dd, h_dd - 4*alt_diff),
        arrowprops=dict(facecolor='black', shrink=0.005),
        horizontalalignment='center', verticalalignment='top'
    )
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()