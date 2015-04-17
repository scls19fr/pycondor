#!/usr/bin/env python
#-*- coding:utf-8 -*-

import click

import os
import json
import yaml
import pprint

from constants_windows import program_files, \
    condor_path_default

from condor_dll import init_navicon_dll
    
@click.command()
@click.option('--outdir', default='', help="Output directory - default is 'script_directory\out'")
@click.option('--condor_path', default='', help="Condor Soaring installation path - default is %s" % condor_path_default)
def main(outdir, condor_path):
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    if condor_path=='':
        condor_path = condor_path_default
    landscapes_path = os.path.join(condor_path, "Landscapes")
    d = {}
    d["Landscapes"] = {}
    print landscapes_path
    for landscape in os.listdir(landscapes_path):
        d["Landscapes"][landscape] = {}
        navicon_dll = init_navicon_dll(condor_path, landscape)
        max_x, max_y = navicon_dll.GetMaxX(), navicon_dll.GetMaxY()
        d["Landscapes"][landscape]['max_x'] = max_x
        d["Landscapes"][landscape]['max_y'] = max_y
    
    print("")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(d)
    print(json.dumps(d, indent=4))
    print(yaml.dump(d))
    print("")
    
    filename_out = os.path.join(outdir, "condor.yml")
    print("Output '%s'" % filename_out)

    
if __name__ == '__main__':
    main()
