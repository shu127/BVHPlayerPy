# -*- coding: utf-8 -*-

# "BVHPlayerPy" Player control components
# Author: T.Shuhei
# Last Modified: 2017/09/28

# Using these icon resource:
# https://vmware.github.io/clarity/icons/icon-sets#core-shapes
# 
# Clarity is licensed under the MIT License.  
# https://github.com/vmware/clarity/blob/master/LICENSE  
# 

import os
import numpy as np
from PyQt5.Qt import *

class ControlWidget(QGroupBox):
    fPlayMode = False
    hParentWidget = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.pathResourceDir = os.path.join(parent.pathCurrentDir, "IconResource")
        self.setTitle("Control")

        playerLayout = QHBoxLayout()
        self.rewindButton = _createButton("rewind", 60, self.rewindButtonAction, os.path.join(self.pathResourceDir, "rewind-solid.svg"))
        playerLayout.addWidget(self.rewindButton)
        self.rewindButton.setEnabled(False)
        self.rewindButton.setFocusPolicy(Qt.NoFocus)


        self.playButton = _createButton("play", 60, self.playButtonAction, os.path.join(self.pathResourceDir, "play-solid.svg"))
        playerLayout.addWidget(self.playButton)
        self.playButton.setEnabled(False)
        self.playButton.setFocusPolicy(Qt.NoFocus)
        
        self.pauseButton = _createButton("pause", 60, self.playButtonAction, os.path.join(self.pathResourceDir, "pause-solid.svg"))
        playerLayout.addWidget(self.pauseButton)
        self.pauseButton.setVisible(False)
        self.pauseButton.setFocusPolicy(Qt.NoFocus)

        self.stopButton = _createButton("stop", 60, self.stopButtonAction, os.path.join(self.pathResourceDir, "stop-solid.svg"))
        playerLayout.addWidget(self.stopButton)
        self.stopButton.setEnabled(False)
        self.stopButton.setFocusPolicy(Qt.NoFocus)

        self.forwardButton = _createButton("forward", 60, self.forwardButtonAction, os.path.join(self.pathResourceDir, "fast-forward-solid.svg"))
        playerLayout.addWidget(self.forwardButton)
        self.forwardButton.setEnabled(False)
        self.forwardButton.setFocusPolicy(Qt.NoFocus)

        camCtlLayout = QHBoxLayout()
        self.camResetButton = _createButton("Camera Reset", 100, self.hParentWidget.drawPanel.resetCamera)
        camCtlLayout.addWidget(self.camResetButton)
        self.camResetButton.setFocusPolicy(Qt.NoFocus)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(playerLayout)
        mainLayout.addLayout(camCtlLayout)
        self.setLayout(mainLayout)

    def setPlayMode(self, fPlay):
        self.setActive()
        self.fPlayMode = fPlay
        if self.fPlayMode:
            self.playButton.setVisible(False)
            self.pauseButton.setVisible(True)
        else:
            self.pauseButton.setVisible(False)
            self.playButton.setVisible(True)
        
    def setActive(self):
        self.forwardButton.setEnabled(True)
        self.rewindButton.setEnabled(True)
        self.playButton.setEnabled(True)
        self.pauseButton.setEnabled(True)
        self.stopButton.setEnabled(True)

    def playButtonAction(self):
        self.fPlayMode = not self.fPlayMode
        self.hParentWidget.drawPanel.fastRatio = 1.0
        if self.fPlayMode:
            self.playButton.setVisible(False)
            self.pauseButton.setVisible(True)
            self.hParentWidget.drawPanel.isPlaying = True
        else:
            self.pauseButton.setVisible(False)
            self.playButton.setVisible(True)
            self.hParentWidget.drawPanel.isPlaying = False
    
    def stopButtonAction(self):
        self.fplayMode = False
        self.hParentWidget.drawPanel.isPlaying = False
        self.pauseButton.setVisible(False)
        self.playButton.setVisible(True)
        self.hParentWidget.drawPanel.frameCount = 0
        self.hParentWidget.drawPanel.fastRatio = 1.0

    def rewindButtonAction(self):
        if self.fPlayMode:
            if self.hParentWidget.drawPanel.fastRatio > 0:
                self.hParentWidget.drawPanel.fastRatio = -1.0
            else:
                self.hParentWidget.drawPanel.fastRatio *= 2.0
        else:
            self.hParentWidget.drawPanel.frameCount -= 1

    def forwardButtonAction(self):
        if self.fPlayMode:
            if self.hParentWidget.drawPanel.fastRatio < 0:
                self.hParentWidget.drawPanel.fastRatio = 1.0
            else:
                self.hParentWidget.drawPanel.fastRatio *= 2.0
        else:
            self.hParentWidget.drawPanel.frameCount += 1

## Support Functions
def _createButton(title, width, func, iconPath = None):
    if iconPath is None:
        button = QPushButton(title)
    else:
        button = QPushButton()
        button.setIcon(QIcon(QPixmap(iconPath)))

    button.setFixedWidth(width)
    button.clicked.connect(func)
    return button