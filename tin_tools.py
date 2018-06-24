# encoding: utf-8


import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QAction,QToolBar, QLabel, QMessageBox
from qgis.core import    QgsMapLayer, QgsMapLayerProxyModel, QgsGeometry,   QgsPoint
from qgis.gui import QgsMapLayerComboBox , QgsHighlight
from .plane_calc import PlaneCalc


class TinTools:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar=None
        self.highlight=None
        self.msgBar = iface.messageBar()
        self.plugin_dir = os.path.dirname(__file__)
        print('plugin init en ' + self.plugin_dir)

    def initGui(self):
        self.toolbar=self.iface.addToolBar(u'TIN Tools')
        self.toolbar.setObjectName(u'tintools')
        label=QLabel('Capa TIN:')
        self.toolbar.addWidget(label)
        self.tin_cb=QgsMapLayerComboBox()
        self.tin_cb.setMinimumWidth(200)
        self.tin_cb.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.tin_cb.layerChanged.connect(self.tinLayerChanged)
        self.toolbar.addWidget(self.tin_cb)

#        icon_path = self.plugin_dir +'/icon.png'
#        icon = QIcon(icon_path)
        #'\u0394 \u2B16  \u20E4  \u2350 \u21C8 \u2963 \u2B7F \u2b85 \u23C4  \u25e9'
        self.calc_plane_action = QAction('\u0394', self.iface.mainWindow())
        self.calc_plane_action.triggered.connect(self.calcPlaneEquation)
        self.toolbar.addAction(self.calc_plane_action)

        self.calc_z = QAction('\u21C8', self.iface.mainWindow())
        self.calc_z.triggered.connect(self.calcZ)
        self.toolbar.addAction(self.calc_z)

        self.adjust_to_tin = QAction('\u25e9', self.iface.mainWindow())
        self.adjust_to_tin.triggered.connect(self.adjustToTin)
        self.toolbar.addAction(self.adjust_to_tin)

        self.tinLayerChanged(self.tin_cb.currentLayer())

    def unload(self):
        self.planeCalc=None
        self.setHighlight(None, None)
        self.iface.removeToolBarIcon(self.calc_plane_action)
        self.iface.removeToolBarIcon(self.calc_z)
        self.iface.removeToolBarIcon(self.adjust_to_tin)
        del self.toolbar
        print('unload toolbar5')

    def msg(self, text):
        self.msgBar.pushWarning('TIN tool',text )

    def info(self, text):
        self.msgBar.pushInfo('TIN tool',text )

    def setHighlight(self, ly, vertex):
        if self.highlight:
                self.highlight.hide()
                self.highlight=None
        if vertex:
            color = QColor(255, 0, 100,  255)
            lv=vertex+[vertex[0]]
            g= QgsGeometry.fromPolyline(lv ).convertToType(2)

            print(g.asWkt(3))
            self.highlight = QgsHighlight(self.iface.mapCanvas(), g, ly)
            self.highlight.setColor(color)
            self.highlight.setWidth(5)
            color.setAlpha(50)
            self.highlight.setFillColor(color)
            self.highlight.show()

    def tinLayerChanged(self, layer):
        self.calc_plane_action.setEnabled(layer is not None )
        self.adjust_to_tin.setEnabled(layer is not None )
        self.calc_z.setEnabled(False)
        self.planeCalc=None
        self.setHighlight(None, None)


    def calcPlaneEquation(self):
        ly = self.tin_cb.currentLayer()
        self.setHighlight(None, None)
        if not ly:
            self.msg('No hay ninguna capa seleccionada')
            return
        ver=None
        feat=ly.selectedFeatures()
        geometry_type = ly.geometryType()
        if geometry_type == 0 :# point
            if len(feat)==3:
                ver=[ f.geometry().vertexAt(0) for f in feat]
            else :
                self.msg('Hay que seleccionar 3 puntos')
        elif geometry_type == 2: #polygon
            if len(feat)==1:
                geom=feat[0].geometry()
                ver = list( geom.vertices())
                if len(ver)==4 :
                    ver=ver[:3]
                else:
                    self.msg('El polígono tiene que ser un triángulo' )
            else:
                self.msg('Seleccionar solo un triángulo' )
        else:
            self.msg('seleccionar tres puntos o un triángulo' )
        if ver:
            self.planeCalc=PlaneCalc(ver)
            self.info('Selecciona los elementos de una capa para calcular su Z en el plano')
            self.calc_z.setEnabled(True)
            self.setHighlight(ly, ver)
        else :
            self.planeCalc=None
            self.calc_z.setEnabled(False)

    def calcZ(self):

        layer =self.iface.activeLayer()
        if not layer:
            QMessageBox.warning(None, 'TIN Tools', 'Selecciona elemenos de una capa')
            return
        if not layer.isEditable() :
            QMessageBox.information(None, 'TIN cal', 'La capa no está en modo edición')
            return
        for f in layer.getSelectedFeatures():
            geom = f.geometry()
            n = 0
            v = geom.vertexAt(0)
            while(v != QgsPoint(0,0)):
                z= self.planeCalc.cal_z(v.x(), v.y())
                v.setZ(z)
                geom.moveVertex(v, n)
                n +=1
                v=geom.vertexAt(n)
            layer.changeGeometry(f.id(), geom)


    def adjustToTin(self):
        print('calc tin')
