from django.contrib.gis.db import models
from django.contrib.gis.geos import LineString, MultiPolygon


class GisIndex1(models.Model):
    """Sequential migrations with implicit gis index"""

    # 0001
    # mpoint = models.PointField(spatial_index=True)
    # 0002
    mline = models.LineStringField(spatial_index=True, default=LineString(((0, 0), (0, 0))))
    # 0003
    mpoly = models.MultiPolygonField(db_index=True, default=MultiPolygon())
