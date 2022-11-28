import cv2
import numpy as np
from skimage import filters
import time
#import math
from PIL import Image, ImageEnhance
from rembg import remove


def find_sigle_squares(cnt,min_perimeter):
    squares = []
    cnt_len = cv2.arcLength(cnt, True)  
    cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)  
  
    if len(cnt) == 4 and cv2.contourArea(cnt) > min_perimeter and cv2.isContourConvex(cnt):
        cnt = cnt.reshape(-1, 2)
        squares.append(cnt)
        #print("square: ",cnt)
    return squares


def order_points(pts):
    ''' sort rectangle points by clockwise '''
    sort_x = pts[np.argsort(pts[:, 0]), :]

    Left = sort_x[:2, :]
    Right = sort_x[2:, :]
    # Left sort
    Left = Left[np.argsort(Left[:, 1])[::-1], :]
    # Right sort
    Right = Right[np.argsort(Right[:, 1]), :]

    return np.concatenate((Left, Right), axis=0)

class Enhancer:
    def bright(self, image, brightness):
        
        print("image brightness")
        image = Image.fromarray(image)  ## np to PIL
        imageBrightend = ImageEnhance.Brightness(image).enhance(brightness)
        imageBrightend = np.array(imageBrightend)
        return imageBrightend

    def color(self, image, color):
       
        print("image color")
        image = Image.fromarray(image)  ## np to PIL
        imageColored = ImageEnhance.Color(image).enhance(color)
        imageColored = np.array(imageColored)
        return imageColored

    def contrast(self, image, contrast):
       
        print("image contrast")
        image = Image.fromarray(image)  ## np to PIL
        image_contrasted = ImageEnhance.Contrast(image).enhance(contrast)
        image_contrasted = np.array(image_contrasted)  ## PIL to np
        return image_contrasted

    def sharp(self, image, sharpness):
       
        print("image sharpness")
        image = Image.fromarray(image)  ## np to PIL
        image_sharped = ImageEnhance.Sharpness(image).enhance(sharpness)
        image_sharped = np.array(image_sharped) ## PIL to np
        return image_sharped

    def gamma(self, image, gamma):
        print("gamma operator")
        gamma_image = np.power(image / float(np.max(image)), gamma)
        return gamma_image
    def laplace(self, image):
        print("Laplace operator")
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)  
        laplace_image = cv2.filter2D(image, -1, kernel=kernel)  
        return laplace_image

    def hisEqulColorYCrCb(self, image):
        
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCR_CB)
        channels = cv2.split(ycrcb)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe.apply(channels[0], channels[0])

        ycrcb = cv2.merge(channels)
        img = cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR)
        return img

    def hisEqulColorYUV(self, image):
        
        image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe.apply(image_yuv[:, :, 0])
        img = cv2.cvtColor(image_yuv, cv2.COLOR_YUV2BGR)
        return img


def whitebg_black(image):
    sgray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = cv2.adaptiveThreshold(sgray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY,55,25)
    return mask

def remove_red_bule(image):
    kernel = np.ones((5, 5), np.uint8)
    grid_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(grid_RGB, cv2.COLOR_RGB2HSV)
    lower_red1 = np.array([0, 43, 46])
    upper_red1 = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    #mask1 = cv2.dilate(mask1, kernel, iterations=1)
    #res1 = cv2.bitwise_and(grid_RGB, grid_RGB, mask=mask1)

    lower_red2 = np.array([156, 43, 46])
    upper_red2 = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    #mask2 = cv2.dilate(mask2, kernel, iterations=1)
    #res2 = cv2.bitwise_and(grid_RGB, grid_RGB, mask=mask2)

    lower_blue = np.array([100, 43, 46])
    upper_blue = np.array([124, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    #mask_blue = cv2.dilate(mask_blue, kernel, iterations=1)
    # res = cv2.bitwise_and(image, image, mask=~mask)
    mask3 = (mask1 + mask2 + mask_blue)
    mask3_copy = mask1 + mask2 + mask_blue
   # print(mask3[0:30, 0:30])
    mask3[mask3 == 0] = 1
    mask3[mask3 > 1] = 0   ## red blue

    mask3_gray = np.repeat(np.expand_dims(mask3, 2), 3, 2)
    #print(mask3_gray.shape)
    #result = np.multiply(image,np.expand_dims(mask3, 2))
    result = mask3_gray * image + np.repeat(np.expand_dims(mask3_copy, 2), 3, 2)


    return result

def transfrom2size(src_img,a):


    dst_h = int(np.sqrt(np.power(a[1][0]-a[0][0], 2) + np.power(a[1][1]-a[0][1], 2)))
    dst_w = int(np.sqrt(np.power(a[2][0]-a[1][0], 2) + np.power(a[2][1]-a[1][1], 2)))

    dst = np.float32([[0, dst_h], [0, 0], [dst_w, 0], [dst_w, dst_h]])
  
    M = cv2.getPerspectiveTransform(np.float32(a),dst)
    dstImage = cv2.warpPerspective(src_img, M, (dst_w, dst_h))
    return dstImage
