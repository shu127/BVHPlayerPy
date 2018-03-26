# -*- coding: utf-8 -*-

# "BVHPlayerPy" BVH Splitting Tools
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

from python_bvh import BVH

class SplitWidget(QGroupBox):
    hParentWidget = None

    def __init__(self, parent = None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.pathResourceDir = os.path.join(parent.pathCurrentDir, "IconResource")
        self.pathDstDir = parent.pathMotionFileDir
        self.setTitle("Motion Splitter")

        settingButtonLayout = QHBoxLayout()
        self.beginButton = QPushButton()
        beginIcon = QPixmap(os.path.join(self.pathResourceDir, "step-forward-solid.svg"))
        self.beginButton.setIcon(QIcon(beginIcon))
        settingButtonLayout.addWidget(self.beginButton)
        self.beginButton.setEnabled(False)
        self.beginButton.setFocusPolicy(Qt.NoFocus)
        self.beginButton.clicked.connect(self.setBeginFrame)

        self.addSplitButton = QPushButton("New")
        settingButtonLayout.addWidget(self.addSplitButton)
        self.addSplitButton.setEnabled(False)
        self.addSplitButton.setFocusPolicy(Qt.NoFocus)
        self.addSplitButton.clicked.connect(self.createItem)

        self.delSplitButton = QPushButton("Delete")
        settingButtonLayout.addWidget(self.delSplitButton)
        self.delSplitButton.setEnabled(False)
        self.delSplitButton.setFocusPolicy(Qt.NoFocus)
        self.delSplitButton.clicked.connect(self.deleteItem)

        self.endButton = QPushButton()
        endIcon = beginIcon.transformed(QTransform(-1.0,  0.0, 0.0,
                                                    0.0, -1.0, 0.0,
                                                    0.0,  0.0, 1.0))
        self.endButton.setIcon(QIcon(endIcon))
        settingButtonLayout.addWidget(self.endButton)
        self.endButton.setEnabled(False)
        self.endButton.setFocusPolicy(Qt.NoFocus)
        self.endButton.clicked.connect(self.setEndFrame)

        self.splitDataGrid = QTableWidget(0, 3)
        self.splitDataGrid.setHorizontalHeaderLabels(["Enable", "Begin Frame","End Frame"])
        self.splitDataGrid.setColumnWidth(0, 45)
        self.splitDataGrid.setColumnWidth(1, 84)
        self.splitDataGrid.setColumnWidth(2, 84)
        self.splitDataGrid.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.splitDataGrid.setSelectionBehavior(QAbstractItemView.SelectRows)

        exportButtonsLayout = QHBoxLayout()
        self.dstinationButton = QPushButton("Destination...")
        exportButtonsLayout.addWidget(self.dstinationButton)
        self.dstinationButton.setFocusPolicy(Qt.NoFocus)
        self.dstinationButton.clicked.connect(self.setDestinationDir)

        self.exportButton = QPushButton()
        exportIcon = QPixmap(os.path.join(self.pathResourceDir, "export-solid.svg"))
        self.exportButton.setIcon(QIcon(exportIcon))
        exportButtonsLayout.addWidget(self.exportButton)
        self.exportButton.setEnabled(False)
        self.exportButton.setFocusPolicy(Qt.NoFocus)
        self.exportButton.clicked.connect(self.exportSplittedBVH)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(settingButtonLayout)
        mainLayout.addWidget(self.splitDataGrid)
        mainLayout.addLayout(exportButtonsLayout)
        self.setLayout(mainLayout)

    def setActive(self):
        self.beginButton.setEnabled(True)
        self.addSplitButton.setEnabled(True)
        self.delSplitButton.setEnabled(True)
        self.endButton.setEnabled(True)
        self.exportButton.setEnabled(True)

    def initMotionData(self, filename, root, motion, frameTime):
        self.origFileName = filename
        self.root = root
        self.origMotion = motion
        self.frameTime = frameTime
        for i in reversed(range(0, self.splitDataGrid.rowCount())):
            self.splitDataGrid.removeRow(i)

    def createItem(self):
        rows = self.splitDataGrid.rowCount()
        self.splitDataGrid.setRowCount(rows + 1)
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Checked)
        self.splitDataGrid.setItem(rows, 0, item)
        self.splitDataGrid.setItem(rows, 1, QTableWidgetItem())
        self.splitDataGrid.setItem(rows, 2, QTableWidgetItem())

    def setBeginFrame(self):
        if self.splitDataGrid.rowCount() != 0:
            select = self.splitDataGrid.selectedIndexes()
            if len(select) == 0:
                rowIndex = self.splitDataGrid.rowCount() - 1
            else:
                rowIndex = select[0].row()
            item = self.splitDataGrid.item(rowIndex, 1)
            item.setText(str(self.hParentWidget.drawPanel.frameCount))

    def setEndFrame(self):
        if self.splitDataGrid.rowCount() != 0:
            select = self.splitDataGrid.selectedIndexes()
            if len(select) == 0:
                rowIndex = self.splitDataGrid.rowCount() - 1
            else:
                rowIndex = select[0].row()
            item = self.splitDataGrid.item(rowIndex, 2)
            item.setText(str(self.hParentWidget.drawPanel.frameCount))
        
    def deleteItem(self):
        if self.splitDataGrid.rowCount() != 0:
            select = self.splitDataGrid.selectedIndexes()
            if len(select) == 0:
                rowIndex = self.splitDataGrid.rowCount() - 1
            else:
                rowIndex = select[0].row()
            self.splitDataGrid.removeRow(rowIndex)

    def setDestinationDir(self):
        filePath = QFileDialog.getExistingDirectory(self, "Choose Destination Folder ...", self.pathDstDir)
        if filePath == "":
#            print("Error: Destination Folder is not given")
            pass
        else:
            self.pathDstDir = filePath

    def exportSplittedBVH(self):
        if self.splitDataGrid.rowCount() != 0:
            splitdata = []
            for row in range(0, self.splitDataGrid.rowCount()):
                if self.splitDataGrid.item(row, 0).checkState() == Qt.Checked:
                    try:
                        begin = int(self.splitDataGrid.item(row, 1).text())
                        end = int(self.splitDataGrid.item(row, 2).text())
                        if begin >= end:
                            raise ValueError
                        splitdata.append((row, begin, end))
                    except ValueError:
                        pass
            
            if len(splitdata) != 0:
                progress = QProgressDialog()
                progress.setRange(0, len(splitdata))
                for i, data in enumerate(splitdata):
                    row, begin, end = data
                    strRow = str(row) if row > 10 else "0" + str(row)
                    dstFilePath = os.path.join(self.pathDstDir, self.origFileName.split(".")[0] + "_" + strRow + ".bvh")
                    motion = self.origMotion[begin:end]
                    BVH.writeBVH(dstFilePath, self.root, motion, end - begin, self.frameTime)
                    self.splitDataGrid.item(row, 0).setCheckState(Qt.Unchecked)
                    progress.setValue(i+1)
