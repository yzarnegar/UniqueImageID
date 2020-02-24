import os
import requests
import json
import pandas as pd
from shapely.geometry import box


def read_query(json_file):
    """
    The function to extract the URLs from the results of a query.
    """
    with open(json_file) as fid:
        json_query = json.load(fid)

    df = pd.DataFrame(json_query[0])
    urls = df.downloadUrl

    print("number of frames to download:", len(urls))

    return urls

def query_asf(snwe,  output_query_file, sat='Sentinel-1A'): 
    '''
    The function to query the Sentinel-1 archive of Alaska Satellite Facility (ASF)
    modified from scottyhq github.
    
    Parameters:
    snwe: a list of coordinates as [south, north, west, east]
    output_query_file: filename for the output jason file
    sat: the satellite to query (Sentinel-1A or Sentinel-1B)
    '''
    print('Querying ASF Vertex...')
    miny, maxy, minx, maxx = snwe
    roi = box(minx, miny, maxx, maxy)
    polygonWKT = roi.to_wkt()

    baseurl = 'https://api.daac.asf.alaska.edu/services/search/param'
    data=dict(intersectsWith=polygonWKT,
            platform=sat,
            processingLevel='SLC',
            beamMode='IW',
            start = '2016-01-01',
            end = '2016-04-01',
            output='json')

    r = requests.get(baseurl, params=data)
    with open(output_query_file, 'w') as j:
        j.write(r.text)

    return None

