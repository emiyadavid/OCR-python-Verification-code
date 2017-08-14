# -*- coding: utf-8 -*-
import os
from pytesseract import *
from PIL import Image, ImageDraw, ImageChops, ImageEnhance
import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import sys
reload(sys)
sys.setdefaultencoding('utf8')

threshold = 180
table = []
t2val = {}
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

rep={'O':'0',
    'I':'1','L':'1','U':'1',
    'Z':'2',
    'S':'8',
    '°':'0'
    }

color = np.zeros(256)

def pretreat(image):
    w,h = image.size
    box = (1, 1, w-1, h-1)
    image = image.crop(box)
    return image

def findColor(image):
    w,h=image.size
    data = image
    for x in range(w):
        for y in range(h):
            temp_color = data.getpixel((x,y))
            #print temp_color
            color[temp_color] += 1.0

    sort_color = np.sort(color)
    second_color = int(np.argwhere(color==sort_color[254]))
    max_color  = int(np.argwhere(color==sort_color[255]))
    return max_color,second_color

#denoise
def denoise(image,max_color,second_color):
    w,h=image.size
    data = image
    for x in range(w):
        for y in range(h):
            if (data.getpixel((x,y)) == max_color | data.getpixel((x,y)) == second_color):
                continue
            else:
                data.putpixel((x,y),max_color)
    return data

def cut_one_char(image):
    #clear_noise(image,4)
    CharWidth=10
    CharHeight=20
    Width,Height=image.size
    box = (3, 0, 3+CharWidth, CharHeight)
    image_char = crop_white(image,box)

    if CharWidth > Width:
        image_residue = None
    else:
        box = (CharWidth,0,Width,Height)
        image_residue = crop_white(image,box)
    return [image_char,image_residue]

def cut_all_char(image):
    image_char1,image = cut_one_char(image)
    image_char2,image = cut_one_char(image)
    image_char3,image = cut_one_char(image)
    image_char4,image = cut_one_char(image)
    return [image_char1,image_char2,image_char3,image_char4]

def crop_white(image,box):
    # 255 - old
    image = ImageChops.invert(image)
    image = image.crop(box)
    return ImageChops.invert(image)


#recognize
def  recognize_full(image):  #识别全图
    text = image_to_string(image)
    text = text.strip()
    text = text.upper()
    for r in rep:
        text = text.replace(r,rep[r])
    #out.save(text+'.jpg')
    return text

def  recognize_single(image):   #识别单字符
    text = image_to_string(image,config='-psm 5')
    text = text.strip()
    text = text.upper()
    for r in rep:
        text = text.replace(r,rep[r])
    #out.save(text+'.jpg')
    return text

def main():
   image_origin = Image.open('newfile_path')   #读取原图片
   image_box = pretreat(image_origin)
   image_box.save('savetobmp_path','bmp')   #转换成bmp格式
   image_temp = Image.open('readbmp_path')  #读取bmp格式图片

   first_color,second_color = findColor(image_temp)
   image_deal = denoise(image_temp,first_color,second_color)

   image_deal.save('savetodenoise_path','bmp')   #保存去噪声之后的bmp图片  可不用

   imgry = image_deal.convert('L')
   out = imgry.point(table,'1')
   out.save('black_path')   #保存为黑白图  可不用
   text = recognize_full(out)

   image_char_list = cut_all_char(out)
   image_char_list[0].save('cut_path1')   #保存第一个数字  可不用
   image_char_list[1].save('cut_path2')   #保存第二个数字  可不用
   image_char_list[2].save('cut_path3')   #保存第三个数字  可不用
   image_char_list[3].save('cut_path4')   #保存第四个数字  可不用

   first = recognize_single(image_char_list[0])
   second = recognize_single(image_char_list[1])
   third = recognize_single(image_char_list[2])
   fourth = recognize_single(image_char_list[3])

   if (text == ""):
       text = first+second+third+fourth
   print text

if __name__ == '__main__':
    main()
