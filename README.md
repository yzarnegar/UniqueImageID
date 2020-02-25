# CompasSentinel
An address book for satellite images from Sentinel-1
# Introduction
Sentinel-1 mission from the European Space Agency (ESA) captures radar images from earth and provides a unique tool to monitor our planet, track changes in different components of earth system through time. The Alaska Satellite Facility (ASF) allows to query the archived Sentinel-1 data. The data can be downloaded as a zipfile for each frame which includes multiple files including the image data and some meta data. Each frame includes 3 parts called swath and each swath contains smaller images called burst (e.g one swath may contain 10 bursts). However, Researchers and scientists who work with these data are interested in tracking units of images called bursts for more focused studies through time and to more conveniently scale their processing on cloud. They might be interested to just study a small location such as a city however there is no path or indicator to that specific burst (with a size of ~150 MB) and they should download the whole frame (~2.5 or ~4.5 GB) and find the bursts they are interested in it. As a solution to this problem, this repository provides tools to create a database including meta data information for each of the bursts and a unique ID for each burst. The metadata contains the location and coordinates of the bursts as polygons to allow spatial qureying the database. Using this database one can use already existing tools (e.g., GDAL) to download only a specific burst. 


# Architecture
The Sentinel-1 data from ASF are stored on a private s3 bucket. The provided tools allow to query ASF and download the data from ASF to EC2s instance, extract the required metadata (using python libraries) and coordinates (using GDAL), create a geopandas dataframe which then can be stored (e.g, in CSV format) and uploaded to S3 bucket. 

I was able to use Athena on AWS to create a database including tables for the bursts to query the database. Since the database is geographical, I also imported csv files into the PostGIS which is specilized for getting queries from geospatial data.

<img width="878" alt="Screen Shot 2020-02-24 at 12 56 25 PM" src="https://user-images.githubusercontent.com/57342758/75190475-41e1ee00-5705-11ea-9da4-f11692af1aa8.png">

# Dataset

The data that I used was about 250 GB downloded from ASF: https://asf.alaska.edu.
The location was south California and part of Nevada and spans 3 consecutive months.

Each frame has a zip file (about 2.5 to 4.5 GB) and the tiff file and xml file inside the zip file were used to extract information about the coordinates, swats and metadata for each burst to create the polygons and unique burst IDs. The first CSV file (580 kb) includes unique burst IDs, time series data for the bursts and some information about the corresponding urls and date etc. The second CSV file (528 kb) includes unique burst IDs as well as coordinates and polygons information.  



# Engineering challenges
One of my main challenges was how to come up with a unique burst id that specifically belongs to a burst with specified coordinates and is meaningful. I needed to find some feature in the meta data that won’t change and is constant.  As an example, let’s look at the following boxes. The difference between the time satellite passes the equator and the time the image was captured for burst is constant. So, this could be good to create unique IDs but it was not enough. For different satellite tracks around the earth it is possible that the time difference to be equal for two different bursts. Therefore, I needed to add the information about the track. But again, not enough!
Each frame includes 3 swaths and there might be a chance that the image for parallel burst was provided at same time so I needed to add the swath number as well and calculated the unique burst ID as this.

<img width="873" alt="Screen Shot 2020-02-20 at 4 24 09 PM" src="https://user-images.githubusercontent.com/57342758/74992625-7ef46a80-53fd-11ea-8cec-ef79065a7a60.png">

Another challenge was creating the polygons from coordinates and I needed to do it in such a way that shape of the burst preserves. The polygon info could be very useful to do queries based on favorite shape. Let’s assume this is our first burst. For each burst, there is about 1500 lines. The zero line has some points coordinates as well as last line, 1500. I reversed the coordinates for last line and then create the polygon to keep the right shape. I also calculated the centroid for each polygon. 

<img width="786" alt="Screen Shot 2020-02-20 at 4 24 18 PM" src="https://user-images.githubusercontent.com/57342758/74992656-9a5f7580-53fd-11ea-9272-86086b03f6b5.png">


# Trade-offs
I used Athena to do simple queries since my data was on S3 and it was easy to just use Athena. However as the metadata included polygons and coordinates information it was best to use PostGIS database which is specifically used for geospatial data.

# Front-end
A dashboard was built using DASH and Plotly as an interactive web app to get queries from burst's metadata based on a given location of interest. Using CompasSentinel app, it is posibble to find the bursts associated with a given location and all the information related to that bursts also are provided. The returned query is enough information to download only a specific burst from ASF using existing tools such as GDAL.

http://34.214.199.22:8050
