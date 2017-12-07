from __future__ import print_function
import sys

import sip
sip.setapi('QVariant', 2)

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import cv2

from functools import partial

from gradients import magThresh, dirThresh, absSobelThresh
from hls import HLS_Channel


absSobelThresh_X = partial(absSobelThresh, orient='x')
absSobelThresh_Y = partial(absSobelThresh, orient='y')
HLS_Channel_H = partial(HLS_Channel, channel='h')
HLS_Channel_L = partial(HLS_Channel, channel='l')
HLS_Channel_S = partial(HLS_Channel, channel='s')



class SliderUnit(QWidget):
    def __init__(self, function, name):
        self.function = function

        self.layout = QGridLayout()
        layoutLow = QHBoxLayout()
        self.button = QRadioButton()
        self.button.setChecked(False)
        
        self.sliderLow = QSlider(Qt.Vertical)
        self.sliderLow.setMinimum(0)
        self.sliderLow.setMaximum(255)
        self.sliderLow.setValue(50)
        self.sliderLow.setTickPosition(QSlider.TicksBelow)
        self.sliderLow.setTickInterval(32)

        self.sliderHigh = QSlider(Qt.Vertical)
        self.sliderHigh.setMinimum(0)
        self.sliderHigh.setMaximum(255)
        self.sliderHigh.setValue(200)
        self.sliderHigh.setTickPosition(QSlider.TicksBelow)
        self.sliderHigh.setTickInterval(32)

        layoutLow.addWidget(self.sliderLow)
        layoutLow.addWidget(self.sliderHigh)
        self.layout.addWidget(self.button, 1, 1, Qt.AlignCenter)
        self.layout.addLayout(layoutLow, 2, 1)

        self.label = QLabel(name)
        self.layout.addWidget(self.label, 3, 1, Qt.AlignCenter)

        self.displayHigh = QLineEdit()
        self.displayHigh.setText(str(self.sliderHigh.value()))
        self.displayHigh.setFixedWidth(35)
        self.displayHigh.setAlignment(Qt.AlignCenter)

        self.displayLow = QLineEdit()
        self.displayLow.setText(str(self.sliderLow.value()))
        self.displayLow.setFixedWidth(35)
        self.displayLow.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.displayHigh, 4, 1, Qt.AlignCenter)
        self.layout.addWidget(self.displayLow, 5, 1, Qt.AlignCenter)
        



class Analyzer(QTabWidget):

    currentSlider = None
    

    def __init__(self, parent = None):
        super(Analyzer, self).__init__(parent)

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.addTab(self.tab1, "Gradients")
        self.addTab(self.tab2, "Colors")

        self.gradientSliders()
        self.colorSliders()
        
        self.currentSlider = self.magSlider
        self.currentSlider.button.setChecked(True)



    def gradientSliders(self):
        layout = QHBoxLayout()

        self.magSlider = SliderUnit(magThresh, "Mag")
        self.dirSlider = SliderUnit(dirThresh, "Dir")
        self.sobelxSlider = SliderUnit(absSobelThresh_X, "Sobel_x")
        self.sobelySlider = SliderUnit(absSobelThresh_Y, "Sobel_y")
        
        layout.addLayout(self.magSlider.layout)
        layout.addLayout(self.dirSlider.layout)
        layout.addLayout(self.sobelxSlider.layout)
        layout.addLayout(self.sobelySlider.layout)

        self.tab1.setLayout(layout)


    def colorSliders(self):
        layout = QHBoxLayout()

        self.H_Slider = SliderUnit(HLS_Channel_H, "H")
        self.L_Slider = SliderUnit(HLS_Channel_L, "L")
        self.S_Slider = SliderUnit(HLS_Channel_S, "S")
        
        layout.addLayout(self.H_Slider.layout)
        layout.addLayout(self.L_Slider.layout)
        layout.addLayout(self.S_Slider.layout)

        self.tab2.setLayout(layout)





