from PyQt4 import QtGui, QtWebKit, QtCore
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
import os
from requests.exceptions import RequestException

class SearchDialog(QtGui.QDialog):

    def __init__(self):
        super(SearchDialog, self).__init__(iface.mainWindow())
        self.navigator = navigator
        self.initGui()
        self.mapstory = None

    def initGui(self):
        hlayout = QtGui.QHBoxLayout()
        layout = QtGui.QVBoxLayout()
        self.searchBox = QtGui.QLineEdit()
        self.searchBox.returnPressed.connect(self.search)
        self.searchBox.setPlaceholderText("[Enter search string and press enter to search for maps]")
        hlayout.addWidget(self.searchBox)
    
        self.button = QtGui.QToolButton()
        self.button.setText("Search")
        self.button.clicked.connect(self.search)
        self.button.adjustSize()
        self.searchBox.setFixedHeight(self.button.height())
        hlayout.addWidget(self.button)
        layout.addLayout(hlayout)

        w = QtGui.QFrame()
        self.browser = QtWebKit.QWebView()
        w.setStyleSheet("QFrame{border:1px solid rgb(0, 0, 0);}")
        innerlayout = QtGui.QHBoxLayout()
        innerlayout.setSpacing(0)
        innerlayout.setMargin(0)
        innerlayout.addWidget(self.browser)
        w.setLayout(innerlayout)
        layout.addWidget(w)
        self.setLayout(layout)

        self.browser.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.browser.settings().setUserStyleSheetUrl(QtCore.QUrl("file://" + resourceFile("search.css").replace("\\", "/")))
        self.browser.linkClicked.connect(self.linkClicked)
        self.resize(600, 500)
        self.setWindowTitle("Search stories")

    def linkClicked(self, url):
        self.mapstory = url.path()
        self.close()

    def search(self):
        text = self.searchBox.text().strip()
        if text:
            try:
                r = requests.get("http://mapstory.org/api/maps", params={"limit":50, "q": text})
                r.raise_for_status()
                mapstories = r.json()["objects"]
                if mapstories:
                    s = "<div><ul>"
                    for mapstory in mapstories:
                        link = "<a href='%s' class='button'>Open</a>" % (mapstory["id"])
                        s += "<li>%s <h3>%s</h3> %s <br> </li>" % (link, mapstory["title"], mapstory["abstract"])
                    s += "</ul></div>"
                else:
                    s = "<h2>No maps matching your search criteria were found.</h2>"
                self.browser.setHtml(s)
            except RequestException, e:
                    QtGui.QMessageBox.warning(self, "Search",
                        u"There has been a problem performing the search:\n" + unicode(e.args[0]),
                        QtGui.QMessageBox.Ok)
