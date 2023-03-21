import os
import time
import numpy as np
import cv2 as cv
import tensorflow as tf
from PIL import Image
from IPython.display import display

import sys
sys.path.append('..')

from RemoveHandwritten.helpers.main_helper import remove_handwritting
from RemoveHandwritten.filters.color_filter import color_filter


# imgpath = sys.argv[1]
# save = sys.argv[2]
# name = imgpath.split('/')[-1]
#
# if len(name) >= 5 and (name[-4:] == '.jpg' or name[-4:] == '.png'):
#     name = name[:-4]
# elif len(name) >= 6 and name[-5:] == '.jpeg':
#     name = name[:-5]
# else:
#     print('Error: unsupported file type!')
#     exit()
#
# if save:
#     boxpath = os.path.join('datasets/boxes', name + '_boxes')
#     if not os.path.exists(boxpath):
#         os.mkdir(boxpath)
# else:
#     boxpath = ""
#
# start = time.perf_counter()
#
# img0 = cv.imread(imgpath)
#
# if img0 is None:
#     print('Error: file doesn\'t exists!')
#     exit()
#
# print('\nProgram is runing.')
# print('Please wait.')

def remove_handwritten(img0):
    print("************ start remove handwritten *******************")
    save = False
    boxpath = ""

    img0 = color_filter(img0)

    sgray = cv.cvtColor(img0, cv.COLOR_RGB2GRAY)
    mask = cv.adaptiveThreshold(sgray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 55, 25)
    img0[:, :, 0] = mask
    img0[:, :, 1] = mask
    img0[:, :, 2] = mask

    img1, grn1, height = remove_handwritting(img0, img0, 1536, score = 0.5, compute_h = True, save = save, savepath = boxpath, level = 1)
    img2, grn2 = remove_handwritting(img0, img1, 1280, score = 0.5, h = height, save = save, savepath = boxpath, level = 2)
    img3, grn3 = remove_handwritting(img0, img2, 1024, score = 0.5, h = height, save = save, savepath = boxpath, level = 3)
    img4, grn4 = remove_handwritting(img0, img3, 1024, score = 0.5, h = height, save = save, savepath = boxpath, level = 4)
    img5, grn5 = remove_handwritting(img0, img4, 1024, score = 0.5, h = height, save = save, savepath = boxpath, level = 5)
    img6, grn6 = remove_handwritting(img0, img5, 1024, score = 0.5, h = height, save = save, savepath = boxpath, level = 6)
    return img0

#remove_handwritten(cv.imread("datasets/example/eg.jpg"))
# cv.imwrite(os.path.join('results', name + '_result.png'), img0)

# end = time.perf_counter()

# print('\nFinished!')
# print('The result is saved in \'results\' directory.')
# if save:
#     print('Boxes are saved in \'datasets/boxes/' + name + '_boxes' + '\' directory.')
# print('Total time is', str(end - start) + 's.\n')