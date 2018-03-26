# -*- coding: utf-8 -*-

# "BVHPlayerPy" Current BVH file info & Playing frame info
# Author: T.Shuhei
# Last Modified: 2017/09/28

import numpy as np
from PyQt5.Qt import *

class InfoWidget(QGroupBox):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setTitle("Information")

        mainLayout = QVBoxLayout()
        self.fileNameLabel = QLabel()
        mainLayout.addWidget(self.fileNameLabel)

        self.frameRateLabel = QLabel()
        mainLayout.addWidget(self.frameRateLabel)

        frameInfoLayout = QHBoxLayout()
        frameRowName = QLabel()
        frameRowName.setText("Frame:")
        frameInfoLayout.addWidget(frameRowName)
        self.frameCounter = QLabel()
        frameInfoLayout.addWidget(self.frameCounter)
        self.framesLabel = QLabel()
        frameInfoLayout.addWidget(self.framesLabel)
        mainLayout.addLayout(frameInfoLayout)
        
        self.initInfo("-  [Press 'Ctrl+L' or File/Open ...]", 0, 1)
        
        self.setLayout(mainLayout)

    
    def initInfo(self, fileName, frameTime, frames):
        if frameTime == 0:
            frameRate = 0
        else:
            frameRate = np.round(1.0 / frameTime, 2)

        self.fileNameLabel.setText("File : " + fileName)
        self.frameRateLabel.setText("Frame Rate : " + str(frameRate) + " fps.") 
        self.framesLabel.setText(" / " + str(frames - 1))
        self.resetFrameCount()

    def updateFrameCount(self, frameCount):
        self.frameCounter.setText(str(frameCount))
    
    def resetFrameCount(self):
        self.frameCount = 0
        self.frameCounter.setText(str(0))
