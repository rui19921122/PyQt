import sys
import requests
from PyQt5 import QtWidgets, QtCore
from UI import FigureShow
from UI.figurebutton import FigureButton
from functools import partial
from url_resolve import parse_url
import ctypes

figure_map = {
    'l1': '左手大拇指',
    'l2': '左手食指',
    'l3': '左手中指',
    'l4': '左手无名指',
    'l5': '左手小拇指',
    'r1': '右手大拇指',
    'r2': '右手食指',
    'r3': '右手中指',
    'r4': '右手无名指',
    'r5': '右手小拇指'
}


class FiguresShowLogic(QtWidgets.QDialog, FigureShow.Ui_Dialog):
    _close = QtCore.pyqtSignal()
    def __init__(self, data, id, session, parent=None):
        super(FiguresShowLogic, self).__init__(parent)
        if parent:
            self._close.connect(parent.get_worker_table)
        self.data = data
        self.id = id  # 职工id
        self.session = session
        figure_data = data['figures']
        self.setupUi(self)
        self.refresh_status(figure_data=self.data['figures'])
        self.dll = ctypes.windll.LoadLibrary('JZTDevDll.dll')
        try:
            self.figure_number = self.dll.FPIDevDetect()
            assert self.figure_number >= 0
        except:
            QtWidgets.QMessageBox.warning(self, "错误",
                                          '初始化指纹仪失败',
                                          QtWidgets.QMessageBox.Yes
                                          )

    def closeEvent(self, QCloseEvent):
        self._close.emit()

    def refresh_status(self, figure_data):
        for button in [self.l1, self.l2, self.l3, self.l4, self.l5, self.r1, self.r2, self.r3, self.r4, self.r5]:
            name = button.objectName()
            if figure_map[name] in figure_data:
                try:
                    button.disconnect()
                except:
                    pass
                button.setStyleSheet("background-image:url(:/FigureImage/resource/Had.jpg);")
                button.clicked.connect(partial(self.handleHadFigureButtonClicked, figure_map[name]))
            else:
                try:
                    button.disconnect()
                except:
                    pass
                button.setStyleSheet("background-image:url(:/FigureImage/resource/NotHad.jpg);")
                button.clicked.connect(partial(self.handleNotHadFigureButtonClicked, figure_map[name]))

    def handleHadFigureButtonClicked(self, name):
        if QtWidgets.QMessageBox.warning(self, "警告",
                                         '职工{}的{}已经录有指纹，此操作将删除其指纹，是否确定?'.format(self.data.get('name'),
                                                                                name),
                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                                         ) == QtWidgets.QMessageBox.Yes:
            response = self.session.delete(parse_url('api/worker/figure-post/'), data={'id': self.id, 'name': name})
            if response.status_code == 202:
                self.refresh_status(figure_data=response.json()['figures'])
            else:
                QtWidgets.QMessageBox.warning(self, "错误",
                                              response.text,
                                              QtWidgets.QMessageBox.Yes
                                              )
        else:
            pass

    def handleNotHadFigureButtonClicked(self, name):
        try:
            psMB = ctypes.create_string_buffer(512)
            length = ctypes.create_string_buffer(512)
            self.dll.FPITemplate(0, psMB, length)
            assert len(psMB.value) == 512
            """:type psMB.value: bytes"""
            response = self.session.post(parse_url('api/worker/figure-post/'), data={'id': self.id, 'name': name,
                                                                                     'value': psMB.value.decode(
                                                                                         'utf-8')})
            if response.status_code == 201:
                self.refresh_status(figure_data=response.json()['figures'])
            else:
                QtWidgets.QMessageBox.warning(self, "错误",
                                              response.text,
                                              QtWidgets.QMessageBox.Yes
                                              )
            del psMB, length
        except Exception:
            QtWidgets.QMessageBox.warning(self, "错误",
                                          '采集指纹失败',
                                          QtWidgets.QMessageBox.Yes
                                          )


if __name__ == '__main__':
    id = 1
    app = QtWidgets.QApplication(sys.argv)
    session = requests.session()
    s = session.post(parse_url('api/auth/login/'), data={'username': 'test', 'password': '111111'})
    data = session.get(parse_url('api/worker/worker/{}'.format(id))).json()
    f = FiguresShowLogic(data=data, id=id, session=session)
    f.show()
    sys.exit(app.exec_())
