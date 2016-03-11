# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os
from PyQt4 import QtGui, QtCore, uic
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
from dateutil import parser
from collections import defaultdict, OrderedDict
import time
import datetime


pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'mapstoryanimation.ui'))

def icon(f):
    return QtGui.QIcon(os.path.join(os.path.dirname(__file__), os.pardir, "resources", f))

backIcon = icon("back.png")
forwardIcon = icon("forward.png")
playIcon = icon("play.png")

INSTANT, CUMULATIVE = 0, 1

class AnimationWidget(BASE, WIDGET):

    def __init__(self):
        super(AnimationWidget, self).__init__(None)

        self.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)

        self.layer = None
        self.field = None
        self.animating = False
        self.mode = INSTANT

        self.setupUi(self)

        self.buttonBack.setIcon(backIcon)
        self.buttonForward.setIcon(forwardIcon)
        self.buttonPlay.setIcon(playIcon)

        self.buttonBack.clicked.connect(self.previousStep)
        self.buttonForward.clicked.connect(self.nextStep)
        self.buttonPlay.clicked.connect(self.toggleAnimation)

        self.closeButton.clicked.connect(self.closeClicked)
        self.timeSlider.valueChanged.connect(self.valueChanged)
        self.comboMode.currentIndexChanged.connect(self.modeChanged)

    def modeChanged(self):
        self.mode = self.comboMode.currentIndex()
        self.valueChanged(self.timeSlider.value())

    def toggleAnimation(self):
        self.animating = not self.animating
        self.animate()

    def animate(self):
        if self.animating:
            if self.nextStep():
                QtCore.QTimer.singleShot(500, self.animate)
            else:
                self.buttonPlay.setChecked(False)
                self.animating = False


    def nextStep(self):
        newValue = self.timeSlider.value() + self.step
        if newValue < self.timeSlider.maximum():
            self.timeSlider.setValue(newValue)
            return True
        else:
            return False

    def previousStep(self):
        newValue = self.timeSlider.value() - self.step
        if newValue > self.timeSlider.minimum():
            self.timeSlider.setValue(newValue)

    def valueChanged(self, val):
        idx = min(next(i for i,v in enumerate(self.times.keys()) if v >= val), len(self.times) -1)

        fids = self.times.values()[idx]
        if self.mode == CUMULATIVE:
            for i in range(idx):
                fids.extend(self.times.values()[i])

        subsetString = "$id IN (%s)" % ",".join(fids)
        self.layer.setSubsetString(subsetString)
        iface.mapCanvas().refresh()
        dt = datetime.datetime(1, 1, 1) + datetime.timedelta(milliseconds=val * 3600 * 1000)
        self.labelCurrent.setText(unicode(dt.replace(microsecond=0)))


    def setLayer(self, layer, fieldname):
        self.layer = layer
        self.fieldname = fieldname
        times = defaultdict(list)
        for feat in layer.getFeatures():
            feattime = feat[self.fieldname]
            dt = parser.parse(feattime)
            h = (dt - datetime.datetime(1,1,1)).total_seconds() / 3600
            times[int(h)].append(str(feat.id()))

        self.times = OrderedDict(sorted(times.items()))

        self.timeSlider.blockSignals(True)
        self.timeSlider.setMinimum(self.times.keys()[0])
        self.timeSlider.setMaximum(self.times.keys()[-1])
        self.timeSlider.blockSignals(False)
        self.timeSlider.setValue(self.times.keys()[0])
        self.valueChanged(self.times.keys()[0])
        self.step = int((self.timeSlider.maximum() - self.timeSlider.minimum()) / 50)


    def closeClicked(self):
        self.layer.setSubsetString("")
        iface.mapCanvas().refresh()
        self.setVisible(False)

animationWidgetInstance = AnimationWidget()



