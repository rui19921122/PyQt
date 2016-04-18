from PyQt5 import QtCore, QtWidgets, QtGui
import LoginForm
import mainWindow
from url_resolve import parse_url


class LoginFormLogic(LoginForm.Ui_Form):
    _submit = QtCore.pyqtSignal(str, str)

    def __init__(self, widget=None):
        super(LoginFormLogic, self).__init__()
        self.setupUi(self)
        self.SubmitButton.clicked.connect(self.post_password)
        if widget:
            self._submit.connect(widget.login_commit)

    def post_password(self):
        username = self.UsernameInput.text()
        password = self.PasswordInput.text()
        # todo change this
        # self._submit.emit(username, password)
        self._submit.emit('test', '111111')
