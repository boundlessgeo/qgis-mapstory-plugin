import os
from qgis.core import *
from PyQt4 import QtGui, QtCore
from mapstory.gui.explorer import explorerInstance
from mapstory.gui.animation import animationWidgetInstance


class MapStoryPlugin:

    def __init__(self, iface):
        self.iface = iface
        try:
            from mapstory.tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, "MapStory")
        except:
            pass
        iface.initializationCompleted.connect(lambda: animationWidgetInstance.setVisible(False))

    def unload(self):
        explorerInstance.setVisible(False)
        del explorerInstance
        animationWidgetInstance.setVisible(False)
        del self.animationWidgetInstance

    def initGui(self):
        icon = QtGui.QIcon(os.path.dirname(__file__) + "/ui/resources/mapstory.png")
        self.explorerAction = explorerInstance.toggleViewAction()
        self.explorerAction.setIcon(icon)
        self.explorerAction.setText("MapStory explorer")
        self.iface.addPluginToMenu(u"&MapStory", self.explorerAction)

        self.iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, explorerInstance)
        self.iface.addDockWidget(QtCore.Qt.TopDockWidgetArea, animationWidgetInstance)








