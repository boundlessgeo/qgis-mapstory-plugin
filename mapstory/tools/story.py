# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
from mapstory.tools.utils import resourceFile
from mapstory.gui.executor import execute
import requests

class Story():

    def __init__(self, storydef):
        self.storydef = storydef
        layers = [lay for lay in self.storydef["map"]["layers"] if "capability" in lay]
        for layer in layers:
            layer["source"] = self.storydef["sources"][layer["source"]]
        self._layers = [StoryLayer(layer) for layer in layers]

    def storyLayers(self):
        return self._layers


    def description(self):
        filename = resourceFile("storydescriptiontemplate.html")
        with open(filename) as f:
            html = f.read()
        html = html.replace("[TITLE]", self.title())
        html = html.replace("[ABSTRACT]", self.storydef["about"]["abstract"])
        html = html.replace("[OWNER]", self.storydef["about"]["owner"])

        return html


        return self.storydef["about"]["abstract"]

    def title(self):
        return self.storydef["about"]["title"]

    @staticmethod
    def storyFromNumberId(storyid):
        url = "http://mapstory.org/maps/%s/data" % storyid
        r = execute(lambda: requests.get(url))
        if r.status_code == 200:
            return Story(r.json())
        else:
            return None

class StoryLayer():

    def __init__(self, layerdef):
        self.layerdef = layerdef

    def title(self):
        return self.layerdef["title"]

    def name(self):
        return self.layerdef["name"]

    def wmsUrl(self):
        url = self.layerdef["source"]["url"]
        if not url.startswith("http://mapstory.org"):
            url = "http://mapstory.org" + url
        return url

    def wfsUrl(self):
        return self.wmsUrl().replace("/wms", "/wfs")

    def crs(self):
        return self.layerdef["capability"]["tileSets"][0]["srs"].keys()[0]

    def description(self):
        filename = resourceFile("layerdescriptiontemplate.html")
        with open(filename) as f:
            html = f.read()
        keywords = "<b>" + "</b> <b>".join(self.layerdef["capability"]["keywords"]) + "</b>"
        html = html.replace("[TITLE]", self.layerdef["title"])
        html = html.replace("[ABSTRACT]", self.layerdef["capability"]["abstract"])
        html = html.replace("[KEYWORDS]", keywords)
        html = html.replace("[WMS]", self.wmsUrl())
        html = html.replace("[WFS]", self.wfsUrl())
        html = html.replace("[NAME]", self.name())
        html = html.replace("[CRS]", self.crs())
        return html

