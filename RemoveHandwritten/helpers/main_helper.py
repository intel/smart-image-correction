import os
import time
import numpy as np
import cv2 as cv
import tensorflow as tf
from PIL import Image

from IPython.display import display

import sys

from RemoveHandwritten.cut_text.text import detect_lines as text_model

model = tf.keras.models.load_model('RemoveHandwritten/models/classify.h5')

def solve(box):
    [x1, y1], [x2, y2], [x3, y3], [x4, y4] = box
    cx = (x1 + x3 + x2 + x4) / 4.0
    cy = (y1 + y3 + y4 + y2) / 4.0  
    w = (np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) + np.sqrt((x3 - x4) ** 2 + (y3 - y4) ** 2)) / 2
    h = (np.sqrt((x2 - x3) ** 2 + (y2 - y3) ** 2) + np.sqrt((x1 - x4) ** 2 + (y1 - y4) ** 2)) / 2   
    sinA = (h * (x1 - cx) - w * (y1 - cy)) * 1.0 / (h * h + w * w) * 2
    angle = np.arcsin(sinA)
    return angle, w, h, cx, cy
    
def rotate_cut_img(im, box, left_adjust = 0.0, right_adjust = 0.0):
    [x1, y1], [x2, y2], [x3, y3], [x4, y4] = box
    img = im.copy()
    img = img.crop([x1, y1, x3, y3])
    degree, w, h, x_center, y_center = solve(box)
    xmin_ = min(box[:, 0])
    xmax_ = max(box[:, 0])
    ymin_ = min(box[:, 1])
    ymax_ = max(box[:, 1])
    x_center = x_center - xmin_
    y_center = y_center - ymin_
    im = im.crop([xmin_, ymin_, xmax_, ymax_])
    degree_ = degree * 180.0 / np.pi
    xmin = max(1, x_center - w / 2 - left_adjust * (w / 2))
    ymin = y_center - h / 2
    xmax = min(x_center + w / 2 + right_adjust * (w / 2), im.size[0] - 1)
    ymax = y_center + h / 2
    tmp_img = im.rotate(degree_, center = (x_center, y_center)).crop([xmin, ymin, xmax, ymax])
    box = {'cx': x_center + xmin_, 'cy': y_center + ymin_, 'w': xmax - xmin, 'h': ymax - ymin, 'degree': degree_}
    return degree_, np.asarray(tmp_img)
    
