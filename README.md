# CompasSentinel
An address book for satellite images
# Introduction
Alaska space facility has a joint mission with European space Agency called Sentinel-1, having two satellites capturing the radar images from the earth. At ASF website you can query any location of favorite and download image data for it which are zip files for each frame including the image data and some meta data as well.   Each of these images cover a vast location called frame. Each frame includes 3 parts called swath. However, Researchers and scientists who work with these data are interested in tracking units of images called bursts for more focused studies through time. They might be interested to just study a small location such as a city however there is no path or indicator to that specific burst and they should download the whole frame data and find the bursts they are interested in it. As a solution to this problem, I created a database including meta data information for each of the bursts and created a unique ID for each of them.  I also extracted the location and coordinate information for the bursts and created the polygons to make it possible to qurey based on polygon information.  


# Architecture
Data from Sentinel-1 is stored on s3. However, it is private so I downloaded the data from ASF. On my EC2s, using python I extract the information that I needed about the metadata and coordinates from zip files, and did some processing and created pandas data frames including information about the bursts and save those as CSV files on my s3 bucket. Then I used Athena and created a database including tables for the bursts to get query from. However since the data is geographical, I also imported csv files into the postGIS and created tables as it is specilized for getting queries from this type of data.

<img width="878" alt="Screen Shot 2020-02-24 at 12 56 25 PM" src="https://user-images.githubusercontent.com/57342758/75190475-41e1ee00-5705-11ea-9da4-f11692af1aa8.png">

# Dataset
The data I worked with was about 250 GB and resulted csv files are 580 and 528 kb. Each frame has a zip file data about 5 GB and the tiff file and xml file inside the zip file were used to extract information about the coordinates, swats and metadata for each burst to create the polygons and unique burst IDs. The first CSV file includes unique burst IDs, time series data for the bursts and some information about the corresponding urls and date etc. The second CSV file includes unique burst IDs as well as coordinates and polygons information.  The location that was covered was south California and part of Nevada and the data was downloded for 3 consecutive months.



# Engineering challenges
One of my main challenges was how to come up with a unique burst id that specifically belongs to a burst with specified coordinates and is meaningful. I needed to find some feature in the meta data that won’t change and is constant.  As an example, let’s look at the following boxes. The difference between the time satellite passes the equator and the time the image was captured for burst is constant. So, this could be good to create unique IDs but it was not enough. For different satellite tracks around the earth it is possible that the time difference to be equal for two different bursts. Therefore, I needed to add the information about the track. But again, not enough!
Each frame includes 3 swaths and there might be a chance that the image for parallel burst was provided at same time so I needed to add the swath number as well and calculated the unique burst ID as this.

<img width="873" alt="Screen Shot 2020-02-20 at 4 24 09 PM" src="https://user-images.githubusercontent.com/57342758/74992625-7ef46a80-53fd-11ea-8cec-ef79065a7a60.png">

Another challenge was creating the polygons from coordinates and I needed to do it in such a way that shape of the burst preserves. The polygon info could be very useful to do queries based on favorite shape. Let’s assume this is our first burst. For each burst, there is about 1500 lines. The zero line has some points coordinates as well as last line, 1500. I reversed the coordinates for last line and then create the polygon to keep the right shape. I also calculated the centroid for each polygon. 

<img width="786" alt="Screen Shot 2020-02-20 at 4 24 18 PM" src="https://user-images.githubusercontent.com/57342758/74992656-9a5f7580-53fd-11ea-9272-86086b03f6b5.png">


# Trade-offs
I used Athena to do simple queries since my data was on S3 and it was easy to just use Athena. However as the metadata included polygon and coordinated information it was best to use postGIS which is specifically used for geografical data.

# Front-end
A dash was built to get queries from metadata based on a given location of interest. Using compasSentinel app, it is posibble to find the bursts associated with a given location and all the information related to that bursts also are provided.

http://34.214.199.22:8050
