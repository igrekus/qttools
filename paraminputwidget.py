from io import BytesIO

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QComboBox, QDoubleSpinBox, QCheckBox, QFrame, QLineEdit, QSpinBox

markup = BytesIO(bytes('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>widgetMeasure</class>
 <widget class="QWidget" name="widgetMeasure">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>224</width>
    <height>113</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <layout class="QVBoxLayout" name="layparams">
   <property name="leftMargin">
    <number>3</number>
   </property>
   <property name="topMargin">
    <number>3</number>
   </property>
   <property name="rightMargin">
    <number>3</number>
   </property>
   <property name="bottomMargin">
    <number>0</number>
   </property>
   <item>
    <widget class="QGroupBox" name="grpParams">
     <property name="sizePolicy">
      <sizepolicy hsizetype="Minimum" vsizetype="Minimum">
       <horstretch>0</horstretch>
       <verstretch>0</verstretch>
      </sizepolicy>
     </property>
     <property name="minimumSize">
      <size>
       <width>0</width>
       <height>0</height>
      </size>
     </property>
     <property name="title">
      <string>Параметры</string>
     </property>
     <property name="checkable">
      <bool>true</bool>
     </property>
     <layout class="QVBoxLayout" name="verticalLayout">
      <property name="spacing">
       <number>0</number>
      </property>
      <property name="leftMargin">
       <number>0</number>
      </property>
      <property name="topMargin">
       <number>0</number>
      </property>
      <property name="rightMargin">
       <number>0</number>
      </property>
      <property name="bottomMargin">
       <number>0</number>
      </property>
      <item>
       <widget class="QWidget" name="widget" native="true">
        <layout class="QFormLayout" name="layParams"/>
       </widget>
      </item>
     </layout>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
''', encoding='utf-8'))


class ParamInputWidget(QWidget):

    def __init__(self, parent=None, primaryParams=None, secondaryParams=None):
        super().__init__(parent=parent)

        self._ui = uic.loadUi(markup, self)

        self._combo = QComboBox()
        for i, label in enumerate(primaryParams.keys()):
            self._combo.addItem(label)
        self._combo.setCurrentIndex(0)

        self._ui.layParams.addRow('Прибор', self._combo)

        self._enabled = True
        self._secondaryParamWidgets = {}
        self._secondaryParams = secondaryParams

        self._createWidgets(self._secondaryParams.required)

    @property
    def selected(self):
        return self._combo.currentText()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        self._combo.setEnabled(value)

    def _createWidgets(self, params):
        makers = {
            float: _make_double_spinbox,
            int: _make_double_spinbox,
            bool: _make_checkbox,
            type(None): _make_separator,
            str: _make_lineedit,
        }
        for key, settings in params.items():
            label, args = settings
            make = type(args['value'])
            widget = makers[make](self, **args)

            self._secondaryParamWidgets[key] = widget
            self._ui.layParams.addRow(label, widget)

    def loadConfig(self):
        self._secondaryParams.load_from_config()
        for key, value in self._secondaryParams.params.items():
            self._secondaryParamWidgets[key].setValue(value)

    def collectParams(self):
        self._secondaryParams.params = self.params

    @property
    def params(self):
        return {k: w.value() for k, w in self._secondaryParamWidgets.items()}

    def saveConfig(self):
        self.collectParams()
        self._secondaryParams.save_config()


def _make_double_spinbox(parent, start=0.0, end=1.0, step=0.1, decimals=2, value=0.1, suffix=''):
    spinbox = QDoubleSpinBox(parent=parent)
    spinbox.setRange(start, end)
    spinbox.setSingleStep(step)
    spinbox.setDecimals(decimals)
    spinbox.setValue(value)
    spinbox.setSuffix(suffix)
    return spinbox


def _make_int_spinbox(parent, start=0, end=10, step=1, value=1, suffix=''):
    spinbox = QSpinBox(parent=parent)
    spinbox.setRange(start, end)
    spinbox.setSingleStep(step)
    spinbox.setValue(value)
    spinbox.setSuffix(suffix)
    return spinbox


def _make_checkbox(parent, value):
    checkbox = QCheckBox(parent=parent)
    checkbox.setChecked(value)
    checkbox.value = checkbox.isChecked
    checkbox.valueChanged = checkbox.toggled
    checkbox.setValue = checkbox.setChecked
    return checkbox


def _make_separator(parent, *args, **kwargs):
    sep = QFrame(parent=parent)
    sep.setFrameShape(QFrame.HLine)
    sep.setFrameShadow(QFrame.Sunken)
    sep.value = lambda: None
    sep.valueChanged = sep.objectNameChanged
    sep.setValue = lambda *a: None
    return sep


def _make_lineedit(parent, value):
    lineedit = QLineEdit(parent=parent)
    lineedit.setText(value)
    lineedit.value = lineedit.text
    lineedit.valueChanged = lineedit.textChanged
    lineedit.setValue = lineedit.setText
    return lineedit
