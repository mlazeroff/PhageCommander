import os
import pickle
import pathlib
from typing import List
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from Bio import SeqIO
from phagecommander import Gene
import phagecommander.GuiWidgets
from phagecommander.Utilities import ThreadData, ProdigalRelease, Aragorn
from phagecommander.Utilities.Tools import *

APP_NAME = 'Phage Commander'

# mappings of tool names to appropriate methods
# [queryMethod, parseMethod]
TOOL_METHODS = {GENEMARK: [Gene.GeneFile.genemark_query,
                           Gene.GeneParse.parse_genemark],
                HMM: [Gene.GeneFile.genemarkhmm_query,
                      Gene.GeneParse.parse_genemarkHmm],
                HEURISTIC: [Gene.GeneFile.genemark_heuristic_query,
                            Gene.GeneParse.parse_genemarkHeuristic],
                GENEMARKS: [Gene.GeneFile.genemarks_query,
                            Gene.GeneParse.parse_genemarkS],
                GENEMARKS2: [Gene.GeneFile.genemarks2_query,
                             Gene.GeneParse.parse_genemarkS2],
                GLIMMER: [Gene.GeneFile.glimmer_query,
                          Gene.GeneParse.parse_glimmer],
                PRODIGAL: [Gene.GeneFile.prodigal_query,
                           Gene.GeneParse.parse_prodigal],
                RAST: [Gene.GeneFile.rastQuery,
                       Gene.GeneParse.parse_rast],
                METAGENE: [Gene.GeneFile.metageneQuery,
                           Gene.GeneParse.parse_metagene],
                ARAGORN: [Gene.GeneFile.aragornQuery,
                          Gene.GeneParse.parse_aragorn]}


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
        # Key - tool (from TOOL_NAMES)
        # Value - List of Genes
        self.toolData = dict()
        # sequence
        self.sequence = ''
        # RAST related information
        self.rastUser = ''
        self.rastPass = ''
        self.rastJobID = None

    def wipeUserCredentials(self):
        """
        Deletes any data relating to a RAST query
        """
        self.rastJobID = None
        self.rastUser = None
        self.rastPass = None


