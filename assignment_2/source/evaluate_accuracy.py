import pandas as pd
import math

import utm

def evaluate_results(csv_path):
    link_iterator =  pd.read_csv(csv_path, sep=',', chunksize=1)
    #previous_link_match = None
    #previous_probe_point = [None for i in range(7)]
    N = 0
    average_error = 0

    for link_data in link_iterator:
        slope = link_data.slope.values[0]
        # slope = '0:2.5, 1:4.7, 0:6.7'
        if(type(slope) != type('aa')):
            continue

        slope_list  = slope.split(',')

        gt_slope  = link_data.slopeInfo.values[0]

        # Sometimes the gt_slop goes to nan when it is not available.
        # This is a very crappy way to check the data but works

        if slope == '' or type(gt_slope) != type('aa'):
            continue

        shape_points_list = link_data.shapeInfo.values[0].split('|')
        cartesian_shape_points = []
        for shape_pt in shape_points_list:
            shape_latitude, shape_longitude = shape_pt.split('/')[:2]
            utm_e, utm_n, _, _= utm.from_latlon(float(shape_latitude), float(shape_longitude))
            cartesian_shape_points.append([utm_e, utm_n])

        distances = []
        previous_pt = cartesian_shape_points[0]
        for current_pt in cartesian_shape_points[1:]:
            x1, y1 = previous_pt
            x2, y2 = current_pt

            dst =  math.sqrt((x1-x2)**2+ (y1 - y2)**2)
            previous_pt = current_pt
            distances.append(dst)

        divide_sum = 0
        weighted_slope = 0

        data_count = 0


        for slope_value in slope_list:
            sub_link_idx, slope_value = slope_value.split(':')
            sub_link_idx = int(sub_link_idx)
            slope_value = float(slope_value)
            # Again very crappy code and software architecture. I let the 
            # system run into zero / zero error during slope calculation.
            # Couldn't cut it down in the middle and change it since more than
            # few ten thousands of data poitns were already processed. This
            # is just a short circuit to eliminate that faulty dat
            if(math.isnan(slope_value)):
                continue
            divide_sum += distances[sub_link_idx]
            weighted_slope += distances[sub_link_idx] * slope_value
            data_count += 1
        if(data_count == 0):
            continue
        weighted_slope = weighted_slope / divide_sum

        gt_slope = gt_slope.split('|')
        gt_divide_sum = 0
        gt_weighted_slope = 0
        previous_distance = 0

        if not gt_slope:
            continue

        for slope_value in gt_slope:
            distance, slope = slope_value.split('/')
            distance = float(distance) 
            slope = float(slope)
            segment_length = distance - previous_distance
            gt_weighted_slope += segment_length * slope 
            gt_divide_sum += segment_length
            previous_distance = distance
        gt_weighted_slope = gt_weighted_slope / gt_divide_sum
        average_error = (average_error * N + (gt_weighted_slope - weighted_slope) ** 2)/ (N+1) 
        #print(gt_weighted_slope, weighted_slope, average_error)
        N = N+1
        if N % 200== 0:
            print('current accuracy:', math.sqrt(average_error))






if __name__=='__main__':
    csv_path='/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_2/source/link_data_final.csv'
    evaluate_results(csv_path)
