from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class RastJobDialog(QDialog):

    def __init__(self, parent=None):
        super(RastJobDialog, self).__init__(parent)

        mainLayout = QGridLayout()

        # WIDGETS -----------------------------------------------------------------------
        # user widgets
        userLabel = QLabel('Username')
        userLineEdit = QLineEdit()

        # password widgets
        passwordLabel = QLabel('Password')
        passwordLineEdit = QLineEdit()
        passwordLineEdit.setEchoMode(QLineEdit.Password)

        # option JobID widgets
        jobLabel = QLabel('JobID')
        jobLineEdit = QLineEdit()
        jobLineEdit.setPlaceholderText('OPTIONAL - Leave Blank for New Job')

        # buttons
        enterButton = QPushButton('Enter')
        viewJobsButton = QPushButton('View Jobs')

        mainLayout.addWidget(userLabel, 0, 0)
        mainLayout.addWidget(userLineEdit, 0, 1)
        mainLayout.addWidget(passwordLabel, 1, 0)
        mainLayout.addWidget(passwordLineEdit, 1, 1)
        mainLayout.addWidget(jobLabel, 2, 0)
        mainLayout.addWidget(jobLineEdit, 2, 1)
        mainLayout.addWidget(enterButton, 3, 0)
        mainLayout.addWidget(viewJobsButton, 3, 1)

        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication([])
    window = RastJobDialog()
    window.show()
    app.exec_()
