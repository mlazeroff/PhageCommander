import os
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from genequery import Gene

APP_NAME = 'GeneQuery'

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


class ColorTable(QWidget):
    CELL_COLOR_SETTING = 'table/cell_color/'
    MAJORITY_TEXT_SETTING = 'table/majority_text_color/'
    MINORITY_TEXT_SETTING = 'table/minority_text_color/'
    _TABLE_COLUMN_HEADERS = ['Cell Color', 'Majority Text', 'Minority Text']
    _TABLE_MAJORITY_MINORITY_DEFAULT_TEXT = '4099'
    _CELL_COLOR_COLUMN = 0
    _MAJORITY_TEXT_COLUMN = 1
    _MINORITY_TEXT_COLUMN = 2
    _DEFAULT_CELL_COLORS = [
        (255, 255, 255),
        (218, 238, 243),
        (183, 222, 232),
        (146, 205, 220),
        (49, 134, 155),
        (33, 89, 103),
        (21, 59, 68)
    ]
    _DEFAULT_MAJORITY_COLORS = [
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (255, 255, 255),
        (255, 255, 255),
        (255, 255, 255)
    ]
    _DEFAULT_MINORITY_COLORS = [
        (255, 75, 75),
        (255, 75, 75),
        (255, 75, 75),
        (255, 75, 75),
        (255, 75, 75),
        (255, 75, 75),
        (255, 75, 75),
    ]

    def __init__(self, settings, parent=None):
        super(ColorTable, self).__init__(parent)
        self.settings = settings

        layout = QVBoxLayout()

        # WIDGETS ------------------------------------------------------------------------------------------------------
        # Color Selection Table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(7)
        self.tableWidget.setColumnCount(len(self._TABLE_COLUMN_HEADERS))
        self.tableWidget.setHorizontalHeaderLabels(self._TABLE_COLUMN_HEADERS)
        self.tableWidget.horizontalHeader()
        self.tableWidget.setSelectionMode(QTableWidget.NoSelection)
        self.tableWidget.cellClicked.connect(self.tableClick)
        self.tableWidget.setCornerButtonEnabled(False)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.horizontalScrollBar().setDisabled(True)
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.verticalScrollBar().setDisabled(True)
        columnWidth = self.tableWidget.columnWidth(0)
        vertHeaderWidth = self.tableWidget.verticalHeader().width()
        self.tableWidget.setMinimumWidth(vertHeaderWidth + (3 * columnWidth))
        self.tableWidget.setMaximumWidth(vertHeaderWidth + (3 * columnWidth))

        # insert items into table
        tableHeight = self.tableWidget.horizontalHeader().height()
        for i in range(7):
            self.tableWidget.setRowHeight(i, 20)
            tableHeight += self.tableWidget.rowHeight(i)
            item = QTableWidgetItem()
            majorityItem = QTableWidgetItem(self._TABLE_MAJORITY_MINORITY_DEFAULT_TEXT)
            minorityItem = QTableWidgetItem(self._TABLE_MAJORITY_MINORITY_DEFAULT_TEXT)

            # set default cell color if no setting is found
            colorSetting = self.settings.value(self.CELL_COLOR_SETTING + str(i))
            if colorSetting is not None:
                colors = [int(num) for num in colorSetting.split(' ')]
                color = QColor(*colors)
            else:
                color = QColor(*self._DEFAULT_CELL_COLORS[i])
                colorStr = [str(num) for num in self._DEFAULT_CELL_COLORS[i]]
                self.settings.setValue(self.CELL_COLOR_SETTING + str(i), ' '.join(colorStr))
            item.setBackground(color)
            majorityItem.setBackground(color)
            minorityItem.setBackground(color)

            # set default majority color if no setting is found
            majoritySetting = self.settings.value(self.MAJORITY_TEXT_SETTING + str(i))
            if majoritySetting is not None:
                colors = [int(num) for num in majoritySetting.split(' ')]
                color = QColor(*colors)
                majorityItem.setForeground(color)
            else:
                defaultColor = QColor(*self._DEFAULT_MAJORITY_COLORS[i])
                majorityItem.setForeground(defaultColor)
                defaultColorStr = ' '.join([str(x) for x in defaultColor.getRgb()[:3]])
                self.settings.setValue(self.MAJORITY_TEXT_SETTING + str(i), defaultColorStr)

            # set default minority color if no setting is found
            minoritySetting = self.settings.value(self.MINORITY_TEXT_SETTING + str(i))
            if minoritySetting is not None:
                colors = [int(num) for num in minoritySetting.split(' ')]
                color = QColor(*colors)
                minorityItem.setForeground(color)
            else:
                defaultColor = QColor(*self._DEFAULT_MINORITY_COLORS[i])
                minorityItem.setForeground(defaultColor)
                defaultColorStr = ' '.join([str(x) for x in defaultColor.getRgb()[:3]])
                self.settings.setValue(self.MINORITY_TEXT_SETTING + str(i), defaultColorStr)

            # add items to table
            self.tableWidget.setItem(i, self._CELL_COLOR_COLUMN, item)
            self.tableWidget.setItem(i, self._MAJORITY_TEXT_COLUMN, majorityItem)
            self.tableWidget.setItem(i, self._MINORITY_TEXT_COLUMN, minorityItem)
            majorityItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            minorityItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.tableWidget.setMaximumHeight(tableHeight)
        self.tableWidget.setMinimumHeight(tableHeight)

        # reset button
        resetButton = QPushButton('Reset ALL')
        resetButton.clicked.connect(self.resetToDefaultAll)
        layout.addWidget(self.tableWidget)
        layout.addWidget(resetButton)

        self.setLayout(layout)

    @pyqtSlot(int, int)
    def tableClick(self, row, column):
        """
        Called when an item in the table is clicked
        Performs the appropriate action on the item based on the column of item
        :param row:  int
        :param column: int
        """
        if column == self._CELL_COLOR_COLUMN:
            self.changeCellColor(row, column)
        if column == self._MAJORITY_TEXT_COLUMN or column == self._MINORITY_TEXT_COLUMN:
            self.changeTextColor(row, column)

    def changeTextColor(self, row, column):
        """
        Changes the text color of the cell and saves the color to settings
        :param row: int
        :param column: int
        """
        tableItem = self.tableWidget.item(row, column)
        colorDialog = QColorDialog()
        currColor = tableItem.foreground().color()
        color = colorDialog.getColor(currColor, self, 'Select Text Color')
        if color.isValid():
            tableItem.setForeground(color)
            colorStr = ' '.join([str(x) for x in color.getRgb()[:3]])
            if column == self._MAJORITY_TEXT_COLUMN:
                self.settings.setValue(self.MAJORITY_TEXT_SETTING + str(row), colorStr)
            if column == self._MINORITY_TEXT_COLUMN:
                self.settings.setValue(self.MINORITY_TEXT_SETTING + str(row), colorStr)

    def changeCellColor(self, row, column):
        """
        Changes the color of the row and saves color to setting
        :param row: int
        :param column: int
        """
        item = self.tableWidget.item(row, column)
        majorityItem = self.tableWidget.item(row, column + 1)
        minorityItem = self.tableWidget.item(row, column + 2)
        colorDialog = QColorDialog()
        currColor = item.background().color()
        color = colorDialog.getColor(currColor, self, 'Select Cell Color')
        if color.isValid():
            item.setBackground(color)
            majorityItem.setBackground(color)
            minorityItem.setBackground(color)
            colorStr = ' '.join([str(x) for x in color.getRgb()[:3]])
            self.settings.setValue(self.CELL_COLOR_SETTING + str(row), colorStr)

    def resetToDefaultAll(self):
        """
        Resets all rows to default colors
        """
        # prompt user if they wish to reset
        response = QMessageBox.warning(self,
                                       'Reset to Default',
                                       'Reset to Default? - Existing settings will be reset',
                                       QMessageBox.Ok | QMessageBox.Cancel)

        if response == QMessageBox.Ok:
            for row in range(self.tableWidget.rowCount()):
                # set majority text color
                majorityItem = self.tableWidget.item(row, self._MAJORITY_TEXT_COLUMN)
                majorityColor = QColor(*self._DEFAULT_MAJORITY_COLORS[row])
                majorityItem.setForeground(majorityColor)
                majorityColorStr = ' '.join([str(x) for x in majorityColor.getRgb()[:3]])
                self.settings.setValue(self.MAJORITY_TEXT_SETTING + str(row), majorityColorStr)

                # set minority text color
                minorityItem = self.tableWidget.item(row, self._MINORITY_TEXT_COLUMN)
                minorityColor = QColor(*self._DEFAULT_MINORITY_COLORS[row])
                minorityItem.setForeground(minorityColor)
                minorityColorStr = ' '.join([str(x) for x in minorityColor.getRgb()[:3]])
                self.settings.setValue(self.MINORITY_TEXT_SETTING + str(row), minorityColorStr)

                # set cell color
                cellColorItem = self.tableWidget.item(row, self._CELL_COLOR_COLUMN)
                cellColor = QColor(*self._DEFAULT_CELL_COLORS[row])
                cellColorItem.setBackground(cellColor)
                majorityItem.setBackground(cellColor)
                minorityItem.setBackground(cellColor)
                cellColorStr = ' '.join([str(x) for x in cellColor.getRgb()[:3]])
                self.settings.setValue(self.CELL_COLOR_SETTING + str(row), cellColorStr)


