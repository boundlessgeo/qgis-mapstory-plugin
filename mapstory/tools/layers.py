try:
    import builtins
except ImportError:
    builtins = __builtin__
from builtins import str
# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from qgis.core import *
from qgis.PyQt import QtCore
import os
from qgis.utils import iface

ALL_TYPES = -1

class WrongLayerNameException(BaseException) :
    pass

class WrongLayerSourceException(BaseException) :
    pass

def resolveLayer(name):
    layers = getAllLayers()
    for layer in layers:
        if layer.name() == name:
            return layer
    raise WrongLayerNameException()

def resolveLayerFromSource(source):
    layers = getAllLayers()
    for layer in layers:
        if os.path.normcase(layer.source()) == os.path.normcase(source):
            return layer
    raise WrongLayerSourceException()


def getVectorLayers(shapetype = -1):
    layers = iface.legendInterface().layers()
    vector = list()
    for layer in layers:
        if layer.type() == layer.VectorLayer:
            if shapetype == ALL_TYPES or layer.geometryType() == shapetype:
                uri = str(layer.source())
                if not uri.lower().endswith("csv") and not uri.lower().endswith("dbf"):
                    vector.append(layer)
    return vector

def getAllLayers():
    return getVectorLayers()

def getGroups():
    groups = {}
    rels = iface.legendInterface().groupLayerRelationship()
    for rel in rels:
        groupName = rel[0]
        if groupName != '':
            groupLayers = rel[1]
            groups[groupName] = [QgsMapLayerRegistry.instance().mapLayer(layerid) for layerid in groupLayers]
    return groups
