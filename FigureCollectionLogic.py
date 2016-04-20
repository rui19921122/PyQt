import requests
from PyQt5 import QtWidgets, QtCore

import customWidget
from UI import FigureCollect
from url_resolve import parse_url
from FigureShowLogic import FiguresShowLogic


class FigureCollectionLogic(QtWidgets.QWidget, FigureCollect.Ui_Form):
    _update_table_widget = QtCore.pyqtSignal(object)

    def __init__(self, main_window, session: requests.Session):
        super(FigureCollectionLogic, self).__init__()
        self._update_table_widget.connect(self.update_table_widget)
        self.mainWindow = main_window
        self.session = session
        self.setupUi(self)
        self.departmentLabel.setText("部门:" + self.mainWindow.department)
        self.personLabel.setText("录入人:" + self.mainWindow.username)
        self.get_worker_table()
        self.tableWidget.cellDoubleClicked.connect(self.cellDoubleClicked)

    def get_worker_table(self):
        response = self.session.get(parse_url('api/worker/worker/'))
        if response.status_code == 200:
            self._update_table_widget.emit(response.json())
        else:
            message = QtWidgets.QMessageBox.warning(self.mainWindow, "错误", str(response.json()),
                                                    QtWidgets.QMessageBox.Yes)

    def update_table_widget(self, obj):
        self.tableWidget.setRowCount(len(obj))
        row = 0
        for person in obj:
            self.tableWidget.setItem(row, 0, customWidget.TableItem(str(person['id'])))
            self.tableWidget.setItem(row, 1, customWidget.TableItem(person['name']))
            self.tableWidget.setItem(row, 2, customWidget.TableItem(str(person['class_number']) + '班'))
            self.tableWidget.setItem(row, 3, customWidget.TableItem('是' if person['is_study'] else '否'))
            self.tableWidget.setItem(row, 4, customWidget.TableItem(str(len(person['figures']))))
            row += 1

    def cellDoubleClicked(self, row, col):
        item = self.tableWidget.item(row, 0)
        """:type item:QtWidgets.QTableWidgetItem"""
        person_id = item.text()
        response = self.session.get(url=parse_url('api/worker/worker/{}/'.format(person_id)))
        if response.status_code == 200:
            json = response.json()
            f = FiguresShowLogic(id=person_id,data=response.json(), session=self.session, parent=self)
            f.exec_()
        else:
            message = QtWidgets.QMessageBox.warning(self.mainWindow, "错误", str(response.json()),
                                                    QtWidgets.QMessageBox.Yes)
