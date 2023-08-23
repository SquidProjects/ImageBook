# Image Book Creator
Simple software to process images and descriptions to a descriptive image book of your holiday.

The kick of for the image book creator was that I had loads of holiday pictures which I wanted to describe so that I still remember what happened years later. But I couldn't find any software which allows for easy processing of hundreds of pictures, doesn't store the pictures on a company cloud and let me export it in high resolution as PDF.
Moreover since the image name and text is stored in a config file no copy of the pictures is needed, making the file size small.
This software is made to create a travel report with simple descriptions it is not made for advanced layout.

## Installation Information
**install conda**  
https://www.anaconda.com/products/distribution

**create environment in conda from yaml**  
cd to the folder containing the yaml file
```
conda env create -f environment.yaml
```

activate the new environment  
```
conda activate image-env
```

## How it works:
- create one config.ini file
- create several description files, containing the file names and your text
- run program to process it to a PDF or single image

**Run**  
The best thing is maybe to take a look at the example under "example". Run it via  
```
python ImageBook.py ../example/config.ini
```

**How to use the description file**  
It needs to be a .csv file with the following format:
`imageNameNoEnding;Description`
Important is that the image is as .JPG or .PNG and is here given with no ending. It will search for the images in the folder (and its subfolder) defined in the config. As more pictures and subfolder there are as longer it takes to find the images.

## Formating options 
Beside plain text some formatting options are available:
|keyword|explanation|
|-------|-------|
| |standard text under the image|
|empty|creates an empty image with centered text|
|%h1|Heading of size 1 in the center of the image|
|%h2|Heading of size 2 in the center of the image|
|%h3|Heading of size 3 in the center of the image|
|%blur|Blurs the image|
|%ptr|Text will be placed at the top right of the image|
|%pbr|Text will be placed at the bottom right of the image|
|%ptl|Text will be placed at the top left of the image|
|%pbl|Text will be placed at the bottom left of the image|
|%map|Will create a map, see below for more information|

These keywords do get added behind the file name. For example an image with the file name IMG123.JPG could look like this:  
`IMG123%blur%h2%pbl;This is my image` 
It will take the image, blur it and place a text of the size heading 2 on the bottom left corner of the image.

**Adding a map**  
It is possible to add a map by just giving the coordinates in the form:  
`%mapLat,Lon,Radius;Description`  

An example could be:  
`%map60.4023423628611, 5.289781513207554,100;City of Bergen`  
This will add a map of Bergen (Norway) with a radius of 100km. You can copy the coordinates for example from google maps by right click on the map. The map used here is open street map and it will be downloaded during compilation. So make sure you have a working internet connection.  
The quality of the map can be set in the settings file. Higher quality maps take longer to download.
The text format options like headings and positions can be applied to maps too.

## Other usefull information
- If you want to change the font, or if its installed in the different location, this is defined in "textOnImage.py" in the variable "FONT_PATH"
