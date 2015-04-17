#!/usr/bin/env python
#-*- coding:utf-8 -*-

import yaml

from constants_windows import program_files, \
    condor_path_default

@click.option('--outdir', default='', help="Output directory - default is 'script_directory\out'")
@click.option('--condor_path', default='', help="Condor Soaring installation path - default is %s" % condor_path_default)
def main(outdir, condor_path):
    for dirname, dirnames, filenames in os.walk(condor_path):
        print(dirname, dirnames, filenames)

if __name__ == '__main__':
    main()