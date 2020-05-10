import csv, sqlite3
import pandas as pd
import utm
import math
import numpy as np

class databaseReader:
  PVID_INDEX = 0
  SLOPE_INDEX = 21
  def __init__(self, database_name):
    self.con = sqlite3.connect(database_name)
    self.cur = self.con.cursor()

  def get_record_by_id(self, idno):
    self.cur.execute("select * from link_data where linkPVID = %d"%(idno))
    rows = self.cur.fetchall()
    return rows

  def filter_matching_links(self, latitude, longitude):
    query = 'select * from link_data where min_latitude < %f and max_latitude\
            > %f and min_longitude < %f and max_longitude > %f'%(latitude, latitude,
                                                                 longitude, longitude)

    self.cur.execute(query)
    rows = self.cur.fetchall()
    print("rows: ")
    print(rows)
    return rows

  def insert_slope_data(self, linkrecord, newslope):

    print('link_record $$$$$$$$$$$$')
    print(linkrecord)
    # linkPVID = linkrecord[self.PVID_INDEX]
    linkPVID = linkrecord
    print('linkPVID')
    print(linkPVID)
    if(linkrecord):
      slope_string = str(linkrecord) + ',' + str(newslope)
    else:
      slope_string = str(newslope)
    query = " UPDATE link_data SET slope = '%s' WHERE linkPVID=%d;"%(slope_string, int(linkPVID))

    self.cur.execute(query)
    self.con.commit()

  def __del__(self):
    self.con.close()


def map_match(links, probe):
    # Design map matching algorithm and return the mathched link

    closest_node_dist_sqr = 1000
    probe_lat = probe[2]
    probe_lon = probe[3]
    probe_utm_e, probe_utm_n, probe_zone_num, probe_zone_let = utm.from_latlon(float(probe_lat), float(probe_lon))

    closest_link = 0;
    for link in links:
        print('link^^^^')
        print(link[14])
        node_list = []
        node_list.append(link[14].split('|'))
        node_list = node_list[0]
        print('node_list %%%%')
        print(node_list)
        for node in node_list:
            print('node!!!!!!')
            print(node)
            node_info = []
            node_info = node.split('/')
            # convert to cartesian cord
            utm_e, utm_n, zone_num, zone_let = utm.from_latlon(float(node_info[0]), float(node_info[1]))
            if (utm_e - probe_utm_e)**2 + (utm_n - probe_utm_n)**2 < closest_node_dist_sqr:
                # save link PVID of closest link
                closest_link = int(link[0])
                closest_node_dist_sqr = (utm_e - probe_utm_e)**2 + (utm_n - probe_utm_n)**2


    return closest_link

def return_gaussian_probability(error, std):
    probability = 1/ (np.sqrt(2 * np.pi) * std) * np.exp(-(error)**2/(2 * std**2))
    return probability


