import os
from abc import abstractmethod
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from phagecommander.Utilities.Tools import *

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
    _INVALID_SAVE_FILE_BORDER = 'border: 1px solid red'

    def __init__(self, queryData, settings, parent=None):
        super(exportDialog, self).__init__(parent)

        self.queryData = queryData
        self.settings = settings

        # VARIABLES -----------------------------------------------------------------
        # currently selected radiobutton - defaults to ALL
        self.currentSelection = self._LESS_THAN_EQUAL_BUTTON_TEXT
        self.toolCount = 0
        for tool in self.queryData.tools:
            if tool in GENE_TOOLS and self.queryData.tools[tool] is True:
                self.toolCount += 1
        self.saveFileName = ''

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
        self.filterSpinBox.setMaximum(self.toolCount)
        self.filterSpinBox.setMinimum(1)
        self.filterSpinBox.setValue(self.filterSpinBox.maximum())

        callsLabel = QLabel('Calls')

        self.radioButtons = []
        exactlyRadioButton = QRadioButton(self._EXACTLY_BUTTON_TEXT)
        exactlyRadioButton.clicked.connect(lambda: self.buttonClicked(exactlyRadioButton))
        self.radioButtons.append(exactlyRadioButton)
        greaterThanRadioButton = QRadioButton(self._GREATER_THAN_BUTTON_TEXT)
        greaterThanRadioButton.clicked.connect(lambda: self.buttonClicked(greaterThanRadioButton))
        self.radioButtons.append(greaterThanRadioButton)
        lessThanEqualRadioButton = QRadioButton(self._LESS_THAN_EQUAL_BUTTON_TEXT)
        lessThanEqualRadioButton.clicked.connect(lambda: self.buttonClicked(lessThanEqualRadioButton))
        lessThanEqualRadioButton.setChecked(True)
        self.radioButtons.append(lessThanEqualRadioButton)
        allRadioButton = QRadioButton(self._ALL_BUTTON_TEXT)
        allRadioButton.clicked.connect(lambda: self.buttonClicked(allRadioButton))
        self.radioButtons.append(allRadioButton)
        oneRadioButton = QRadioButton(self._ONE_BUTTON_TEXT)
        oneRadioButton.clicked.connect(lambda: self.buttonClicked(oneRadioButton))
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

    def buttonClicked(self, radioButton: QRadioButton):
        """
        Called when a radio button is toggled
        :param radioButton: QRadioButton which was toggled
        """

        # set the range of the spinbox
        self.setSpinBoxRange(radioButton)

        # set the currentSelection
        self.currentSelection = radioButton.text()

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
            maxVal = self.toolCount
            self.filterSpinBox.setMaximum(maxVal)
            self.filterSpinBox.setMinimum(1)

        # set range from 0, max - 1
        elif buttonText == self._GREATER_THAN_BUTTON_TEXT:
            maxVal = self.toolCount - 1
            self.filterSpinBox.setMaximum(maxVal)
            self.filterSpinBox.setMinimum(0)

        elif buttonText == self._ALL_BUTTON_TEXT:
            # set box to max and disable
            self.filterSpinBox.setValue(self.toolCount)
            self.filterSpinBox.setDisabled(True)

        elif buttonText == self._ONE_BUTTON_TEXT:
            # set box to one and disable
            self.filterSpinBox.setValue(1)
            self.filterSpinBox.setDisabled(True)

    def getSelection(self):
        """
        :return: The currently selected button and filter amount in a tuple
                (<selected_button_text>, <filter_amount>)
        """
        return self.currentSelection, self.filterSpinBox.value()

    def getFilterFunction(self):
        """
        :return: A filter function based upon the current dialog selection
            * Filter function is of the following form:
                lambda x: x <= <filter_amount>
                lambda x: x == <filter_amount>
                lambda x: x > <filter_amount>
        """
        filterAmount = self.filterSpinBox.value()

        filterFunctions = {
            self._ALL_BUTTON_TEXT: lambda x: x == filterAmount,
            self._LESS_THAN_EQUAL_BUTTON_TEXT: lambda x: x <= filterAmount,
            self._GREATER_THAN_BUTTON_TEXT: lambda x: x > filterAmount,
            self._EXACTLY_BUTTON_TEXT: lambda x: x == filterAmount,
            self._ONE_BUTTON_TEXT: lambda x: x == filterAmount
        }

        return filterFunctions[self.currentSelection]

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

        invalid = False
        # if empty save file
        if self.saveLineEdit.text() == '':
            self.saveLineEdit.setStyleSheet(self._INVALID_SAVE_FILE_BORDER)
            QMessageBox.warning(self,
                                'File Not Given',
                                'Select a file to save to.')
            invalid = True

        # if the given directory exists
        elif not os.path.isdir(os.path.split(self.saveLineEdit.text())[0]):
            self.saveLineEdit.setStyleSheet(self._INVALID_SAVE_FILE_BORDER)
            QMessageBox.warning(self,
                                'Directory Does Not Exist',
                                'Selected directory does not exist.')
            invalid = True

        # check if a directory and file were given
        elif os.path.split(self.saveLineEdit.text())[1] == '':
            self.saveLineEdit.setStyleSheet(self._INVALID_SAVE_FILE_BORDER)
            QMessageBox.warning(self,
                                'Select a Save File',
                                'Please select a file to save to.')
            invalid = True

        if invalid:
            return False

        # save file is valid
        else:
            self.saveFileName = self.saveLineEdit.text()
            return True


if __name__ == '__main__':
    from phagecommander.phagecom import QueryData

    app = QApplication([])
    dig = exportDialog(QueryData(), QSettings())
    dig.show()
    app.exec_()
    print(dig.saveFileName)
