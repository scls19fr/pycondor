#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import matplotlib.pyplot as plt

def plot_geodesic(outdir, landscape, df, flag_show):
    fig, axarr = plt.subplots(2, 2)
    plt.suptitle(landscape)
    for i, val_i in enumerate(["PosX", "PosY"]):
        for j, val_j in enumerate(["Lat", "Lon"]):
            #d_df['measures'].plot(x=val_i, y=val_j, ax=axarr[i,j])
            #axarr[i,j].plot(df[val_j], df[val_i])
            axarr[i,j].scatter(df[val_j], df[val_i], s=1, lw=0, facecolor='0')
            axarr[i,j].set_xlabel(val_j)
            axarr[i,j].set_ylabel(val_i)

    filename_out = os.path.join(outdir, "geodesic_%s.png" % (landscape))
    print("Output '%s'" % filename_out)
    plt.savefig(filename_out)
    if flag_show:
        plt.show()
