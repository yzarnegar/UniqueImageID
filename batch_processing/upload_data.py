"""Python S3 Manager"""

import sys
import os
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import json
from shapely.geometry import box
import requests


class s3filemanager:
    def __init__(self):
        session = boto3.Session(
           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
           aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.client = session.client('s3')
        self.resource = session.resource('s3')
        self.bucket_name = None

    def set_bucket_name(self, bucket_name):
        self.bucket_name = bucket_name

    def pull_file(self, file_name):
        self.check_bucket_exists()
        try:
            self.client.download_file(self.bucket_name, file_name, file_name)
        except ClientError:
            return False
        return True

    def put_file(self, file_name, object_name=None):
        if object_name is None:
            object_name = file_name
        self.check_bucket_exists()
        try:
            self.client.upload_file(file_name, self.bucket_name, object_name)
        except ClientError:
            return False
        return True

    def check_bucket_exists(self):
        if not self.bucket_name:
            tb = sys.exc_info()[2]
            raise NameError("bucket_name not assigned").with_traceback(tb)



def read_query(jason_file):
    with open(jason_file) as fid:
        jason_query = json.load(fid)

    df = pd.DataFrame(jason_query[0])
    urls = df.downloadUrl

    print("number of frames to download:", len(urls))

    return urls

def query_asf(snwe,  output_query_file, sat='Sentinel-1A'):
    '''
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

snwe = (33.0, 35.0, -120, -117)
query_file = 'query_asf.json'
query_asf(snwe, query_file, sat='Sentinel-1A')
urls = read_query(query_file)

urls = urls[0:10]
for url in urls:
    cmd = "wget " + url
    print("Dowloading  " + url)
    os.system(cmd)
    urlname = os.path.basename(url)
    print("upload " + urlname + " to S3")
    fileObj = s3filemanager()
    fileObj.set_bucket_name(sys.argv[1])
    fileObj.put_file(urlname)
    
    cmd = "rm " + urlname
    print("removing " + urlname)
    os.system(cmd)

