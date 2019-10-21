import os
from abc import abstractmethod
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class exportDialog(QDialog):
    """
    Abstract class for representing an export dialogue

    Must Implement:
    saveFile()

    accept() and reject() can be overloaded to change behavior when Export/Cancel are clicked respectively
    Default behavior is to call QDialog.accept()/QDialog.reject()
    """

    _EXACTLY_BUTTON_TEXT = 'Exactly'
    _LESS_THAN_EQUAL_BUTTON_TEXT = 'Less than or equal to'
    _GREATER_THAN_BUTTON_TEXT = 'Greater than'
    _ALL_BUTTON_TEXT = 'ALL'
    _ONE_BUTTON_TEXT = 'ONE'

    def __init__(self, queryData, parent=None):
        super(exportDialog, self).__init__(parent)

        self.queryData = queryData

        # WIDGETS ------------------------------------------------------------------
        mainLayout = QVBoxLayout()
        spinBoxLayout = QHBoxLayout()
        radioButtonLayout = QGridLayout()
        saveFileLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()

        selectionText = QLabel('Select genes with:')

        self.filterSpinBox = QSpinBox()
        self.filterSpinBox.setMaximumWidth(50)
        # set max possible value to total amount of tools
        self.filterSpinBox.setMaximum(list(toolVal for toolVal in queryData.tools.values()).count(True))
        self.filterSpinBox.setMinimum(1)
        self.filterSpinBox.setValue(self.filterSpinBox.maximum())

        callsLabel = QLabel('Calls')

        self.radioButtons = []
        exactlyRadioButton = QRadioButton(self._EXACTLY_BUTTON_TEXT)
        exactlyRadioButton.clicked.connect(lambda: self.setSpinBoxRange(exactlyRadioButton))
        self.radioButtons.append(exactlyRadioButton)
        greaterThanRadioButton = QRadioButton(self._GREATER_THAN_BUTTON_TEXT)
        greaterThanRadioButton.clicked.connect(lambda: self.setSpinBoxRange(greaterThanRadioButton))
        self.radioButtons.append(greaterThanRadioButton)
        lessThanEqualRadioButton = QRadioButton(self._LESS_THAN_EQUAL_BUTTON_TEXT)
        lessThanEqualRadioButton.clicked.connect(lambda: self.setSpinBoxRange(lessThanEqualRadioButton))
        lessThanEqualRadioButton.setChecked(True)
        self.radioButtons.append(lessThanEqualRadioButton)
        allRadioButton = QRadioButton(self._ALL_BUTTON_TEXT)
        allRadioButton.clicked.connect(lambda: self.setSpinBoxRange(allRadioButton))
        self.radioButtons.append(allRadioButton)
        oneRadioButton = QRadioButton(self._ONE_BUTTON_TEXT)
        oneRadioButton.clicked.connect(lambda: self.setSpinBoxRange(oneRadioButton))
        self.radioButtons.append(oneRadioButton)

        exportButton = QPushButton('Export')
        exportButton.clicked.connect(self.exportPressed)
        exportButton.setDefault(True)

        cancelButton = QPushButton('Cancel')
        cancelButton.clicked.connect(self.cancelPressed)

        self.saveLineEdit = QLineEdit()
        self.saveLineEdit.setMinimumWidth(200)
        self.saveLineEdit.textEdited.connect(self.saveLineEdited)
        saveButton = QPushButton('Save as...')
        saveButton.clicked.connect(self.saveFile)

        # LAYOUT -------------------------------------------------------------------
        spinBoxLayout.addWidget(self.filterSpinBox)
        spinBoxLayout.addWidget(callsLabel)

        mainLayout.addWidget(selectionText)
        mainLayout.addLayout(spinBoxLayout)

        radioButtonLayout.addWidget(lessThanEqualRadioButton, 0, 0)
        radioButtonLayout.addWidget(allRadioButton, 0, 1)
        radioButtonLayout.addWidget(greaterThanRadioButton, 1, 0)
        radioButtonLayout.addWidget(oneRadioButton, 1, 1)
        radioButtonLayout.addWidget(exactlyRadioButton, 2, 0)

        mainLayout.addLayout(radioButtonLayout)

        saveFileLayout.addWidget(self.saveLineEdit)
        saveFileLayout.addWidget(saveButton)

        buttonLayout.addWidget(exportButton)
        buttonLayout.addWidget(cancelButton)

        mainLayout.addLayout(saveFileLayout)
        mainLayout.addLayout(buttonLayout)

        # WINDOW --------------------------------------------------------------------
        self.setWindowTitle('Export Dialogue')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setLayout(mainLayout)

    def exportPressed(self):
        """
        Called when export is pressed
        :return:
        """
        if not self._checkValidSaveFile():
            return
        else:
            self.accept()

    def cancelPressed(self):
        """
        Called when cancel is pressed
        """
        self.reject()

    def accept(self):
        """
        Called by exportPressed
        """
        QDialog.accept(self)

    def reject(self):
        """
        Called by cancelPressed
        """
        QDialog.reject(self)

    @abstractmethod
    def saveFile(self):
        """
        TO BE IMPLEMENTED BY SUBCLASS
        """
        pass

    def setSpinBoxRange(self, radioButton: QRadioButton):
        """
        Dynamically sets the range of spinboxes based upon the selected filter type
        :param radioButton: radioButton which was toggled
        """
        buttonText = radioButton.text()

        # enable the spinbox if it was disabled
        self.filterSpinBox.setEnabled(True)

        # set range from 1-max
        if buttonText == self._EXACTLY_BUTTON_TEXT or buttonText == self._LESS_THAN_EQUAL_BUTTON_TEXT:
            maxVal = list(toolVal for toolVal in self.queryData.tools.values()).count(True)
            self.filterSpinBox.setMaximum(maxVal)
            self.filterSpinBox.setMinimum(1)

        # set range from 0, max - 1
        elif buttonText == self._GREATER_THAN_BUTTON_TEXT:
            maxVal = list(toolVal for toolVal in self.queryData.tools.values()).count(True) - 1
            self.filterSpinBox.setMaximum(maxVal)
            self.filterSpinBox.setMinimum(0)

        elif buttonText == self._ALL_BUTTON_TEXT:
            # set box to max and disable
            self.filterSpinBox.setValue(list(toolVal for toolVal in self.queryData.tools.values()).count(True))
            self.filterSpinBox.setDisabled(True)

        elif buttonText == self._ONE_BUTTON_TEXT:
            # set box to one and disable
            self.filterSpinBox.setValue(1)
            self.filterSpinBox.setDisabled(True)

    def saveLineEdited(self):
        """
        Called when the save line edit is changed
        :return:
        """
        # reset border to default
        self.saveLineEdit.setStyleSheet('')

    def _checkValidSaveFile(self):
        """
        Checks if the file path given in the line edit is valid
        """

        # if the given directory exists
        if not os.path.isdir(os.path.split(self.saveLineEdit.text())[0]):
            self.saveLineEdit.setStyleSheet('border: 1px solid red')
            QMessageBox.warning(self,
                                'Directory Does Not Exist',
                                'Selected directory does not exist.')
            return False

        # check if a directory and file were given
        elif os.path.split(self.saveLineEdit.text())[1] == '':
            self.saveLineEdit.setStyleSheet('border: 1px solid red')
            QMessageBox.warning(self,
                                'Select a Save File',
                                'Please select a file to save to.')
            return False

        # save file is valid
        else:
            return True
