from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from genequery import Gene
import os
import time

# list of tool calls
TOOL_NAMES = ['gm', 'hmm', 'heuristic', 'gms', 'gms2', 'glimmer', 'prodigal']

# mappings of tool names to appropriate methods
# [queryMethod, parseMethod]
TOOL_METHODS = {'gm': [Gene.GeneFile.genemark_query,
                       Gene.GeneParse.parse_genemark],
                'hmm': [Gene.GeneFile.genemarkhmm_query,
                        Gene.GeneParse.parse_genemarkHmm],
                'heuristic': [Gene.GeneFile.genemark_heuristic_query,
                              Gene.GeneParse.parse_genemarkHeuristic],
                'gms': [Gene.GeneFile.genemarks_query,
                        Gene.GeneParse.parse_genemarkS],
                'gms2': [Gene.GeneFile.genemarks2_query,
                         Gene.GeneParse.parse_genemarkS2],
                'glimmer': [Gene.GeneFile.glimmer_query,
                            Gene.GeneParse.parse_glimmer],
                'prodigal': [Gene.GeneFile.prodigal_query,
                             Gene.GeneParse.parse_prodigal]}


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


class QueryData:
    """
    Class for representing tool/species selections
    """
    # tools to call
    tools = {key: True for key in TOOL_NAMES}
    # species of the DNA sequence
    species = ''
    # path of the DNA file
    fileName = ''
    # tool data
    toolData = dict()


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
        self.queryData = tools

        mainLayout = QVBoxLayout()
        checkBoxLayout = QGridLayout()
        speciesLayout = QHBoxLayout()
        dnaFileLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()

        # label font
        labelFont = QFont()
        labelFont.setUnderline(True)

        # WIDGETS ----------------------------------------------------------------------------------
        # genemark boxes
        genemarkLabel = QLabel('Genemark')
        genemarkLabel.setFont(labelFont)
        gmBox = QCheckBox('Genemark')
        gmBox.setChecked(self.queryData.tools['gm'])
        hmmBox = QCheckBox('HMM')
        hmmBox.setChecked(self.queryData.tools['hmm'])
        heuristicBox = QCheckBox('Heuristic')
        heuristicBox.setChecked(self.queryData.tools['heuristic'])
        gmsBox = QCheckBox('GMS')
        gmsBox.setChecked(self.queryData.tools['gms'])
        gms2Box = QCheckBox('GMS2')
        gms2Box.setChecked(self.queryData.tools['gms2'])

        # glimmer box
        glimmerLabel = QLabel('Glimmer')
        glimmerLabel.setFont(labelFont)
        glimmerBox = QCheckBox('Glimmer')
        glimmerBox.setChecked(self.queryData.tools['glimmer'])

        # prodigal box
        prodigalLabel = QLabel('Prodigal')
        prodigalLabel.setFont(labelFont)
        prodigalBox = QCheckBox('Prodigal')
        prodigalBox.setChecked(self.queryData.tools['prodigal'])

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

        # dna file input
        fileLabel = QLabel('Fasta File:')
        fileLabel.setFont(labelFont)
        self.fileEdit = QLineEdit()
        fileButton = QPushButton('Open...')
        fileButton.clicked.connect(self.openFileDialog)

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

        # file
        dnaFileLayout.addWidget(self.fileEdit)
        dnaFileLayout.addWidget(fileButton)

        # buttons
        buttonLayout.addWidget(self.queryButton)
        buttonLayout.addWidget(self.cancelButton)

        mainLayout.addLayout(checkBoxLayout)
        mainLayout.addLayout(speciesLayout)
        mainLayout.addWidget(fileLabel)
        mainLayout.addLayout(dnaFileLayout)
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
        # update tool calls based on user selection + allocates entry in toolData
        for key in self.queryData.tools.keys():
            self.queryData.tools[key] = self.toolCheckBoxes[key].isChecked()
            if self.queryData.tools[key] is True:
                self.queryData.toolData[key] = None

        # check if no tools were selected
        if True not in self.queryData.tools.values():
            QMessageBox.warning(self, 'Please select a tool',
                                'No tools are selected. Please choose at least one.')
            return

        # update species
        self.queryData.species = self.speciesComboBox.currentText()

        # check if dna file was given
        if self.fileEdit.text() == '':
            QMessageBox.warning(self, 'Missing DNA File',
                                'Please provide a fasta DNA file.')
            return

        # check if file exists
        if not os.path.isfile(self.fileEdit.text()):
            QMessageBox.warning(self, 'File Does not Exist',
                                'Selected DNA file does not exist.')
            return

        # update return values
        self.queryData.fileName = self.fileEdit.text()

        QDialog.accept(self)

    @pyqtSlot()
    def reject(self):
        """
        On Clicking "Cancel"
        """
        QDialog.reject(self)

    def openFileDialog(self):
        """
        Open a dialog for user to select DNA file
        """
        file = QFileDialog.getOpenFileName(self, 'Open DNA File')

        # if file was chosen, set file line edit
        if file[0]:
            self.fileEdit.setText(file[0])


