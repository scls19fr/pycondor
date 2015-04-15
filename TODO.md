convert Condor (x, y) coordinates to lat, long
see https://github.com/mpusz/Condor2Nav/blob/master/src/condor.cpp
see NaviCon.dll
depends of Landscape
http://forum.condorsoaring.com/viewtopic.php?t=8824

	# https://docs.python.org/2/library/ctypes.html
	# http://starship.python.net/crew/theller/ctypes/tutorial.html
	# https://github.com/mpusz/Condor2Nav/blob/master/src/condor.cpp
	# http://stackoverflow.com/questions/252417/how-can-i-use-a-dll-from-python
	# https://docs.python.org/2/library/ctypes.html

	import os
	import ctypes
	from ctypes import *

	condor_path = "C:\\Program Files (x86)\\Condor"
	dll_filename = os.path.join(condor_path, 'NaviCon.dll')

	#NaviConInit, GetMaxX, GetMaxY, XYToLon, XYToLat function
	#// NaviCon.dll interface
	#using FNaviConInit = int(WINAPI*)(const char *trnFile);
	#using FXYToLon = float(WINAPI*)(float X, float Y);
	#using FXYToLat = float(WINAPI*)(float X, float Y);
	#using FGetMaxX = float(WINAPI*)();
	#using FGetMaxY = float(WINAPI*)();
	  
	trn_name = "alps_XL"
	trn_path = os.path.join(condor_path, "Landscapes", trn_name, trn_name + ".trn")

	#mydll.NaviConInit(byref(trn_path))
	#----> 1 mydll.NaviConInit(c_char_p(trn_path))
	#ValueError: Procedure called with not enough arguments (4 bytes missing) or wrong calling conventio

	#mydll = ctypes.cdll.LoadLibrary(dll_filename)

	mydll = ctypes.WinDLL(dll_filename)

	mydll.NaviConInit.argtypes = [c_char_p]
	mydll.NaviConInit.restype = c_int

	mydll.GetMaxX.argtypes = []
	mydll.GetMaxX.restype = c_float

	mydll.GetMaxY.argtypes = []
	mydll.GetMaxY.restype = c_float

	mydll.XYToLon.argtypes = [c_float, c_float]
	mydll.XYToLon.restype = c_float

	mydll.XYToLat.argtypes = [c_float, c_float]
	mydll.XYToLat.restype = c_float

	mydll.NaviConInit(trn_path)

	mydll.GetMaxX()
	mydll.GetMaxY()

	mydll.XYToLon(0.0,0.0)
	mydll.XYToLat(0.0,0.0)

generate XCSoar 6 file
http://git.xcsoar.org/cgit/max/xcsoar.git/tree/src/Task
