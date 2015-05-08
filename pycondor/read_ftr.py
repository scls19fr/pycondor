#!/usr/bin/env python
#-*- coding:utf-8 -*-

import click

import os
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from construct import *

@click.command()
@click.argument('ftr_filename')
def main(ftr_filename):

    offset_size = 1859

    ftr_struct = Struct("ftr_header",
        Bytes("raw", 1859),
        ULInt32("size"), # uint32 (4 bytes) @ 1859
    )

    with open(ftr_filename, "rb") as fd:
        dat = ftr_struct.parse_stream(fd)
        #print(dat)

    N = dat["size"] # 12019 (for 50km.ftr)

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

    offset_array = 1863
    a_bytes = np.memmap(ftr_filename, dtype=ftr_dtype, mode='r', offset=offset_array, shape=N)

    df_ftr = pd.DataFrame(a_bytes)

    df_ftr['Datetime'] = pd.to_datetime(df_ftr['Datetime'] * 3600.0, unit='s')
    df_ftr['Timedelta'] = df_ftr['Datetime'] - df_ftr['Datetime'].shift(1)
    df_ftr['Timedelta'] = df_ftr['Timedelta'] / np.timedelta64(1, 's') # Timedelta as seconds
    df_ftr['Vz'] = ((df_ftr['Alt'] - df_ftr['Alt'].shift(1)).fillna(0) / df_ftr['Timedelta']).fillna(0)
    df_ftr = df_ftr.set_index('Datetime')

    df_ftr['Alt'].plot()
    plt.show()

if __name__ == '__main__':
    main()