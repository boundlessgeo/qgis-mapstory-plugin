from builtins import str
from builtins import next
from builtins import range
# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os
from dateutil import parser
from collections import defaultdict, OrderedDict
import time
import datetime

from PyQt import uic
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsVectorLayer
from qgis.utils import iface

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'mapstoryanimation.ui'))

def icon(f):
    return QIcon(os.path.join(os.path.dirname(__file__), os.pardir, "resources", f))

backIcon = icon("back.png")
forwardIcon = icon("forward.png")
playIcon = icon("play.png")

INSTANT, CUMULATIVE = 0, 1

ZERO = datetime.timedelta(0)

class AnimationWidget(BASE, WIDGET):

    IGNORE_PREFIX = "IgnoreGetFeatureInfoUrl=1&IgnoreGetMapUrl=1&"

    class UTC(datetime.tzinfo):
        def utcoffset(self, dt):
            return ZERO
        def tzname(self, dt):
            return "UTC"
        def dst(self, dt):
            return ZERO

    utc = UTC()

    def __init__(self):
        super(AnimationWidget, self).__init__(None)

        self.setAllowedAreas(Qt.TopDockWidgetArea)

        self.layer = None
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
                QTimer.singleShot(500, self.animate)
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
        if isinstance(self.layer, QgsVectorLayer):
            idx = min(next(i for i,v in enumerate(self.times.keys()) if v >= val), len(self.times) - 1)

            fids = list(self.times.values())[idx]
            if self.mode == CUMULATIVE:
                for i in range(idx):
                    fids.extend(list(self.times.values())[i])

            subsetString = "$id IN (%s)" % ",".join(fids)
            self.layer.setSubsetString(subsetString)
            iface.mapCanvas().refresh()
            dt = datetime.datetime(1, 1, 1) + datetime.timedelta(milliseconds=val * 3600 * 1000)
            self.labelCurrent.setText(str(dt.replace(microsecond=0)))
        else:
            idx = min(next(i for i,v in enumerate(self.times.keys()) if v >= val), len(self.times) - 1)
            t = list(self.times.values())[idx]
            self.layer.dataProvider().setDataSourceUri(self.IGNORE_PREFIX +
                                                       self.originalUri + "&TIME=%s" % t)
            iface.mapCanvas().refresh()


    def setVectorLayer(self, layer, fieldname):
        self.layer = layer
        self.times = defaultdict(list)
        for feat in layer.getFeatures():
            feattime = feat[fieldname]
            dt = parser.parse(feattime)
            h = (dt - datetime.datetime(1,1,1)).total_seconds() / 3600
            self.times[int(h)].append(str(feat.id()))
        self.comboMode.setVisible(True)
        self.configForTimes()

    def setRasterLayer(self, layer, timeValues):
        self.layer = layer
        self.originalUri = self.layer.dataProvider().dataSourceUri()
        self.times = {}
        for time in timeValues:
            dt = parser.parse(time)
            h = (dt - datetime.datetime(1,1,1, tzinfo=self.utc)).total_seconds() / 3600
            self.times[int(h)] = time
        self.comboMode.setVisible(False)
        self.configForTimes()

    def configForTimes(self):
        self.times = OrderedDict(sorted(self.times.items()))
        self.timeSlider.blockSignals(True)
        self.timeSlider.setMinimum(list(self.times.keys())[0])
        self.timeSlider.setMaximum(list(self.times.keys())[-1])
        self.timeSlider.blockSignals(False)
        self.timeSlider.setValue(list(self.times.keys())[0])
        self.valueChanged(list(self.times.keys())[0])
        self.step = int((self.timeSlider.maximum() - self.timeSlider.minimum()) / 50)


    def closeClicked(self):
        self.animating = False
        if isinstance(self.layer, QgsVectorLayer):
            self.layer.setSubsetString("")
        else:
            self.layer.dataProvider().setDataSourceUri(self.originalUri)
        iface.mapCanvas().refresh()
        self.setVisible(False)

animationWidgetInstance = AnimationWidget()



