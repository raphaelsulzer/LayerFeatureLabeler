# -*- coding: utf-8 -*-
"""
/***************************************************************************
 attributePainter
                                 A QGIS plugin
 Plugin for easy replication of attributes between features
                              -------------------
        begin                : 2014-03-11
        copyright            : (C) 2014 by Enrico Ferreguti
        email                : enricofer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
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

from qgis.PyQt.QtGui import QColor, QIcon, QBrush
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
import os
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


        #init the combo boxes
        # self.initLayerCombo()



        #setting dock view buttons behavior
        # self.dock.PickSource.toggled.connect(self.setSourceMapTool)
        # self.dock.ResetSource.clicked.connect(self.resetSource)
        # self.dock.PickDestination.clicked.connect(self.applyToDestination)
        # self.dock.PickDestination.setDisabled(True)
        # self.dock.PickApply.setDisabled(True)
        # self.dock.PickApply.toggled.connect(self.setDestinationMapTool)
        # self.dock.checkBox.clicked.connect(self.selectAllCheckbox)
        # self.dock.tableWidget.setColumnCount(3)
        # self.initTable()
        #setting interface behaviours
        # try:
        #     #QGIS2 API
        #     self.iface.legendInterface().currentLayerChanged.connect(self.checkOnLayerChange)
        # except:
        #     #QGIS3 API
        #     self.iface.currentLayerChanged.connect(self.checkOnLayerChange)
        # self.iface.addDockWidget( Qt.RightDockWidgetArea, self.apdockwidget )
        # self.iface.projectRead.connect(self.resetSource)
        # self.iface.newProjectCreated.connect(self.resetSource)
        # self.canvas.mapToolSet.connect(self.toggleMapTool)

        # here the map tool is choosen
        self.sourceMapTool = IdentifyGeometry(self.canvas,pickMode='active')
        self.destinationMapTool = IdentifyGeometry(self.canvas,pickMode='active')
        # here the feature is selected
        # self.sourceMapTool.geomIdentified.connect(self.setSourceFeature)
        # self.destinationMapTool.geomIdentified.connect(self.setDestinationFeature)



    def run(self):
        # show the dockwidget

        #self.loadProjectFile()
        self.initLayerCombo()


        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)

        self.dockwidget.setWindowTitle('Regional Game Mobiele Stad')
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
            print('no valid QGIS version')


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

        # activeLayer = uf.getCanvasLayerByName(self.canvas, text)
        #activeLayer = uf.getLegendLayerByName(self.canvas, text)



        self.iface.setActiveLayer(self.activeLayer)
        self.initAttributeCombo(self.activeLayer)



    def attributeComboChanged(self):

        activeAttribute = str(self.dock.attributeCombo.currentText())
        self.activeAttributeID = uf.getFieldIndex(self.activeLayer, activeAttribute)


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

        #QGIS3
        #QgsProject.instance().addMapLayer(your_Qgs_whaterver_Layer)

        self.dock.layerCombo.clear()
        self.dock.layerCombo.addItems(layerList)


        #set the currently selected layer (for the first time)
        self.layerComboChanged()


        self.dock.layerCombo.currentIndexChanged.connect(self.layerComboChanged)



    def initAttributeCombo(self, layer):



        #QGIS2
        #fields = layer.pendingFields()
        # if layer:
        #     fields = layer.fields()
        # # if version == 2:
        # #     fields = layer.pendingFields()
        # # elif version == 3:
        # #     fields = layer.fields()
        # # else:
        # #     print('unknown QGIS version')
        #     fieldList = [field.name() for field in fields]
        # #QGIS3
        # #QgsProject.instance().addMapLayer(your_Qgs_whaterver_Layer)
        #
        #     self.dock.attributeCombo.clear()
        #     self.dock.attributeCombo.addItems(fieldList)

        stringFieldNames = []
        stringFieldIDs = []
        fields = layer.fields()
        for field in fields:
            if field.typeName() == 'String':
                stringFieldNames.append(field.name())
                stringFieldIDs.append(fields.indexFromName(field.name()))


        #fieldList = uf.getFieldNames(layer)
        self.dock.attributeCombo.clear()
        self.dock.attributeCombo.addItems(stringFieldNames)

        #set the currently selected attribute (for the first time)
        self.attributeComboChanged()
        #init label combo
        self.initLabelCombo(layer, stringFieldIDs)






    def initLabelCombo(self, layer, ids):

        # QGIS2
        # fields = layer.pendingFields()
        # if layer:
        #
        #
        #
        # fields = layer.fields()
        # # if version == 2:
        # #     fields = layer.pendingFields()
        # # elif version == 3:
        # #     fields = layer.fields()
        # # else:
        # #     print('unknown QGIS version')
        # fieldList = [field.name() for field in fields]
        # # QGIS3
        # # QgsProject.instance().addMapLayer(your_Qgs_whaterver_Layer)
        #
        # self.dock.labelCombo.clear()
        # self.dock.labelCombo.addItems(fieldList)
        # ids = uf.getAllFeatureIds(layer)
        values = []
        for item in ids:
            uvals = layer.uniqueValues(item)
            # I don't want a list of lists but a flat list, that's why I'm doing this
            for val in uvals:
                if type(val) is unicode:
                    if uf.isNumeric(val) == False:
                        values.append(val)
        #uniqueValueList = set(values)
        #print(values)
        self.dock.labelCombo.clear()
        self.dock.labelCombo.addItems(values)

        #set the currently selected label (for the first time)
        self.labelComboChanged()


    def startPainting(self):

        # deactivate painting
        if self.painting == True:
            self.painting = False
            self.activeLayer.selectionChanged.disconnect(self.applyLabel)
            self.dock.paintingButton.setChecked(False)
            self.iface.actionPan().trigger()
        #activate painting
        else:
            self.painting = True
            self.activeLayer.selectionChanged.connect(self.applyLabel)
            self.dock.paintingButton.setChecked(True)
            self.iface.actionSelect().trigger()


        #self.dock.paintingButton.setChecked(True)

        self.iface.mainWindow().findChild(QAction, 'mActionToggleEditing').trigger()


        # self.iface.mainWindow().findChild(QAction, 'mActionToggleEditing').activate(True)
        # self.iface.actionSelect().activate(True)


    def applyLabel(self):

        features = self.activeLayer.selectedFeatures()

        for feature in features:
            self.activeLayer.changeAttributeValue(feature.id(), self.activeAttributeID, self.activeLabel)
            # self.apply_style(feature)
            self.apply_style(feature)

    def setComboField(self,content,type,layer):
        '''
        returns a qcombobox loaded with compatible field names (depending on selected layer)
        '''
        combo = QComboBox();
        fieldNames = self.scanLayerFieldsNames(layer)
        fieldTypes = self.scanLayerFieldsTypes(layer)
        choices = []
        for n in range(0,len(fieldTypes)):
            if fieldTypes[n] == type:
                choices.append(fieldNames[n])
        combo.addItems(choices)
        if content in choices:
            combo.setCurrentIndex(choices.index(content))
        else:
            combo.addItem(content)
            combo.setCurrentIndex(combo.count()-1)
        combo.activated.connect(lambda: self.highlightCompatibleFields(LayerChange=None))
        return combo


    def getFieldsIterator(self,layer):
        try:
            return layer.pendingFields
        except:
            return layer.fields
                

    def scanLayerFieldsNames(self,layer):
        '''
        returns fields names as strings list
        '''
        if layer:
            return [field.name() for field in self.getFieldsIterator(layer)()]
        else:
            return []

    def scanLayerFieldsTypes(self,layer):
        '''
        returns fields types as qvariant list
        '''
        if layer:
            return [field.type() for field in self.getFieldsIterator(layer)()]
        else:
            return []


    def highLightCellOverride(obj,item):
        '''
        landing method on cell value change
        '''
        if item.column() == 2:
            item.setBackground(QBrush(QColor(183,213,225)))
            #item.setForeground (QBrush(QColor(255,0,0)))


    def checkEditable(self):
        '''
        method to enable or disable apply to destination button
        '''
        if self.layerHighlighted:
            self.highlightCompatibleFields()
            if self.layerHighlighted.isEditable() and self.sourceFeat:
                self.dock.PickDestination.setEnabled(True)
                self.dock.PickApply.setEnabled(True)
            else:
                self.dock.PickDestination.setDisabled(True)
                self.dock.PickApply.setDisabled(True)


    def applyToDestination(self):
        '''
        method to apply selected fields to selected destination features
        '''
        if self.canvas.currentLayer().selectedFeatures()!=[]:
            self.sourceAttributes = self.getSourceAttrs()
            #apply source attribute values to selected destination features
            for f in self.canvas.currentLayer().selectedFeatures():
                self.applyToFeature(f,self.sourceAttributes)
            self.iface.activeLayer().removeSelection() 
            self.canvas.currentLayer().triggerRepaint()
        else:
            pass
            #print ("nothing selected")



    def applyToFeature(self,feature,sourceSet):
        '''
        method to apply destination fields cyclying between feature fields
        '''
        #print (sourceSet.items())
        for attrId,attrValue in sourceSet.items():
            try:
                feature[attrValue[0]]=attrValue[1]
                self.canvas.currentLayer().updateFeature(feature)
                self.canvas.currentLayer().triggerRepaint()
            except Exception as e:
                print ('Exception in applyToFeature',e)
            self.highlight(feature.geometry())

    def highlight(self,feature):
        def processEvents():
            try:
                qApp.processEvents()
            except:
                QApplication.processEvents()
                
        highlight = QgsRubberBand(self.canvas, feature.geometry().type())
        highlight.setColor(QColor("#f00"))
        # highlight.setFillColor(QColor("#36AF6C"))
        highlight.setFillColor(QColor("#f00"))
        highlight.setWidth(2)
        highlight.setToGeometry(feature.geometry(),self.canvas.currentLayer())
        processEvents()
        sleep(.1)
        highlight.hide()
        processEvents()
        sleep(.1)
        highlight.show()
        processEvents()
        sleep(.1)
        highlight.reset()
        processEvents()
        


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




    def apply_style(self,feature):
        # Get currently selected layer in combo box
        # current_layer = self.dlg.comboBox_layer.currentText()
        # layer = QgsMapLayerRegistry.instance().mapLayersByName(str(current_layer))[0]
        layer = self.canvas.currentLayer()

        print("style applied")

        # Define style parameters: value, colour, legend
        # TODO: get distinct list of possible attribute values and draw the color from a random palette
        # have to apply this from the very start of loading the layer in the best case, e.g. check if it has a style, and if not, make one
        # the QgsCategorizedSymbolRenderer(column, categories) https://qgis.org/api/classQgsCategorizedSymbolRenderer.html
        # also has a clone() method, with wich I could save the original style
        land_class = {
            'FLEVOLAND': ('#f00', 'FLEVOLAND'),
            'ZEELAND': ('#0f0', 'ZEELAND')
        }

        # Define a list for categories
        categories = []
        # Define symbology depending on layer type, set the relevant style parameters
        for classes, (color, label) in land_class.items():
            # symbol = QgsRubberBand(self.canvas, feature.geometry().type())
            symbol = QgsSymbol.defaultSymbol(feature.geometry().type())
            symbol.setColor(QColor(color))
            category = QgsRendererCategory(classes, symbol, label)
            categories.append(category)

        # Column/field name to be used to read values from
        column = "NAM"
        # Apply the style rendering
        renderer = QgsCategorizedSymbolRenderer(column, categories)
        layer.setRenderer(renderer)
        # Refresh the layer
        layer.triggerRepaint()
