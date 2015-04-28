#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Tools


http://en.wikipedia.org/wiki/Haversine_formula

ToDo: ToFix / ToTest

"""

import math

def waypoint_bearing(lat1, lon1, lat2, lon2):
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


def haversine_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing from 1 point to 1 other
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
 
    b = math.atan2(math.sin(dlon) * math.cos(lat2),
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)) # bearing calc

    bd = math.degrees(b)

    br, bn = divmod(bd + 360, 360) # the bearing remainder and final bearing
    
    return bn

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371.0 # Radius of earth in kilometers. Use 3956 for miles
    return(c * r)

def main():
    # Just some tests (should be removed)

    (lon1, lat1, lon2, lat2) = (45.0, 1.0, 45.5, 2.0)

    bearing = waypoint_bearing(lon1, lat1, lon2, lat2)
    print(bearing)
    bearing = haversine_bearing(lon1, lat1, lon2, lat2)
    print(bearing)

if __name__ == '__main__':
    main()
