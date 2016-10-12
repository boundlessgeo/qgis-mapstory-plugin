import os

from qgis.core import QgsApplication

from PyQt4.QtCore import Qt, QCoreApplication, QUrl
from PyQt4.QtGui import QAction, QIcon, QDesktopServices, QMessageBox

from mapstory.gui.explorer import explorerInstance
from mapstory.gui.animation import animationWidgetInstance

pluginPath = os.path.dirname(__file__)


class MapStoryPlugin:

    def __init__(self, iface):
        self.iface = iface
        try:
            from mapstory.tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, "MapStory")
        except:
            pass

    def unload(self):
        try: #to avoid some random errors that seem to appear sometimes
            explorerInstance.setVisible(False)
            del explorerInstance
            animationWidgetInstance.setVisible(False)
            del animationWidgetInstance
        except:
            pass

        try:
            from mapstory.tests import testerplugin
            from qgistester.tests import removeTestModule
            removeTestModule(testerplugin, "MapStory")
        except:
            pass

    def initGui(self):
        icon = QIcon(os.path.dirname(__file__) + "/ui/resources/mapstory.png")
        self.explorerAction = explorerInstance.toggleViewAction()
        self.explorerAction.setIcon(icon)
        self.explorerAction.setText("MapStory explorer")
        self.iface.addPluginToMenu(u"&MapStory", self.explorerAction)

        self.actionHelp = QAction(
            self.tr('Help'), self.iface.mainWindow())
        self.actionHelp.setIcon(
            QgsApplication.getThemeIcon('/mActionHelpContents.svg'))
        self.actionHelp.setWhatsThis(
            self.tr('Boundless Connect documentation'))
        self.actionHelp.setObjectName('actionMapStoryHelp')
        self.actionHelp.triggered.connect(self.showHelp)
        self.iface.addPluginToMenu(u"&MapStory", self.actionHelp)

        self.iface.addDockWidget(Qt.RightDockWidgetArea, explorerInstance)

    def showHelp(self):
        if not QDesktopServices.openUrl(
                QUrl('file://{}'.format(os.path.join(pluginPath, 'docs', 'html', 'index.html')))):
            QMessageBox.warning(None,
                                self.tr('Error'),
                                self.tr('Can not open help URL in browser'))

    def tr(self, text):
        return QCoreApplication.translate('Boundless Connect', text)
