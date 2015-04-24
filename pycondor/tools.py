#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Tools



ToDo: ToFix / ToTest

"""

import math

def waypoint_bearing(lon1, lat1, lon2, lat2)
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

    return (x==0 && y==0) ? 0 : (static_cast<unsigned>(360 + math.degrees(math.atan2(y, x)) + 0.5) % 360)

