#!/usr/bin/env python3
import json
import os
import datetime                                                                                                                                                   
import xml
import xml.etree.ElementTree as ET
import boto3
import zipfile
import fnmatch
import pandas as pd
import io
from io import StringIO
import geopandas as gpd 
from shapely.geometry import Polygon

from upload_data import s3filemanager
from query import query_asf, read_query

from BurstDataFrame import BurstDataFrame 

if __name__ == "__main__":

    bucket_name = "burstdatabucket"
    snwe = (34.0, 35.0, -120.0, -117.0)
    output_query_file = "query_asf.json"
    query_asf(snwe,  output_query_file, sat='Sentinel-1A')
    urls = read_query(output_query_file)
    
    print("number of files found: ", len(urls))

    dfObj = BurstDataFrame()
    for url in urls:
      try:
         print("downloading {}".format(url))
         cmd = "wget {}".format(url)
         os.system(cmd)

         frame = os.path.basename(url)
         print("update database using {}".format(frame))
         dfObj.url = url
         for swath in range(3):
            dfObj.swath = str(swath+1)
            dfObj.update(frame)
         os.system("rm {}".format(frame))
         dfObj.to_csv("burstID_database.csv", "burstID_database_tseries.csv")
      except:
         print("something went wrong with {}".format(url))

    uplodList = ["burstID_database.csv", "burstID_database_tseries.csv"]
    print("upload to s3")
    for filename in uplodList:
        dfObj.upload_to_s3(filename, bucket_name)


