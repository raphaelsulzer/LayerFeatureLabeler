# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerFeatureLabeler
                                 A QGIS plugin
 Plugin for easy replication of attributes between features
                              -------------------
        begin                : 2019
        copyright            : Raphael Sulzer
        email                : raphaelsulzer@gmx.de
 ***************************************************************************/
"""

import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_LayerFeatureLabeler.ui'))


class attributePainterDialog(QtWidgets.QWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()
    def __init__(self, iface):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)