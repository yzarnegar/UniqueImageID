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

def getxmlattr( xml_root, path, key):
        try:
            res = xml_root.find(path).attrib[key]
        except:
            raise Exception('Cannot find attribute %s at %s'%(key, path))

        return res

def getxmlvalue( xml_root, path):
        try:
            res = xml_root.find(path).text
        except:
            raise Exception('Tag= %s not found'%(path))

        if res is None:
            raise Exception('Tag = %s not found'%(path))

        return res

def getxmlelement(xml_root,  path):
        try:
            res = xml_root.find(path)
        except:
            raise Exception('Cannot find path %s'%(path))

        if res is None:
            raise Exception('Cannot find path %s'%(path))

        return res


def read_time(input_str, fmt="%Y-%m-%dT%H:%M:%S.%f"):
    dt = datetime.datetime.strptime(input_str, fmt)
    return dt


class BurstDataFrame:

    def __init__(self):
      self.df = pd.DataFrame(columns=['Node_Time','Burst_Start','Time_Difference','Track_Number','Burst_ID','Pass_Direction','Ground_Coordinate'])
    

    def getCoordinates(self, zipname):
        zf = zipfile.ZipFile(zipname, 'r')

        tiffpath = os.path.join('*SAFE','measurement', 's1a-iw1-slc*tiff')
        match = fnmatch.filter(zf.namelist(), tiffpath)
        zf.close()

        tiffname = os.path.join('/vsizip/' + zipname, match[0])
        cmd = "gdalinfo -json {} >> info.json".format(tiffname)
        print(cmd)
        os.system(cmd)
        with open("info.json", 'r') as fid:
           info = json.load(fid)


        df_coordinates = pd.DataFrame(info['gcps']['gcpList'])
        print(df_coordinates) 
        os.system('rm info.json')

    def update(self, zipname):
        zf = zipfile.ZipFile(zipname, 'r')
        xmlpath = os.path.join('*SAFE','annotation', 's1a-iw1-slc*xml')
        match = fnmatch.filter(zf.namelist(), xmlpath)
        xmlstr = zf.read(match[0])

        xml_root = ET.fromstring(xmlstr)

        ascNodeTime = getxmlvalue(xml_root, "imageAnnotation/imageInformation/ascendingNodeTime")
        numBursts = getxmlattr(xml_root, 'swathTiming/burstList', 'count')
        burstList = getxmlelement(xml_root, 'swathTiming/burstList')
        passtype=getxmlvalue(xml_root, 'generalAnnotation/productInformation/pass')
        orbitnumber = int(getxmlvalue(xml_root, 'adsHeader/absoluteOrbitNumber'))
        trackNumber = (orbitnumber-73)%175 + 1

        for index, burst in enumerate(list(burstList)):
            sensingStart = burst.find('azimuthTime').text
            dt = read_time(sensingStart)-read_time(ascNodeTime)
            burstID = str(trackNumber) + str(dt.seconds)
            
            # check if self.df has this dt for this track. If not append it
            self.df = self.df.append({'Node_Time':ascNodeTime,'Burst_Start':sensingStart,'Time_Difference':dt, 'Track_Number':trackNumber,'Burst_ID':burstID, 'Pass_Direction':passtype,'Ground_Coordinate':0}, ignore_index=True)    
    
        zf.close()
  

   
####################

if __name__ == "__main__":

    # query ASF dataset
    dataDir = '/home/ubuntu/Downloads/test_data'
    frames = [os.path.join(dataDir, 'S1A_IW_SLC__1SSV_20160326T135945_20160326T140013_010541_00FA9F_3D82.zip'), 
            os.path.join(dataDir, 'S1A_IW_SLC__1SDV_20200121T132744_20200121T132811_030899_038BEA_CC3A.zip')]


    dfObj = BurstDataFrame()
    for ff in frames:
        print(ff)
        dfObj.update(ff)
        dfObj.getCoordinates(ff)

    print(dfObj.df)

    





        #Download the zip file to S3 bucket
        #df extract_metadata(zipname, df)

        # extract the metadata form "annotation/s1*.xml" files

        # Assign a unique burst ID for each burst in the frame



'''

bucketname = "yaldabucket"
s3 = boto3.resource('s3')
obj = s3.Object(bucketname,"s1a-iw1-slc-vh-20200121t132745-20200121t132810-030899-038bea-001.xml" )
body = obj.get()['Body']

xmlstr=body.read()

xml_root = ET.fromstring(xmlstr)
ascNodeTime = getxmlvalue(xml_root, "imageAnnotation/imageInformation/ascendingNodeTime")
numBursts = getxmlattr(xml_root, 'swathTiming/burstList', 'count')
burstList = getxmlelement(xml_root, 'swathTiming/burstList')

print("ascNodeTime: ", ascNodeTime)
print(numBursts)

for index, burst in enumerate(list(burstList)):
    sensingStart = burst.find('azimuthTime').text
    print(sensingStart)
    print(read_time(sensingStart)-read_time(ascNodeTime))

'''
