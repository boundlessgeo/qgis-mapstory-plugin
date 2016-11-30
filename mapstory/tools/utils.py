# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os
from PyQt import QtCore, QtGui
from qgis.core import *
from qgis.gui    import *
import sip
from qgis.utils import iface

def resourceFile(f):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", f)


def loadLayerNoCrsDialog(filename, layername, provider):
    settings = QtCore.QSettings()
    prjSetting = settings.value('/Projections/defaultBehaviour')
    settings.setValue('/Projections/defaultBehaviour', '')
    layer = QgsVectorLayer(filename, layername, provider)
    settings.setValue('/Projections/defaultBehaviour', prjSetting)
    return layer


progress = None

def closeProgressBar():
    global progress
    if progress is not None:
        iface.messageBar().clearWidgets()
        progress = None

def setProgress(value):
    global progress
    if progress is not None and not sip.isdeleted(progress):
        progress.setValue(value)

def startProgressBar(maxValue, msg = ""):
    global progress
    progressMessageBar = iface.messageBar().createMessage(msg)
    progress = QtGui.QProgressBar()
    progress.setMaximum(maxValue)
    progress.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, QgsMessageBar.INFO)
