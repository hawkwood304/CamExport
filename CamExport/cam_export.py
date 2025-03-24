from shiboken2 import wrapInstance

import os
import maya.cmds as cm
# import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2 import QtWidgets, QtCore, QtGui
from maya.mel import eval

# import sys


class QHLine(QtWidgets.QFrame):

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)


class QVLine(QtWidgets.QFrame):

    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)


class QHLineName(QtWidgets.QGridLayout):

    def __init__(self, name):
        super(QHLineName, self).__init__()
        name_lb = QtWidgets.QLabel(name)
        name_lb.setAlignment(QtCore.Qt.AlignCenter)
        name_lb.setStyleSheet("font: italic 9pt;" "color: azure;")
        self.addWidget(name_lb, 0, 0, 1, 1)
        self.addWidget(QHLine(), 0, 1, 1, 2)


# noinspection PyAttributeOutsideInit
class CamExportTool(QtWidgets.QWidget):
    fbxVersions = {
        '2016': 'FBX201600',
        '2014': 'FBX201400',
        '2013': 'FBX201300',
        '2017': 'FBX201700',
        '2018': 'FBX201800',
        '2019': 'FBX201900'
    }

    def __init__(self):
        super(CamExportTool, self).__init__()

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.file_path_lb = QtWidgets.QLabel("File path: ")
        self.file_path_le = QtWidgets.QLineEdit()

        self.select_file_path_btn = QtWidgets.QPushButton('')
        self.select_file_path_btn.setIcon(QtGui.QIcon(':fileOpen.png'))
        self.select_file_path_btn.setToolTip('Select File')

        self.shot_name_lb = QtWidgets.QLabel("Shot name: ")
        self.shot_name_le = QtWidgets.QLineEdit()

        self.cam_name_lb = QtWidgets.QLabel("Cam name:")
        self.cam_name_le = QtWidgets.QLineEdit()
        self.cam_name_btn = QtWidgets.QPushButton("Assign")

        self.offset_time_lb = QtWidgets.QLabel("Offset frames: ")
        self.zero_frames_rb = QtWidgets.QRadioButton("0")
        self.zero_frames_rb.setChecked(True)
        self.thirty_frames_rb = QtWidgets.QRadioButton("30")
        self.sixty_frames_rb = QtWidgets.QRadioButton("60")
        self.ninety_frames_rb = QtWidgets.QRadioButton("90")

        self.bake_cb = QtWidgets.QCheckBox("Bake Animation")
        self.bake_cb.setChecked(True)
        self.fbxVersion_combobox = QtWidgets.QComboBox()
        for fbxVersion in sorted(self.fbxVersions):
            self.fbxVersion_combobox.addItem(fbxVersion)
            self.fbxVersion_combobox.setCurrentText("2019")

        self.fbx_export_btn = QtWidgets.QPushButton("FBX Export")
        self.fbx_export_btn.setStyleSheet('QPushButton {background-color: lightsteelblue; color: black;}')

    def create_layouts(self):
        file_option_layout = QtWidgets.QGridLayout()
        file_option_layout.addWidget(self.file_path_lb, 0, 0)
        file_option_layout.addWidget(self.file_path_le, 0, 1)
        file_option_layout.addWidget(self.select_file_path_btn, 0, 2)

        scene_option_layout = QtWidgets.QGridLayout()
        scene_option_layout.addWidget(self.shot_name_lb, 0, 0, 1, 1)
        scene_option_layout.addWidget(self.shot_name_le, 0, 1, 1, 2)
        scene_option_layout.addWidget(self.cam_name_lb, 1, 0, 1, 1)
        scene_option_layout.addWidget(self.cam_name_le, 1, 1, 1, 1)
        scene_option_layout.addWidget(self.cam_name_btn, 1, 2, 1, 1)

        fbx_option_layout = QtWidgets.QHBoxLayout()
        fbx_option_layout.addWidget(self.bake_cb)
        fbx_option_layout.addWidget(self.fbxVersion_combobox)
        fbx_option_layout.addWidget(self.fbx_export_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(QHLineName("File option"))
        main_layout.addLayout(file_option_layout)
        main_layout.addLayout(QHLineName("Scene option"))
        main_layout.addLayout(scene_option_layout)
        main_layout.addLayout(QHLineName("Fbx option"))
        main_layout.addLayout(fbx_option_layout)

    def create_connections(self):
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog)
        self.fbx_export_btn.clicked.connect(self.fbx_export)
        self.cam_name_btn.clicked.connect(self.assign_cam_button)

    def fbx_export_option(self, path, min_time, max_time):
        fbx_version = self.fbxVersion_combobox.currentText()
        version = self.fbxVersions[fbx_version]

        eval("FBXExportSmoothingGroups -v true")
        eval("FBXExportHardEdges -v false")
        eval("FBXExportTangents -v false")
        eval("FBXExportSmoothMesh -v true")
        eval("FBXExportInstances -v false")
        eval("FBXExportReferencedAssetsContent -v false")

        if self.bake_cb.isChecked():
            eval('FBXExportBakeComplexAnimation -v true')
            eval("FBXExportBakeComplexStep -v 1")
            eval("FBXExportBakeComplexStart -v {}".format(min_time))
            eval("FBXExportBakeComplexEnd -v {}".format(max_time))
        else:
            eval('FBXExportBakeComplexAnimation -v false')

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
        eval("FBXExportEmbeddedTextures -v false")
        # Connections
        eval("FBXExportInputConnections -v true")
        # Axis Conversion
        eval("FBXExportUpAxis y")
        # Version
        eval('FBXExportFileVersion -v {}'.format(version))

        # Export!

        eval('FBXExport -f "{0}" -s'.format(path))

    def assign_cam_button(self):
        list_selection = cm.ls(sl=True)
        list_selection_cam = []
        if len(list_selection) != 0:
            for obj in list_selection:

                children = cm.listRelatives(obj, children=True, fullPath=True) or []

                if len(children) >= 1:
                    child = children[0]
                    obj_type = cm.objectType(child)

                else:
                    obj_type = cm.objectType(obj)

                if obj_type == 'camera':
                    list_selection_cam.append(obj)
        else:
            om.MGlobal_displayError("Please chose at least one camera")

        list_selection_cam = str(list_selection_cam)
        list_selection_cam = list_selection_cam.replace("[", "")
        list_selection_cam = list_selection_cam.replace("]", "")
        list_selection_cam = list_selection_cam.replace("'", "")
        self.cam_name_le.setText(list_selection_cam)

    def get_list_camera_name(self):

        """
        Convert data to Maya language

        Returns:
            list camera name(list)
        """

        if self.cam_name_le.text():
            list_camera_name_raw = self.cam_name_le.text()
            list_camera_name_raw = list_camera_name_raw.replace(" ", "")
            list_camera_name_raw = list_camera_name_raw.split(",")
            list_camera_name = list(list_camera_name_raw)
            return list_camera_name
        else:
            list_camera_name = []
            return list_camera_name

    def show_file_select_dialog(self):
        self.file_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory')

        self.file_path_le.setText(self.file_path)

    def get_convert_file_path(self):

        """
        Convert the link for the folder will contain export file to language Maya understand

        Returns:
            file patch(str)
        """

        filepath_raw = self.file_path_le.text()
        filepath = filepath_raw.replace('\\', '/')
        if not os.path.isdir(filepath):
            return om.MGlobal.displayError("File path doesn't exist")
        return filepath

    def get_shot_name(self):
        """
        Assign shot name for this scene

        Returns:
            Shot name(str)
        """

        shot_name = self.shot_name_le.text()
        if len(shot_name) == 0:
            return om.MGlobal_displayError("Shot name can't be empty")

        return shot_name

    @staticmethod
    def get_time_range():

        min_time = cm.playbackOptions(q=True, min=True)
        max_time = cm.playbackOptions(q=True, max=True)
        return min_time, max_time

    def fbx_export(self):
        filepath = self.get_convert_file_path()
        shot_name = self.get_shot_name()
        min_time, max_time = self.get_time_range()
        list_export_cam = self.get_list_camera_name()

        if not shot_name == None and not filepath == None:

            new_filepath = (os.path.join(filepath, shot_name)).replace(os.sep, '/')

            if not os.path.isdir(new_filepath):
                os.mkdir(new_filepath)
            if len(list_export_cam) != 0:
                for obj in list_export_cam:
                    cam_shapes = cm.listRelatives(obj, shapes=True)
                    new_cam = cm.camera()
                    multMatrix_node = cm.createNode("multMatrix", name="cam_multMatrix")
                    decomposeMatrix_node = cm.createNode("decomposeMatrix", name="cam_decomposeMatrix")
                    cm.connectAttr(f"{obj}.worldMatrix[0]", f"{multMatrix_node}.matrixIn[0]")
                    cm.connectAttr(f"{multMatrix_node}.matrixSum", f"{decomposeMatrix_node}.inputMatrix")
                    cm.connectAttr(f"{decomposeMatrix_node}.outputTranslate", f"{new_cam[0]}.translate")
                    cm.connectAttr(f"{decomposeMatrix_node}.outputRotate", f"{new_cam[0]}.rotate")

                    cm.connectAttr("{0}.focalLength".format(cam_shapes[0]), "{0}.focalLength".format(new_cam[1]),
                                   f=1)
                    cm.select(new_cam[0])
                    eval(
                        'bakeResults -simulation true -t "{0}:{1}" -sampleBy 1 -oversamplingRate 1 '
                        '-disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false '
                        '-removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer '
                        'false -minimizeRotation true -controlPoints false -shape false;'.format(
                            min_time, max_time))
                    cm.select("{0}.focalLength".format(new_cam[1]))
                    eval(
                        'bakeResults -simulation true -t "{0}:{1}" -sampleBy 1 -oversamplingRate 1 '
                        '-disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false '
                        '-removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer '
                        'false -minimizeRotation true -controlPoints false -shape true;'.format(
                            min_time, max_time))

                    cm.keyframe(new_cam[0], edit=True, relative=True, timeChange=-min_time)

                    cm.select(new_cam[0])
                    if len(list_export_cam) == 1:
                        cam_name = '{0}_cam.fbx'.format(shot_name)
                    else:
                        cam_name = '{0}_cam.fbx'.format(obj)
                    cam_part = (os.path.join(str(new_filepath), str(cam_name))).replace(os.sep, '/')
                    self.fbx_export_option(path=cam_part, min_time=min_time, max_time=max_time)
                    cm.delete(new_cam[0], multMatrix_node, decomposeMatrix_node)


# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit,PyMethodOverriding
class MainWindow(QtWidgets.QDialog):
    WINDOW_TITLE = "Camera Export"

    SCRIPTS_DIR = cm.internalVar(userScriptDir=True)
    ICON_DIR = os.path.join(SCRIPTS_DIR, 'Thi/Icon')

    dlg_instance = None

    @classmethod
    def display(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = MainWindow()

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
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):
        super(MainWindow, self).__init__(self.maya_main_window())

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.geometry = None

        self.setMinimumSize(400, 200)
        self.create_widget()
        self.create_layouts()
        self.create_connections()

    def create_widget(self):
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.addWidget(CamExportTool())

        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layouts(self):

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(self.content_layout)

    def create_connections(self):
        self.close_btn.clicked.connect(self.close)

    def showEvent(self, e):
        super(MainWindow, self).showEvent(e)

        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        super(MainWindow, self).closeEvent(e)

        self.geometry = self.saveGeometry()
