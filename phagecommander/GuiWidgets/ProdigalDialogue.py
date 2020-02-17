import platform
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from phagecommander.Utilities import ThreadData, ProdigalRelease


class ProdigalDownloadDialog(QDialog):

    def __init__(self, prodRelease: ProdigalRelease, td: ThreadData, parent=None):
        super(ProdigalDownloadDialog, self).__init__(parent)

        self.release = prodRelease
        self.td = td

        # Widgets ---------------------------------------------------
        downloadLabel = QLabel(
            'Prodigal was not detected and will not be available to use.\nWould you like to download it?')
        downloadLabelFont = QFont()
        downloadLabelFont.setPointSize(10)
        downloadLabel.setAlignment(Qt.AlignCenter)
        downloadLabel.setFont(downloadLabelFont)
        downloadButton = QPushButton('Download')
        downloadButton.clicked.connect(self.downloaded)
        downloadButton.setDefault(True)
        cancelButton = QPushButton('Cancel')
        cancelButton.clicked.connect(self.canceled)

        # Layout ----------------------------------------------------
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(downloadLabel)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(downloadButton)
        buttonLayout.addWidget(cancelButton)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        # Settings ---------------------------------------------------
        self.setWindowTitle('Prodigal Not Found')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)

    @pyqtSlot()
    def downloaded(self):
        downloadThread = DownloadProdigal(self.release, self.td)
        dig = ProdigalProgressDialog(downloadThread)
        dig.exec_()

        # self.td.data contains the path of the Prodigal binary if download was successful
        #                       Exception if errors while downloading

        # check if any errors while downloading
        if isinstance(self.td.data, Exception):
            QMessageBox.warning(self,
                                'Error Downloading Prodigal',
                                'Error while downloading Prodigal: {}'.format(str(self.td.data)))
            self.reject()

        # data returned was valid
        else:
            self.accept()

    @pyqtSlot()
    def canceled(self):
        self.reject()


class ProgressDialog(QDialog):

    def __init__(self, thread: QThread, parent=None):
        super(ProgressDialog, self).__init__(parent)

        # WIDGETS ---------------------------------------------
        self.progressBar = QProgressBar()
        # set max/min to 0 for active progress bar
        self.progressBar.setMaximum(0)
        self.progressBar.setMinimum(0)
        self.progressBar.setAlignment(Qt.AlignCenter)

        # LAYOUT ----------------------------------------------
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.progressBar)
        self.setLayout(mainLayout)

        # SETTINGS ---------------------------------------------
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setWindowTitle('Replace Me')

        self.thread = thread
        self.thread.finished.connect(self.onThreadFinish)
        self.thread.start()

    def onThreadFinish(self):
        self.accept()


class ProdigalProgressDialog(ProgressDialog):

    def __init__(self, thread: QThread, parent=None):
        super(ProdigalProgressDialog, self).__init__(thread, parent)

        self.setWindowTitle('Downloading Prodigal...')


class DownloadProdigal(QThread):

    def __init__(self, prodRelease: ProdigalRelease, td: ThreadData):
        super(DownloadProdigal, self).__init__()
        self.td = td
        self.release = prodRelease

    def run(self):
        try:
            prodigalPath = self.release.getBinary(platform.system(), self.td.data)
            self.td.data = prodigalPath
        except Exception as e:
            self.td.data = e


if __name__ == '__main__':
    app = QApplication([])
    release = ProdigalRelease()
    td = ThreadData(r'C:\Users\mdlaz\Desktop')
    dig = ProdigalDownloadDialog(release, td)
    dig.show()
    app.exec_()
    print(td.data)