def map_match_line_interpolated(links, probe):
    # Design map matching algorithm and return the mathched link

    probe_lat = probe[2]
    probe_lon = probe[3]
    px, py, probe_zone_num, probe_zone_let = utm.from_latlon(float(probe_lat), float(probe_lon))
    closest_link = []
    probe_heading = probe[-1]

    d_std = 5.0
    h_std = 1.047 # 60 degrees

    sub_link_indices = []
    all_link_probs = []

    for link in links:
        shape_points_list = link[14].split('|')
        direction = link[5]
        lines = []
        first_point = []
        cartesian_shape_points = []
        for shape_pt in shape_points_list:
            shape_latitude, shape_longitude = shape_pt.split('/')[:2]
            utm_e, utm_n, _, _= utm.from_latlon(float(shape_latitude), float(shape_longitude))
            cartesian_shape_points.append([utm_e, utm_n])

        previous_pt = cartesian_shape_points[0]
        all_sublink_probs = []
        for current_pt in cartesian_shape_points[1:]:
            vx1, vy1 = previous_pt
            vx2, vy2 = current_pt
            t = ((vx1 - px) * (vx2 - vx1) + (vy1 - py) * (vy2 - vy1)) / ((vx2-vx1)**2 + (vy2-vy1)**2)
            if (0 <= t <= 1):
                dst = abs((vx2-vx1)*(vy1-py) - (vy2-vy1) * (vx1-px)) / (math.sqrt(vx2-vx1) + (vy2-vy1)**2)
            else:
                d1 = math.sqrt((vx1-px)**2 + (vy1-py)**2)
                d2 = math.sqrt((vx2-px)**2 + (vy2-py)**2)
                dst = min(d1, d2)
            if direction == 'F':
                heading = math.atan2(vy2-vy1, vx2-vx1)
            else:
                heading = math.atan2(vy1-vy2, vx1-vx2)
            h_error  = heading - math.radians(probe_heading)
            heading_difference = math.atan2(np.sin(h_error), np.cos(h_error))
            p_link_probability = return_gaussian_probability(dst, d_std) *\
                                 return_gaussian_probability(heading_difference, h_std)
            all_sublink_probs.append(p_link_probability)
        max_index = all_sublink_probs.index(max(all_sublink_probs))
        sub_link_indices.append(max_index)
        all_link_probs.append(all_sublink_probs[max_index])
    matched_link_index = all_link_probs.index(max(all_link_probs))
    sublink_index = sub_link_indices[matched_link_index]
    closest_link = links[matched_link_index]
 
    return closest_link, sublink_index

def calculate_slope(probe_data, previous_probe_data):
    # calculate the slope of the point with probe data

    return 4.5

def analyse_probedata(probe_csv_path, op_csv_path):
    linkdatabase = databaseReader('roadlink_4.db')
    probe_iterator =  pd.read_csv(probe_csv_path, sep=',', header = None, chunksize=1)
    previous_link_match = None
    previous_probe_point = [None for i in range(7)]

    for probe_data in probe_iterator:

        # All probe details
        sampleID = int(probe_data[0].values[0])
        dateTime = probe_data[1].values[0]
        sourcecode = int(probe_data[2].values[0])
        latitude = float(probe_data[3].values[0])
        longitude = float(probe_data[4].values[0])
        altitude = float(probe_data[5].values[0])
        speed = float(probe_data[6].values[0])
        heading = float(probe_data[7].values[0])
        probe_data_formatted = [sampleID, dateTime, latitude, longitude, altitude,
                               speed, heading]
        print(probe_data)

        # Primitive filtering of link data
        relevant_links = linkdatabase.filter_matching_links(latitude, longitude)

        # core function
        # matched_link = map_match(relevant_links, probe_data_formatted)
        matched_link, sublink_index = map_match_line_interpolated(relevant_links, probe_data_formatted)
        if previous_probe_point[0] == probe_data_formatted[0] and\
           previous_link_match == matched_link:
          slope_value = calculate_slope(probe_data_formatted, previous_probe_point)
          linkdatabase.insert_slope_data(matched_link, slope_value)

        # Update map matching data
        direction = 'T'
        reference_node_distance = 10
        distance_from_link = 11

        print('matched_link')
        print(matched_link)
        probe_data.insert(8, 'linkPVID', matched_link)
        probe_data.insert(9, 'direction', direction)
        probe_data.insert(10, 'distFromRef', reference_node_distance)
        probe_data.insert(11, 'distFromLink', distance_from_link)

        # Write results back to a csv file

        probe_data.to_csv(op_csv_path,
             index=False,
             header=False,
             mode='a',#append data to csv file
             chunksize=1)


        previous_probe_point = probe_data_formatted
        previous_link_match = matched_link

        # Write slope values back to db


if __name__=='__main__':

    probe_path = '/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_2/probe_data_map_matching (1)/Partition6467ProbePoints.csv'
    op_path = '/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_2/probe_data_map_matching (1)/op_mathced.csv'
    analyse_probedata(probe_path, op_path)


