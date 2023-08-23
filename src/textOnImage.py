import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import textwrap
import math

FONT_PATH = "C:\Windows\Fonts\\arial.ttf"

class PrintSettings:
    def __init__(self, config):
        self.config=config
        self.blur = False
        self.text_type = "normal"
        self.text_position = "normal"
        self.imgResMP = np.sqrt(float(config['settings']['imageSizeMP'])*1e6)
        self.blur_size = int(config['settings']['blurSize'])
        self.map_quality = float(config['settings']['mapQuality'])
        self.set_text_size()

    def set_text_size(self):
        if self.text_type == "normal":
            self.tex_size = int(self.config['settings']['textSize'])
        elif self.text_type == "h1":
            self.tex_size = int(self.config['settings']['h1TextSize'])
        elif self.text_type == "h2":
            self.tex_size = int(self.config['settings']['h2TextSize'])
        elif self.text_type == "h3":
            self.tex_size = int(self.config['settings']['h3TextSize'])
    
    def set_text_type(self,type):
        self.text_type=type
        self.set_text_size()


    def check_filename(self,file_name):
        file_name_end = len(file_name)
        # check for blur request
        blur_pos = file_name.find("%blur")
        if(blur_pos>-1):
            self.blur=True
            file_name_end=min(blur_pos,file_name_end)
        # check for size request
        heading_pos = file_name.find("%h")
        if(heading_pos>-1):
            self.text_type=file_name[heading_pos+1:heading_pos+3]
            file_name_end=min(heading_pos,file_name_end)
        # check for position request
        possible_pos = ["%pbl","%ptl","%pbr","%ptr"]
        for pos in possible_pos:
            position_pos = file_name.find(pos)
            if(position_pos>-1):
                self.text_position=file_name[position_pos+1:position_pos+4]
                file_name_end=min(position_pos,file_name_end)

        # set the text size accordingly
        self.set_text_size()
        return file_name[:file_name_end]
    
    def is_headline(self):
        return self.text_type=="h1" or self.text_type=="h2" or self.text_type=="h3"
        
# calculate size of the text
def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)

def scale_image_to_resolution(img, resolution_MP):
    dim=img.shape
    resolution=np.sqrt(dim[0]*dim[1])
    scaleFactor = (resolution_MP)/resolution
    resizeX=int(dim[1]*scaleFactor)
    resizeY=int(dim[0]*scaleFactor)
    img=cv2.resize(img, (resizeX,resizeY))
    return img

def get_text_pos(img_dim, text_size_pix, text_pos_request):
    if(text_pos_request=="ptl"):
        text_pos = (img_dim[1]*0.1,img_dim[0]*0.1)
    if(text_pos_request=="pbl"):
        text_pos = (img_dim[1]*0.1,img_dim[0] - img_dim[0]*0.1)

    if(text_pos_request=="ptr"):
        text_pos = (img_dim[1]*0.9 - text_size_pix,img_dim[0]*0.1)
    if(text_pos_request=="pbr"):
        text_pos = (img_dim[1]*0.9 - text_size_pix,img_dim[0] - img_dim[0]*0.1)
    return text_pos


def addTextToImage(img,text,print_settings: PrintSettings):
    line_dist = 1.2
    # scale the image down to the requested resolution
    img=scale_image_to_resolution(img,print_settings.imgResMP)
    dim=img.shape

    # blur the image if requested
    if(print_settings.blur):
        #print(f"blur image with {print_settings.blur_size}")
        blur = print_settings.blur_size
        img= cv2.blur(img, (blur,blur)) 

    # check if no text was requested
    if text ==" ":
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img)
        return pil_image


    # define a font
    font = ImageFont.truetype(FONT_PATH, print_settings.tex_size)

    # get the text split over lines
    text_width, text_height = get_text_dimensions(text,font)
    number_of_lines = text_width/(dim[1])
    characters_per_line = int(len(text)/number_of_lines*0.95)
    # text wrap width in characters
    textWrapWith=max(characters_per_line,10)
    # distance between lines
    yDistance = text_height * line_dist

    # prepare options to print
    if(print_settings.is_headline()):
        # prepare text options for headline
        # position of the text in center
        if(print_settings.text_position=="normal"):
            textPos=(int(dim[1]/2),int(dim[0]/2-(number_of_lines/2)*yDistance))
            anchor ="ms"
        else:
            textPos=get_text_pos(dim,text_width,print_settings.text_position)
            anchor ="la"
        textWrapWith = int(textWrapWith*2/3)
        stroke_width = 4
        # use the image as it is
        newImg = img
    else:
        # prepare text options for normal text
        # position of the text in left under image
        textPos = (20,dim[0]+10)
        anchor ="la"
        stroke_width = 0
        
        # expand the image by a free space for text underneath
        y_extra = int(yDistance*(math.ceil(number_of_lines*1.05)) + text_height*0.5)
        newImg = np.zeros((dim[0]+y_extra,dim[1],3), np.uint8)
        newImg[:]=(255,255,255)
        newImg[:dim[0],:dim[1]]=img

    # convert to pil
    newImg = cv2.cvtColor(newImg, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(newImg)
    
    # add text
    draw = ImageDraw.Draw(pil_image)
    dy=0
    lines = textwrap.wrap(text, width=textWrapWith)
    for line in lines:
        draw.text((textPos[0],textPos[1]+dy), line, font=font,fill ="black",anchor=anchor, stroke_width=stroke_width, stroke_fill='white')
        dy+=yDistance
    
    return pil_image