class SampleThread(QThread):
    incrementSig = pyqtSignal()

    def __init__(self, num):
        QThread.__init__(self)
        self.num = num
        self.abort = False

    def run(self):
        index = 0
        while index <= self.num and not self.abort:
            index += 1
            self.incrementSig.emit()
            time.sleep(2)

    def __del__(self):
        # self.wait()
        print('hi im about to be deleted')

    @pyqtSlot()
    def abortThread(self):
        self.abort = True


class QueryThread(QThread):
    """
    Thread for making performing the call to a gene prediction tool and parsing the data
    Returns the list of Genes via reference
    """

    def __init__(self, geneFile, tool, queryData):
        """
        Constructor
        :param geneFile: GeneFile object of DNA file
        :param tool: tool to call
            * See TOOL_NAMES global
        :param geneData:
        """
        super(QueryThread, self).__init__()

        self.tool = tool
        self.queryData = queryData
        self.geneFile = geneFile

    def run(self):
        """
        Performs the query of the gene prediction tool and parses the output data
        :return: a list of Genes is returned through self.geneData
        """
        queryMethod = TOOL_METHODS[self.tool][0]
        parseMethod = TOOL_METHODS[self.tool][1]

        # perform query
        # if query is unsuccessful, return the error instead
        try:
            queryMethod(self.geneFile)
        except Exception as e:
            self.queryData.toolData[self.tool] = e
            return

        # perform parsing of data
        try:
            genes = parseMethod(self.geneFile.query_data[self.tool])
        except Exception as e:
            self.queryData.toolData[self.tool] = e
            return

        # update query object with genes
        self.queryData.toolData[self.tool] = genes


class QueryManager(QThread):
    """
    Thread for managing gene prediction tool calls
    """
    # signal emitted each time a querying thread returns
    progressSig = pyqtSignal()

    def __init__(self, queryData):
        """
        Initializes and starts threads for each tool to be called
        :param queryData: QueryData object
        :param filePath: path to the DNA fasta file
            * file should be checked to exist prior
        """
        super(QueryManager, self).__init__()

        # VARIABLES --------------------------------------------------------------------------------
        self.queryData = queryData

        # create GeneFile
        self.geneFile = Gene.GeneFile(self.queryData.fileName, self.queryData.species)

        # THREAD ALLOCATIONS -----------------------------------------------------------------------
        self.threads = []
        for tool in self.queryData.tools:
            if self.queryData.tools[tool] is True:
                self.threads.append(QueryThread(self.geneFile, tool, self.queryData))

        for thread in self.threads:
            thread.finished.connect(self.queryReturn)

        for thread in self.threads:
            thread.start()

    @pyqtSlot()
    def queryReturn(self):
        # emit progressSig to update progressBar
        self.progressSig.emit()

        # keep waiting until all calls have returned
        for tool in self.queryData.toolData:
            if self.queryData.toolData[tool] is None:
                return

        self.exit()

    def abort(self):
        self.exit()


class QueryDialog(QDialog):
    """
    Dialog for querying prediction tools
    """

    def __init__(self, queryData, parent=None):
        super(QueryDialog, self).__init__(parent)

        self.queryData = queryData

        mainLayout = QVBoxLayout()
        # WIDGETS ----------------------------------------------------------------------------------
        self.thread = QueryManager(queryData)
        self.thread.finished.connect(self.queryStop)
        self.thread.progressSig.connect(self.updateProgress)

        self.progressBar = QProgressBar()
        # set progress max to the amount of tools to be queried
        print(self.queryData.tools)
        self.progressBar.setMaximum(list(self.queryData.tools.values()).count(True))

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.thread.abort)

        # WIDGET LAYOUT ----------------------------------------------------------------------------
        mainLayout.addWidget(self.progressBar)
        mainLayout.addWidget(self.cancelButton)
        self.setLayout(mainLayout)

        # SETTINGS ---------------------------------------------------------------------------------
        self.setWindowFlags(Qt.WindowTitleHint)
        self.setWindowTitle('Querying Tools...')

        self.progressBar.setValue(0)
        self.thread.start()

    def updateProgress(self):
        """
        Increment the progress bar by one
        """
        self.progressBar.setValue(self.progressBar.value() + 1)

    def queryStop(self):
        """
        Called when query thread stops - whether by finishing or user pressing cancel
        """
        # if successful query - display success message
        if self.progressBar.value() == self.progressBar.maximum():
            QMessageBox.information(self, 'Done', 'Done! Query Successful')
            print(self.queryData.toolData)
            QDialog.accept(self)
        else:
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
        self.queryData = QueryData()

        # SETTINGS ---------------------------------------------------------------------------------
        self.setWindowTitle('GeneQuery')

    # ACTION METHODS -------------------------------------------------------------------------------
    @pyqtSlot()
    def fileNew(self):
        dialog = NewFileDialog(self.queryData)
        # if user initiates a query
        if dialog.exec_():
            queryDialog = QueryDialog(self.queryData)
            # query to tools is successful
            if queryDialog.exec_():
                pass
            # query was canceled by user
            else:
                pass

        # user does not initiate query
        else:
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
