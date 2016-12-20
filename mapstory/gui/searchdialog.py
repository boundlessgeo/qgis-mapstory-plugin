try:
    import builtins
except ImportError:
    builtins = __builtin__
from builtins import str
import os

import requests
from requests.exceptions import RequestException

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLineEdit, QToolButton, QFrame, QMessageBox
from qgis.PyQt.QtWebKitWidgets import QWebView, QWebPage

from qgis.utils import iface

from mapstory.tools.utils import resourceFile
from mapstory.gui.executor import execute

class SearchDialog(QDialog):

    def __init__(self):
        super(SearchDialog, self).__init__(iface.mainWindow())
        self.initGui()
        self.mapstory = None

    def initGui(self):
        hlayout = QHBoxLayout()
        layout = QVBoxLayout()
        self.searchBox = QLineEdit()
        self.searchBox.returnPressed.connect(self.search)
        self.searchBox.setPlaceholderText("[Enter search string and press enter to search for maps]")
        hlayout.addWidget(self.searchBox)

        self.button = QToolButton()
        self.button.setText("Search")
        self.button.clicked.connect(self.search)
        self.button.adjustSize()
        self.searchBox.setFixedHeight(self.button.height())
        hlayout.addWidget(self.button)
        layout.addLayout(hlayout)

        w = QFrame()
        self.browser = QWebView()
        w.setStyleSheet("QFrame{border:1px solid rgb(0, 0, 0);}")
        innerlayout = QHBoxLayout()
        innerlayout.setSpacing(0)
        innerlayout.setMargin(0)
        innerlayout.addWidget(self.browser)
        w.setLayout(innerlayout)
        layout.addWidget(w)
        self.setLayout(layout)

        self.browser.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.browser.settings().setUserStyleSheetUrl(QUrl("file://" + resourceFile("search.css").replace("\\", "/")))
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
                r = execute(lambda: requests.get("http://mapstory.org/api/base/search", params={"type__in":"map", "limit":50, "q": text}))
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
            except RequestException as e:
                    QMessageBox.warning(self, "Search",
                        u"There has been a problem performing the search:\n" + str(e.args[0]),
                        QMessageBox.Ok)
