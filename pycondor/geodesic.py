#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import matplotlib.pyplot as plt

def plot_geodesic(outdir, filename_base, df):    
    fig, axarr = plt.subplots(2, 2)
    for i, val_i in enumerate(["PosX", "PosY"]):
        for j, val_j in enumerate(["Lat", "Lon"]):
            #d_df['measures'].plot(x=val_i, y=val_j, ax=axarr[i,j])
            axarr[i,j].plot(df[val_j], df[val_i])
            axarr[i,j].set_xlabel(val_j)
            axarr[i,j].set_ylabel(val_i)

    filename_out = os.path.join(outdir, "%s_geodesic.png" % (filename_base))
    print("Output '%s'" % filename_out)
    plt.savefig(filename_out)
    plt.show()
