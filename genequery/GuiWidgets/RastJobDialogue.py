from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import webbrowser
from genequery.Utilities import RastPy


class RastJobDialog(QDialog):
    _INVALID_INPUT_BORDER = 'border: 1px solid red'

    def __init__(self, parent=None):
        super(RastJobDialog, self).__init__(parent)

        mainLayout = QGridLayout()

        # WIDGETS -----------------------------------------------------------------------
        # user widgets
        userLabel = QLabel('Username')
        self.userLineEdit = QLineEdit()

        # password widgets
        passwordLabel = QLabel('Password')
        self.passwordLineEdit = QLineEdit()
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)

        # option JobID widgets
        jobLabel = QLabel('JobID')
        self.jobLineEdit = QLineEdit()
        self.jobLineEdit.setPlaceholderText('OPTIONAL - Leave Blank for New Job')

        # buttons
        enterButton = QPushButton('Enter')
        enterButton.setDefault(True)
        enterButton.clicked.connect(self.onEnter)
        viewJobsButton = QPushButton('View Jobs')

        mainLayout.addWidget(userLabel, 0, 0)
        mainLayout.addWidget(self.userLineEdit, 0, 1)
        mainLayout.addWidget(passwordLabel, 1, 0)
        mainLayout.addWidget(self.passwordLineEdit, 1, 1)
        mainLayout.addWidget(jobLabel, 2, 0)
        mainLayout.addWidget(self.jobLineEdit, 2, 1)
        mainLayout.addWidget(viewJobsButton, 3, 0)
        mainLayout.addWidget(enterButton, 3, 1)

        self.setLayout(mainLayout)

    @pyqtSlot()
    def onEnter(self):
        """
        Slot when the "Enter" button is pressed
        """
        # perform check that username and password were entered
        userInput = self.userLineEdit.text()
        passInput = self.passwordLineEdit.text()
        if userInput == '':
            self.userLineEdit.setStyleSheet(self._INVALID_INPUT_BORDER)
        if passInput == '':
            self.passwordLineEdit.setStyleSheet(self._INVALID_INPUT_BORDER)


if __name__ == '__main__':
    app = QApplication([])
    window = RastJobDialog()
    window.show()
    app.exec_()
