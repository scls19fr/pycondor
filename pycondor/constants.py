#!/usr/bin/env python
#-*- coding:utf-8 -*-

supported_input_extensions = ['.fpl']
supported_versions = ['1150']
supported_output_formats = ['excel', 'xls',
    'xlsx', 'excelx',
    'CSV', \
    'matplotlib', 'mpl', 'bmp', 'png', 'jpg',
    'tsk', 'xcsoar',
    'kml', 'google earth', 'ge', 'googleearth',
    'gmaps', 'google maps', 'gm'
    ]

# convert to lower case (if that's not the case)

supported_input_extensions = map(lambda s: s.lower(), supported_input_extensions)
supported_versions = map(lambda s: s.lower(), supported_versions)
supported_output_formats = map(lambda s: s.lower(), supported_output_formats)
