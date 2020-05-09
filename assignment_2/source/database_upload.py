import csv, sqlite3
import pandas as pd

class databaseReader:
  PVID_INDEX = 0
  SLOPE_INDEX = 17
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
    return rows

  def insert_slope_data(self, linkrecord, newslope):

    linkPVID = linkrecord[self.PVID_INDEX]
    if(linkrecord[self.SLOPE_INDEX]):
      slope_string = linkrecord[self.SLOPE_INDEX] + ',' + str(newslope)
    else:
      slope_string = str(newslope)
    query = " UPDATE link_data SET slope = '%s' WHERE linkPVID=%d;"%(slope_string, linkPVID)
    print(query)

    self.cur.execute(query)
    self.con.commit()

  def __del__(self):
    self.con.close()



def map_match(links, probe):
    # Design map matching algorithm and return the mathched link
    return links[0]

def calculate_slope(probe_data):
    # calculate the slope of the point with probe data
    return 4.5

def analyse_probedata(probe_csv_path, op_csv_path):
    linkdatabase = databaseReader('roadlink_4.db')
    probe_iterator =  pd.read_csv(probe_csv_path, sep=',', header = None, chunksize=1)
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
        matched_link = map_match(relevant_links, probe_data_formatted)
        slope_value = calculate_slope(probe_data_formatted)

        # Update map matching data
        direction = 'T'
        reference_node_distance = 10
        distance_from_link = 11

        probe_data.insert(8, 'linkPVID', matched_link[0])
        probe_data.insert(9, 'direction', direction)
        probe_data.insert(10, 'distFromRef', reference_node_distance)
        probe_data.insert(11, 'distFromLink', distance_from_link)

        # Write results back to a csv file

        probe_data.to_csv(op_csv_path,
             index=False,
             header=False,
             mode='a',#append data to csv file
             chunksize=1)


        linkdatabase.insert_slope_data(matched_link, slope_value)

        # Write slope values back to db

        


if __name__=='__main__':

    probe_path = '/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_2/probe_data_map_matching (1)/Partition6467ProbePoints.csv'
    op_path = '/home/senthilpalanisamy/work/courses/495_geospatial_vision/geospatial_assignments/assignment_2/probe_data_map_matching (1)/op_mathced.csv'
    analyse_probedata(probe_path, op_path)


