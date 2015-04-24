#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Tools


http://en.wikipedia.org/wiki/Haversine_formula

ToDo: ToFix / ToTest

"""

import math

def waypoint_bearing(lon1, lat1, lon2, lat2):
    """
    Calculates the bearing between 2 locations.

    Method calculates the bearing between 2 locations.

    @param lon1 First point longitude.
    @param lat1 First point latitude.
    @param lon2 Second point longitude.
    @param lat2 Second point latitude.

    @return The bearing between 2 locations.
    """


    longitude1 = math.radians(lon1)
    latitude1 = math.radians(lat1)
    longitude2 = math.radians(lon2)
    latitude2 = math.radians(lat2)
  
    clat1 = math.cos(latitude1)
    clat2 = math.cos(latitude2)
    dlon = longitude2 - longitude1

    y = math.sin(dlon) * clat2
    x = clat1 * math.sin(latitude2) - math.sin(latitude1) * clat2 * math.cos(dlon)

    if x==0 and y==0:
        return(0.0)
    else:
        return((360 + math.degrees(math.atan2(y, x)) + 0.5) % 360.0)


def haversine_bearing(lon1, lat1, lon2, lat2):
	rlat1 = math.radians(lat1)
	rlat2 = math.radians(lat2)
	rlon1 = math.radians(lon1)
	rlon2 = math.radians(lon2)
	dlon = math.radians(lon2-lon1)
 
	b = math.atan2(math.sin(dlon)*math.cos(rlat2),math.cos(rlat1)*math.sin(rlat2)-math.sin(rlat1)*math.cos(rlat2)*math.cos(dlon)) # bearing calc
	bd = math.degrees(b)
	br, bn = divmod(bd+360,360) # the bearing remainder and final bearing
	
	return bn

(lon1, lat1, lon2, lat2) = (45.0, 1.0, 45.5, 2.0)

bearing = waypoint_bearing(lon1, lat1, lon2, lat2)
print(bearing)
bearing = haversine_bearing(lon1, lat1, lon2, lat2)
print(bearing)
