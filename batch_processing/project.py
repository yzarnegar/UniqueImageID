#!/usr/bin/env python3

import datetime                                                                                                                                                                                   
import xml
import xml.etree.ElementTree as ET
import boto3



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