def resize(im, h = 64, w = 560, mode = 'padding'):
    img = im.copy()
    if img.shape[0] != h:
        rate = h / img.shape[0]
        img = cv.resize(img, None, fx = rate, fy = rate)
    if (img.shape[1] < w):
        if mode == 'padding':
            img = cv.copyMakeBorder(img, 0, 0, 0, w - img.shape[1], cv.BORDER_CONSTANT, value = (255, 255, 255))
        elif mode == 'repeat':
            img = cv.repeat(img, 1, w // img.shape[1] + 1)[:, :w]
    elif (img.shape[1] > w):
        img = img[:, :w]
    return img

def is_handwritten(img, h):
    shape = img.shape
    if shape[1] < h * 3.731 and shape[0] >= h * 1.309:
        return True
    elif shape[1] >= h * 3.731 and shape[1] < h * 7.117 and shape[0] >= h * 1.517:
        return True
    elif shape[1] >= h * 7.117 and shape[1] < h * 15.168 and shape[0] >= h * 1.547:
        return True
    elif shape[1] >= h * 15.168 and shape[0] >= h * 1.519:
        return True
    else:
        img = resize(img, mode = 'repeat') / 255
        img = np.expand_dims(img, axis = 0)
        return model.predict(img)[0, 0] < 0.9
        
def is_title(shape, y, total_height, h):
    return shape[0] > h * 1.328 and shape[1] >= h * 8.815 and shape[1] < h * 27.670 and y <= total_height * 0.227

def too_small(shape, h):
    return shape[0] < h * 0.674 and shape[1] / shape[0] >= 1.5

def is_valid(shape, degree, h):
    return shape[0] > h * 0.842 and shape[0] < h * 2.477 and shape[0] < shape[1] * 2.072 and abs(degree) < 19.19
    
def handle_box(im, box, res, ret, grn, height, offset = 0):
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    white = (255, 255, 255)
    thick = np.max(grn.shape[:2]) // 1024 + 1
    box = box.reshape(4, 2)
    box[:, 1] += offset
    
    degree, tmp_img = rotate_cut_img(im, box, left_adjust = 0.01, right_adjust = 0.01)
    shape = tmp_img.shape
    
    print_class = False
    
    points = np.array(box, np.int32).reshape((-1, 1, 2))
    grn = cv.polylines(grn, [points], isClosed = True, color = green, thickness = thick)
    
    if too_small(shape, height):
        if print_class:
            print(1)
        grn = cv.polylines(grn, [points], isClosed = True, color = red, thickness = thick)
        res = cv.fillPoly(res, [points], color = white)
        ret = cv.fillPoly(ret, [points], color = white)
        
        return False, tmp_img
    
    elif is_title(shape, box[0, 1], res.shape[0], height) or not is_valid(shape, degree, height):
        if print_class:
            print(2)
        grn = cv.polylines(grn, [points], isClosed = True, color = red, thickness = thick)
        if shape[1] >= 2 * shape[0]:
            ret = cv.fillPoly(ret, [points], color = white)
        
        return False, tmp_img
    
    else: 
        if is_handwritten(tmp_img, height):
            if print_class:
                print(3)
            grn = cv.polylines(grn, [points], isClosed = True, color = green, thickness = thick)
            res = cv.fillPoly(res, [points], color = white)
            ret = cv.fillPoly(ret, [points], color = white)
        elif shape[1] >= 2 * shape[0]: #eliminate left half
            if print_class:
                print(4)
            grn = cv.polylines(grn, [points], isClosed = True, color = blue, thickness = thick)
            points[1] = (points[0] + points[1]) // 2
            points[2] = (points[2] + points[3]) // 2
            ret = cv.fillPoly(ret, [points], color = white)
        else:
            if print_class:
                print(5)
            grn = cv.polylines(grn, [points], isClosed = True, color = blue, thickness = thick)
            ret = cv.fillPoly(ret, [points], color = white)
        
        return True, tmp_img
        
def remove_handwritting(res, img, scale = 6831, max_scale = 6831, score = 0.75, compute_h = False, h = 0, save = False, savepath = "", level = 0):
    mid = img.shape[0] // 2
    bias = img.shape[0] // 20
    ret = img.copy()
    grn = img.copy()
    im = Image.fromarray(img)
    height = h
    
    boxes1, scores1 = text_model(img[:mid + bias], scale = scale, maxScale = max_scale)
    boxes2, scores2 = text_model(img[mid - bias:], scale = scale, maxScale = max_scale)
    
    if compute_h:
        count = 0
        for i, box in enumerate(boxes1):
            if scores1[i] > score and box[1] <= mid:
                height += (box[7] + box[5] - box[1] - box[3]) / 2
                count += 1
        for i, box in enumerate(boxes2):
            if scores2[i] > score and box[1] > bias:
                height += (box[7] + box[5] - box[1] - box[3]) / 2
                count += 1
        height /= count
    
    idx = 0
    
    for i, box in enumerate(boxes1):
        if scores1[i] > score and box[1] <= mid:
            can_save, tmp_img = handle_box(im, box, res, ret, grn, height)
            if save and can_save:
                cv.imwrite(os.path.join(savepath, str(level) + '_' + str(idx) + '.png'), tmp_img)
            idx += 1
    
    for i, box in enumerate(boxes2):
        if scores2[i] > score and box[1] > bias:
            can_save, tmp_img = handle_box(im, box, res, ret, grn, height, mid - bias)
            if save and can_save:
                cv.imwrite(os.path.join(savepath, str(level) + '_' + str(idx) + '.png'), tmp_img)
            idx += 1
    
    if compute_h:
        return ret, grn, height
    else:
        return ret, grn