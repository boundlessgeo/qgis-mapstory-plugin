# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from qgis.PyQt.QtCore import pyqtSignal, Qt, QThread, QCoreApplication
from qgis.PyQt.QtWidgets import QApplication, QProgressDialog
from qgis.PyQt.QtGui import QCursor


class Thread(QThread):

    finished = pyqtSignal()

    def __init__(self, func):
        QThread.__init__(self, config.iface.mainWindow())
        self.func = func
        self.returnValue = []
        self.exception = None

    def run (self):
        try:
            self.returnValue = self.func()
            self.finished.emit()
        except Exception as e:
            self.exception = e
            self.finished.emit()

_dialog = None

def execute(func, message = None, useThread = False):
    global _dialog
    cursor = QApplication.overrideCursor()
    waitCursor = (cursor is not None and cursor.shape() == Qt.WaitCursor)
    dialogCreated = False
    try:
        QCoreApplication.processEvents()
        if not waitCursor:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        if message is not None and useThread:
            t = Thread(func)
            loop = QEventLoop()
            t.finished.connect(loop.exit, Qt.QueuedConnection)
            if _dialog is None:
                dialogCreated = True
                _dialog = QProgressDialog(message, "Mapstory", 0, 0, config.iface.mainWindow())
                _dialog.setWindowTitle("Mapstory")
                _dialog.setWindowModality(Qt.WindowModal);
                _dialog.setMinimumDuration(1000)
                _dialog.setMaximum(100)
                _dialog.setValue(0)
                _dialog.setMaximum(0)
                _dialog.setCancelButton(None)
            else:
                oldText = _dialog.labelText()
                _dialog.setLabelText(message)
            QApplication.processEvents()
            t.start()
            loop.exec_(flags = QEventLoop.ExcludeUserInputEvents)
            if t.exception is not None:
                raise t.exception
            return t.returnValue
        else:
            return func()
    finally:
        if message is not None and useThread:
            if dialogCreated:
                _dialog.reset()
                _dialog = None
            else:
                _dialog.setLabelText(oldText)
        if not waitCursor:
            QApplication.restoreOverrideCursor()
        QCoreApplication.processEvents()
