# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from qgis.core import *
from qgis.utils import iface
from PyQt4 import QtGui
from mapstory.gui.animation import animationWidgetInstance

def addAnimation(layer, field):
    animateAction = QtGui.QAction(u"Animate layer", iface.legendInterface())
    iface.legendInterface().addLegendLayerAction(animateAction, u"MapStory", u"id1", QgsMapLayer.VectorLayer, False)
    iface.legendInterface().addLegendLayerActionForLayer(animateAction, layer)
    animateAction.triggered.connect(lambda: animateLayer(layer, field))

def animateLayer(layer, field):
    animationWidgetInstance.setVisible(True)
    animationWidgetInstance.setLayer(layer, field)