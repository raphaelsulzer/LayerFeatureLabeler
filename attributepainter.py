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

# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import Qt
# if False:
#     from PyQt4.QtCore import *
#     from PyQt4.QtGui import *
#     from PyQt4 import uic
#     from qgis.core import *
#     from qgis.utils import *
#     from qgis.gui import *
#     print('False')


try:
    #QGIS3
    from qgis.core import Qgis
except ImportError:
    #QGIS2
    from qgis.core import QGis as Qgis

from qgis.PyQt.QtGui import QColor, QIcon, QBrush, QImage, QPainter, QPixmap
from qgis.PyQt.QtWidgets import QComboBox, QDockWidget, QAction, QTableWidgetItem, QApplication, QHeaderView
from qgis.PyQt import uic
from qgis.core import *
from qgis.gui import QgsRubberBand



#version
version = int(str(Qgis.QGIS_VERSION[0]))


# Import the code for the dialog
from .attributepainterdialog import attributePainterDialog
from .identifygeometry import IdentifyGeometry
from . import utility_functions as uf


# Initialize Qt resources from file resources.py
import sip
import os, random
from time import sleep


class AttributePainterClass:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # Source feature rubberband definition
        colorSource = QColor(250,0,0,200)
        self.sourceEvid = QgsRubberBand(self.canvas)
        self.sourceEvid.setColor(colorSource)
        self.sourceEvid.setWidth(3)


        self.dock = attributePainterDialog(self.iface)


        #connect signals
        self.dock.layerCombo.currentIndexChanged.connect(self.layerComboChanged)
        self.dock.attributeCombo.currentIndexChanged.connect(self.attributeComboChanged)
        self.dock.labelCombo.currentIndexChanged.connect(self.labelComboChanged)


        self.dock.paintingButton.clicked.connect(self.startPainting)
        self.dock.saveButton.clicked.connect(self.startPainting)


        #plugin state
        self.pluginIsActive = False
        #painting state
        self.painting = False





    def initGui(self):
        # Create action that will show plugin widget
        self.action = QAction(
            QIcon(os.path.join(self.plugin_dir,"icons/select2.png")),
            # the following does not seem to work anymore, maybe since PyQt5?!
            #QIcon(':/plugins/LayerFeatureLabeler/icons/select.png'),
            u"LayerFeatureLabeler", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&VectorLayerTool", self.action)

        #creating dock view intance
        # self.dock = attributePainterDialog(self.iface)
        self.dockwidget = QDockWidget("Layer Feature Labeler" , self.iface.mainWindow() )
        self.dockwidget.setObjectName("Layer Feature Labeler")
        self.dockwidget.setWidget(self.dock)
        self.layerHighlighted = None
        self.sourceFeat = None

        # here the map tool is choosen
        self.sourceMapTool = IdentifyGeometry(self.canvas,pickMode='active')
        self.destinationMapTool = IdentifyGeometry(self.canvas,pickMode='active')



    def run(self):
        # show the dockwidget

        # self.loadProjectFile()
        self.initLayerCombo()


        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)

        self.dockwidget.setWindowTitle('Layer Feature Labeler')
        self.dockwidget.show()

        self.pluginIsActive = True

        #QgsMapLayerRegistry.instance().legendLayersAdded.connect(self.initLayerCombo)

        #QGIS2:
        if version == 2:
            QgsMapLayerRegistry.instance().layersRemoved.connect(self.initLayerCombo)
            QgsMapLayerRegistry.instance().layersAdded.connect(self.initLayerCombo)
        elif version == 3:
            QgsProject.instance().layersRemoved.connect(self.initLayerCombo)
            QgsProject.instance().layersAdded.connect(self.initLayerCombo)
        else:
            print('only QGIS 2 and QGIS 3 is supported')

        self.dock.closingPlugin.connect(self.onClosePlugin)

    def onClosePlugin(self):
        print("closing plugin")

        # deactivate painting
        if self.painting == True:
            self.iface.mainWindow().findChild(QAction, 'mActionToggleEditing').trigger()
            self.painting == False

        self.dock.closingPlugin.disconnect(self.onClosePlugin)






    def loadProjectFile(self):

        # open the QGIS project file
        scenario_open = False
        scenario_file = os.path.join(os.path.dirname(__file__),'data', 'project.qgs')

        # check if file exists
        if os.path.isfile(scenario_file):
            self.iface.addProject(scenario_file)
            scenario_open = True
        else:
            last_dir = uf.getLastDir("PlanningToolClass")
            new_file = QtWidgets.QFileDialog.getOpenFileName(self, "", last_dir, "(*.qgs)")
            if new_file:
                self.iface.addProject(unicode(new_file))
                scenario_open = True


    def layerComboChanged(self):

        if self.painting == True:
            self.startPainting() # which in fact means quit painting, when the layer is changed

        text = str(self.dock.layerCombo.currentText())

        try:    #this fails if plugin is opened without a layer
            if version == 2:
                self.activeLayer = QgsMapLayerRegistry.instance().mapLayersByName(text)[0]      # 0 element because it returns a list
            elif version == 3:
                self.activeLayer = QgsProject.instance().mapLayersByName(text)[0]
        except:
            return

        self.iface.setActiveLayer(self.activeLayer)
        # set the columns (=attributes) of the current layer to the attribute combo box
        self.initAttributeCombo(self.activeLayer)


    def attributeComboChanged(self):
        activeAttribute = str(self.dock.attributeCombo.currentText())
        self.activeAttributeID = uf.getFieldIndex(self.activeLayer, activeAttribute)
        self.applyStyle()


    def labelComboChanged(self):
        self.activeLabel = str(self.dock.labelCombo.currentText())


    def initLayerCombo(self):

        try:
            self.dock.layerCombo.currentIndexChanged.disconnect(self.layerComboChanged)
        except:
            pass


        layerList = []
        #QGIS2
        if version == 2:
            layerList = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
        elif version == 3:
            layerList = [layer.name() for layer in list(QgsProject.instance().mapLayers().values())]
        else:
            print('unkown QGIS version')

        self.dock.layerCombo.clear()
        layerList.insert(0,'')
        self.dock.layerCombo.addItems(layerList)

        #set the currently selected layer (for the first time)
        self.layerComboChanged()

        self.dock.layerCombo.currentIndexChanged.connect(self.layerComboChanged)



    def initAttributeCombo(self, layer):


        stringFieldNames = []
        stringFieldIDs = []
        fields = layer.fields()
        for field in fields:
            if field.typeName() == 'String':
                stringFieldNames.append(field.name())
                stringFieldIDs.append(fields.indexFromName(field.name()))

        # init label combo
        # do this first so the self.valColTuple is initialised
        self.initLabelCombo(layer, stringFieldIDs)

        #fieldList = uf.getFieldNames(layer)
        self.dock.attributeCombo.clear()
        stringFieldNames.insert(0,'')
        self.dock.attributeCombo.addItems(stringFieldNames)

        #set the currently selected attribute (for the first time)
        self.attributeComboChanged()


    def initLabelCombo(self, layer, ids):

        values = []
        for item in ids:
            uvals = layer.uniqueValues(item)
            # I don't want a list of lists but a flat list, that's why I'm doing this
            for val in uvals:
                if type(val) is unicode:
                    if uf.isNumeric(val) == False:
                        if any(char.isdigit() for char in val) == False:
                            values.append(val)
        values = sorted(set(values))

        ## initialize color list
        self.initColors(values)

        self.dock.labelCombo.clear()
        # self.dock.labelCombo.addItems(values)

        for i,item in enumerate(self.valColTuple):
            pixmap = QPixmap(16, 16)
            pixmap.fill(item[1])
            # self.dock.labelCombo.addItem(item[0])
            self.dock.labelCombo.insertItem(i,QIcon(pixmap),item[0])

        #set the currently selected label (for the first time)
        self.labelComboChanged()




    #### EDITING ####
    def startPainting(self):

        # deactivate painting
        if self.painting == True:
            self.painting = False
            self.activeLayer.selectionChanged.disconnect(self.applyLabel)
            self.dock.paintingButton.setChecked(False)
            self.iface.actionPan().trigger()
            layer = self.canvas.currentLayer()
            layer.removeSelection()
        #activate painting
        else:
            self.painting = True
            self.activeLayer.selectionChanged.connect(self.applyLabel)
            self.dock.paintingButton.setChecked(True)
            self.iface.actionSelect().trigger()

        self.iface.mainWindow().findChild(QAction, 'mActionToggleEditing').trigger()

        #unfortunately this does not work:
        # TODO: actually I can use layer.startEditing in the if, and layer.commitChanges in the else statement
        # self.iface.mainWindow().findChild(QAction, 'mActionToggleEditing').activate(True)
        # self.iface.actionSelect().activate(True)


    def applyLabel(self):

        features = self.activeLayer.selectedFeatures()

        for feature in features:
            self.activeLayer.changeAttributeValue(feature.id(), self.activeAttributeID, self.activeLabel)
            # self.apply_style(feature)
            # self.apply_style(feature)


    #### STYLING ####
    def initColors(self, values):

        self.valColTuple = []
        for i,val in enumerate(values):
            r = random.randrange(0,256,1)
            g = random.randrange(0,256,1)
            b = random.randrange(0,256,1)
            self.valColTuple.append((val, QColor(r,g,b)))


    def applyStyle(self):

        #get currently active layer
        layer = self.activeLayer

        #for every possible value (=all the non-numeric values in the layer), set a color from the valColTuple
        categories = []
        for i,attribute in enumerate(self.valColTuple):
            if version == 2:
                symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
                symbol.setColor(attribute[1])
                category = QgsRendererCategoryV2(attribute[0], symbol, attribute[0])
            elif version == 3:
                symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                # symbol = QgsSymbol.defaultSymbol(feature.geometry().type())
                symbol.setColor(attribute[1])
                category = QgsRendererCategory(attribute[0], symbol, attribute[0])
            else:
                print('only QGIS 2 and QGIS 3 is supported')
            categories.append(category)

        # Apply the colors to the currently selected column
        fieldName = self.dock.attributeCombo.currentText()
        if version == 2:
            renderer = QgsCategorizedSymbolRendererV2(fieldName, categories)
            layer.setRendererV2(renderer)
        elif version == 3:
            renderer = QgsCategorizedSymbolRenderer(fieldName, categories)
            layer.setRenderer(renderer)
        else:
            print('only QGIS 2 and QGIS 3 is supported')

        # Refresh the layer
        layer.triggerRepaint()




    def unload(self):
        '''
        Remove the plugin widget and clear source feature highlight
        '''
        if self.sourceFeat:
            self.sourceEvid.reset()
        self.iface.removeToolBarIcon(self.action)
        self.iface.removeDockWidget(self.dockwidget)
        # self.canvas.mapToolSet.disconnect(self.toggleMapTool)
        # try:
        #     self.iface.legendInterface().currentLayerChanged.disconnect(self.checkOnLayerChange)
        # except:
        #     self.iface.currentLayerChanged.disconnect(self.checkOnLayerChange)
        # self.iface.projectRead.disconnect(self.resetSource)

        if self.pluginIsActive:
            self.onClosePlugin()



