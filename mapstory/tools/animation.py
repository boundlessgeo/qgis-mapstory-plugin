# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from qgis.core import *
from qgis.utils import iface
from PyQt4 import QtGui, QtCore
from mapstory.gui.animation import animationWidgetInstance

def addAnimation(layer, field):
    animateAction = QtGui.QAction(u"Animate layer", iface.legendInterface())
    iface.legendInterface().addLegendLayerAction(animateAction, u"MapStory", u"id1", QgsMapLayer.VectorLayer, False)
    iface.legendInterface().addLegendLayerActionForLayer(animateAction, layer)
    animateAction.triggered.connect(lambda: animateLayer(layer, field))

animationWidget = None
def animateLayer(layer, field):
    global animationWidget
    if animationWidget is None:
        animationWidget = animationWidgetInstance
        iface.addDockWidget(QtCore.Qt.TopDockWidgetArea, animationWidget)
    animationWidget.setVisible(True)
    animationWidget.setLayer(layer, field)