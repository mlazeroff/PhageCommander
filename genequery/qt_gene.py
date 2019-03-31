from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from genequery import Gene

# list of tool calls
TOOL_NAMES = ['gm', 'hmm', 'heuristic', 'gms', 'gms2', 'glimmer', 'prodigal']


class SettingsDialog(QDialog):
    """
    Dialog for Settings
    """

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        # WIDGETS ----------------------------------------------------------------------------------
        self.tabWidget = QTabWidget()

        # TAB WIDGET TABS --------------------------------------------------------------------------
        self.toolTab = QWidget()
        self.tabWidget.addTab(self.toolTab, 'Tools')

        # Tools Tab Layout
        toolLayout = QVBoxLayout()

        # genemark widgets
        genemarkLabel = QLabel('Genemark')
        genemarkLabelFont = QFont()
        genemarkLabelFont.setUnderline(True)
        genemarkLabel.setFont(genemarkLabelFont)
        toolLayout.addWidget(genemarkLabel)
        genemarkBoxes = QGridLayout()
        gmBox = QCheckBox('Genemark')
        hmmBox = QCheckBox('HMM')
        heuristicBox = QCheckBox('Heuristic')
        gmsBox = QCheckBox('GMS')
        gms2Box = QCheckBox('GMS2')

        genemarkBoxes.addWidget(gmBox, 0, 0)
        genemarkBoxes.addWidget(hmmBox, 0, 1)
        genemarkBoxes.addWidget(heuristicBox, 0, 2)
        genemarkBoxes.addWidget(gmsBox, 1, 0)
        genemarkBoxes.addWidget(gms2Box, 1, 1)
        toolLayout.addLayout(genemarkBoxes)

        # glimmer widgets
        glimmerLabel = QLabel('Glimmer')
        glimmerLabel.setFont(genemarkLabelFont)
        genemarkBoxes.addWidget(glimmerLabel, 2, 0)
        glimmerBox = QCheckBox('Glimmer')
        genemarkBoxes.addWidget(glimmerBox, 3, 0)

        # prodigal widgets
        prodigalLabel = QLabel('Prodigal')
        prodigalLabel.setFont(genemarkLabelFont)
        prodigalBox = QCheckBox('Prodigal')
        genemarkBoxes.addWidget(prodigalLabel, 2, 1)
        genemarkBoxes.addWidget(prodigalBox, 3, 1)

        self.toolTab.setLayout(toolLayout)

        # Tools - Genemark Widgets
        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)


class ToolSpecies:
    """
    Class for representing tool/species selections
    """
    tools = {key: True for key in TOOL_NAMES}
    species = ''


