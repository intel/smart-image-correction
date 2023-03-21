import os
import sys
import cv2 as cv
import numpy as np

lower_black = np.array([0, 0, 0])
upper_black = np.array([180, 255, 46])

lower_gray = np.array([0, 0, 46])
upper_gray = np.array([180, 43, 220])

lower_white = np.array([0, 0, 221])
upper_white = np.array([180, 30, 255])

def color_filter(img):
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
  
    black = cv.inRange(hsv, lower_black, upper_black)
    gray = cv.inRange(hsv, lower_gray, upper_gray)
    white = cv.inRange(hsv, lower_white, upper_white)

    mask = ~(black | gray | white)

    rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (4, 4))
    dilation = cv.dilate(mask, rect_kernel, iterations=1)

    res = img.copy()
    res[:, :, 0] = cv.bitwise_or(res[:, :, 0], dilation)
    res[:, :, 1] = cv.bitwise_or(res[:, :, 1], dilation)
    res[:, :, 2] = cv.bitwise_or(res[:, :, 2], dilation)

    return res

if __name__ == '__main__':
    imgpath = sys.argv[1]
    name = imgpath.split('/')[-1]

    if len(name) >= 5 and (name[-4:] == '.jpg' or name[-4:] == '.png'):
        name = name[:-4]
    elif len(name) >= 6 and name[-5:] == '.jpeg':
        name = name[:-5]
    else:
        print('Error: unsupported file type')
        exit()
        
    img = cv.imread(imgpath)

    if img is None:
        print('Error: file doesn\'t exists')
        exit()
    
    print('\nProgram is runing.')
    print('Please wait.')
    
    img = color_filter(img)
    
    cv.imwrite(os.path.join('datasets/filtered', name + '_filtered.png'), img)
    
    print('\nFinished!')
    print('Filtered image is saved in \'datasets/filtered\' directory.\n')