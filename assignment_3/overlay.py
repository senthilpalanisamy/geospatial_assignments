import overpy

from tilesystem import TileSystem
import numpy as np
import cv2

api = overpy.Overpass()
min_latitude= 42.049457
max_latitude = 42.062380
min_longitude = -87.681498  
max_longitude = -87.668744

roadcolor = (255, 0, 0) # Red
roadthickness = 50

aerial_image = cv2.imread('/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_3/nu_campus_original_level20.png')


# fetch all ways and nodes
result = api.query("""
    way(%f, %f, %f, %f) ["highway"];
    (._;>;);
    out body;
    """%(min_latitude, min_longitude, max_latitude, max_longitude))


tile_level = 20
x1, y1 = TileSystem.latlong_to_pixelXY(min_latitude, min_longitude, tile_level)
x2, y2 = TileSystem.latlong_to_pixelXY(max_latitude, max_longitude, tile_level)


image = np.zeros((abs(y2-y1), abs(x2-x1), 3))
start_x = min(x1, x2)
start_y = min(y1, y2)

for way in result.ways:
    print("Name: %s" % way.tags.get("name", "n/a"))
    print("  Highway: %s" % way.tags.get("highway", "n/a"))
    print("  Nodes:")
    prev_nodeX = way.nodes[0].lat
    prev_nodeY = way.nodes[0].lon

    prev_nodeX, prev_nodeY = TileSystem.latlong_to_pixelXY(float(way.nodes[0].lat), float(way.nodes[0].lon), tile_level)
    prev_nodeX = prev_nodeX - start_x
    prev_nodeY = prev_nodeY - start_y
    for node in way.nodes[1:]:

       current_nodeX, current_nodeY = TileSystem.latlong_to_pixelXY(float(node.lat), float(node.lon), tile_level)
       current_nodeX = current_nodeX - start_x
       current_nodeY = current_nodeY -  start_y

       image = cv2.line(image,(prev_nodeX,prev_nodeY),(current_nodeX, current_nodeY), roadcolor,roadthickness)
       aerial_image = cv2.line(aerial_image,(prev_nodeX,prev_nodeY),(current_nodeX, current_nodeY), roadcolor,roadthickness)
       prev_nodeX = current_nodeX
       prev_nodeY = current_nodeY
cv2.imwrite('original_image.png', image)
resized_image = cv2.resize(image, None, fx=0.2, fy = 0.2)
cv2.imwrite('resized_image.png', resized_image)
cv2.imwrite('aerial_origianl.png', aerial_image)
Taerial_resized = cv2.resize(aerial_image, None, fx=0.2, fy=0.2)
cv2.imwrite("aerial_rezied.png", aerial_resized)

       # print("    Lat: %f, Lon: %f" % (node.lat, node.lon))

# 41.882981 -87.623496 41.882397 -87.623076

# import overpy
# api = overpy.Overpass()
# r = api.query(""" way["highway"](42.052476, -87.682073, 42.061279, -87.669325);out;""")
# print (len(r.ways))