class NewFileDialog(QDialog):
    """
    Dialog shown when making a new query
    :returns: list of tools user selected to make queries to
    """

    def __init__(self, tools, parent=None):
        """
        Initialize Dialog
        :param tools: ToolSpecies object
        :param parent: parent widget
        """
        super(NewFileDialog, self).__init__(parent)
        self.toolCalls = tools

        mainLayout = QVBoxLayout()
        checkBoxLayout = QGridLayout()
        speciesLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()

        # label font
        labelFont = QFont()
        labelFont.setUnderline(True)

        # WIDGETS ----------------------------------------------------------------------------------
        # genemark boxes
        genemarkLabel = QLabel('Genemark')
        genemarkLabel.setFont(labelFont)
        gmBox = QCheckBox('Genemark')
        gmBox.setChecked(self.toolCalls.tools['gm'])
        hmmBox = QCheckBox('HMM')
        hmmBox.setChecked(self.toolCalls.tools['hmm'])
        heuristicBox = QCheckBox('Heuristic')
        heuristicBox.setChecked(self.toolCalls.tools['heuristic'])
        gmsBox = QCheckBox('GMS')
        gmsBox.setChecked(self.toolCalls.tools['gms'])
        gms2Box = QCheckBox('GMS2')
        gms2Box.setChecked(self.toolCalls.tools['gms2'])

        # glimmer box
        glimmerLabel = QLabel('Glimmer')
        glimmerLabel.setFont(labelFont)
        glimmerBox = QCheckBox('Glimmer')
        glimmerBox.setChecked(self.toolCalls.tools['glimmer'])

        # prodigal box
        prodigalLabel = QLabel('Prodigal')
        prodigalLabel.setFont(labelFont)
        prodigalBox = QCheckBox('Prodigal')
        prodigalBox.setChecked(self.toolCalls.tools['prodigal'])

        # dictionary mapping tools to checkboxes
        self.toolCheckBoxes = dict()
        self.toolCheckBoxes['gm'] = gmBox
        self.toolCheckBoxes['hmm'] = hmmBox
        self.toolCheckBoxes['heuristic'] = heuristicBox
        self.toolCheckBoxes['gms'] = gmsBox
        self.toolCheckBoxes['gms2'] = gms2Box
        self.toolCheckBoxes['glimmer'] = glimmerBox
        self.toolCheckBoxes['prodigal'] = prodigalBox

        # species combo box
        speciesLabel = QLabel('Species:')
        speciesLabel.setFont(labelFont)
        self.speciesComboBox = QComboBox()
        self.speciesComboBox.addItems(Gene.SPECIES)
        self.speciesComboBox.setMaximumWidth(200)

        # buttons
        self.queryButton = QPushButton('Query')
        self.queryButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.reject)

        # Widget Layout ----------------------------------------------------------------------------
        # genemark
        checkBoxLayout.addWidget(genemarkLabel, 0, 0)
        checkBoxLayout.addWidget(gmBox, 1, 0)
        checkBoxLayout.addWidget(hmmBox, 1, 1)
        checkBoxLayout.addWidget(heuristicBox, 1, 2)
        checkBoxLayout.addWidget(gmsBox, 2, 0)
        checkBoxLayout.addWidget(gms2Box, 2, 1)
        # glimmer
        checkBoxLayout.addWidget(glimmerLabel, 3, 0)
        checkBoxLayout.addWidget(glimmerBox, 4, 0)
        # prodigal
        checkBoxLayout.addWidget(prodigalLabel, 3, 1)
        checkBoxLayout.addWidget(prodigalBox, 4, 1)

        # species
        speciesLayout.addWidget(speciesLabel)
        speciesLayout.addWidget(self.speciesComboBox)

        # buttons
        buttonLayout.addWidget(self.queryButton)
        buttonLayout.addWidget(self.cancelButton)

        mainLayout.addLayout(checkBoxLayout)
        mainLayout.addLayout(speciesLayout)
        mainLayout.addLayout(buttonLayout)

        # Dialog Settings --------------------------------------------------------------------------
        self.setLayout(mainLayout)
        self.setWindowTitle('Select Query Tools')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)

    @pyqtSlot()
    def accept(self):
        """
        On Clicking "Query"
        """
        # update tool calls based on user selection
        for key in self.toolCalls.tools.keys():
            self.toolCalls.tools[key] = self.toolCheckBoxes[key].isChecked()

        # update species
        self.toolCalls.species = self.speciesComboBox.currentText()

        QDialog.accept(self)

    @pyqtSlot()
    def reject(self):
        """
        On Clicking "Cancel"
        """
        QDialog.reject(self)


class GeneMain(QMainWindow):
    """
    Main Window
    """

    def __init__(self, parent=None):
        super(GeneMain, self).__init__(parent)

        # WIDGETS ----------------------------------------------------------------------------------
        # dock
        tableDock = QDockWidget('Table', self)
        tableDock.setObjectName('tableDock')
        tableDock.setAllowedAreas(Qt.TopDockWidgetArea)
        tableDock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        # status bar
        status = self.statusBar()
        status.showMessage('Ready', 5000)

        # ACTIONS ----------------------------------------------------------------------------------
        # new query
        newFileAction = self.createAction('&New...', self.fileNew, QKeySequence.New,
                                          tip='Create a new query')

        # MENUS ------------------------------------------------------------------------------------
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenuActions = (newFileAction,)
        self.fileMenu.addActions(self.fileMenuActions)

        # VARIABLES --------------------------------------------------------------------------------
        self.toolCalls = ToolSpecies()

        # SETTINGS ---------------------------------------------------------------------------------
        self.setWindowTitle('GeneQuery')

    # ACTION METHODS -------------------------------------------------------------------------------
    @pyqtSlot()
    def fileNew(self):
        dialog = NewFileDialog(self.toolCalls)
        if dialog.exec_():
            """
            User initiated query
            """
            print(self.toolCalls.tools)
            print(self.toolCalls.species)
        else:
            """
            User canceled query
            """
            pass

    # HELPER METHODS -------------------------------------------------------------------------------
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False,
                     signal='triggered()'):
        """
        Helper method for generating QActions
        :param text: name of the action
        :param slot: pyqtSlot
        :param shortcut: shortcut to map to
        :param icon: path to action icon
        :param tip: tooltip help string
        :param checkable: True if an ON/OFF action
        :param signal:
        :return: QAction
        """
        action = QAction(text, self)
        if slot is not None:
            action.triggered.connect(slot)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if icon is not None:
            action.setIcon(QIcon(icon))
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if checkable:
            action.setCheckable(True)

        return action


if __name__ == '__main__':
    app = QApplication([])
    window = GeneMain()
    window.show()
    app.exec_()
