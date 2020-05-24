from urllib import request
import requests
from tilesystem import TileSystem
from PIL import Image
import os
import numpy as np

import cv2


MAPMAXSIZE = 8192 * 8192 * 8 
TILESIZE = 256              


def download_image(location_coordinates, tileSystem_level, null_image, op_path):
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
        r = requests.get(mapurl.format(quadkey))
        with request.urlopen(mapurl.format(quadkey)) as file:
          image = Image.open(file)
          #image = cv2.imread(file)
        resp = requests.get(mapurl.format(quadkey), stream=True).raw
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        if(np.equal(image, null_image).all()):
            success_status = False
            break
        final_image[start_y:end_y, start_x:end_x, :] = image
        start_x += TILESIZE
        end_x += TILESIZE

        cv2.imwrite('image_iter'+str(Y)+str(X)+'.png', image)
      start_x = 0
      end_x = TILESIZE
      start_y += TILESIZE
      end_y += TILESIZE
      temp_view = cv2.resize(final_image, (2000, 2000))
      cv2.imwrite('image'+str(Y)+str(X)+'.png', temp_view)

      print(success_status)


      if(not success_status):
          break

    if(not success_status):
      download_image(location_coordinates, tileSystem_level-1, null_image, op_path)
    else:
      return
      
 
    
        # imagelist = []
        # for tileX in range(tileX_start, tileX_end + 1):
        #     quadkey = TileSystem.tileXY_to_quadkey(tileX, tileY, level)
        #     image = self.download_image(quadkey)
        #     if self.is_valid_image(image):
        #         imagelist.append(image)
        #     else:
        #         #print(quadkey)
        #         print("Cannot find tile image at level {0} for tile coordinate ({1}, {2})".format(level, tileX, tileY))
        #         return False, None
        # result = Image.new('RGB', (len(imagelist) * TILESIZE, TILESIZE))

       
       # or levl in range(TileSystem.MAXLEVEL, 0, -1):
        #     pixelX1, pixelY1 = TileSystem.latlong_to_pixelXY(self.lat1, self.lon1, levl)
        #     pixelX2, pixelY2 = TileSystem.latlong_to_pixelXY(self.lat2, self.lon2, levl)

        #     pixelX1, pixelX2 = min(pixelX1, pixelX2), max(pixelX1, pixelX2)
        #     pixelY1, pixelY2 = min(pixelY1, pixelY2), max(pixelY1, pixelY2)


        #     #Bounding box's two coordinates coincide at the same pixel, which is invalid for an aerial image.
        #     #Raise error and directly return without retriving any valid image.
        #     if abs(pixelX1 - pixelX2) <= 1 or abs(pixelY1 - pixelY2) <= 1:
        #         print("Cannot find a valid aerial imagery for the given bounding box!")
        #         return

        #     if abs(pixelX1 - pixelX2) * abs(pixelY1 - pixelY2) > IMAGEMAXSIZE:
        #         print("Current level {} results an image exceeding the maximum image size (8192 * 8192), will SKIP".format(levl))
        #         continue

        #     tileX1, tileY1 = TileSystem.pixelXY_to_tileXY(pixelX1, pixelY1)
        #     tileX2, tileY2 = TileSystem.pixelXY_to_tileXY(pixelX2, pixelY2)

        #     # Stitch the tile images together
        #     result = Image.new('RGB', ((tileX2 - tileX1 + 1) * TILESIZE, (tileY2 - tileY1 + 1) * TILESIZE))
        #     retrieve_sucess = False
        #     for tileY in range(tileY1, tileY2 + 1):
        #         retrieve_sucess, horizontal_image = self.horizontal_retrieval_and_stitch_image(tileX1, tileX2, tileY, levl)
        #         if not retrieve_sucess:
        #             break
        #         result.paste(horizontal_image, (0, (tileY - tileY1) * TILESIZE))

        #     if not retrieve_sucess:
        #         continue

        #     # Crop the image based on the given bounding box
        #     leftup_cornerX, leftup_cornerY = TileSystem.tileXY_to_pixelXY(tileX1, tileY1)
        #     retrieve_image = result.crop((pixelX1 - leftup_cornerX, pixelY1 - leftup_cornerY, \
        #                                 pixelX2 - leftup_cornerX, pixelY2 - leftup_cornerY))
        #     print("Finish the aerial image retrieval, store the image aerialImage_{0}.jpeg in folder {1}".format(levl, self.tgtfolder))
        #     filename = os.path.join(self.tgtfolder, 'aerialImage_{}.jpeg'.format(levl))
        #     retrieve_image.save(filename)
        #     return True
        # return False
if __name__=='__main__':

  # Northwestern 42.052597, -87.680291, 42.061201, -87.669271
  min_lat = 42.052597
  max_lat = 42.061201
  min_lon = -87.680291
  max_lon = -87.669271

  mapurl = "http://h0.ortho.tiles.virtualearth.net/tiles/h{0}.jpeg?g=131"
  null_key = '11111111111111111111'

  resp = requests.get(mapurl.format(null_key), stream=True).raw
  null_image = np.asarray(bytearray(resp.read()), dtype="uint8")
  null_image = cv2.imdecode(null_image, cv2.IMREAD_COLOR)

  coodinates = [min_lat, max_lat, min_lon, max_lon]
  download_image(coodinates, TileSystem.MAXLEVEL, null_image, op_path='./results')

