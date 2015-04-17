#!/usr/bin/env python
#-*- coding:utf-8 -*-

from aerofiles.xcsoar import Writer, TaskType, PointType, ObservationZoneType, AltitudeReference

# see https://github.com/Turbo87/aerofiles/blob/master/aerofiles/xcsoar/

class ObservationZone:
    def __init__(self, **kw):
        assert 'type' in kw

        self.type = kw['type']

        if kw['type'] == ObservationZoneType.LINE:
            assert 'length' in kw
            self.length = kw['length']

        elif kw['type'] == ObservationZoneType.CYLINDER:
            assert 'radius' in kw
            self.radius = kw['radius']

        elif kw['type'] == ObservationZoneType.SECTOR:
            assert 'radius' in kw
            assert 'start_radial' in kw
            assert 'end_radial' in kw
            self.radius = kw['radius']
            self.start_radial = kw['start_radial']
            self.end_radial = kw['end_radial']

        elif kw['type'] == ObservationZoneType.SYMMETRIC_QUADRANT:
            assert 'radius' in kw
            self.radius = kw['radius']

        elif kw['type'] == ObservationZoneType.CUSTOM_KEYHOLE:
            assert 'radius' in kw
            assert 'inner_radius' in kw
            assert 'angle' in kw
            self.radius = kw['radius']
            self.inner_radius = kw['inner_radius']
            self.angle = kw['angle']

    def __str__(self):
        s = self.type + " "
        for key, val in self.__dict__.items():
            if key!="type":
                s += "%s: %s" % (key, val)
        return(s)


