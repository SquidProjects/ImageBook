import os
import pandas as pd
import cv2
import numpy as np
import configparser
import errno
import sys

from textOnImage import PrintSettings
from mapCreation import Map
from utils import Empty
from utils import FileDictionary
from utils import ProgressPrinter
from textOnImage import addTextToImage



def read_description(labelFiles, pathToLables, config):
    # result object containing [object, description, text options]
    labels = []
    for labelFile in labelFiles:
        fullPathToLables = os.path.join(pathToLables, labelFile)
        if not os.path.exists(fullPathToLables):
            print("Error label file doesn't exsist")
            raise FileNotFoundError(
        errno.ENOENT, os.strerror(errno.ENOENT), fullPathToLables)

        print(f"read label file {labelFile}")
        df = pd.read_csv(fullPathToLables,delimiter=";",header=None)

        # read file contend
        for i in range(len(df)):
            fileName=df.iloc[i][0]
            # check if it contains additional arguments
            print_settings = PrintSettings(config)
            obj=print_settings.check_filename(fileName)

            # if no description is given use empty space
            description = df.iloc[i][1]
            if pd.isna(description):
                description=" "

            # check if it is a map rather than an image
            if Map.is_map(obj):
                obj = Map(obj)

            # check if it is empty rathen than an image
            if Empty.is_empty(obj):
                obj=Empty()

            labels.append([obj,description,print_settings,labelFile])

    return labels


def main():
    path_to_config = sys.argv[1]
    if not os.path.exists(path_to_config):
        print("Path to config is wrong")
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path_to_config)
    
    config = configparser.ConfigParser()
    config.read(path_to_config)

    labelFiles=config['path']['lableFiles'].split(',')
    pathToLables=config['path']['pathToLabels']
    savePath=config['path']['savePath']
    searchPath=config['path']['imageSearchPath']
    save_pdf = True if config['control']['saveTo']=="PDF" else False


    print("Analyze image files")
    # list all the files in the given dictionary and sub dicts
    file_dict = FileDictionary(searchPath)
    # read csv description files
    labels = read_description(labelFiles, pathToLables, config)

    print("check if all requested files are present")
    for obj, _,_, label_file in labels:
        if isinstance(obj,Empty) or isinstance(obj,Map):
            continue

        if obj not in file_dict.file_dict:
            print(f"Error file not found {obj} in {label_file}")
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), obj)
    print("All files are present")
    print("Start processing images")

    # setup a progress bar
    progress_print = ProgressPrinter("processed img",len(labels),10)
    image_list = []

    for obj, description, print_settings, _ in labels:
        # check if its an empty image
        if isinstance(obj,Empty):
            img = obj.generate_img(description,print_settings)
            image_list.append(img)
        
        # check if its a map
        elif isinstance(obj,Map):
            img = obj.generate_img(description, print_settings)
            image_list.append(img)
        
        # check if its an image
        else: 
            img = cv2.imread(file_dict.file_dict[obj])
            img = addTextToImage(img, description, print_settings)
            image_list.append(img)

        progress_print.print_progess()

    if(save_pdf):
        # save images to pdf
        image_list[0].save(
            savePath+"/book.pdf", "PDF" ,resolution=100.0, save_all=True, append_images=image_list[1:]
        )
    else:
        # save single images
        imgCounter=0
        for image in image_list:
            # convert to opencv img
            image = np.asarray(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(savePath+"/"+str(imgCounter)+"_"+obj+"_labeled.jpg",image)
            imgCounter+=10

if __name__ == "__main__":
    main()
    print("##### DONE #####")
        

