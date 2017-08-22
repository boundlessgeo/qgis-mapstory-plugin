# -*- coding: utf-8 -*-

import sys
import os
import site

site.addsitedir(os.path.abspath(os.path.dirname(__file__) + '/extlibs'))

def classFactory(iface):
    from mapstory.plugin import MapStoryPlugin
    return MapStoryPlugin(iface)
