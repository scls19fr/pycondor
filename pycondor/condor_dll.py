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
    if not os.path.isfile(trn_path):
        return

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

class NaviConDLL(object):
    def __init__(self, condor_path):
        self.condor_path = condor_path
        dll_filename = os.path.join(condor_path, 'NaviCon.dll')
        print("Using functions from '%s'" % dll_filename)

        self._dll = WinDLL(dll_filename)

        self._dll.NaviConInit.argtypes = [c_char_p]
        self._dll.NaviConInit.restype = c_int

        self._dll.GetMaxX.argtypes = []
        self._dll.GetMaxX.restype = c_float

        self._dll.GetMaxY.argtypes = []
        self._dll.GetMaxY.restype = c_float

        self._dll.XYToLon.argtypes = [c_float, c_float]
        self._dll.XYToLon.restype = c_float

        self._dll.XYToLat.argtypes = [c_float, c_float]
        self._dll.XYToLat.restype = c_float
        
    def init(self, landscape):
        print("With landscape '%s'" % landscape)
        print("")
        trn_path = os.path.join(self.condor_path, "Landscapes", landscape, landscape + ".trn")
        if not os.path.isfile(trn_path):
            raise(Exception("Can't init landscape '%s' from '%s'" % (landscape, trn_path)))

        return(self._dll.NaviConInit(trn_path))

    def xy_max(self):
        return(self._dll.GetMaxX(), self._dll.GetMaxY())

    def xy_to_lat_lon(self, x, y):
        return(self._dll.XYToLat(x, y), self._dll.XYToLon(x, y))
        
        
def iter_landscapes(condor_path):
    landscapes_path = os.path.join(condor_path, "Landscapes")
    for landscape in os.listdir(landscapes_path):
        if not os.path.isdir(os.path.join(landscapes_path, landscape)):
            break
        yield(landscape)
