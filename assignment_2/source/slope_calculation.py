import pandas as pd

def initiliase_dataset_iterators(link_path, probe_path):
    link_iterator =  pd.read_csv(link_path)
    probe_iterator = pd.read_csv(probe_path)
    iterators = [link_iterator, probe_iterator]

def add_min_max_longitude(in_csv, out_csv):

    #get the number of lines of the csv file to be read
    number_lines = sum(1 for row in (open(in_csv)))
    #number_lines = 20

    #size of chunks of data to write to the csv
    chunksize = 1

    #start looping through data writing it to a new file for each chunk
    for i in range(1,number_lines,chunksize):
        df = pd.read_csv(in_csv,
             header=None,
             nrows = chunksize,#number of rows to read at each loop
             skiprows = i)#skip rows that have been read
        shape_info = df[14].values[0].split('|')
        min_latitude = float("inf")
        max_latitude = float("-inf")
        min_longitude = float("inf")
        max_longitude = float("-inf")

        for shape_point in shape_info:
            if shape_info == '':
                continue
            latitude, longitude = shape_point.split('/')[:2]
            latitude = float(latitude)
            longitude = float(longitude)
            if latitude == '' or longitude == '':
                continue
            if latitude< min_latitude:
                min_latitude = latitude

            if latitude> max_latitude:
                max_latitude = latitude

            if longitude < min_longitude: 
                 min_longitude = longitude

            if longitude > max_longitude:
                max_longitude = longitude
        if min_longitude == float('inf') or max_longitude == float('-inf') or\
           min_latitude == float('inf') or max_longitude == float('-inf'):
               continue
        df.insert(17, 'min_latitude', min_latitude)
        df.insert(18, 'max_latitude', max_latitude)
        df.insert(19, 'min_longtitude', min_longitude)
        df.insert(20, 'max_longitude', max_longitude)

        df.to_csv(out_csv,
             index=False,
             header=False,
             mode='a',#append data to csv file
             chunksize=chunksize)

if __name__=='__main__':
    link_path = '/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_2/probe_data_map_matching (1)/Partition6467LinkData.csv'
    probe_path = '/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_2/probe_data_map_matching (1)/Partition6467ProbePoints.csv'
    op_path = '/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_2/probe_data_map_matching (1)/output.csv'
    #iterators = initiliase_dataset_iterators(link_path, probe_path)
    #link_iterator, probe_iterator = iterators
    add_min_max_longitude(link_path, op_path)
    
