from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import webbrowser
from phagecommander.Utilities import RastPy


class RastJobDialog(QDialog):
    _INVALID_INPUT_BORDER = 'border: 1px solid red'
    _DEFAULT_STYLE_SHEET = ''

    def __init__(self, queryData, parent=None):
        super(RastJobDialog, self).__init__(parent)

        mainLayout = QGridLayout()
        self.queryData = queryData

        # WIDGETS -----------------------------------------------------------------------
        # user widgets
        userLabel = QLabel('Username')
        self.userLineEdit = QLineEdit()
        self.userLineEdit.textEdited.connect(self.onUserLineEdit)

        # password widgets
        passwordLabel = QLabel('Password')
        self.passwordLineEdit = QLineEdit()
        self.passwordLineEdit.textEdited.connect(self.onPassLineEdit)
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)

        # option JobID widgets
        jobLabel = QLabel('JobID')
        self.jobLineEdit = QLineEdit()
        jobLineEditText = 'OPTIONAL - Leave Blank for New Job '
        self.jobLineEdit.setPlaceholderText(jobLineEditText)
        self.jobLineEdit.textEdited.connect(self.onJobLineEdit)
        # set width according to size of line edit placeholder text
        font = QFont()
        metric = QFontMetrics(font)
        self.jobLineEdit.setMinimumWidth(metric.width(jobLineEditText) + 6)
        # jobs are only integers
        self.jobLineEdit.setValidator(QIntValidator(0, 100000000))

        # buttons
        enterButton = QPushButton('Enter')
        enterButton.setDefault(True)
        enterButton.clicked.connect(self.onEnter)
        viewJobsButton = QPushButton('View Jobs')
        viewJobsButton.clicked.connect(self.onViewJobs)

        mainLayout.addWidget(userLabel, 0, 0)
        mainLayout.addWidget(self.userLineEdit, 0, 1)
        mainLayout.addWidget(passwordLabel, 1, 0)
        mainLayout.addWidget(self.passwordLineEdit, 1, 1)
        mainLayout.addWidget(jobLabel, 2, 0)
        mainLayout.addWidget(self.jobLineEdit, 2, 1)
        mainLayout.addWidget(viewJobsButton, 3, 0)
        mainLayout.addWidget(enterButton, 3, 1)

        self.setLayout(mainLayout)

        # WINDOW --------------------------------------------------------------
        self.setWindowTitle('RAST Credentials')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)

    @pyqtSlot()
    def onEnter(self):
        """
        Slot when the "Enter" button is pressed
        """
        # perform check that username and password were entered
        userInput = self.userLineEdit.text()
        passInput = self.passwordLineEdit.text()
        jobInput = self.jobLineEdit.text()
        jobInput = int(jobInput) if jobInput != '' else None
        badCreds = False
        if userInput == '':
            self.userLineEdit.setStyleSheet(self._INVALID_INPUT_BORDER)
            badCreds = True
        if passInput == '':
            self.passwordLineEdit.setStyleSheet(self._INVALID_INPUT_BORDER)
            badCreds = True
        if badCreds:
            return

        # check that credentials are valid
        try:
            client = RastPy.Rast(userInput, passInput, jobId=jobInput)
        except RastPy.RastInvalidCredentialError:
            QMessageBox.critical(self, 'Invalid Credentials', 'Invalid credentials. Check username and password.')
            return
        except RastPy.RastInvalidJobError:
            QMessageBox.critical(self, 'Invalid JobID', 'Given JobID "{}" is not valid.'.format(jobInput))
            self.jobLineEdit.setStyleSheet(self._INVALID_INPUT_BORDER)
            return
        except Exception as e:
            QMessageBox.critical(self, 'Unexpected Error', 'Error: {}'.format(e))
            return

        # creds and jobID at this point are valid, return values
        self.queryData.rastUser = userInput
        self.queryData.rastPass = passInput
        self.queryData.rastJobID = jobInput

        QDialog.accept(self)

    @pyqtSlot()
    def onViewJobs(self):
        """
        Slot when "View Jobs" is clicked
        """
        # open up browser to RAST login
        webbrowser.open(RastPy.RAST_USER_URL)

    @pyqtSlot()
    def onUserLineEdit(self):
        """
        Slot when username line is edited
        """
        self.userLineEdit.setStyleSheet(self._DEFAULT_STYLE_SHEET)

    @pyqtSlot()
    def onPassLineEdit(self):
        """
        Slot when password line is edited
        """
        self.passwordLineEdit.setStyleSheet(self._DEFAULT_STYLE_SHEET)

    @pyqtSlot()
    def onJobLineEdit(self):
        """
        Slot when the jobID line is edited
        """
        self.jobLineEdit.setStyleSheet(self._DEFAULT_STYLE_SHEET)


if __name__ == '__main__':
    from phagecommander.phagecom import QueryData

    app = QApplication([])
    data = QueryData()
    window = RastJobDialog(data)
    window.show()
    app.exec_()
