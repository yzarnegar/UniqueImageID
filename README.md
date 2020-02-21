# CompasSentinel
An address book for satellite images from Sentinel1
# Introduction
Alaska space facility has a joint mission with European space Agency called Sentonal1, having two satellites capturing the radar images from earth. At ASF website you can query any location of favorite and download image data for it which are zip files for each frame including the image data and some meta data as well.   Each of these images cover a vast location called frame. Each frame includes 3 parts called swath. However, Researchers and scientists who work with these data are interested in locating the exact units of images called bursts for more focused studies through time. They might be interested to just study a small location such as a city however there is no path or indicator to that specific burst and they should download the whole frame data and find the bursts they are interested in. As a solution to this problem, I created a database including meta data information for each of the bursts and created a unique ID for each of them.  I also extracted the location and coordinate information for the bursts and created the polygons.  


# Architecture

<img src="https://user-images.githubusercontent.com/57342758/74991778-d72a6d00-53fb-11ea-85e1-392e1b7b5468.png" width="800" height="400">

# Dataset
# Engineering challenges
# Trade-offs
