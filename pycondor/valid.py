#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Script to output corners coordinates of each installed landcape
"""

import click

import os
import glob
import pandas as pd
import numpy as np

from condor_dll import ValiConDLL, iter_landscapes

from constants_windows import paths_default

@click.command()
@click.option("--condor_path", default="", help="Condor Soaring installation path - default is %s" % paths_default['Condor'])
@click.option('--filenames', default="{CondorFlightTracks}/*.ftr", help="Condor Track Record .ftr file")
def main(condor_path, filenames):
    basepath = os.path.dirname(__file__)
    if condor_path=="":
        condor_path = paths_default['Condor']
    d_name = paths_default.copy()
    filenames = filenames.format(**d_name)      
    valicon_dll = ValiConDLL(condor_path)
    
    filenames = glob.glob(filenames)
    N_filenames = len(filenames)
    
    df_valid = pd.DataFrame(index=np.arange(N_filenames), columns=["Filename", "Valid"])

    for i, filename in enumerate(filenames):
        valid = valicon_dll.validate(filename)
        df_valid["Filename"][i] = os.path.basename(filename)
        df_valid["Valid"][i] = valid
        
    print(df_valid)
    
    #df_valid.to_excel("valid.xls")
        
    
if __name__ == "__main__":
    main()