from urllib import request
import requests
from tilesystem import TileSystem
from PIL import Image
import os
import numpy as np

import cv2


TILESIZE = 256              


def download_image(location_coordinates, tileSystem_level, null_image):
    min_latitude, max_latitude, min_longitude, max_longitude = location_coordinates
    x1, y1 = TileSystem.latlong_to_pixelXY(min_latitude, min_longitude, tileSystem_level)
    x2, y2 = TileSystem.latlong_to_pixelXY(max_latitude, max_longitude, tileSystem_level)
    X1, Y1 = TileSystem.pixelXY_to_tileXY(min(x1,x2), min(y1,y2))
    X2, Y2 = TileSystem.pixelXY_to_tileXY(max(x1,x2), max(y1,y2))
    success_status = True

    mapurl = "http://h0.ortho.tiles.virtualearth.net/tiles/h{0}.jpeg?g=131"
    final_image = np.zeros( ((Y2-Y1+1) * TILESIZE, (X2-X1+1) * TILESIZE, 3), dtype=np.uint8)
    start_y = 0
    end_y = TILESIZE
    start_x = 0
    end_x = TILESIZE

    for Y in range(Y1, Y2+1):
      for X in range(X1, X2 +1):
        quadkey = TileSystem.tileXY_to_quadkey(X, Y, tileSystem_level)
        resp = requests.get(mapurl.format(quadkey), stream=True).raw
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        if(np.equal(image, null_image).all()):
            success_status = False
            break
        final_image[start_y:end_y, start_x:end_x, :] = image
        start_x += TILESIZE
        end_x += TILESIZE

        #cv2.imwrite('image_iter'+str(Y)+str(X)+'.png', image)
      start_x = 0
      end_x = TILESIZE
      start_y += TILESIZE
      end_y += TILESIZE
      #temp_view = cv2.resize(final_image, (2000, 2000))
      #cv2.imwrite('image'+str(Y)+str(X)+'.png', temp_view)



      if(not success_status):
          break

    if(not success_status):
      final_image, tileSystem_level = download_image(location_coordinates, tileSystem_level-1, null_image)
    return  final_image, tileSystem_level

def retrieve_aerial_image(coodinates, op_path, image_name):

  mapurl = "http://h0.ortho.tiles.virtualearth.net/tiles/h{0}.jpeg?g=131"
  null_key = '11111111111111111111'

  resp = requests.get(mapurl.format(null_key), stream=True).raw
  null_image = np.asarray(bytearray(resp.read()), dtype="uint8")
  null_image = cv2.imdecode(null_image, cv2.IMREAD_COLOR)

  original_image, tile_size = download_image(coodinates, TileSystem.MAXLEVEL, null_image)
  cv2.imwrite(os.path.join(op_path, image_name+'_original_'+'level'+str(tile_size)+'.png'), original_image)

  resized_image = cv2.resize(original_image, (2000, 2000))
  cv2.imwrite(os.path.join(op_path, image_name+'_resized'+'level'+str(tile_size)+'.png'), resized_image)

      
if __name__=='__main__':

  # Northwestern 42.052597, -87.680291, 42.061201, -87.669271
  # min_lat = 42.052597
  # max_lat = 42.061201
  # min_lon = -87.680291
  # max_lon = -87.669271
     
  min_lat = 40.428509
  max_lat = 40.438538
  min_lon = 116.561515
  max_lon = 116.579476
  coodinates = [min_lat, max_lat, min_lon, max_lon]
  retrieve_aerial_image(coodinates, op_path='./', image_name='nu_campus')



