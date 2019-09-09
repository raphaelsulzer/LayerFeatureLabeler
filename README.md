
# LayerFeatureLabeler
A QGIS plugin (for QGIS 2.xx and 3.xx) for labeling vector layer features.

## Getting started

1. Download the latest version of the plugin from here: 
https://github.com/raphaelsulzer/LayerFeatureLabeler/releases/download/v1.0/LayerFeatureLabeler.zip

2. Open QGIS and go to _Plugins > Manage and Install Plugins..._

3. In the panel on the left, click on _Install from ZIP_

4. Navigate to the ZIP file you just downloaded and click on _Install Plugin_

5. The plugin is ready to use and can be opened by clicking on its icon
![alt text](https://raw.githubusercontent.com/raphaelsulzer/LayerFeatureLabeler/master/icons/selectForReadMe.png?token=AEDVDXCQAQWVKZVP6VOVWS25QACSU)
or via _Plugins > VectorLayerTool > LayerFeatureLabeler_

## How to use the plugin

![alt text](https://raw.githubusercontent.com/raphaelsulzer/LayerFeatureLabeler/master/GUI.png?token=AEDVDXGNJCMZYZAL4D3XXSC5QAB7I)

Simply select a layer, an attribute-field and a label. 
To apply the label to a feature, first click on _Enable Painting_ and paint
features by selecting them on the map. After you are finished with labelling, click _Save_, to save the changes to the layer.


Note: only attribute-fields without numerical values are supported. 
Thus, the layer will not be displayed, if the selected attribute-field includes
features which contain numbers.
