#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Script to output corners coordinates of each installed landcape
"""

import click

import os
import json
#import yaml
import pprint

from constants_windows import program_files, \
    condor_path_default

from condor_dll import init_navicon_dll, iter_landscapes

@click.command()
@click.option("--outdir", default="", help="Output directory - default is 'script_directory\out'")
@click.option("--condor_path", default="", help="Condor Soaring installation path - default is %s" % condor_path_default)
def main(outdir, condor_path):
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=="":
        outdir = os.path.join(basepath, "out")
    if condor_path=="":
        condor_path = condor_path_default
    d = {}
    d["Landscapes"] = {}
    print landscapes_path

    for i, landscape in iter_landscapes(condor_path):
        d["Landscapes"][landscape] = {}

        navicon_dll = init_navicon_dll(condor_path, landscape)
        max_x, max_y = navicon_dll.GetMaxX(), navicon_dll.GetMaxY()
        d["Landscapes"][landscape]["max"] = (max_x, max_y)
        
        P = {}
        P[0] = (0, 0)
        P[1] = (max_x, 0)
        P[2] = (0, max_y)
        P[3] = (max_x, max_y)

        d["Landscapes"][landscape]["points"] = {}
        d["Landscapes"][landscape]["points"]["xy"] = {}
        for j, xy in P.items():
            d["Landscapes"][landscape]["points"]["xy"][j] = xy

        d["Landscapes"][landscape]["points"]["LatLon"] = {}
        for j, xy in P.items():
            d["Landscapes"][landscape]["points"]["LatLon"][j] = (navicon_dll.XYToLat(*P[i]), navicon_dll.XYToLon(*P[j]))
    
    print("")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(d)
    json_dat = json.dumps(d, indent=4)
    #print(json_dat)
    #print(yaml.dump(d))
    print("")
    
    filename_out = os.path.join(outdir, "condor.json")
    print("Output '%s'" % filename_out)
    with open(filename_out, "w") as fd:
        fd.write(json_dat)

    
if __name__ == "__main__":
    main()
