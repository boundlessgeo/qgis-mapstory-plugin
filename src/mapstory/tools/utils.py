# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os
from PyQt4 import QtCore
from qgis.core import *

def resourceFile(f):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", f)


def loadLayerNoCrsDialog(filename, layername, provider):
    settings = QtCore.QSettings()
    prjSetting = settings.value('/Projections/defaultBehaviour')
    settings.setValue('/Projections/defaultBehaviour', '')
    layer = QgsVectorLayer(filename, layername, provider)
    settings.setValue('/Projections/defaultBehaviour', prjSetting)
    return layer

