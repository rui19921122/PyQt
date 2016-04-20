# -*- coding: utf-8 -*-
import sys

import requests
from PyQt5 import QtWidgets, QtCore

import DisplayLogic
import LoginFormLogic
import FigureCollectionLogic
import url_resolve


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.username = None
        self.department = None
        self.setupUi(self)
        self.session = requests.session()
        self.setWindowTitle("芜湖东站点名会系统")
        login = LoginFormLogic.LoginFormLogic(widget=self)
        self.setCentralWidget(login)
        self.show()

    def login_commit(self, username, password, boolean):
        response = self.session.post(url=url_resolve.parse_url('api/auth/login/'),
                                     data={'email': '',
                                           'password': password,
                                           'username': username
                                           })
        """:type :requests.Response """
        if response.status_code == 200:
            _get_detail_response = self.session.get(url=url_resolve.parse_url('api/menu/get-user-detail'))
            self.username = _get_detail_response.json().get('name')
            self.department = _get_detail_response.json().get('department')
            if boolean:
                self.setCentralWidget(FigureCollectionLogic.FigureCollectionLogic(main_window=self,session=self.session))
            else:
                self.setCentralWidget(DisplayLogic.DisplayStarting(session=self.session, main_window=self))
        else:
            message = QtWidgets.QMessageBox.warning(self, "错误", str(response.json()), QtWidgets.QMessageBox.Yes)

    def start_call_over(self):
        response = self.session.post(url=url_resolve.parse_url('api/call_over/begin-call-over/'))
        assert isinstance(response,requests.Response)
        if response.status_code == 200:
            print(response.json())
        else:
            message = QtWidgets.QMessageBox.warning(self, "错误", str(response.json()), QtWidgets.QMessageBox.Yes)
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1082, 731)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
