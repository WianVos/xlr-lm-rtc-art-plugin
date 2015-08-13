import sys, time, ast, os

import xml.parsers.expat
import xml.etree.ElementTree as ET

import pprint

from java.lang import String
from java.util import Arrays

from lm.DarBuildServer import DarBuildServer

server = DarBuildServer.createServer(darBuildServer)

server.package_dar(appName, appVersion)

server.upload_dar_package(appName, appVersion, xldeployServer)

