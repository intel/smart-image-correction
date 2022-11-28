import time
from rembg import remove
import cv2
import numpy as np
import os
from skimage import filters
import Mainfunction
import ACE

def find_max_p(z,xy,center):
    distance = 0
    temp = -1
    # find square
    for i in xy:
        x = z[i][0] - center[0]
        y = z[i][1] - center[1]
        d = x * x + y * y
        if d > distance:
            temp = i
            distance = d
    if temp >=0 :
        return [z[temp][0], z[temp][1]]

def find_square_point(p,hull,h,w):
    if len(np.array(hull).shape) == 3:
        s = [[1, 2]]
        z = [[2, 3]]
        for i in hull:
            s.append([i[0][0], i[0][1]])
            z.append([i[0][0], i[0][1]])
        del s[0]
        del z[0]
    else:
        s = [[1, 2]]
        z = [[2, 3]]
        for i in hull:
            s.append([i[0], i[1]])
            z.append([i[0], i[1]])
        del s[0]
        del z[0]

    center = [w / 2, h / 2]

    for i in range(len(s)):
        s[i][0] = s[i][0] - center[0]
        s[i][1] = s[i][1] - center[1]
    one = []
    two = []
    three = []
    four = []
    # find quadrant
    for i in range(len(z)):
        if s[i][0] <= 0 and s[i][1] < 0:
            one.append(i) ## 左上
        elif s[i][0] > 0 and s[i][1] < 0:
            two.append(i)  ## 右上
        elif s[i][0] >= 0 and s[i][1] > 0:
            four.append(i)  ## 右下
        else:
            three.append(i) ## 左下

    if len(one) > 0:
        p.append(find_max_p(z,one,center))
    if len(two) > 0:
        p.append(find_max_p(z, two, center))
    if len(three) > 0:
        p.append(find_max_p(z, three, center))
    if len(four) > 0:
        p.append(find_max_p(z, four, center))
    return p


def order_points(pts):
    ''' pts is np.array'''
    sort_x = pts[np.argsort(pts[:, 0]), :]

    Left = sort_x[:2, :]
    Right = sort_x[2:, :]
    # Left sort
    Left = Left[np.argsort(Left[:, 1])[::-1], :]
    # Right sort
    Right = Right[np.argsort(Right[:, 1]), :]
    return np.concatenate((Left, Right), axis=0)


class Point(object):
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
def distance(l):
    return np.sqrt((l.p1.x - l.p2.x)**2 + (l.p1.y - l.p2.y)**2)

def GetCrossAngle(l1, l2):
    ## angle between two straight lines： https://blog.csdn.net/panfengzjz/article/details/80377501

    arr_0 = np.array([(l1.p2.x - l1.p1.x), (l1.p2.y - l1.p1.y)])
    arr_1 = np.array([(l2.p2.x - l2.p1.x), (l2.p2.y - l2.p1.y)])
    cos_value = (float(arr_0.dot(arr_1)) / (np.sqrt(arr_0.dot(arr_0)) * np.sqrt(arr_1.dot(arr_1))))   
    return np.arccos(cos_value) * (180/np.pi)

def detect_hard(input,reply="DC-04"):
    ## AI model
    width = input.shape[1]
    height = input.shape[0]

    output = remove(input)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  
    closed = cv2.morphologyEx(output, cv2.MORPH_CLOSE, kernel)  
    output = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)  

    cannyPic = cv2.Canny(output, 75, 200) 

    contours, hierarchy = cv2.findContours(cannyPic, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    p = []
    for i in range(len(contours)):
        find_square_point(p, contours[i], height, width)

    squares = []
    find_square_point(squares, p, height, width)

    squares = order_points(np.array(squares))  ## type = np.array

    ####### PDT test
    if reply == "DC-01":
        return output
    elif reply == "DC-02":
        return contours
    elif reply == "DC-03":
        return p

    ############# 

    p1 = Point(squares[0,0],squares[0,1])
    p2 = Point(squares[1,0],squares[1,1])
    line1 = Line(p1, p2)

    p3 = Point(squares[3,0],squares[3,1])
    p4 = Point(squares[2,0],squares[2,1])
    line2 = Line(p3, p4)
    angle = GetCrossAngle(line1, line2)

    if angle < 8:  ## parallel
        pert = distance(line2)/distance(line1)
        print("parallel")
        if pert < 0.95:           
            squares[3,1] = squares[0,1]
        elif pert > 1.05:           
            squares[0,1] = squares[3,1]

    for k in range(4):
        cv2.circle(input, squares[k], 1, (255, 0, 0), 8)

    a = []
    b = []

    def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            xy = "[%d,%d]" % (x, y)
            a.append(x)
            b.append(y)
            cv2.circle(input, (x, y), 3, (0, 0, 255), thickness=-1)
            cv2.putText(input, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                        1.0, (0, 0, 0), thickness=1)  
            cv2.imshow("Adjust 4 corners OR Close this dialog", input)
            #print("[{},{}]".format(a[-1], b[-1]))  
        return a, b

    cv2.namedWindow("Adjust 4 corners OR Close this dialog")
    cv2.setMouseCallback("Adjust 4 corners OR Close this dialog", on_EVENT_LBUTTONDOWN)
    cv2.imshow("Adjust 4 corners OR Close this dialog", input)
    cv2.waitKey(0)
   
    center = [width / 2, height / 2]
    for i in range(len(a)):
        aa = a[i] - center[0]
        bb = b[i] - center[1]
        if aa <= 0 and bb < 0:
            squares[1, 0], squares[1, 1] = a[i], b[i] ## left top
        elif aa > 0 and bb < 0:
            squares[2, 0], squares[2, 1] = a[i], b[i]  ## right top
        elif aa >= 0 and bb > 0:
            squares[3, 0], squares[3, 1] = a[i], b[i]  ## right down
        else:
            squares[0, 0], squares[0, 1] = a[i], b[i] ## left down
    
    return squares

