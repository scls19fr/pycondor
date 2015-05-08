#!/usr/bin/env python
#-*- coding:utf-8 -*-

import click

import os
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from construct import Struct, Bytes, ULInt32, LFloat32, Array

@click.command()
@click.argument('ftr_filename')
def main(ftr_filename):

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
        Bytes("undefined", offset_size),
        ULInt32("length"), # uint32 (4 bytes) @ 1859
        Array(lambda ctx: ctx.length, ftr_record_struct),
    )

    with open(ftr_filename, "rb") as fd:
        dat = ftr_struct.parse_stream(fd)

    a_bytes = dat['record']
    df_ftr = pd.DataFrame(a_bytes)

    df_ftr['Datetime'] = pd.to_datetime(df_ftr['Datetime'] * 3600.0, unit='s')
    df_ftr['Timedelta'] = df_ftr['Datetime'] - df_ftr['Datetime'].shift(1)
    df_ftr['Timedelta'] = df_ftr['Timedelta'] / np.timedelta64(1, 's') # Timedelta as seconds
    df_ftr['Vz'] = ((df_ftr['Alt'] - df_ftr['Alt'].shift(1)).fillna(0) / df_ftr['Timedelta']).fillna(0)
    df_ftr = df_ftr.set_index('Datetime')

    print(df_ftr)

    df_ftr['Alt'].plot()
    plt.show()

if __name__ == '__main__':
    main()