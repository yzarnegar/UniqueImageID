import os
import requests
import json
import pandas as pd
from shapely.geometry import box


def read_query(json_file):
    with open(json_file) as fid:
        json_query = json.load(fid)

    df = pd.DataFrame(json_query[0])
    urls = df.downloadUrl

    print("number of frames to download:", len(urls))

    return urls

def query_asf(snwe,  output_query_file, sat='Sentinel-1A'): 
    '''
    modified from scottyhq github ...
    takes list of [south, north, west, east]
    '''
    print('Querying ASF Vertex...')
    miny, maxy, minx, maxx = snwe
    roi = box(minx, miny, maxx, maxy)
    polygonWKT = roi.to_wkt()

    baseurl = 'https://api.daac.asf.alaska.edu/services/search/param'
    #relativeOrbit=$ORBIT
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

