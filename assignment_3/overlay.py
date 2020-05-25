import random

import numpy as np
import cv2

import overpy
from tilesystem import TileSystem

def overlay_ways(coorindates, aerial_image_path):
  min_latitude, max_latitude, min_longitude, max_longitude = coorindates

  api = overpy.Overpass()
  
  #roadcolor = (255, 0, 0) #  blue color
  roadthickness = 50
  
  aerial_image = cv2.imread(aerial_image_path)
  colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (203, 192, 255),
            (0, 255, 255), (42, 42, 165), (0, 165, 255), (216, 235, 52)]
  
  
  # fetch all ways and nodes
  result = api.query("""
      way(%f, %f, %f, %f) ["highway"];
      (._;>;);
      out body;
      """%(min_latitude, min_longitude, max_latitude, max_longitude))
  
  
  tile_level = int(aerial_image_path[-6:-4])
  x1, y1 = TileSystem.latlong_to_pixelXY(min_latitude, min_longitude, tile_level)
  x2, y2 = TileSystem.latlong_to_pixelXY(max_latitude, max_longitude, tile_level)
  
  
  image = np.zeros((abs(y2-y1), abs(x2-x1), 3))
  start_x = min(x1, x2)
  start_y = min(y1, y2)
  
  for way in result.ways:
      # print("Name: %s" % way.tags.get("name", "n/a"))
      # print("  Highway: %s" % way.tags.get("highway", "n/a"))
      # print("  Nodes:")
      if 'highway' in way.tags.keys():

        prev_nodeX = way.nodes[0].lat
        prev_nodeY = way.nodes[0].lon
  
        prev_nodeX, prev_nodeY = TileSystem.latlong_to_pixelXY(float(way.nodes[0].lat), float(way.nodes[0].lon), tile_level)
        prev_nodeX = prev_nodeX - start_x
        prev_nodeY = prev_nodeY - start_y
        color = random.choice(colors)
        for node in way.nodes[1:]:
  
           current_nodeX, current_nodeY = TileSystem.latlong_to_pixelXY(float(node.lat), float(node.lon), tile_level)
           current_nodeX = current_nodeX - start_x
           current_nodeY = current_nodeY -  start_y
  
           image = cv2.line(image,(prev_nodeX,prev_nodeY),(current_nodeX, current_nodeY), color,roadthickness)
           aerial_image = cv2.line(aerial_image,(prev_nodeX,prev_nodeY),(current_nodeX, current_nodeY), color,roadthickness)
           prev_nodeX = current_nodeX
           prev_nodeY = current_nodeY

  cv2.imwrite('network_only.png', image)
  resized_image = cv2.resize(image, None, fx=0.2, fy = 0.2)
  cv2.imwrite('network_only_resized.png', resized_image)
  cv2.imwrite('final_result.png', aerial_image)
  aerial_resized = cv2.resize(aerial_image, None, fx=0.2, fy=0.2)
  cv2.imwrite("final_result_resized.png", aerial_resized)

if __name__=='__main__':
  image_path = '/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_3/nu_campus_original_level20.png'
  min_lat = 42.049457   
  max_lat = 42.062380
  min_lon = -87.681498
  max_lon = -87.668744
  coordinates = [min_lat, max_lat, min_lon, max_lon]
  overlay_ways(coordinates, image_path)