class SettingsDialog(QDialog):
    """
    Dialog for Settings
    """
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, APP_NAME, APP_NAME)

        # WIDGETS --------------------------------------------------------------------
        layout = QVBoxLayout()
        self.tabWidget = QTabWidget()
        self.tableTab = QWidget()

        # UI Initializations
        self.initTableTab()

        # Layout
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        # Window Settings
        self.setWindowTitle('Settings')
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def initTableTab(self):
        self.tableTab = ColorTable(self.settings)
        self.tabWidget.addTab(self.tableTab, 'Table')


class QueryData:
    """
    Class for representing tool/species selections
    """

    def __init__(self):
        # tools to call
        self.tools = {key: True for key in TOOL_NAMES}
        # species of the DNA sequence
        self.species = ''
        # path of the DNA file
        self.fileName = ''
        # tool data
        self.toolData = dict()


class NewFileDialog(QDialog):
    """
    Dialog shown when making a new query
    :returns: list of tools user selected to make queries to
    """

    def __init__(self, queryData, parent=None):
        """
        Initialize Dialog
        :param queryData: ToolSpecies object
        :param parent: parent widget
        """
        super(NewFileDialog, self).__init__(parent)
        self.queryData = queryData

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
        gmBox.setChecked(True)
        hmmBox = QCheckBox('HMM')
        hmmBox.setChecked(True)
        heuristicBox = QCheckBox('Heuristic')
        heuristicBox.setChecked(True)
        gmsBox = QCheckBox('GMS')
        gmsBox.setChecked(True)
        gms2Box = QCheckBox('GMS2')
        gms2Box.setChecked(True)

        # glimmer box
        glimmerLabel = QLabel('Glimmer')
        glimmerLabel.setFont(labelFont)
        glimmerBox = QCheckBox('Glimmer')
        glimmerBox.setChecked(True)

        # prodigal box
        prodigalLabel = QLabel('Prodigal')
        prodigalLabel.setFont(labelFont)
        prodigalBox = QCheckBox('Prodigal')
        prodigalBox.setChecked(True)

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
            genes = parseMethod(self.geneFile.query_data[self.tool], identity=self.tool)
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

    @pyqtSlot()
    def updateProgress(self):
        """
        Increment the progress bar by one
        """
        self.progressBar.setValue(self.progressBar.value() + 1)

    @pyqtSlot()
    def queryStop(self):
        """
        Called when query thread stops - whether by finishing or user pressing cancel
        """
        # if successful query - display success message
        if self.progressBar.value() == self.progressBar.maximum():
            QMessageBox.information(self, 'Done', 'Done! Query Successful')
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

        # gene table
        self.geneTable = QTableWidget()

        # status bar
        self.status = self.statusBar()
        self.status.showMessage('Ready')

        # LAYOUT -----------------------------------------------------------------------------------
        self.setCentralWidget(self.geneTable)

        # ACTIONS ----------------------------------------------------------------------------------
        # new query
        self.newFileAction = self.createAction('&New...', self.fileNew, QKeySequence.New,
                                               tip='Create a new query')

        self.openFileAction = self.createAction('&Open...', self.openFile, QKeySequence.Open,
                                                tip='Open a query file')

        self.saveAsAction = self.createAction('Save as...', self.saveAs,
                                              QKeySequence('Ctrl+Shift+S'),
                                              tip='Save gene data')
        self.saveAsAction.setDisabled(True)

        self.saveAction = self.createAction('&Save', self.save, QKeySequence.Save,
                                            tip='Save gene data')
        self.saveAction.setDisabled(True)

        self.settingsAction = self.createAction('Settings', self.settings, None, )

        # MENUS ------------------------------------------------------------------------------------
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenuActions = (self.newFileAction, self.openFileAction,
                                self.saveAction, self.saveAsAction)
        self.fileMenu.addActions(self.fileMenuActions)
        self.fileMenu.addSeparator()
        self.fileMenu.addActions([self.settingsAction])

        # VARIABLES --------------------------------------------------------------------------------
        self.queryData = QueryData()
        # whether a file is currently opened
        self.fileOpened = False
        # if unsaved changes are present
        self.dirty = False

        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, APP_NAME, APP_NAME)

        # SETTINGS ---------------------------------------------------------------------------------
        self.setWindowTitle('GeneQuery')

    # ACTION METHODS -------------------------------------------------------------------------------
    @pyqtSlot()
    def fileNew(self):
        """
        Action performed when user clicks new file
        """
        # check for unsaved data
        if not self.okToContinue():
            return

        # open query dialog
        dialog = NewFileDialog(self.queryData)
        # if user initiates a query
        if dialog.exec_():
            queryDialog = QueryDialog(self.queryData)
            # query to tools is successful
            if queryDialog.exec_():
                # update open variable
                self.fileOpened = True
                self.dirty = True
                # enable / disable actions
                self.saveAsAction.setEnabled(True)
                self.saveAction.setEnabled(False)
                # update window title with temporary file name
                self.setWindowTitle('GeneQuery - {}'.format('untitled*'))
                # display gene data
                self.updateTable()
            # query was canceled by user - back to main window
            else:
                pass

        # user does not initiate query - back to main window
        else:
            pass

    def openFile(self):
        """
        Open a query data file
        :param fileName: name of the file
        """
        # open file dialog
        fileExtensions = ['GQ Files (*.gq)', 'All Files (*.*)']
        openFileName = QFileDialog.getOpenFileName(self,
                                                   'Open Query File...',
                                                   '',
                                                   ';;'.join(fileExtensions))

        # check if user provided a file
        if openFileName[0] != '':
            # try to open file
            try:
                with open(openFileName[0], 'rb') as openFile:
                    tempQueryData = pickle.load(openFile)
                    # check if file is QueryData object
                    if not isinstance(tempQueryData, QueryData):
                        # show error message
                        QMessageBox.Warning(self, "Invalid File",
                                            "File: {} was not .gq formatted file".format(
                                                openFileName[0]))
                        return
                    # assign new data
                    self.queryData = tempQueryData
                    self.fileOpened = True
                    # change window titles
                    baseFileName = os.path.split(self.queryData.fileName)[1]
                    self.setWindowTitle('GeneQuery - {}'.format(baseFileName))
                    # update table
                    self.updateTable()
            # opening file was unsuccessful
            except FileNotFoundError:
                QMessageBox.warning(self, 'File Does not Exist',
                                    'File: {} does not exist.'.format(openFileName[0]))
            except Exception as e:
                QMessageBox.warning(self, 'Error Opening File',
                                    str(e))

    @pyqtSlot()
    def save(self):
        """
        Action performed when user clicks save
        Saves changes to file
        :return True/False if save was successful
        """
        # save file
        with open(self.queryData.fileName, 'wb') as saveFile:
            pickle.dump(self.queryData, saveFile)
        # update status bar
        self.status.showMessage('Changes saved to: {}'.format(self.queryData.fileName, 5000))
        return True

    @pyqtSlot()
    def saveAs(self):
        """
        Action performed when user clicks Save As...
        Prompts user for a file name and saves content to file
        :return True/False if save was successful
        """
        # ask user what to save file as
        fileExtensions = ['GQ Files (*.gq)', 'All Files (*.*)']
        saveFileName = QFileDialog.getSaveFileName(self,
                                                   'Save as...',
                                                   '',
                                                   ';;'.join(fileExtensions))

        # check if user didn't provide file
        if saveFileName[0] != '':
            with open(saveFileName[0], 'wb') as saveFile:
                self.queryData.fileName = saveFileName[0]
                pickle.dump(self.queryData, saveFile)
            self.status.showMessage('File saved to: {}'.format(saveFileName[0]), 5000)
            # update file name
            # update window title
            baseFileName = os.path.split(self.queryData.fileName)[1]
            self.setWindowTitle('GeneQuery - {}'.format(baseFileName))
            # allow normal saves
            self.saveAction.setEnabled(True)
            self.dirty = False
            return True

        return False

    @pyqtSlot()
    def settings(self):
        preferencesDialog = SettingsDialog()
        preferencesDialog.exec_()
        self.updateTable()

    # WINDOW METHODS -------------------------------------------------------------------------------
    def closeEvent(self, event):
        if self.okToContinue():
            # exit
            pass
        else:
            event.ignore()

    # HELPER METHODS -------------------------------------------------------------------------------
    def okToContinue(self):
        """
        Checks if any unsaved changes exist and prompts user if there are if they'd like to continue
        Called when user tries to close window
        :return True / False
        """
        if self.dirty:
            userReply = QMessageBox.question(self,
                                             'GeneQuery - Unsaved Changes',
                                             'Save changes? - Data may be lost',
                                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            # User cancels - return to main window
            if userReply == QMessageBox.Cancel:
                return False
            # User discards changes - exit
            elif userReply == QMessageBox.No:
                return True
            # User wants to save - save appropriately
            elif userReply == QMessageBox.Yes:
                # if no current save file, prompt for save
                if self.saveAction.isEnabled():
                    self.save()
                else:
                    saveSuccess = self.saveAs()
                    # check if user completed save
                    # don't exit if not saved
                    if not saveSuccess:
                        return False

        return True

    def updateTable(self):
        """
        Displays Gene data to Table
        :return:
        """
        # remove any existing cells
        self.geneTable.setRowCount(0)

        # table options
        self.geneTable.setSelectionMode(QTableWidget.NoSelection)

        # sort genes
        genes = []
        for tool in self.queryData.toolData:
            genes += self.queryData.toolData[tool]
        genes = sorted(genes, key=self.__sort_genes)

        # calculate columns for tools
        toolNumber = len(self.queryData.toolData.keys())
        toolColumns = toolNumber * 4 + toolNumber - 1
        totalColumns = toolColumns + 3
        # add 3 columns for statistics
        self.geneTable.setColumnCount(totalColumns)

        # generate headers
        headerIndexes = dict()
        TOTAL_CALLS_COLUMN = 0
        ALL_COLUMN = 1
        ONE_COLUMN = 2
        currIndex = 3
        headers = ['TOTAL CALLS', 'ALL', 'ONE']
        for ind, tool in enumerate(self.queryData.toolData.keys()):
            headerIndexes[tool] = currIndex
            for i in range(4):
                currIndex += 1
                headers.append(tool.upper())
            if ind != toolNumber - 1:
                headers.append('')
                currIndex += 1

        # set headers
        self.geneTable.setHorizontalHeaderLabels(headers)

        # populate table
        # insert first gene
        currentRow = 0
        self.geneTable.insertRow(currentRow)
        previousGene = genes[0]
        currentGeneCount = 1
        currentGenes = dict()
        geneIndex = headerIndexes[previousGene.identity]
        # direction
        directionItem = QTableWidgetItem(previousGene.direction)
        directionItem.setTextAlignment(Qt.AlignCenter)
        self.geneTable.setItem(currentRow, geneIndex, directionItem)
        # start
        startItem = QTableWidgetItem(str(previousGene.start))
        startItem.setTextAlignment(Qt.AlignCenter)
        self.geneTable.setItem(currentRow, geneIndex + 1, startItem)
        # stop
        stopItem = QTableWidgetItem(str(previousGene.stop))
        stopItem.setTextAlignment(Qt.AlignCenter)
        self.geneTable.setItem(currentRow, geneIndex + 2, stopItem)
        # length
        lengthItem = QTableWidgetItem(str(previousGene.length))
        lengthItem.setTextAlignment(Qt.AlignCenter)
        self.geneTable.setItem(currentRow, geneIndex + 3, lengthItem)

        if previousGene.direction == '+':
            comparingNum = previousGene.start
        else:
            comparingNum = previousGene.stop
        # insert comparing num into dict
        if comparingNum not in currentGenes.keys():
            currentGenes[comparingNum] = 1
        else:
            currentGenes[comparingNum] += 1

        # insert rest of genes
        for gene in genes[1:]:
            geneIndex = headerIndexes[gene.identity]

            # same gene - add to current row
            if gene == previousGene:
                currentGeneCount += 1
            # different gene - create new row
            else:
                # record TOTAL_CALLS, ALL and ONE for previous gene
                totalItem = QTableWidgetItem(str(currentGeneCount))
                totalItem.setTextAlignment(Qt.AlignCenter)
                self.geneTable.setItem(currentRow, TOTAL_CALLS_COLUMN, totalItem)
                if currentGeneCount == toolNumber:
                    allItem = QTableWidgetItem(str('X'))
                    allItem.setTextAlignment(Qt.AlignCenter)
                    self.geneTable.setItem(currentRow, ALL_COLUMN, allItem)
                elif currentGeneCount == 1:
                    oneItem = QTableWidgetItem(str('X'))
                    oneItem.setTextAlignment(Qt.AlignCenter)
                    self.geneTable.setItem(currentRow, ONE_COLUMN, oneItem)

                print('{} - {}'.format(currentRow + 1, currentGenes))

                # color row
                colorSetting = self.settings.value(ColorTable.CELL_COLOR_SETTING + str(currentGeneCount - 1))
                colorNums = [int(num) for num in colorSetting.split(' ')]
                color = QColor(*colorNums)
                # color text
                textColorSetting = self.settings.value(ColorTable.MAJORITY_TEXT_SETTING + str(currentGeneCount - 1))
                textNums = [int(num) for num in textColorSetting.split(' ')]
                textColor = QColor(*textNums)
                # TODO: Figure out minority rule
                for column in range(totalColumns):
                    item = self.geneTable.item(currentRow, column)
                    # insert blank item if none is present
                    if item is None:
                        item = QTableWidgetItem('')
                        self.geneTable.setItem(currentRow, column, item)
                    item.setBackground(color)
                    item.setForeground(textColor)

                # record new gene
                currentGeneCount = 1
                currentGenes = dict()
                currentRow += 1
                self.geneTable.insertRow(currentRow)

            # add gene to table
            # direction
            directionItem = QTableWidgetItem(gene.direction)
            directionItem.setTextAlignment(Qt.AlignCenter)
            self.geneTable.setItem(currentRow, geneIndex, directionItem)
            # start
            startItem = QTableWidgetItem(str(gene.start))
            startItem.setTextAlignment(Qt.AlignCenter)
            self.geneTable.setItem(currentRow, geneIndex + 1, startItem)
            # stop
            stopItem = QTableWidgetItem(str(gene.stop))
            stopItem.setTextAlignment(Qt.AlignCenter)
            self.geneTable.setItem(currentRow, geneIndex + 2, stopItem)
            # length
            lengthItem = QTableWidgetItem(str(gene.length))
            lengthItem.setTextAlignment(Qt.AlignCenter)
            self.geneTable.setItem(currentRow, geneIndex + 3, lengthItem)

            if gene.direction == '+':
                comparingNum = gene.start
            else:
                comparingNum = gene.stop
                # insert comparing num into dict
            if comparingNum not in currentGenes.keys():
                currentGenes[comparingNum] = 1
            else:
                currentGenes[comparingNum] += 1

            # set gene to compare next against
            previousGene = gene

        # record TOTAL_CALLS, ALL and ONE for last gene
        totalItem = QTableWidgetItem(str(currentGeneCount))
        totalItem.setTextAlignment(Qt.AlignCenter)
        self.geneTable.setItem(currentRow, TOTAL_CALLS_COLUMN, totalItem)
        if currentGeneCount == toolNumber:
            allItem = QTableWidgetItem(str('X'))
            allItem.setTextAlignment(Qt.AlignCenter)
            self.geneTable.setItem(currentRow, ALL_COLUMN, allItem)
        elif currentGeneCount == 1:
            oneItem = QTableWidgetItem(str('X'))
            oneItem.setTextAlignment(Qt.AlignCenter)
            self.geneTable.setItem(currentRow, ONE_COLUMN, oneItem)

        print('{} - {}'.format(currentRow + 1, currentGenes))

        # color last row
        colorSetting = self.settings.value(ColorTable.CELL_COLOR_SETTING + str(currentGeneCount - 1))
        colorNums = [int(num) for num in colorSetting.split(' ')]
        color = QColor(*colorNums)
        # color text
        textColorSetting = self.settings.value(ColorTable.MAJORITY_TEXT_SETTING + str(currentGeneCount - 1))
        textNums = [int(num) for num in textColorSetting.split(' ')]
        textColor = QColor(*textNums)
        # TODO: Figure out minority rule
        for column in range(totalColumns):
            item = self.geneTable.item(currentRow, column)
            # insert blank item if blank cell
            if item is None:
                item = QTableWidgetItem('')
                self.geneTable.setItem(currentRow, column, item)
            item.setBackground(color)
            item.setForeground(textColor)

    def __sort_genes(self, gene):
        """
        Used to sort equivalent genes
        :param gene: Gene
        """
        if gene.direction == '+':
            return gene.stop
        else:
            return gene.start

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


# MAIN FUNCTION
def main():
    app = QApplication([])
    window = GeneMain()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
