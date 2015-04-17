#!/usr/bin/env python
#-*- coding:utf-8 -*-

import click

import os
import yaml

from constants_windows import program_files, \
    condor_path_default

@click.command()
@click.option('--outdir', default='', help="Output directory - default is 'script_directory\out'")
@click.option('--condor_path', default='', help="Condor Soaring installation path - default is %s" % condor_path_default)
def main(outdir, condor_path):
    if condor_path=='':
        condor_path = condor_path_default
    path = os.path.join(condor_path, "Landscapes")
    print path
    print os.listdir(path)

if __name__ == '__main__':
    main()