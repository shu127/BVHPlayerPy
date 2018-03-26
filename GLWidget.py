# -*- coding: utf-8 -*-

# "BVHPlayerPy" OpenGL drawing component
# Author: T.Shuhei
# Last Modified: 2017/09/28

import numpy as np
import time

from PyQt5.Qt import *
from OpenGL.GL import *
from OpenGL.GLU import *

from python_bvh import BVHNode

class GLWidget(QOpenGLWidget):
    frameChanged = pyqtSignal(int)
    hParentWidget = None
    checkerBoardSize = 50
    camDist = 500
    floorObj = None
    rotateXZ = 0
    rotateY = 45
    translateX = 0
    translateY = 0
    frameCount = 0
    isPlaying = True
    fastRatio = 1.0
    scale = 1.0
    root = None
    motion = None
    frames = None
    frameTime = None
    drawMode = 0    # 0:rotation, 1:position

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.setMinimumSize(500, 500)
        self.lastPos = QPoint()

    def resetCamera(self):
        self.rotateXZ = 0
        self.rotateY = 45
        self.translateX = 0
        self.translateY = 0
        self.camDist = 500

    def setMotion(self, root:BVHNode, motion, frames:int, frameTime:float):
        self.root = root
        self.motion = motion
        self.frames = frames
        self.frameTime = frameTime
        self.frameCount = 0
        self.isPlaying = True

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_CONSTANT_ALPHA)
        glEnable(GL_BLEND)
        glClearColor(0.2, 0.2, 0.2, 0)
        self.floorObj = self.makeFloorObject(0)
        self.start = time.time()

    def updateFrame(self):
        if (self.frames is not None) and (self.frameTime is not None):
            now = time.time()
            if self.isPlaying:
                self.frameCount += int(1 * self.fastRatio) if abs(self.fastRatio) >= 1.0 else 1
                if self.frameCount >= self.frames:
                    self.frameCount = 0
                elif self.frameCount < 0:
                    self.frameCount = self.frames - 1
                self.frameChanged.emit(self.frameCount)
        self.update()
        self.hParentWidget.infoPanel.updateFrameCount(self.frameCount)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        qs = self.sizeHint()
        gluPerspective(60.0, float(qs.width()) / float(qs.height()), 1.0, 1000.0)
        camPx = self.camDist * np.cos(self.rotateXZ / 180.0)
        camPy = self.camDist * np.tanh(self.rotateY / 180.0)
        camPz = self.camDist * np.sin(self.rotateXZ / 180.0)
        transX = self.translateX * -np.sin(self.rotateXZ / 180.0)
        transZ = self.translateX * np.cos(self.rotateXZ / 180.0)
        gluLookAt(camPx + transX, camPy + self.translateY, camPz + transZ, transX, self.translateY, transZ, 0.0, 1.0, 0.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glCallList(self.floorObj)
        self.drawSkeleton()
        glPopMatrix()
        glFlush()
#        self.update()
        self.updateFrame()

    def drawSkeleton(self):
        def _RenderBone(quadObj, x0, y0, z0, x1, y1, z1):
            dir = [x1 - x0, y1 - y0, z1 - z0]
            boneLength = np.sqrt(dir[0]**2 + dir[1]**2 + dir[2]**2)

            if quadObj is None:
                quadObj = GLUQuadric()
            gluQuadricDrawStyle(quadObj, GLU_FILL)
            gluQuadricNormals(quadObj, GLU_SMOOTH)

            glPushMatrix()
            glTranslated(x0, y0, z0)

            length = np.sqrt(dir[0]**2 + dir[1]**2 + dir[2]**2)
            if length < 0.0001:
                dir = [0.0, 0.0, 1.0]
                length = 1.0
            dir = [data / length for data in dir]            
            
#            up   = [0.0, 1.0, 0.0]
#            side = [up[1]*dir[2] - up[2]*dir[1], up[2]*dir[0] - up[0]*dir[2], up[0]*dir[1] - up[1]*dir[0]]
            side = [dir[2], 0.0, -dir[0]]
            length = np.sqrt(side[0]**2 + side[1]**2 + side[2]**2)
            if length < 0.0001:
                side = [1.0, 0.0, 0.0]
                length = 1.0
            side = [data / length for data in side]

            up = [dir[1]*side[2] - dir[2]*side[1], dir[2]*side[0] - dir[0]*side[2], dir[0]*side[1] - dir[1]*side[0]]
            glMultMatrixd((side[0], side[1], side[2], 0.0,
                             up[0],   up[1],   up[2], 0.0,
                            dir[0],  dir[1],  dir[2], 0.0,
                               0.0,     0.0,     0.0, 1.0))
            radius = 1.5
            slices = 8
            stack = 1
            gluCylinder(quadObj, radius, radius, boneLength, slices, stack)
            glPopMatrix()

        def _RenderJoint(quadObj):
            if quadObj is None:
                quadObj = GLUQuadric()
            gluQuadricDrawStyle(quadObj, GLU_FILL)
            gluQuadricNormals(quadObj, GLU_SMOOTH)

            if self.drawMode == 0:  # rotation mode
                glColor3f(1.000, 0.271, 0.000)
            else:                   # position mode
                glColor3f(0.000, 1.052, 0.000)

            gluSphere(quadObj, 3.0, 16, 16)            

            if self.drawMode == 0:  # rotation mode
                glColor3f(1.000, 0.549, 0.000)
            else:                   # position mode
                glColor3f(0.000, 1.000, 0.000)

        def _RenderFigure(node:BVHNode):
            quadObj = None
            glPushMatrix()
            if self.drawMode == 0:
                # Translate
                if node.nodeIndex == 0:     # ROOT
                    glTranslatef(self.motion[self.frameCount][0] * self.scale,
                                 self.motion[self.frameCount][1] * self.scale,
                                 self.motion[self.frameCount][2] * self.scale)
                else:   # general node
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)

                # Rotation
                for i, channel in enumerate(node.chLabel):
                    if "Xrotation" in channel:
                        glRotatef(self.motion[self.frameCount][node.frameIndex + i], 1.0, 0.0, 0.0)
                    elif "Yrotation" in channel:
                        glRotatef(self.motion[self.frameCount][node.frameIndex + i], 0.0, 1.0, 0.0)
                    elif "Zrotation" in channel:
                        glRotatef(self.motion[self.frameCount][node.frameIndex + i], 0.0, 0.0, 1.0)
                
                # Drawing Links
                if node.fHaveSite:
                    _RenderBone(quadObj, 0.0, 0.0, 0.0, node.site[0] * self.scale, node.site[1] * self.scale, node.site[2] * self.scale)
                for child in node.childNode:
                    _RenderBone(quadObj, 0.0, 0.0, 0.0, child.offset[0] * self.scale, child.offset[1] * self.scale, child.offset[2] * self.scale)
                
                # Drawing Joint Sphere
                _RenderJoint(quadObj)

                # Child drawing
                for child in node.childNode:
                    _RenderFigure(child)
            glPopMatrix()

        # drawSkeleton Main Codes
        if (self.root is not None) and (self.motion is not None):
            if self.drawMode == 0:  # rotation mode
                glColor3f(1.000, 0.549, 0.000)
            else:                   # position mode
                glColor3f(0.000, 1.000, 0.000)
            _RenderFigure(self.root)
        pass



    def makeFloorObject(self, height):
        size = 50
        num = 20
        genList = glGenLists(1)
        glNewList(genList, GL_COMPILE)
        glBegin(GL_QUADS)
        for j in range(-int(num/2), int(num/2)+1):
            glNormal(0.0, 1.0, 0.0)
            for i in range(-int(num/2), int(num/2)+1):
                if (i + j) % 2 == 0:
                    glColor3f(0.4, 0.4, 0.4)
                else:
                    glColor3f(0.2, 0.2, 0.2)
                glVertex3i(i*size, height, j*size)
                glVertex3i(i*size, height, j*size+size)
                glVertex3i(i*size+size, height, j*size+size)
                glVertex3i(i*size+size, height, j*size)
        glEnd()
        glEndList()
        return genList


    ## Mouse & Key Events
    def mousePressEvent(self, event:QMouseEvent):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event:QMouseEvent):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.rotateXZ += dx
            self.rotateY  += dy
        if event.buttons() & Qt.RightButton:
            self.translateX += dx
            self.translateY += dy
        self.lastPos = event.pos()
        self.update()

    def wheelEvent(self, event:QWheelEvent):
        angle = event.angleDelta()
        steps = angle.y() / 8.0

        self.camDist -= steps
        if self.camDist < 1:
            self.camDist = 1
        elif self.camDist > 750:
            self.camDist = 750
        self.update()

#    def keyPressEvent(self, event:QKeyEvent):
#        if event.key() == Qt.Key_Escape:
#            self.parent().quit()
#        elif event.key() == Qt.Key_S:
#            self.isPlaying = not self.isPlaying
#        elif event.key() == Qt.Key_F:
#            self.fastRatio *= 2.0
#        elif event.key() == Qt.Key_D:
#            self.fastRatio /= 2.0
#        elif event.key() == Qt.Key_Right:
#            self.frameCount += 1
#        elif event.key() == Qt.Key_Left:
#            self.frameCount -= 1
#        else:
#            None
#        self.update()