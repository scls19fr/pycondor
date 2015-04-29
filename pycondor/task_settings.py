#!/usr/bin/env python
#-*- coding:utf-8 -*-

from aerofiles.xcsoar import Writer, TaskType, PointType, ObservationZoneType, AltitudeReference
from observation_zone import ObservationZone

class SettingsTask(object):
    AATEnabled = False

    aat_min_time = 0

    start_min_height = 0
    start_min_height_ref = AltitudeReference.AGL

    start_max_height = 0
    start_max_height_ref = AltitudeReference.AGL

    start_max_speed = 0

    finish_min_height = 0
    finish_min_height_ref = AltitudeReference.AGL

    def __init__(self):
        pass

def add_observation_zone(settings_task, df_task):
    for i, tp in df_task.iterrows():
        if i==0:
            df_task.loc[i,'Type'] = PointType.START
            df_task.loc[i, 'ObservationZone'] = ObservationZone(type=ObservationZoneType.CYLINDER, radius=500)
        elif i==df_task.index[-1]:
            df_task.loc[i,'Type'] = PointType.FINISH
            df_task.loc[i, 'ObservationZone'] = ObservationZone(type=ObservationZoneType.LINE, length=500)
        elif settings_task.AATEnabled:
            df_task.loc[i,'Type'] = PointType.AREA
            df_task.loc[i, 'ObservationZone'] = ObservationZone(type=ObservationZoneType.CYLINDER, radius=1000)
        else:
            df_task.loc[i,'Type'] = PointType.TURN
            df_task.loc[i, 'ObservationZone'] = ObservationZone(type=ObservationZoneType.CYLINDER, radius=1000)
    return(df_task)
