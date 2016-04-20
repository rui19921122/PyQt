from PyQt5 import QtWidgets, QtCore


class TableItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text):
        super(TableItem, self).__init__()
        self.setText(text)
        self.setTextAlignment(QtCore.Qt.AlignCenter)
