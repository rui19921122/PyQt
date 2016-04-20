# -*- coding: utf-8 -*-
import ctypes
import sys

import requests
from PyQt5 import QtWidgets, QtMultimedia, QtCore

from UI.Display import Ui_DisplayWorker
from customWidget import TableItem
from url_resolve import parse_url


class DisplayStarting(QtWidgets.QWidget,Ui_DisplayWorker):

    _figure = QtCore.pyqtSignal(bytes)
    _metion = QtCore.pyqtSignal(str,bool)

    def __init__(self, session, main_window):
        """
        :type session:requests.Session
        :param session:
        """
        super(DisplayStarting, self).__init__()
        self.can_collect_figure = False  # 指示定时器是否可以运行的参数
        self.checked = False  # 人员确认按钮状态
        self.setupUi(self)
        self.session = session
        self.get_initial_state()
        self._figure.connect(self.post_figure_data)
        self.pushButton.clicked.connect(self.refresh_person_state)
        self.mainWindow = main_window
        self._metion.connect(self.refresh_prompt_label)
        # 获取点名会相关信息，不将此放在refresh函数中是因为可以省下一次网络请求
        response = self.session.get(url=parse_url('api/call_over/get-call-over-person/'))
        """:type response:requests.Response"""
        json = response.json()
        self.pk = json.get('id')
        self.BeginButton.clicked.connect(self.BeginButtonClicked)
        if json.get('lock') == False:
            self.checked = False
        elif json.get('lock') == True:
            self.checked = True
            self.BeginButtonClicked()
        self.refresh_person_state()

    def get_initial_state(self):
        # 录音设备
        self.AudioStatus.setText("初始化中...")
        self.VideoStatus.setText("初始化中...")
        self.FigureStatus.setText("初始化中...")
        audio_devices = QtMultimedia.QAudioDeviceInfo().availableDevices(0)
        if len(audio_devices) == 0:
            self.AudioStatus.setText("未找到")
        elif len(audio_devices) == 1:
            self.AudioStatus.setText("正常")
        else:
            self.AudioStatus.setText("发现{}个，使用{}"
                                     .format(len(audio_devices),
                                             QtMultimedia.QAudioDeviceInfo()
                                             .defaultInputDevice().deviceName()))
        # 视频设备
        video_devices = QtMultimedia.QCameraInfo().availableCameras()
        if len(video_devices) == 0:
            self.VideoStatus.setText("未找到")
        elif len(video_devices) == 1:
            self.VideoStatus.setText("正常")
        else:
            self.VideoStatus.setText("发现{}个，使用{}"
                                     .format(len(video_devices),
                                             QtMultimedia.QCameraInfo.defaultCamera().deviceName()))
        # 指纹仪
        try:
            self.dll = ctypes.windll.JZTDevDll
            self.figure_number = self.dll.FPIDevDetect()
            if self.figure_number < 0:
                self.FigureStatus.setText("指纹仪设备:未发现指纹仪设备")
            else:
                self.FigureStatus.setText("指纹仪设备:正常")
                self.can_collect_figure = True
        except:
            self.FigureStatus.setText("指纹仪设备:加载驱动设备出错，请联系管理员")

    def refresh_person_state(self):
        another = self.session.get(url=parse_url('api/call_over/get-call-over-person-detail'),
                                   params={'number': self.pk})
        """:type another:requests.Response"""
        print(another.json())
        self.re_render(data=another.json())

    def re_render(self, data):
        self.tableWidget.setRowCount(len(data))
        row = 0
        for i in data:
            self.tableWidget.setItem(row, 0, TableItem(i.get('worker')))
            self.tableWidget.setItem(row, 1, TableItem(i.get('position')))
            self.tableWidget.setItem(row, 2, TableItem('是' if i.get('study') else '否'))
            self.tableWidget.setItem(row, 3, TableItem(i.get('checked') if i.get('checked') else '未打点'))
            row += 1

    def BeginButtonClicked(self):
        response = self.session.post(url=parse_url('api/call_over/lock-call-over-person/'),data={'number':self.pk})
        assert isinstance(response, requests.Response)
        if response.status_code == 201 or 200:
            self.label_2.setText('人员已确认完毕，可以开始录制指纹')
            self.BeginButton.disconnect()
            self.BeginButton.clicked.connect(self.mainWindow.start_call_over)
            if self.can_collect_figure:
                self.Timer = QtCore.QTimer()
                self.Timer.timeout.connect(self.checkFigure)
                self.Timer.start(1500)
        else:
            message = QtWidgets.QMessageBox.warning(self.mainWindow, "错误", str(response.text), QtWidgets.QMessageBox.Yes)
    def checkFigure(self):
        if self.can_collect_figure:
            try:
                f = self.dll.FPICheckFinger(self.figure_number)
                if f == 0:
                    self.Timer.stop()
                    pstz = ctypes.create_string_buffer(512)
                    length = ctypes.create_string_buffer(512)
                    self.dll.FPIFeatureWithoutUI(0, pstz, length)
                    self._figure.emit(pstz.raw)
                    del pstz, length
                    self.Timer.start(1500)
                elif f == 1:
                    pass
            except:
                self.can_collect_figure = False
                self.FigureLabel.setText("出错，请联系管理员")
                self.Time.stop()

    def post_figure_data(self,value:bytes):
        response = self.session.post(parse_url('api/call_over/post-figure/'),
                                     data={'number':self.pk,'figure_data':value.decode('utf-8')})
        """:type response:requests.Response"""
        if response.status_code == 201:
            name = response.json().get('people')
            self._metion.emit(name,True)
        else:
            self._metion.emit(response.text,False)

    def refresh_prompt_label(self, string, boolean):
        if boolean:
            self.label_2.setText(string+'已签到')
        else:
            self.label_2.setText('错误:'+str(string))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = DisplayStarting()
    mainWindow.show()
    sys.exit(app.exec_())