class Sliders(QWidget):
    images = []
    currentIndex = 0

    def __init__(self, parent = None):
        super(Sliders, self).__init__(parent)

        primaryLayout = QHBoxLayout()
        leftLayout = QVBoxLayout()

        self.imageCB = QComboBox()

        testImageList = [   'test1.jpg', 'test2.jpg', 
                            'test3.jpg', 'test4.jpg', 
                            'test5.jpg', 'test6.jpg']
        
        self.imageCB.addItems(testImageList)
        self.imageCB.currentIndexChanged.connect(self.valueChange_imageCB)
        leftLayout.addWidget(self.imageCB)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        leftLayout.addWidget(self.label) 
       
        self.gradientLogic = QLineEdit()
        #self.textBox.setText("((binaryMag==1)|(binaryDir==1))")
        self.gradientLogic.setText("((binaryGradx==0)|(binaryGrady==0)) & ((binaryMag==0)|(binaryDir==0))")
        leftLayout.addWidget(self.gradientLogic)
        self.gradientLogic.returnPressed.connect(self.sobelComposite)

        self.colorLogic = QLineEdit()
        self.colorLogic.setText("(h_binary==1) | (l_binary==1) | (s_binary==1)")
        leftLayout.addWidget(self.colorLogic)
        self.colorLogic.returnPressed.connect(self.colorComposite)

        self.compositeButton = QPushButton("Create Composite")
        leftLayout.addWidget(self.compositeButton)


        primaryLayout.addLayout(leftLayout)

        self.tabs = Analyzer()
        primaryLayout.addWidget(self.tabs)

        self.setLayout(primaryLayout)


        self.tabs.magSlider.button.toggled.connect(lambda x: self.buttonchange(self.tabs.magSlider))
        self.tabs.magSlider.sliderLow.valueChanged.connect(lambda x: self.valuechange(self.tabs.magSlider))
        self.tabs.magSlider.sliderHigh.valueChanged.connect(lambda x: self.valuechange(self.tabs.magSlider))

        self.tabs.dirSlider.button.toggled.connect(lambda x: self.buttonchange(self.tabs.dirSlider))
        self.tabs.dirSlider.sliderLow.valueChanged.connect(lambda x: self.valuechange(self.tabs.dirSlider))
        self.tabs.dirSlider.sliderHigh.valueChanged.connect(lambda x: self.valuechange(self.tabs.dirSlider))

        self.tabs.sobelxSlider.button.toggled.connect(lambda x: self.buttonchange(self.tabs.sobelxSlider))
        self.tabs.sobelxSlider.sliderLow.valueChanged.connect(lambda x: self.valuechange(self.tabs.sobelxSlider))
        self.tabs.sobelxSlider.sliderHigh.valueChanged.connect(lambda x: self.valuechange(self.tabs.sobelxSlider))

        self.tabs.sobelySlider.button.toggled.connect(lambda x: self.buttonchange(self.tabs.sobelySlider))
        self.tabs.sobelySlider.sliderLow.valueChanged.connect(lambda x: self.valuechange(self.tabs.sobelySlider))
        self.tabs.sobelySlider.sliderHigh.valueChanged.connect(lambda x: self.valuechange(self.tabs.sobelySlider))

        self.tabs.H_Slider.button.toggled.connect(lambda x: self.buttonchange_HLS(self.tabs.H_Slider))
        self.tabs.H_Slider.sliderLow.valueChanged.connect(lambda x: self.valuechange_HLS(self.tabs.H_Slider))
        self.tabs.H_Slider.sliderHigh.valueChanged.connect(lambda x: self.valuechange_HLS(self.tabs.H_Slider))

        self.tabs.L_Slider.button.toggled.connect(lambda x: self.buttonchange_HLS(self.tabs.L_Slider))
        self.tabs.L_Slider.sliderLow.valueChanged.connect(lambda x: self.valuechange_HLS(self.tabs.L_Slider))
        self.tabs.L_Slider.sliderHigh.valueChanged.connect(lambda x: self.valuechange_HLS(self.tabs.L_Slider))

        self.tabs.S_Slider.button.toggled.connect(lambda x: self.buttonchange_HLS(self.tabs.S_Slider))
        self.tabs.S_Slider.sliderLow.valueChanged.connect(lambda x: self.valuechange_HLS(self.tabs.S_Slider))
        self.tabs.S_Slider.sliderHigh.valueChanged.connect(lambda x: self.valuechange_HLS(self.tabs.S_Slider))

        self.compositeButton.clicked.connect(self.totalComposite)


        self.setWindowTitle("Gradient and Color Analyzer")
        self.loadImages(testImageList)

        #self.statusBar()
        #mainMenu = self.menuBar()
        #fileMenu = mainMenu.addMenu('&File')

        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)



    def loadImages(self, fileList):
        self.images = []

        for i in range(6):
            self.images.append(cv2.imread("./test_images/" + fileList[i]))

        self.valueChange_imageCB(0)

    def valuechange(self, sl):  
        #self.pixmap.fill(Qt.white)
        sl.button.setChecked(True)
        sl.displayHigh.setText(str(sl.sliderHigh.value()))
        sl.displayLow.setText(str(sl.sliderLow.value()))
        self.currentSlider = sl
        img = sl.function(self.images[self.currentIndex], 3, (sl.sliderLow.value(), sl.sliderHigh.value())) * 255
        self.refreshImage(img)

    def valuechange_HLS(self, sl):  
        #self.pixmap.fill(Qt.white)
        sl.button.setChecked(True)
        sl.displayHigh.setText(str(sl.sliderHigh.value()))
        sl.displayLow.setText(str(sl.sliderLow.value()))
        self.currentSlider = sl
        img = sl.function(self.images[self.currentIndex], (sl.sliderLow.value(), sl.sliderHigh.value())) * 255
        self.refreshImage(img)


    def buttonchange(self, sl):  
        self.currentSlider = sl
        img = sl.function(self.images[self.currentIndex], 3, (sl.sliderLow.value(), sl.sliderHigh.value())) * 255
        self.refreshImage(img)

    def buttonchange_HLS(self, sl):  
        self.currentSlider = sl
        img = sl.function(self.images[self.currentIndex], (sl.sliderLow.value(), sl.sliderHigh.value())) * 255
        self.refreshImage(img)


    def refreshImage(self, img):
        width = img.shape[1]
        img = np.dstack((img, img, img))
        img = QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)
        self.pixmap = QPixmap(img).scaledToWidth(width//1.5)
        self.label.setPixmap(self.pixmap)


    def valueChange_imageCB(self, index):
        self.tabs.currentIndex = index
        img = self.tabs.currentSlider.function(self.images[index], 3, (self.tabs.currentSlider.sliderLow.value(), self.tabs.currentSlider.sliderHigh.value())) * 255
        self.refreshImage(img)



    def sobelComposite(self):
        img = self.images[0]

        binaryMag = magThresh(img, sobel_kernel=3, thresh=(self.tabs.magSlider.sliderLow.value(),self.tabs.magSlider.sliderHigh.value()) )
        binaryDir = dirThresh(img, sobel_kernel=3, thresh=(self.tabs.dirSlider.sliderLow.value(), self.tabs.dirSlider.sliderHigh.value()) )
        binaryGradx = absSobelThresh_X(img, sobel_kernel=3, thresh=(self.tabs.sobelxSlider.sliderLow.value(),self.tabs.sobelxSlider.sliderHigh.value()))
        binaryGrady = absSobelThresh_Y(img, sobel_kernel=3, thresh=(self.tabs.sobelySlider.sliderLow.value(),self.tabs.sobelySlider.sliderHigh.value()))

        binaryGrad = np.zeros_like(binaryMag)
   
        codeString = "binaryGrad[%s] = 255" % self.gradientLogic.text()
        exec(codeString)
        self.refreshImage(binaryGrad)


    def colorComposite(self):
        img = self.images[0]

        h_binary = HLS_Channel_H(img, thresh=(self.tabs.H_Slider.sliderLow.value(), self.tabs.H_Slider.sliderHigh.value()))
        l_binary = HLS_Channel_L(img, thresh=(self.tabs.L_Slider.sliderLow.value(), self.tabs.L_Slider.sliderHigh.value()))
        s_binary = HLS_Channel_S(img, thresh=(self.tabs.S_Slider.sliderLow.value(), self.tabs.S_Slider.sliderHigh.value()))

        binaryColor = np.zeros_like(h_binary)
   
        codeString = "binaryColor[%s] = 255" % self.colorLogic.text()
        exec(codeString)
        self.refreshImage(binaryColor)


    def totalComposite(self):
        img = self.images[0]

        binaryMag = magThresh(img, sobel_kernel=3, thresh=(self.tabs.magSlider.sliderLow.value(),self.tabs.magSlider.sliderHigh.value()) )
        binaryDir = dirThresh(img, sobel_kernel=3, thresh=(self.tabs.dirSlider.sliderLow.value(), self.tabs.dirSlider.sliderHigh.value()) )
        binaryGradx = absSobelThresh_X(img, sobel_kernel=3, thresh=(self.tabs.sobelxSlider.sliderLow.value(),self.tabs.sobelxSlider.sliderHigh.value()))
        binaryGrady = absSobelThresh_Y(img, sobel_kernel=3, thresh=(self.tabs.sobelySlider.sliderLow.value(),self.tabs.sobelySlider.sliderHigh.value()))
        binaryGrad = np.zeros_like(binaryMag)
        codeString = "binaryGrad[%s] = 1" % self.gradientLogic.text()
        exec(codeString)
        
        h_binary = HLS_Channel_H(img, thresh=(self.tabs.H_Slider.sliderLow.value(), self.tabs.H_Slider.sliderHigh.value()))
        l_binary = HLS_Channel_L(img, thresh=(self.tabs.L_Slider.sliderLow.value(), self.tabs.L_Slider.sliderHigh.value()))
        s_binary = HLS_Channel_S(img, thresh=(self.tabs.S_Slider.sliderLow.value(), self.tabs.S_Slider.sliderHigh.value()))
        binaryColor = np.zeros_like(h_binary)
        codeString = "binaryColor[%s] = 1" % self.colorLogic.text()
        exec(codeString)

        binaryComposite = np.zeros_like(h_binary)
        binaryComposite[(binaryGrad==1)|(binaryColor==1)] = 255
        self.refreshImage(binaryComposite)


def main():
    app = QApplication(sys.argv)
    sliders = Sliders()
    sliders.show()
    #adjust_threshold()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()





# Extremely slow conversion algorithm
"""
qimage = QImage(image.shape[1], image.shape[0], QImage.Format_RGB888)
for j in range(image.shape[1]):
    for i in range(image.shape[0]):
        qimage.setPixel(j, i, QColor(image[i][j][0],image[i][j][0],image[i][j][0]).rgb())
"""






