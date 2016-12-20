# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from qgis.core import *
from qgis.utils import iface
from qgis.PyQt import QtGui, QtCore
from mapstory.gui.animation import animationWidgetInstance

def addWfsAnimation(layer, field):
    animateAction = QtGui.QAction(u"Animate layer", iface.legendInterface())
    iface.legendInterface().addLegendLayerAction(animateAction, u"MapStory", u"id1", QgsMapLayer.VectorLayer, False)
    iface.legendInterface().addLegendLayerActionForLayer(animateAction, layer)
    animateAction.triggered.connect(lambda: animateWfsLayer(layer, field))

def addWmsAnimation(layer, instants):
    animateAction = QtGui.QAction(u"Animate layer", iface.legendInterface())
    iface.legendInterface().addLegendLayerAction(animateAction, u"MapStory", u"id1", QgsMapLayer.RasterLayer, False)
    iface.legendInterface().addLegendLayerActionForLayer(animateAction, layer)
    animateAction.triggered.connect(lambda: animateWmsLayer(layer, instants))

animationWidget = None
def animateWfsLayer(layer, field):
    global animationWidget
    if animationWidget is None:
        animationWidget = animationWidgetInstance
        iface.addDockWidget(QtCore.Qt.TopDockWidgetArea, animationWidget)
    animationWidget.setVisible(True)
    animationWidget.setVectorLayer(layer, field)


def animateWmsLayer(layer, timeValues):
    global animationWidget
    if animationWidget is None:
        animationWidget = animationWidgetInstance
        iface.addDockWidget(QtCore.Qt.TopDockWidgetArea, animationWidget)
    animationWidget.setVisible(True)
    animationWidget.setRasterLayer(layer, timeValues)
