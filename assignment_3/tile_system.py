#  This file is a python version of the code preseneted at:
#  https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system

import os
from math import cos, sin, pi, log, atan, exp, floor
from itertools import chain
import re


class TileSystem(object):


    EarthRadius = 6378137;
    MinLat = -85.05112878;
    MaxLat = 85.05112878;
    MinLong = -180;
    MaxLong = 180;
    MaxLevel = 23



    def Clip(val, minVal, maxVal):
        # Clips a number to the specified minimum and maximum values.
        return min(max(val, minVal), maxVal)


    def Map_Size(levelOfDetail):
        # Determines the map width and height (in pixels) at a specified level of detail.
        return 256 << levelOfDetail


    def Ground_Resolution(latitude, levelOfDetail):
        # Determines the ground resolution (in meters per pixel) at a specified latitude
        # and level of detail.
        latitude = TileSystem.Clip(latitude, TileSystem.MinLat, TileSystem.MaxLat)
        return cos(latitude * pi / 180) * 2 * pi * TileSystem.EarthRadius / TileSystem.Map_Size(levelOfDetail)


    def Map_Scale (latitude, levelOfDetail, screenDpi):
        # Determines the map scale at a specified latitude, level of detail,
        # and screen resolution.
        return TileSystem.Ground_Resolution(latitude, levelOfDetail) * screenDpi / 0.0254


    def LatLong_To_PixelXY(latitude, longitude, levelOfDetail):
        # Converts a point from latitude/longitude WGS-84 coordinates (in degrees)
        # into pixel XY coordinates at a specified level of detail.
        latitude = TileSystem.Clip(latitude, TileSystem.MinLat, TileSystem.MaxLat)
        longitude = TileSystem.Clip(longitude, TileSystem.MinLong,  TileSystem.MaxLong)

        x = (longitude + 180) / 360
        sinLatitude = sin(latitude * pi / 180)
        y = 0.5 - log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * pi)

        mapsize = TileSystem.Map_Size(levelOfDetail)
        pixelX, pixelY = floor(TileSystem.Clip(x * mapsize + 0.5, 0, mapsize - 1)), \
                        floor(TileSystem.Clip(y * mapsize + 0.5, 0, mapsize - 1))
        return pixelX, pixelY


    def PixelXY_To_LatLong(pixelX, pixelY, levelOfDetail):
        # Converts a pixel from pixel XY coordinates at a specified level of detail
        # into latitude/longitude WGS-84 coordinates (in degrees).
        mapsize = TileSystem.Map_Size(levelOfDetail)
        pix_x = TileSystem.Clip(pixelX, 0, mapsize - 1) / mapsize - 0.5
        pix_y = 0.5 - 360 * TileSystem.Clip(pixelY, 0, mapsize - 1) / mapsize

        latitude = 90 - 360 * atan(exp(-pix_y * 2 * pi)) / pi
        longitude = 360 * pix_x
        return latitude, longitude


    def PixelXY_To_TileXY(pixelX, pixelY):
        # Converts pixel XY coordinates into tile XY coordinates of the tile containing
        # the specified pixel.
        return floor(pixelX / 256), floor(pixelY / 256)


    def TileXY_To_PixelXY(tileX, tileY):
        # Converts tile XY coordinates into pixel XY coordinates of the upper-left pixel
        # of the specified tile.
        return tileX * 256, tileY * 256



    def TileXY_To_QuadKey(tileX, tileY, levelOfDetail):
        # Converts tile XY coordinates into a QuadKey at a specified level of detail.
        tileX_bits = '{0:0{1}b}'.format(tileX, levelOfDetail)
        tileY_bits = '{0:0{1}b}'.format(tileY, levelOfDetail)

        quadKey = ''.join(chain(*zip(tileY_bits, tileX_bits)))
        return ''.join([str(int(num, 2)) for num in re.findall('..?', quadKey)])


    def Quadkey_To_TileXY(quadkey):
        #Converts a QuadKey into tile XY coordinates.
        quadKey = ''.join(['{0:02b}'.format(int(num)) for num in quadkey])
        tileX, tileY = int(quadKey[1::2], 2), int(quadKey[::2], 2)
        return tileX, tileY
