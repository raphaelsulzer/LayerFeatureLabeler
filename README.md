
# LayerFeatureLabeler
A QGIS plugin (for QGIS 2.xx and 3.xx) to label vector layer features.

## Getting started

1. Download the latest version of the plugin from here: https://github.com/raphaelsulzer/LayerFeatureLabeler/releases

2. Open QGIS and go to _Plugins > Manage and Install Plugins..._

3. In the panel on the left, click on _Install from ZIP_

4. Navigate to the ZIP file you just downloaded and open it

5. The plugin is ready to use and can be opened by clicking on the _hand icon_
![alt text](https://raw.githubusercontent.com/raphaelsulzer/LayerFeatureLabeler/master/icons/select2.png?token=AEDVDXFNOV6XXTJ6CHPMAZC5QAAME)

## How to use the plugin




Simply select a layer, an attribute-field and a label. 
To apply the label to a feature, first click on _Enable Painting_ and paint
features by selecting them on the map. After you are finished with labelling, click _Save_, to save the changes to the layer.


Note: only attribute-fields without numerical values are supported. 
Thus, the layer will not be displayed, if the selected attribute-field includes
features which contain numbers.
