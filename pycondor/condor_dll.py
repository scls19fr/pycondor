#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from ctypes import WinDLL, c_char_p, c_int, c_float

def init_navicon_dll(condor_path, landscape):
    dll_filename = os.path.join(condor_path, 'NaviCon.dll')
    print("Using functions from '%s'" % dll_filename)
    print("With landscape '%s'" % landscape)
    print("")
    trn_path = os.path.join(condor_path, "Landscapes", landscape, landscape + ".trn")

    navicon_dll = WinDLL(dll_filename)

    navicon_dll.NaviConInit.argtypes = [c_char_p]
    navicon_dll.NaviConInit.restype = c_int

    navicon_dll.GetMaxX.argtypes = []
    navicon_dll.GetMaxX.restype = c_float

    navicon_dll.GetMaxY.argtypes = []
    navicon_dll.GetMaxY.restype = c_float

    navicon_dll.XYToLon.argtypes = [c_float, c_float]
    navicon_dll.XYToLon.restype = c_float

    navicon_dll.XYToLat.argtypes = [c_float, c_float]
    navicon_dll.XYToLat.restype = c_float

    navicon_dll.NaviConInit(trn_path)

    return(navicon_dll)
