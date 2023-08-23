import os
import numpy as np
import errno
from textOnImage import addTextToImage

class Empty:
    """
    Class to create a white image on which text can be placed
    """
    def __init__(self):
        pass

    @staticmethod
    def is_empty(empty_string):
        if empty_string=="empty":
            return True
        return False
    
    @staticmethod
    def generate_img(description, print_settings):
        imgWidth=int(print_settings.imgResMP)
        img = np.zeros((imgWidth,imgWidth,3), np.uint8)
        img[:]=(255,255,255)
        if(print_settings.text_type=="normal"):
            print_settings.set_text_type("h1")
        img = addTextToImage(img, description, print_settings)
        return img


class ProgressPrinter:
    """
    Prints a progress bar
    """
    def __init__(self,out_str, max_el, freq):
        self.out_str = out_str
        self.max_el=max_el
        self.freq = freq
        self.counter = 0
        self.last_output = 0

    def print_progess(self):
        if self.counter>self.last_output + self.freq:
            percent = 100/self.max_el*self.counter
            print(f"{self.out_str}: {percent:.0f}%")
            self.last_output = self.counter
        self.counter+=1

def doesIncludeAtLeastOne(string,listOfIdentifiers):
    res=False
    for id in listOfIdentifiers:
        res=res or (string.find(id)>-1)
    return res

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

class FileDictionary:
    def __init__(self, path):
        self.file_dict ={}
        self.count = 0
        self.create_dict(path)
        print(f"found {self.count} images")

    def create_dict(self, path):
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path,file)
            if os.path.isfile(file_path):
                if doesIncludeAtLeastOne(file,[".jpg",".JPG",".png",".PNG"]):
                    file_no_ending = file[:file.rfind(".")]
                    # check if file already exsists
                    if file_no_ending in self.file_dict:
                        print(f"File name exsists twice {file_no_ending}")
                        print(f"(1) {self.file_dict[file_no_ending]}")
                        print(f"(2) {file_path}")
                        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_no_ending)
                    # check if ascci path
                    if not is_ascii(file_path):
                        print(f"file path contains non ascii letters {file_path}")
                        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_no_ending)

                    # add file to dictionary
                    self.file_dict[file_no_ending] = file_path
                    self.count+=1
            else:
                self.create_dict(file_path)