from io import BytesIO

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget

from .backgroundworker import BackgroundWorker, TaskResult, CancelToken
from .instrumentwidget import InstrumentWidget


markup = BytesIO(bytes('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>widgetInstrumentController</class>
 <widget class="QWidget" name="widgetInstrumentController">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>152</width>
    <height>68</height>
   </rect>
  </property>
  <property name="sizePolicy">
   <sizepolicy hsizetype="Minimum" vsizetype="Minimum">
    <horstretch>0</horstretch>
    <verstretch>0</verstretch>
   </sizepolicy>
  </property>
  <property name="windowTitle">
   <string/>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout_3">
   <property name="leftMargin">
    <number>3</number>
   </property>
   <property name="topMargin">
    <number>0</number>
   </property>
   <property name="rightMargin">
    <number>3</number>
   </property>
   <property name="bottomMargin">
    <number>2</number>
   </property>
   <item>
    <widget class="QGroupBox" name="grpInstruments">
     <property name="enabled">
      <bool>true</bool>
     </property>
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
      <string>Инструменты</string>
     </property>
     <property name="checkable">
      <bool>true</bool>
     </property>
     <property name="checked">
      <bool>true</bool>
     </property>
     <layout class="QVBoxLayout" name="verticalLayout_2">
      <item>
       <widget class="QWidget" name="widgetContainer" native="true">
        <layout class="QVBoxLayout" name="layInstruments">
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
          <layout class="QHBoxLayout" name="horizontalLayout">
           <property name="rightMargin">
            <number>1</number>
           </property>
           <item>
            <spacer name="horizontalSpacer">
             <property name="orientation">
              <enum>Qt::Horizontal</enum>
             </property>
             <property name="sizeHint" stdset="0">
              <size>
               <width>40</width>
               <height>20</height>
              </size>
             </property>
            </spacer>
           </item>
           <item>
            <widget class="QPushButton" name="btnConnect">
             <property name="text">
              <string>Подключить</string>
             </property>
            </widget>
           </item>
          </layout>
         </item>
        </layout>
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


class ConnectionWidgetWithWorker(QWidget):

    _connectFinished = pyqtSignal(TaskResult)
    _connectStarted = pyqtSignal()
    connected = pyqtSignal()

    def __init__(self, parent=None, controller=None):
        super().__init__(parent=parent)

        self._ui = uic.loadUi(markup, self)
        self._controller = controller
        self._worker = BackgroundWorker(self)
        self._token = CancelToken()

        self._widgets = {
            k: InstrumentWidget(parent=self, title=f'{k}', addr=f'{v.addr}')
            for k, v in self._controller.requiredInstruments.items()
        }

        self._connectSignals()
        self._init()

    def _connectSignals(self):
        self._connectStarted.connect(self.on_connectStarted, type=Qt.QueuedConnection)
        self._connectFinished.connect(self.on_connectFinished, type=Qt.QueuedConnection)

    def _init(self):
        for i, iw in enumerate(self._widgets.items()):
            self._ui.layInstruments.insertWidget(i, iw[1])

    def _connectFinishedCallback(self, result: tuple):
        self._connectFinished.emit(TaskResult(*result))

    @pyqtSlot()
    def on_btnConnect_clicked(self):
        self._token = CancelToken()
        self._worker.runTask(
            fn=self._controller.connect,
            fn_finished=self.on_connectFinished,
            token=self._token,
            addrs={k: w.address for k, w in self._widgets.items()},
        )
        self._connectStarted.emit()

    @pyqtSlot(TaskResult)
    def on_connectFinished(self, result):
        if not self._controller.found:
            print('connect error, check connection')
            return

        for w, s in zip(self._widgets.values(), self._controller.status):
            w.status = s
        self.connected.emit()

    def on_connectStarted(self):
        pass

    @pyqtSlot(bool)
    def on_grpInstruments_toggled(self, state):
        self._ui.widgetContainer.setVisible(state)
