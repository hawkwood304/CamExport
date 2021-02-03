from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
from maya.mel import eval
import maya.cmds as cm
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import os


# noinspection PyAttributeOutsideInit,PyMethodOverriding
class CamExportUI(QtWidgets.QDialog):
    fbxVersions = {
        '2016': 'FBX201600',
        '2014': 'FBX201400',
        '2013': 'FBX201300',
        '2017': 'FBX201700',
        '2018': 'FBX201800',
        '2019': 'FBX201900'
    }

    dlg_instance = None

    @classmethod
    def display(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = CamExportUI()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()

        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    @classmethod
    def maya_main_window(cls):
        """

        Returns: The Maya main window widget as a Python object

        """
        main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):
        super(CamExportUI, self).__init__(self.maya_main_window())

        self.setWindowTitle("Cam Export")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.geometry = None

        self.setMinimumSize(300, 80)

        self.create_widget()
        self.create_layouts()
        self.create_connections()

        # Get maya version and convert it to same fbx version
        version_maya = cm.about(version=True)
        self.version_fbx = self.fbxVersions.get(version_maya)

    def create_widget(self):
        self.filepath_le = QtWidgets.QLineEdit()
        self.select_file_path_btn = QtWidgets.QPushButton('')
        self.select_file_path_btn.setIcon(QtGui.QIcon(':fileOpen.png'))
        self.select_file_path_btn.setToolTip('Select File')

        self.export_btn = QtWidgets.QPushButton("Export")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layouts(self):
        filepath_layout = QtWidgets.QHBoxLayout()
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('File path:', self.filepath_le)

        filepath_layout.addLayout(form_layout)
        filepath_layout.addWidget(self.select_file_path_btn)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(filepath_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog)

        self.export_btn.clicked.connect(self.export)
        self.close_btn.clicked.connect(self.close)

    def show_file_select_dialog(self):
        self.file_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory')

        self.filepath_le.setText(self.file_path)

    @staticmethod
    def bake(cam):
        pm.bakeResults(cam, simulation=True,
                       t=(pm.playbackOptions(animationStartTime=True, query=True),
                          pm.playbackOptions(animationEndTime=True, query=True)),
                       sampleBy=1,
                       oversamplingRate=1,
                       disableImplicitControl=True, preserveOutsideKeys=True, sparseAnimCurveBake=False,
                       removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
                       bakeOnOverrideLayer=False,
                       minimizeRotation=True, controlPoints=False, shape=True)

    def export_option(self, path):
        eval("FBXExportSmoothingGroups -v true")
        eval("FBXExportHardEdges -v false")
        eval("FBXExportTangents -v false")
        eval("FBXExportSmoothMesh -v true")
        eval("FBXExportInstances -v false")
        eval("FBXExportReferencedAssetsContent -v false")

        eval('FBXExportBakeComplexAnimation -v true')

        eval("FBXExportBakeComplexStep -v 1")

        eval("FBXExportUseSceneName -v false")
        eval("FBXExportQuaternion -v euler")
        eval("FBXExportShapes -v true")
        eval("FBXExportSkins -v true")

        # Constraints
        eval("FBXExportConstraints -v false")
        # Cameras
        eval("FBXExportCameras -v true")
        # Lights
        eval("FBXExportLights -v true")
        # Embed Media
        eval("FBXExportEmbeddedTextures -v true")
        # Connections
        eval("FBXExportInputConnections -v true")
        # Axis Conversion
        eval("FBXExportUpAxis y")
        # Version
        eval('FBXExportFileVersion -v {}'.format(self.version_fbx))

        # Export!
        eval('FBXExport -f "{0}" -s'.format(path))

    def export(self):
        # Get link to the folder
        filepath_raw = self.filepath_le.text()

        # Change \ to / for maya can read
        filepath = filepath_raw.replace("\\", "/")

        # Check if the link folder exist or not
        if not os.path.isdir(filepath):
            return om.MGlobal.displayError("File path does not exist")

        # Get scene name
        scene_name = cm.file(q=True, sceneName=True, shortName=True)
        scene_name = scene_name.split(".")[0]

        # Check are we select any object right now
        if len(pm.ls(sl=True)) != 1:
            return om.MGlobal.displayError("Please chose only one camera per time")

        # Get camera and camera shape need to export
        camera = pm.ls(sl=True)[0]
        camera_shape = camera.getShape()

        # Check it is a camera or not
        if pm.objectType(camera_shape) != "camera":
            return om.MGlobal.displayError("object chose is not camera")

        # Duplicate camera and get shape of that camera
        camera_export = pm.duplicate(camera, name="{0}_camExport".format(scene_name), rr=True)[0]
        camera_export_shape = camera_export.getShape()

        # Parent this camera to world
        pm.parent(camera_export, world=True)

        # Get attribute of shape node camera to export camera
        camera_shape.horizontalFilmAperture.connect(camera_export_shape.horizontalFilmAperture)
        camera_shape.verticalFilmAperture.connect(camera_export_shape.verticalFilmAperture)
        camera_shape.focalLength.connect(camera_export_shape.focalLength)
        camera_shape.focusDistance.connect(camera_export_shape.focusDistance)

        # Get position to camera export and bake it frame by frame
        constrain = pm.parentConstraint(camera, camera_export, mo=False)
        self.bake(camera_export)
        pm.delete(constrain)

        # Set name of file and the path to folder
        fbxName = "{0}_cam.fbx".format(scene_name)
        path = (os.path.join(filepath, fbxName)).replace(os.sep, '/')

        # Select camera export and export it
        pm.select(camera_export)
        self.export_option(path)

    def showEvent(self, e):
        super(CamExportUI, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        super(CamExportUI, self).closeEvent(e)

        self.geometry = self.saveGeometry()