class ColorTable(QWidget):
    CELL_COLOR_SETTING = 'TABLE/cell_color/'
    MAJORITY_TEXT_SETTING = 'TABLE/majority_text_color/'
    MINORITY_TEXT_SETTING = 'TABLE/minority_text_color/'
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
        (21, 59, 68),
        (2, 47, 58),
        (1, 37, 56)
    ]
    _DEFAULT_MAJORITY_COLORS = [
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (255, 255, 255),
        (255, 255, 255),
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
        self.tableWidget.setRowCount(len(GENE_TOOLS))
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
        for i in range(len(GENE_TOOLS)):
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
        Resets all rows in ColorSettings dialog to default colors
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

    @staticmethod
    def checkDefaultSettings(settings):
        """
        Checks if the default color settings exist in the QSettings. If not, populates them
        :param settings: QSettings
        """
        cellColorSettings = [settings.value(ColorTable.CELL_COLOR_SETTING + str(i)) for i in range(len(GENE_TOOLS))]
        majorityColorSettings = [settings.value(ColorTable.MAJORITY_TEXT_SETTING + str(i)) for i in
                                 range(len(GENE_TOOLS))]
        minorityColorSettings = [settings.value(ColorTable.MINORITY_TEXT_SETTING + str(i)) for i in
                                 range(len(GENE_TOOLS))]

        if None in cellColorSettings or None in majorityColorSettings or None in minorityColorSettings:
            ColorTable._setDefaultSettings(settings)

    @staticmethod
    def _setDefaultSettings(settings):
        """
        Sets the settings related to cell colors to default values
        :param settings: QSettings object
        """
        for i in range(len(GENE_TOOLS)):
            # CELL COLORS
            defaultColorStr = ' '.join(str(color) for color in ColorTable._DEFAULT_CELL_COLORS[i])
            settings.setValue(ColorTable.CELL_COLOR_SETTING + str(i), defaultColorStr)

            # MAJORITY COLOR
            defaultColorStr = ' '.join(str(color) for color in ColorTable._DEFAULT_MAJORITY_COLORS[i])
            settings.setValue(ColorTable.MAJORITY_TEXT_SETTING + str(i), defaultColorStr)

            # MINORITY COLOR
            defaultColorStr = ' '.join(str(color) for color in ColorTable._DEFAULT_MINORITY_COLORS[i])
            settings.setValue(ColorTable.MINORITY_TEXT_SETTING + str(i), defaultColorStr)


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


class NewFileDialog(QDialog):
    """
    Dialog shown when making a new query
    :returns: list of tools user selected to make queries to
    """

    _LAST_FASTA_FILE_LOCATION_SETTING = 'NEW_FILE_DIALOG/last_fasta_location'
    _RAST_USERNAME_SETTING = 'NEW_FILE_DIALOG/rast_username'
    _RAST_PASSWORD_SETTING = 'NEW_FILE_DIALOG/rast_password'

    def __init__(self, queryData, settings, prodigalPath=None, parent=None):
        """
        Initialize Dialog
        :param queryData: ToolSpecies object
        :param settings: QSettings
        :param prodigalPath: path to Prodigal binary
            * str or None
        :param parent: parent widget

        """
        super(NewFileDialog, self).__init__(parent)
        self.queryData = queryData
        self.settings = settings

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
        self.hmmBox = QCheckBox('HMM')
        heuristicBox = QCheckBox('Heuristic')
        gmsBox = QCheckBox('GMS')
        gms2Box = QCheckBox('GMS2')

        # glimmer box
        glimmerLabel = QLabel('Glimmer')
        glimmerLabel.setFont(labelFont)
        glimmerBox = QCheckBox('Glimmer')

        # prodigal box
        prodigalLabel = QLabel('Prodigal')
        prodigalLabel.setFont(labelFont)
        prodigalBox = QCheckBox('Prodigal')

        # rast box
        rastLabel = QLabel('RAST')
        rastLabel.setFont(labelFont)
        rastBox = QCheckBox('RAST')

        # metagene box
        METAGENE_LABEL_TEXT = 'Metagene'
        metageneLabel = QLabel(METAGENE_LABEL_TEXT)
        metageneLabel.setFont(labelFont)
        metageneBox = QCheckBox(METAGENE_LABEL_TEXT)

        # aragorn box
        ARAGORN_LABEL_TEXT = 'Aragorn'
        aragornLabel = QLabel(ARAGORN_LABEL_TEXT)
        aragornLabel.setFont(labelFont)
        aragornBox = QCheckBox(ARAGORN_LABEL_TEXT)

        # dictionary mapping tools to checkboxes
        self.toolCheckBoxes = dict()
        self.toolCheckBoxes['gm'] = gmBox
        self.toolCheckBoxes['hmm'] = self.hmmBox
        self.toolCheckBoxes['heuristic'] = heuristicBox
        self.toolCheckBoxes['gms'] = gmsBox
        self.toolCheckBoxes['gms2'] = gms2Box
        self.toolCheckBoxes['glimmer'] = glimmerBox
        self.toolCheckBoxes['prodigal'] = prodigalBox
        self.toolCheckBoxes['rast'] = rastBox
        self.toolCheckBoxes[METAGENE] = metageneBox
        self.toolCheckBoxes[ARAGORN] = aragornBox
        for box in self.toolCheckBoxes.values():
            # set all boxes to default to being checked
            # box.setChecked(True)
            box.setCheckState(Qt.Checked)
            # check to disable the species combobox on every click of a box
            box.stateChanged.connect(self.disableSpeciesCheck)

        # check if Prodigal binary exists, if not, disable Prodigal
        if prodigalPath is None:
            prodigalBox.setCheckable(False)
            prodigalBox.setEnabled(False)

        # species combo box
        speciesLabel = QLabel('Species:')
        speciesLabel.setFont(labelFont)
        self.speciesComboBox = QComboBox()
        self.speciesComboBox.addItems(Gene.SPECIES)
        self.speciesComboBox.setMaximumWidth(250)

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
        checkBoxLayout.addWidget(self.hmmBox, 1, 1)
        checkBoxLayout.addWidget(heuristicBox, 1, 2)
        checkBoxLayout.addWidget(gmsBox, 2, 0)
        checkBoxLayout.addWidget(gms2Box, 2, 1)
        # glimmer
        checkBoxLayout.addWidget(glimmerLabel, 3, 0)
        checkBoxLayout.addWidget(glimmerBox, 4, 0)
        # prodigal
        checkBoxLayout.addWidget(prodigalLabel, 3, 1)
        checkBoxLayout.addWidget(prodigalBox, 4, 1)
        # rast
        checkBoxLayout.addWidget(rastLabel, 3, 2)
        checkBoxLayout.addWidget(rastBox, 4, 2)
        # metagene
        checkBoxLayout.addWidget(metageneLabel, 5, 0)
        checkBoxLayout.addWidget(metageneBox, 6, 0)
        # aragorn
        checkBoxLayout.addWidget(aragornLabel, 5, 1)
        checkBoxLayout.addWidget(aragornBox, 6, 1)

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
        # reset toolData
        self.queryData.toolData = dict()

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

        # if RAST was selected, prompt credential window
        if self.toolCheckBoxes['rast'].isChecked():
            credDialog = phagecommander.GuiWidgets.RastJobDialog(self.queryData)
            # if user exits window without submitting, do not query
            if not credDialog.exec_():
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
        last_fasta_file_location = self.settings.value(self._LAST_FASTA_FILE_LOCATION_SETTING)
        file = QFileDialog.getOpenFileName(self, 'Open DNA File', last_fasta_file_location)

        # if file was chosen, set file line edit
        if file[0]:
            self.fileEdit.setText(file[0])
            # set new last_fasta_location
            fileFolder = os.path.split(file[0])[0]
            self.settings.setValue(self._LAST_FASTA_FILE_LOCATION_SETTING, fileFolder)

    def disableSpeciesCheck(self):
        """
        Disables the species comboBox if none of the selected tools require it
        * Only Hmm uses the species comboBox
        """
        if not self.hmmBox.isChecked():
            self.speciesComboBox.setDisabled(True)
        else:
            self.speciesComboBox.setDisabled(False)

    @staticmethod
    def checkDefaultSettings(settings):
        """
        Checks if required settings exist - if not, populates them
        :param settings: QSettings obj
        """
        # LAST FASTA FILE LOCATION
        if settings.value(NewFileDialog._LAST_FASTA_FILE_LOCATION_SETTING) is None:
            NewFileDialog._setDefaultSettings(settings)

    @staticmethod
    def _setDefaultSettings(settings):
        """
        Populates the default values for the required settings
        :param settings: QSettings obj
        """
        # LAST FASTA FILE LOCATION
        settings.setValue(NewFileDialog._LAST_FASTA_FILE_LOCATION_SETTING, '')


class QueryThread(QThread):
    """
    Thread for making performing the call to a gene prediction tool and parsing the data
    Returns the list of Genes via reference
    """

    def __init__(self, geneFile, tool, queryData, settings):
        """
        Constructor
        :param geneFile: GeneFile object of DNA file
        :param tool: tool to call
        :param settings: QSettings
            * See TOOL_NAMES global
        """
        super(QueryThread, self).__init__()

        self.tool = tool
        self.queryData = queryData
        self.geneFile = geneFile
        self.settings = settings

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
            if self.tool == RAST:
                username = self.queryData.rastUser
                password = self.queryData.rastPass
                jobID = self.queryData.rastJobID
                queryMethod(self.geneFile, username, password, jobId=jobID)
            else:
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

        # wipe RAST user creds
        if self.tool == RAST:
            self.queryData.wipeUserCredentials()


class QueryManager(QThread):
    """
    Thread for managing gene prediction tool calls
    """
    # signal emitted each time a querying thread returns
    progressSig = pyqtSignal()

    def __init__(self, queryData, settings):
        """
        Initializes and starts threads for each tool to be called
        :param queryData: QueryData object
        """
        super(QueryManager, self).__init__()

        # VARIABLES --------------------------------------------------------------------------------
        self.queryData = queryData
        self.settings = settings

        # create GeneFile
        self.geneFile = Gene.GeneFile(self.queryData.fileName, self.queryData.species,
                                      self.settings.value(GeneMain._PRODIGAL_BINARY_LOCATION_SETTING))

        # load sequence
        # with open(self.queryData.fileName) as seqFile:
        #     self.queryData.sequence = seqFile.read().split('\n')[1].lower()
        for seq_rec in SeqIO.parse(self.queryData.fileName, 'fasta'):
            self.queryData.sequence = seq_rec

        # THREAD ALLOCATIONS -----------------------------------------------------------------------
        self.threads = []
        for tool in self.queryData.tools:
            if self.queryData.tools[tool] is True:
                self.threads.append(QueryThread(self.geneFile, tool, self.queryData, self.settings))

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

    def __init__(self, queryData, settings, parent=None):
        super(QueryDialog, self).__init__(parent)

        self.queryData = queryData
        self.settings = settings

        mainLayout = QVBoxLayout()
        # WIDGETS ----------------------------------------------------------------------------------
        self.thread = QueryManager(queryData, self.settings)
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
            # check for any errors returned
            errors = dict()
            for tool in self.queryData.toolData:
                if isinstance(self.queryData.toolData[tool], Exception):
                    errors[tool] = self.queryData.toolData[tool]

            # errors exist
            if len(errors) != 0:
                # print out all tools and their errors
                errorStr = ['{}: {}'.format(tool.upper(), error) for tool, error in errors.items()]
                QMessageBox.information(self, 'Errors while Querying', '\n'.join(errorStr))
                QDialog.reject(self)
            else:
                # success
                QMessageBox.information(self, 'Done', 'Done! Query Successful')
                QDialog.accept(self)
        else:
            QDialog.reject(self)


class exportGenbankDialog(phagecommander.GuiWidgets.exportDialog):
    _LAST_GENBANK_LOCATION_SETTING = 'EXPORT_GENBANK_DIALOG/last_genbank_location'

    def __init__(self, queryData, settings, parent=None):
        super(exportGenbankDialog, self).__init__(queryData, settings, parent=parent)

        # WINDOW ---------------------------------------------------------------
        self.setWindowTitle('Export to Genbank')

    def saveFile(self):
        fileExtensions = ['Genbank (*.gb)',
                          'All Files (*.*)']
        saveFileLocation = self.settings.value(exportGenbankDialog._LAST_GENBANK_LOCATION_SETTING)
        saveFileName = QFileDialog.getSaveFileName(self,
                                                   'Save Genbank File As...',
                                                   saveFileLocation,
                                                   ';;'.join(fileExtensions))

        # if the user gave a file
        if saveFileName[0]:
            self.saveLineEdit.setText(saveFileName[0])

    def accept(self):
        """
        Called when user presses export
        """

        # put all Genes in one list
        filteredGenes = []
        for geneSet in self.queryData.toolData.values():
            filteredGenes.extend(geneSet)

        # filter based on user selection
        filteredGenes = Gene.GeneUtils.filterGenes(filteredGenes, self.getFilterFunction())
        # filtered genes is now List[List[Gene]]

        genesToExport = []
        # find the most frequent Gene in each set of Genes
        for geneSet in filteredGenes:
            genesToExport.append(Gene.GeneUtils.findMostGeneOccurrences(geneSet))

        # output to file
        try:
            Gene.GeneUtils.genbankToFile(str(self.queryData.sequence.seq).lower(), genesToExport, self.saveFileName)
        except PermissionError as e:
            QMessageBox.warning(self,
                                'Permission Denied',
                                'Could not write to: \"{}\". Permission denied.'.format(self.saveFileName))
            # go back to dialogue
            return
        except Exception as e:
            QMessageBox.warning(self,
                                'Could Not Write to File',
                                'Could not write to: \"{}\".\n{}'.format(self.saveFileName, str(e)))
            # go back to dialogue
            return

        # save file location setting
        saveFileDir = os.path.split(self.saveFileName)[0]
        self.settings.setValue(exportGenbankDialog._LAST_GENBANK_LOCATION_SETTING, saveFileDir)

        QDialog.accept(self)

    @staticmethod
    def checkDefaultSettings(settings):
        """
        Checks if required settings exist - if not, populates them
        :param settings: QSettings obj
        """
        # Last save location
        if settings.value(exportGenbankDialog._LAST_GENBANK_LOCATION_SETTING) is None:
            exportGenbankDialog._setDefaultSettings(settings)

    @staticmethod
    def _setDefaultSettings(settings):
        """
        Populates the default values for the required settings
        :param settings: QSettings obj
        """
        # Last save location
        settings.setValue(exportGenbankDialog._LAST_GENBANK_LOCATION_SETTING, '')


class GeneMain(QMainWindow):
    """
    Main Window
    """

    _LAST_OPEN_FILE_LOCATION_SETTING = 'GENE_MAIN/last_open_file_location'
    _PRODIGAL_BINARY_LOCATION_SETTING = 'GENE_MAIN/prodigal_location'
    _LAST_EXCEL_SAVE_LOCATION_SETTING = 'GENE_MAIN/last_excel_location'
    _GENE_TAB_LABEL = 'Genes'
    _TRNA_TAB_LABEL = 'TRNA'

    def __init__(self, parent=None):
        super(GeneMain, self).__init__(parent)

        # WIDGETS ----------------------------------------------------------------------------------
        # central tab widget
        self.tab = QTabWidget()

        # tables
        self.geneTable = QTableWidget()
        self.trnaTable = QTableWidget()

        # status bar
        self.status = self.statusBar()
        self.status.showMessage('Ready')

        # LAYOUT -----------------------------------------------------------------------------------
        self.setCentralWidget(self.tab)
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        # ACTIONS ----------------------------------------------------------------------------------
        # new query
        self.newFileAction = self.createAction('&New...', self.fileNew, QKeySequence.New,
                                               tip='Create a new query')

        self.openFileAction = self.createAction('&Open...', self.openFile, QKeySequence.Open,
                                                tip='Open a query file')

        self.saveAsAction = self.createAction('Save as...', self.saveAs,
                                              QKeySequence('Ctrl+Shift+S'),
                                              tip='Save gene data')

        self.saveAction = self.createAction('&Save', self.save, QKeySequence.Save,
                                            tip='Save gene data')

        self.settingsAction = self.createAction('Settings', self.settings, None, )

        self.exportExcelAction = self.createAction('Excel', self.exportExcel, None)

        self.exportGenbankAction = self.createAction('Genbank', self.exportGenbank, None)

        # MENUS ------------------------------------------------------------------------------------
        # file menu
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenuActions = (self.newFileAction, self.openFileAction,
                                self.saveAction, self.saveAsAction)
        self.fileMenu.addActions(self.fileMenuActions)
        self.fileMenu.addSeparator()

        # export submenu
        exportSubMenu = self.fileMenu.addMenu('Export as...')
        exportSubMenu.addAction(self.exportExcelAction)
        exportSubMenu.addAction(self.exportGenbankAction)

        self.fileMenu.addActions([self.settingsAction])

        # VARIABLES --------------------------------------------------------------------------------
        self.queryData = QueryData()
        # whether a file is currently opened
        self.fileOpened = False
        # if unsaved changes are present
        self.dirty = False
        # if saving is enabled
        self.saveEnabled = False

        self.genes = []

        # Get Settings, populate defaults if they do not exist
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, APP_NAME, APP_NAME)
        self.checkDefaultSettings()

        self.enableActions()
        # SETTINGS ---------------------------------------------------------------------------------
        self.setWindowTitle(APP_NAME)

        # check for Prodigal binary
        self.checkProdigal()

    # ACTION METHODS -------------------------------------------------------------------------------
    @pyqtSlot()
    def fileNew(self):
        """
        Action performed when user clicks new file
        """
        # check for unsaved data
        if not self.okToContinue():
            return

        # temporary data in case user quits the dialogs
        tmpQueryData = QueryData()
        # open query dialog
        dialog = NewFileDialog(tmpQueryData, self.settings, self.settings.value(self._PRODIGAL_BINARY_LOCATION_SETTING))
        # if user initiates a query
        if dialog.exec_():
            # query tools
            self.queryData = tmpQueryData
            queryDialog = QueryDialog(self.queryData, self.settings)

            # query to tools is successful
            if queryDialog.exec_():
                # update open variable
                self.fileOpened = True
                self.dirty = True
                self.saveEnabled = False
                # enable / disable actions
                self.enableActions()
                # update window title with temporary file name
                self.setWindowTitle('{} - {}'.format(APP_NAME, 'untitled*'))
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
        # check for unsaved progressed
        if not self.okToContinue():
            return

        # open file dialog
        openFileDir = self.settings.value(self._LAST_OPEN_FILE_LOCATION_SETTING)
        fileExtensions = ['GQ Files (*.gq)', 'All Files (*.*)']
        openFileName = QFileDialog.getOpenFileName(self,
                                                   'Open Query File...',
                                                   openFileDir,
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
                    self.saveEnabled = True
                    self.enableActions()
                    # save location
                    self.settings.setValue(self._LAST_OPEN_FILE_LOCATION_SETTING, os.path.split(openFileName[0])[0])
                    # change window titles
                    self.setWindowTitle('{} - {}'.format(APP_NAME, openFileName[0]))
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
            self.setWindowTitle('{} - {}'.format(APP_NAME, baseFileName))
            # allow normal saves
            # self.saveAction.setEnabled(True)
            self.saveEnabled = True
            self.dirty = False
            self.enableActions()
            return True

        return False

    @pyqtSlot()
    def settings(self):
        preferencesDialog = SettingsDialog()
        preferencesDialog.exec_()
        self.updateTable()

    @pyqtSlot()
    def exportExcel(self):
        """
        Save the current table output to a .xlsx file
        """
        # get last saved excel location
        excelLocation = pathlib.Path(self.settings.value(self._LAST_EXCEL_SAVE_LOCATION_SETTING))

        # open a save file dialog
        fileExtensions = ['Excel Spreadsheet (*.xlsx)',
                          'All Files (*.*)']
        excelFileName = QFileDialog.getSaveFileName(self,
                                                    'Save Excel Spreadsheet As...',
                                                    str(excelLocation),
                                                    ';;'.join(fileExtensions))

        # if file name was provided, write to file
        if excelFileName[0] != '':

            GENES_USED = False
            TRNA_USED = False
            for key in self.queryData.toolData.keys():
                if key in GENE_TOOLS:
                    GENES_USED = True
                elif key in TRNA_TOOLS:
                    TRNA_USED = True

            wb = Workbook()
            if GENES_USED:
                self._exportTableToExcel(self.geneTable, 'Genes', wb)
            if TRNA_USED:
                self._exportTableToExcel(self.trnaTable, 'TRNA', wb)

            wb.save(filename=excelFileName[0])

            print(excelFileName[0])
            excelLocation = str(pathlib.Path(excelFileName[0]).parent)
            self.settings.setValue(self._LAST_EXCEL_SAVE_LOCATION_SETTING, excelLocation)

            self.status.showMessage('Exported Excel file to: {}'.format(excelFileName[0]), 5000)

    def _exportTableToExcel(self, table: QTableWidget, label: str, wb: Workbook):
        """
        Adds the given table to the Excel Workbook as a new sheet
        :param table: QTableWidget
        :param label: Name of the new sheet
        :param wb: Excel Workbook
        """

        # check if adding to existing workbook
        # if not, rename first sheet
        if wb.sheetnames[0] == 'Sheet':
            ws = wb['Sheet']
            ws.title = label
        else:
            ws = wb.create_sheet(label)

        # add content to spreadsheet
        # add headers
        currentRow = 1
        for column in range(table.columnCount()):
            headerValue = table.horizontalHeaderItem(column).text()
            cell = ws.cell(row=currentRow, column=column + 1, value=headerValue)
            cell.alignment = Alignment(horizontal='center')
            cell.font = Font(bold=True)

        # add content
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                currCell = table.item(row, column)
                cellValue = currCell.text() if currCell is not None else ''
                if currCell is not None:
                    cellColor = currCell.background().color().getRgb()
                    cellRgbString = ''.join(['{:02x}'.format(num) for num in cellColor[:3]])
                    fontColor = currCell.foreground().color().getRgb()
                    fontRgbString = ''.join(['{:02x}'.format(num) for num in fontColor[:3]])

                # convert an integer string to an integer for spreadsheet functionality
                cellValue = int(cellValue) if cellValue.isdecimal() else cellValue
                cell = ws.cell(row=row + 2, column=column + 1, value=cellValue)
                cell.alignment = Alignment(horizontal='center')
                cell.fill = PatternFill(fgColor=cellRgbString, fill_type='solid')
                cell.font = Font(color=fontRgbString)

    @pyqtSlot()
    def exportGenbank(self):

        # create export dialog
        exportDig = exportGenbankDialog(self.queryData, self.settings)
        if exportDig.exec_():
            # display save status
            self.status.showMessage('Exported Genbank file to: {}'.format(exportDig.saveFileName), 5000)

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
                                             '{} - Unsaved Changes'.format(APP_NAME),
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
        # render tables if data exists
        GENES_COMPLETE = False
        TRNA_COMPLETE = False
        for key in self.queryData.toolData.keys():
            if key in GENE_TOOLS and not GENES_COMPLETE:
                self._update_table(self.geneTable, GENE_TOOLS, 0, self._GENE_TAB_LABEL)
                GENES_COMPLETE = True
            elif key in TRNA_TOOLS and not TRNA_COMPLETE:
                self._update_table(self.trnaTable, TRNA_TOOLS, 1, self._TRNA_TAB_LABEL)
                TRNA_COMPLETE = True

    def _update_table(self, table: QTableWidget, toolList: List[str], index: int, label: str):

        self.tab.removeTab(index)

        # remove any existing cells
        table.setRowCount(0)
        table.setColumnCount(0)

        # table options
        table.setSelectionMode(QTableWidget.NoSelection)

        # sort genes
        genes = []
        usedGeneTools = []
        for tool in self.queryData.toolData:
            if tool in toolList:
                usedGeneTools.append(tool)
                genes += self.queryData.toolData[tool]

        # calculate columns for tools
        toolNumber = len(usedGeneTools)
        toolColumns = toolNumber * 4 + toolNumber - 1
        # add 3 columns for statistics
        totalColumns = toolColumns + 3
        table.setColumnCount(totalColumns)

        # generate headers
        headerIndexes = dict()
        TOTAL_CALLS_COLUMN = 0
        ALL_COLUMN = 1
        ONE_COLUMN = 2
        currIndex = 3
        headers = ['TOTAL CALLS', 'ALL', 'ONE']
        for ind, tool in enumerate(usedGeneTools):
            headerIndexes[tool] = currIndex
            for i in range(4):
                currIndex += 1
                headers.append(tool.upper())
            if ind != toolNumber - 1:
                headers.append('')
                currIndex += 1

        # set headers
        table.setHorizontalHeaderLabels(headers)

        # nothing to display - exit
        if len(genes) == 0:
            # create an empty table
            self.tab.insertTab(index, table, label)
            return

        genes = Gene.GeneUtils.sortGenes(genes)

        # reset genes
        self.genes = []

        # populate table
        # insert first gene
        currentRow = 0
        table.insertRow(currentRow)
        previousGene = genes[0]
        currentGeneCount = 1
        currentGeneSet = [genes[0]]
        currentGenes = dict()
        geneIndex = headerIndexes[previousGene.identity]
        # direction
        directionItem = QTableWidgetItem(previousGene.direction)
        directionItem.setTextAlignment(Qt.AlignCenter)
        table.setItem(currentRow, geneIndex, directionItem)
        # start
        startItem = QTableWidgetItem(str(previousGene.start))
        startItem.setTextAlignment(Qt.AlignCenter)
        table.setItem(currentRow, geneIndex + 1, startItem)
        # stop
        stopItem = QTableWidgetItem(str(previousGene.stop))
        stopItem.setTextAlignment(Qt.AlignCenter)
        table.setItem(currentRow, geneIndex + 2, stopItem)
        # length
        lengthItem = QTableWidgetItem(str(previousGene.length))
        lengthItem.setTextAlignment(Qt.AlignCenter)
        table.setItem(currentRow, geneIndex + 3, lengthItem)

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
                currentGeneSet.append(gene)
            # different gene - create new row
            else:
                # record TOTAL_CALLS, ALL and ONE for previous gene
                totalItem = QTableWidgetItem(str(currentGeneCount))
                totalItem.setTextAlignment(Qt.AlignCenter)
                table.setItem(currentRow, TOTAL_CALLS_COLUMN, totalItem)
                if currentGeneCount == toolNumber:
                    allItem = QTableWidgetItem(str('X'))
                    allItem.setTextAlignment(Qt.AlignCenter)
                    table.setItem(currentRow, ALL_COLUMN, allItem)
                elif currentGeneCount == 1:
                    oneItem = QTableWidgetItem(str('X'))
                    oneItem.setTextAlignment(Qt.AlignCenter)
                    table.setItem(currentRow, ONE_COLUMN, oneItem)

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
                    item = table.item(currentRow, column)
                    # insert blank item if none is present
                    if item is None:
                        item = QTableWidgetItem('')
                        table.setItem(currentRow, column, item)
                    item.setBackground(color)
                    item.setForeground(textColor)

                # record new gene
                currentGeneCount = 1
                currentGenes = dict()
                currentRow += 1
                table.insertRow(currentRow)

                # add full set to genes
                self.genes.append(currentGeneSet)
                currentGeneSet = [gene]

            # add gene to table
            # direction
            directionItem = QTableWidgetItem(gene.direction)
            directionItem.setTextAlignment(Qt.AlignCenter)
            table.setItem(currentRow, geneIndex, directionItem)
            # start
            startItem = QTableWidgetItem(str(gene.start))
            startItem.setTextAlignment(Qt.AlignCenter)
            table.setItem(currentRow, geneIndex + 1, startItem)
            # stop
            stopItem = QTableWidgetItem(str(gene.stop))
            stopItem.setTextAlignment(Qt.AlignCenter)
            table.setItem(currentRow, geneIndex + 2, stopItem)
            # length
            lengthItem = QTableWidgetItem(str(gene.length))
            lengthItem.setTextAlignment(Qt.AlignCenter)
            table.setItem(currentRow, geneIndex + 3, lengthItem)

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
        table.setItem(currentRow, TOTAL_CALLS_COLUMN, totalItem)
        if currentGeneCount == toolNumber:
            allItem = QTableWidgetItem(str('X'))
            allItem.setTextAlignment(Qt.AlignCenter)
            table.setItem(currentRow, ALL_COLUMN, allItem)
        elif currentGeneCount == 1:
            oneItem = QTableWidgetItem(str('X'))
            oneItem.setTextAlignment(Qt.AlignCenter)
            table.setItem(currentRow, ONE_COLUMN, oneItem)

        # append last set of genes
        self.genes.append(currentGeneSet)

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
            item = table.item(currentRow, column)
            # insert blank item if blank cell
            if item is None:
                item = QTableWidgetItem('')
                table.setItem(currentRow, column, item)
            item.setBackground(color)
            item.setForeground(textColor)

        # show tab
        # self.tab.addTab(table, self._GENE_TAB_LABEL)
        self.tab.insertTab(index, table, label)

    def enableActions(self):
        """
        Enables / Disables GUI actions
        :return:
        """
        # file open actions
        if self.fileOpened:
            self.saveAsAction.setEnabled(True)
            self.exportExcelAction.setEnabled(True)
            self.exportGenbankAction.setEnabled(True)
        else:
            self.saveAsAction.setEnabled(False)
            self.exportExcelAction.setEnabled(False)
            self.exportGenbankAction.setEnabled(False)

        if self.saveEnabled:
            self.saveAction.setEnabled(True)
        else:
            self.saveAction.setEnabled(False)

    def checkProdigal(self):

        prodigalPath = self.settings.value(self._PRODIGAL_BINARY_LOCATION_SETTING)
        # if binary does not exist or binary has disappeared, prompt to download
        if prodigalPath is None or not os.path.exists(prodigalPath):
            currRelease = ProdigalRelease()
            # prompt to download prodigal
            # location to store binary is gquery's folder
            td = ThreadData(pathlib.Path(__file__).parent)
            prodigalDownloadDig = phagecommander.GuiWidgets.ProdigalDownloadDialog(currRelease, td)
            if prodigalDownloadDig.exec_():
                self.settings.setValue(self._PRODIGAL_BINARY_LOCATION_SETTING, td.data)
            else:
                self.settings.setValue(self._PRODIGAL_BINARY_LOCATION_SETTING, None)

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

    def checkDefaultSettings(self):
        """
        Check for require default settings
        If they do not exist - populate them
        """
        # NewFileDialog SETTINGS
        NewFileDialog.checkDefaultSettings(self.settings)
        # EXPORT GENBANK SETTINGS
        exportGenbankDialog.checkDefaultSettings(self.settings)
        # COLOR SETTINGS
        ColorTable.checkDefaultSettings(self.settings)

        # OPEN FILE LOCATION
        if self.settings.value(self._LAST_OPEN_FILE_LOCATION_SETTING) is None:
            self.settings.setValue(self._LAST_OPEN_FILE_LOCATION_SETTING, '')

        # EXCEL SAVE LOCATION
        if self.settings.value(self._LAST_EXCEL_SAVE_LOCATION_SETTING) is None:
            self.settings.setValue(self._LAST_EXCEL_SAVE_LOCATION_SETTING, '')


# MAIN FUNCTION
def main():
    app = QApplication([])
    window = GeneMain()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
