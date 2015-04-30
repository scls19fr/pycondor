#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from ctypes import WinDLL, c_char_p, c_int, c_float

class NaviConDLL(WinDLL):
    def __init__(self, condor_path):       
        self.condor_path = condor_path
        dll_filename = os.path.join(condor_path, 'NaviCon.dll')
        print("Using functions from '%s'" % dll_filename)

        super(NaviConDLL, self).__init__(dll_filename)

        self.NaviConInit.argtypes = [c_char_p]
        self.NaviConInit.restype = c_int

        self.GetMaxX.argtypes = []
        self.GetMaxX.restype = c_float

        self.GetMaxY.argtypes = []
        self.GetMaxY.restype = c_float

        self.XYToLon.argtypes = [c_float, c_float]
        self.XYToLon.restype = c_float

        self.XYToLat.argtypes = [c_float, c_float]
        self.XYToLat.restype = c_float
        
    def init(self, landscape):
        print("With landscape '%s'" % landscape)
        print("")
        trn_path = os.path.join(self.condor_path, "Landscapes", landscape, landscape + ".trn")
        if not os.path.isfile(trn_path):
            raise(Exception("Can't init landscape '%s' from '%s'" % (landscape, trn_path)))

        return(self.NaviConInit(trn_path))

    def xy_max(self):
        return(self.GetMaxX(), self.GetMaxY())

    def xy_to_lat_lon(self, x, y):
        return(self.XYToLat(x, y), self.XYToLon(x, y))
        
        
def iter_landscapes(condor_path):
    landscapes_path = os.path.join(condor_path, "Landscapes")
    for landscape in os.listdir(landscapes_path):
        if not os.path.isdir(os.path.join(landscapes_path, landscape)):
            break
        yield(landscape)
