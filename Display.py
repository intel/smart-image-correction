#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/20
# @Author  : kiwi
# @File    : Display.py, Main.py, ImgEnhance.py/ui, ImageAlignment.py/ui, Mainfunction.py
# @Software: PyCharm

import cv2
import threading
from PyQt5.QtCore import QFile
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QMessageBox
import time
import os
import numpy as np
import sys
import Mainfunction
import page_dewarp
import DetectHard


class Display:
    def __init__(self, ui, mainWnd, child_ui, childWnd):
        self.ui = ui
        self.mainWnd = mainWnd
        self.child_ui = child_ui
        self.childWnd = childWnd

        
        ui.input_button.clicked.connect(self.Open)
        ui.quadDetect_button.clicked.connect(self.quadDetect)
        ui.surfaceF_button.clicked.connect(self.surfaceF)
        ui.imgEnhance_button.clicked.connect(self.resetResult)
        ui.saveR_button.clicked.connect(self.saveResult)
        ui.rotate_Button.clicked.connect(self.rotateResult)

        child_ui.Laplace_Button.clicked.connect(self.Laplace)
        child_ui.Gamma_Button.clicked.connect(self.Gamma)
        child_ui.Sharp_Button.clicked.connect(self.Sharp)
        child_ui.Contrast_Button.clicked.connect(self.Contrast)
        child_ui.Color_Button.clicked.connect(self.Color)
        child_ui.Bright_Button.clicked.connect(self.Bright)
        child_ui.Reset_Button.clicked.connect(self.resetResult)
        child_ui.Save_Button.clicked.connect(self.saveResult)
        child_ui.whitebg_Button.clicked.connect(self.whitebg)
        child_ui.remove_redblue_Button.clicked.connect(self.remove_redblue)

    def Open(self):
        self.fileName = ""
        self.fileName = QFileDialog.getOpenFileName(self.mainWnd, 'Choose file', '',"(*.png);(*.jpg)" )[0]

        try:
            file = open(self.fileName)
            file.close()
            qimg = cv2.imread(self.fileName)
            qimg.shape
        except FileNotFoundError:
            self.ui.note_label.setText("No such file or directory")
        except IsADirectoryError:
            self.ui.note_label.setText("Is a directory")
        except PermissionError:
            self.ui.note_label.setText("Permission denied")
        except:
            self.ui.note_label.setText("The path of input image can't include Chinese characters!")
            return

        self.srcImg = QPixmap(self.fileName)
        print(self.fileName[:-4])
        ## adjust to display windows
        self.ratio = min(self.ui.srcImg_View.width()/self.srcImg.width(),self.ui.srcImg_View.height()/self.srcImg.height())
        self.display_w = int(self.ratio * self.srcImg.width())
        self.display_h = int(self.ratio * self.srcImg.height())
        #print(display_w, display_h)
        self.display_src = self.srcImg.scaled(self.display_w, self.display_h)
        self.ui.srcImg_View.setPixmap(self.display_src)
        self.ui.note_label.setText("Select 'Quad Detection' or 'Surface Flatten'.")

    def qimage2mat(self,qimg):
        ptr = qimg.constBits()
        ptr.setsize(qimg.byteCount())
        mat = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)  
        return mat

    def cv2qimageRes(self,result):
        result_n = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        res_img = QImage(result_n.data, result_n.shape[1], result_n.shape[0], 3 * result_n.shape[1], QImage.Format_RGB888)  #
        self.ui.result_View.setPixmap(QPixmap.fromImage(res_img))

    def quadDetect(self):
        time_start = time.time()
        qimg = cv2.imread(self.fileName)
        if abs(qimg.shape[1]//self.display_w - qimg.shape[0]//self.display_h) < 0.1:
            src_img_copy = cv2.resize(qimg, (self.display_w, self.display_h))
        else:
            src_img_copy = cv2.resize(qimg, (self.display_h, self.display_w))


        self.ui.note_label.setText("Squares detecting ......")
        # squares = Mainfunction.squaresDetect(src_img_copy)
        squares = DetectHard.detect_hard(src_img_copy)
        if len(squares) == 0:
            self.ui.note_label.setText("Can't detect Rect! ")
            self.result = src_img_copy
        else:
            time_end = time.time()
            time_sum = round(time_end - time_start,3)  
            self.ui.note_label.setText("Executed time:"+str(time_sum)+"s. Click 'Image Enhancement'.")
            result1 = Mainfunction.transfrom2size(qimg,squares/self.ratio)

            ratio_new = min(self.ui.srcImg_View.width() / result1.shape[1], self.ui.srcImg_View.height() / result1.shape[0])
            display_w_res = int(ratio_new * result1.shape[1] )
            display_h_res = int(ratio_new * result1.shape[0] )

            self.result = cv2.resize(result1, (display_w_res, display_h_res))

            enhancer = Mainfunction.Enhancer()  
            result1 = enhancer.bright(result1, 1.2)
            result1 = enhancer.contrast(result1, 1.2)
            result1 = enhancer.sharp(result1, 1.6)
            cv2.imwrite(self.fileName[:-4]+"_org_res.png",result1)
        # cv2.imshow("src_copy", self.result)
        self.result_copy = self.result

        self.cv2qimageRes( self.result )

    def surfaceF(self):
        self.ui.note_label.setText("Surface Flattening ......")
        time_start = time.time()
        result_s = page_dewarp.surfaceFmain(self.fileName)
        if result_s is None:
            self.ui.note_label.setText("Error: Can't detect surface in this image!")
            return

        ## adjust to display windows
        ratio = min(self.ui.result_View.width()/result_s.shape[1],self.ui.result_View.height()/result_s.shape[0])
        display_wr = int(ratio * result_s.shape[1])
        display_hr = int(ratio * result_s.shape[0])
        self.result = cv2.resize(result_s,(display_wr, display_hr),interpolation=cv2.INTER_AREA)

        self.cv2qimageRes(self.result)
        self.result_copy = self.result
        time_end = time.time()
        time_sum = round(time_end - time_start,3)  
        self.ui.note_label.setText("Executed time:"+str(time_sum)+ "s. Select 'Image Enhancement' or 'Save Result'.")

    def rotateResult(self):
        try:
            self.result = cv2.rotate(self.result, cv2.ROTATE_90_CLOCKWISE)
            self.result_copy = self.result
            self.cv2qimageRes(self.result)
        except:
            self.ui.note_label.setText("Rotate failed.")

    def resetResult(self):
        self.ui.note_label.setText("Reset Done.")
        self.child_ui.Gamma_SpinBox.setProperty("value", 1.0)
        self.child_ui.Bright_SpinBox.setProperty("value", 1.2)
        self.child_ui.Color_SpinBox.setProperty("value", 1.0)
        self.child_ui.Contrast_SpinBox.setProperty("value", 1.2)
        self.child_ui.Sharp_SpinBox.setProperty("value", 1.6)
        self.result = self.result_copy
        enhancer = Mainfunction.Enhancer() 
        self.result = enhancer.bright(self.result, self.child_ui.Bright_SpinBox.value())
        self.result = enhancer.contrast(self.result, self.child_ui.Contrast_SpinBox.value())
        self.result = enhancer.sharp(self.result, self.child_ui.Sharp_SpinBox.value())

        cv2.imshow("Enhanced Result", self.result)

    def saveResult(self):
        try:
            cv2.imwrite(self.fileName[:-4]+"_res.png",self.result)
            self.ui.note_label.setText("Save result at path of input image.")
        except:
            self.ui.note_label.setText("Save result failed!")
            return

    def whitebg(self):
        try:
            self.ui.note_label.setText("white background and black font Done.")
            self.result = Mainfunction.whitebg_black(self.result)
            cv2.imshow("Enhanced Result", self.result)
        except:
            self.ui.note_label.setText("Try it again or select other function.")
            return

    def remove_redblue(self):
        try:
            self.ui.note_label.setText("Remove red and blue area Done.")
            self.result = Mainfunction.remove_red_bule(self.result)
            cv2.imshow("Enhanced Result", self.result)
        except:
            self.ui.note_label.setText("Try it again or select other function.")
            return

    def Laplace(self):
        try:
            self.ui.note_label.setText("Laplace Done.")
            enhancer = Mainfunction.Enhancer()
            self.result = enhancer.laplace(self.result)
            cv2.imshow("Enhanced Result", self.result)
        except:
            self.ui.note_label.setText("Try it again or select other function.")
            return

    def Gamma(self):
        try:
            self.ui.note_label.setText("Gamma Done.")
            enhancer = Mainfunction.Enhancer()
            self.result = enhancer.gamma(self.result, self.child_ui.Gamma_SpinBox.value())
            cv2.imshow("Enhanced Result", self.result)
        except:
            self.ui.note_label.setText("Try it again or select other function.")
            return

    def Sharp(self):
        try:
            self.ui.note_label.setText("Sharpness Done.")
            enhancer = Mainfunction.Enhancer()
            self.result = enhancer.sharp(self.result, self.child_ui.Sharp_SpinBox.value())
            cv2.imshow("Enhanced Result", self.result)
        except:
            self.ui.note_label.setText("Try it again or select other function.")
            return

    def Contrast(self):
        try:
            self.ui.note_label.setText("Contrast Done.")
            enhancer = Mainfunction.Enhancer()
            self.result = enhancer.contrast(self.result, self.child_ui.Contrast_SpinBox.value())
            cv2.imshow("Enhanced Result", self.result)
        except:
            self.ui.note_label.setText("Try it again or select other function.")
            return

    def Color(self): 
        try:
            self.ui.note_label.setText("Color Done.")
            enhancer = Mainfunction.Enhancer()
            self.result = enhancer.color(self.result, self.child_ui.Color_SpinBox.value())
            cv2.imshow("Enhanced Result", self.result)
        except:
            self.ui.note_label.setText("Try it again or select other function.")
            return

    def Bright(self):
        try:
            self.ui.note_label.setText("Brightness Done.")
            enhancer = Mainfunction.Enhancer()
            self.result = enhancer.bright(self.result, self.child_ui.Bright_SpinBox.value())
            cv2.imshow("Enhanced Result", self.result)
        except:
            self.ui.note_label.setText("Try it again or select other function.")
            return

