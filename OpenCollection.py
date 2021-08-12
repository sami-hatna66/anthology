from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import CollectionWindow
import AddItemWindow
import EditItemWindow
import AdvancedSearch
import GraphWindow
import BarcodeSearch
import LoanItem
import ExportCollection
from datetime import datetime

# This object is the window which displays the collection the user has chosen to open
class OpenCollectionWindow(QMainWindow):
    # The window takes the cursor, the database connection and the primary key of the logged in user as arguments
    # It also takes the primary key of the collection which is currently open
    def __init__(self, MyCursor, ActiveUserID, MyDB, OpenCollectionID):
        super(OpenCollectionWindow, self).__init__()

        self.ActiveUserID = ActiveUserID
        self.Yes = ActiveUserID
        self.MyCursor = MyCursor
        self.MyDB = MyDB
        self.OpenCollectionID = OpenCollectionID
        self.MyCursor.execute("SELECT TableName, CollectionName FROM Collections WHERE PK_Collections = " + str(self.OpenCollectionID))
        # OpenCollectionTable is the name of the collection which is currently open
        # It is obtained by joining the string "TABLE" with the primary key of the collection in the Collections table
        MyResult = self.MyCursor.fetchall()
        self.OpenCollectionTable = MyResult[0][0]
        self.setWindowTitle(str(MyResult[0][1]))

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Set window's central widget and initialise main layout
        self.CentralWidget = QWidget()
        self.OpenCollectionVBL1 = QVBoxLayout()
        self.CentralWidget.setLayout(self.OpenCollectionVBL1)
        self.setCentralWidget(self.CentralWidget)

        self.InitUI()

        # Initialise menu bar
        self.MainMenu = QMenuBar(self)
        # Add file menu to menubar
        self.FileMenu = self.MainMenu.addMenu(" &File")
        # Create action for closing current collection window and going back to CollectionWindow
        self.CloseCollectionAction = QAction("Close Collection", self)
        # Bind action to function
        self.CloseCollectionAction.triggered.connect(self.CloseCollection)
        # Add action to file menu
        self.FileMenu.addAction(self.CloseCollectionAction)

        # Create view menu and add to menu bar
        self.ViewMenu = self.MainMenu.addMenu(" &View")
        # The view menu will have two actions: one for show/hiding the thumbnail panel and one for showing/hiding the sorting panel
        self.ShowThumbnailAction = QAction("Show Thumbnail Panel")
        # setCheckable displays a tick next to menu actions when they are active
        self.ShowThumbnailAction.setCheckable(True)
        self.ShowThumbnailAction.setChecked(True)
        # Connect action to method
        self.ShowThumbnailAction.triggered.connect(self.ShowThumbnail)
        # Add action to menu
        self.ViewMenu.addAction(self.ShowThumbnailAction)
        # Create action for showing/hiding the sorting panel
        self.ShowSortingAction = QAction("Show Sorting Panel")
        self.ShowSortingAction.setCheckable(True)
        self.ShowSortingAction.setChecked(False)
        # Connect action to slot
        self.ShowSortingAction.triggered.connect(self.ShowSorting)
        # Add action to menu
        self.ViewMenu.addAction(self.ShowSortingAction)

        # Create shortcuts and bind them to methods
        # Keyboard inputs are captured using the QKeySequence object
        self.AddItemShortcut = QShortcut(QKeySequence("Ctrl+shift+A"), self)
        self.AddItemShortcut.activated.connect(self.AddItemMethod)
        self.DeleteItemShortcut = QShortcut(QKeySequence("Ctrl+shift+D"), self)
        self.DeleteItemShortcut.activated.connect(self.DeleteItemMethod)
        self.EditItemShortcut = QShortcut(QKeySequence("Ctrl+shift+E"), self)
        self.EditItemShortcut.activated.connect(self.EditItemMethod)
        self.GraphShortcut = QShortcut(QKeySequence("Ctrl+shift+G"), self)
        self.GraphShortcut.activated.connect(self.GenerateGraphsMethod)
        self.OrderShortcut1 = QShortcut(QKeySequence(Qt.SHIFT + Qt.Key_Up), self)
        self.OrderShortcut1.activated.connect(lambda: self.TabShortcut(self.OrderShortcut1))
        self.OrderShortcut2 = QShortcut(QKeySequence(Qt.SHIFT + Qt.Key_Down), self)
        self.OrderShortcut2.activated.connect(lambda: self.TabShortcut(self.OrderShortcut2))
        self.ShowShortcut = QShortcut(QKeySequence("Ctrl+shift+S"), self)
        self.ShowShortcut.activated.connect(lambda: self.ShowHideShortcut(self.ShowShortcut))
        self.HideShortcut = QShortcut(QKeySequence("Ctrl+shift+H"), self)
        self.HideShortcut.activated.connect(lambda: self.ShowHideShortcut(self.HideShortcut))

        # Display window at maximum size
        self.showMaximized()
        self.show()

    # This method searches the parameter InputForTesting for any characters which may be used in a SQL injection attack
    def InjectionTest(self, InputForTesting):
        # If the string contains any suspicious characters, cancel the operation and output an error message in the status bar
        if ";" or "--" or "#" or "/*" or "*/" or "=" in InputForTesting:
            self.StatusBar.showMessage("System Integrity Error: Invalid Input")
        else:
            pass

    # This method acts as an arbiter for when the show/hide keyboard shortcut is used
    def ShowHideShortcut(self, sender):
        # If the user has pressed CMD+shift+S then show the two sidebars
        if sender == self.ShowShortcut:
            self.ThumbnailGroupBox.show()
            self.SortingGroupBox.show()
            self.ShowThumbnailAction.setChecked(True)
            self.ShowSortingAction.setChecked(True)
        # If the user has pressed CMD+shift+H then hide the two sidebars
        else:
            self.ThumbnailGroupBox.hide()
            self.SortingGroupBox.hide()
            self.ShowThumbnailAction.setChecked(False)
            self.ShowSortingAction.setChecked(False)

    # This method acts as an arbiter for when the shift+tab shortcut is pressed
    def TabShortcut(self, sender):
        # It changes the order items are displayed in
        if sender == self.OrderShortcut1:
            if self.OrderCB.count() - 1 == self.OrderCB.currentIndex():
                self.OrderCB.setCurrentIndex(0)
            else:
                self.OrderCB.setCurrentIndex(self.OrderCB.currentIndex() + 1)
        else:
            if self.OrderCB.currentIndex() == 0:
                self.OrderCB.setCurrentIndex(self.OrderCB.count() - 1)
            else:
                self.OrderCB.setCurrentIndex(self.OrderCB.currentIndex() - 1)

    # Initialise UI elements
    def InitUI(self):
        # InitToolbar is the function which creates the window toolbar
        self.InitToolbar()

        # Add 20 pixels of space between toolbar and search bar
        self.OpenCollectionVBL1.addSpacing(20)

        # SearchBarHBL is the layout which stores the search bar and the sorting menu
        self.SearchBarHBL = QHBoxLayout()
        self.SearchBarHBL.addWidget(QLabel("Search:"))
        self.SubHBL = QHBoxLayout()
        self.SubHBL.setSpacing(0)
        # SearchBarTB is the text box in which the user inputs search terms
        self.SearchBarTB = QLineEdit()
        self.SearchBarTB.setStyleSheet("border-right: 0px;")
        self.SearchBarTB.setFixedWidth(150)
        # When the user presses enter in a QLineEdit, it emits the editingFinished signal
        # I have bound this signal to the function SimpleSearch so that whenever the user presses enter, the function will be executed
        self.SearchBarTB.editingFinished.connect(self.SimpleSearch)
        self.SubHBL.addWidget(self.SearchBarTB)
        self.SearchBTN = QPushButton()
        self.SearchBTN.clicked.connect(self.SimpleSearch)
        self.SearchBTN.setIcon(QIcon("Resources/SearchIcon.png"))
        self.SearchBTN.setFixedSize(20, 20)
        self.SubHBL.addWidget(self.SearchBTN)
        self.SearchBarHBL.addLayout(self.SubHBL)
        self.SearchBarHBL.addSpacing(50)
        self.SearchBarHBL.addWidget(QLabel("Order:"))
        # OrderCB is a combobox which allows user to choose which order they would like to display their collection in
        self.OrderCB = QComboBox()
        self.OrderCB.addItems(["Date Added", "Ascending", "Descending"])
        self.OrderCB.setFixedWidth(130)

        # When the user selects a new item in the combobox, it emits a signal, I have bound this signal to the function PopulateTable
        # This means that if the user selects a different order for items, the table will be repopulated in that order
        self.OrderCB.currentTextChanged.connect(self.PopulateTable)
        self.SearchBarHBL.addWidget(self.OrderCB)
        # Add horizontal box layout to main layout
        self.OpenCollectionVBL1.addLayout(self.SearchBarHBL)
        self.SearchBarHBL.addStretch()

        # StatusBar displays a horizontal bar along the bottom of the window for presenting status information
        self.StatusBar = QStatusBar()
        self.setStatusBar(self.StatusBar)
        # StatusLBL will be used to convey information to the user such as collection size or when processes are complete
        self.StatusLBL = QLabel("")
        self.StatusLBL.setStyleSheet("padding-left: 5px")
        self.StatusBar.addWidget(self.StatusLBL, 1)
        self.CreditLBL = QLabel("Anthology v1.0 created by Sami Hatna")
        self.CreditLBL.setStyleSheet("padding-right: 5px")
        self.StatusBar.addPermanentWidget(self.CreditLBL)

        # This horizontal box layout displays the table in which the collection is presented and the group box for displaying item thumbnails
        self.OpenCollectionHBL1 = QHBoxLayout()

        # Create groupbox for displaying sorting TreeWidget
        self.SortingGroupBox = QGroupBox()
        self.SortingGroupBox.setFixedWidth(150)
        # Set layout for group box
        self.SortingLayout = QVBoxLayout()
        self.SortingLayout.setContentsMargins(0, 0, 0, 0)
        # Initialise tree widget
        # The tree widget will have parent items for each column/property within the collection
        # These parents will then have child items for each category within that column
        self.SortingTree = QTreeWidget()
        # Style tree widget
        self.SortingTree.setStyleSheet("QTreeWidget { selection-color: black; }")
        self.SortingTree.verticalScrollBar().setStyleSheet("QScrollBar { border-right: 0px; border-top: 0px; border-bottom: 0px; } QScrollBar::handle { border-top: 0px; border-bottom: 0px; }")
        self.SortingTree.setObjectName("BorderlessWidget")
        # Hide tree widget headers
        self.SortingTree.setHeaderHidden(True)
        self.SortingTree.setAttribute(Qt.WA_MacShowFocusRect, 0)
        # Connect the signal emitted when the selected item in the tree widget changes to a slot
        self.SortingTree.itemSelectionChanged.connect(self.SortingTreeClicked)
        # Add tree widget to layout
        self.SortingLayout.addWidget(self.SortingTree)
        self.SortingGroupBox.setLayout(self.SortingLayout)
        # Add group box to main window layout
        self.OpenCollectionHBL1.addWidget(self.SortingGroupBox)
        # The sorting panel is hidden on startup, the user can show it through the view menu
        self.SortingGroupBox.hide()

        # CollectionTable is the table which displays collection items
        self.CollectionTable = QTableWidget()
        self.CollectionTable.setShowGrid(False)
        # Disable table editing, if users want to edit items they have to do it using the edit toolbutton
        self.CollectionTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # The first column is hidden because it stores the primary key of each item
        self.CollectionTable.setColumnHidden(0, True)
        self.CollectionTable.horizontalHeader().setStretchLastSection(True)
        # Users can only select rows rather than individual cells
        self.CollectionTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.CollectionTable.verticalHeader().setVisible(False)
        # When the user selects a new row in the table, DisplayImage is executed to display the thumbnail for that item in ThumbnailGroupBox
        self.CollectionTable.itemSelectionChanged.connect(self.DisplayImage)
        self.OpenCollectionHBL1.addWidget(self.CollectionTable)
        self.CollectionTable.verticalScrollBar().setStyleSheet("QScrollBar::handle { border: 0px; }")
        self.CollectionTable.horizontalScrollBar().setStyleSheet("QScrollBar::handle { border-left: 0px; border-right: 0px; } QScrollBar { border-left: 0px; border-right: 0px; }")
        self.PopulateTable()
        self.CheckTableScrollBar(False)

        # ThumbnailGroupBox displays the thumbnail and metadata of the currently selected item
        self.ThumbnailGroupBox = QGroupBox()
        self.ThumbnailGroupBox.setFixedWidth(150)
        # Set groupbox layout
        self.ThumbnailLayout = QVBoxLayout()
        self.ThumbnailLayout.setContentsMargins(5, 5, 5, 5)
        self.ThumbnailGroupBox.setLayout(self.ThumbnailLayout)
        # ThumbnailImageLabel is the label which will display the thumbnail of the selected item
        # Images in PyQt are displayed by loading a QPixmap onto a QLabel
        self.ThumbnailImageLabel = QLabel()
        self.ThumbnailImageLabel.setAlignment(Qt.AlignCenter)
        self.ThumbnailLayout.addWidget(self.ThumbnailImageLabel)
        # This list stores the labels which will be used to display info about the currently selected item
        # A label is created for each column in the SQL table and used to display its corresponding contents
        self.ThumbnailLabelsArray = []
        # Get the number of columns in the SQL table
        self.MyCursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '" + self.OpenCollectionTable + "'")
        # For each column in the table, create a label (excluding the Rare, Rating and Thumbnail columns)
        for x in range(1, self.MyCursor.fetchall()[0][0] - 3):
            Temp = QLabel("")
            Temp.setWordWrap(True)
            self.ThumbnailLayout.addWidget(Temp)
            # Because there is a variable amount of labels, they are each appended to this list after they are created
            self.ThumbnailLabelsArray.append(Temp)
        self.ThumbnailRatingLBL = QLabel()
        self.ThumbnailLayout.addWidget(self.ThumbnailRatingLBL)
        self.ThumbnailLayout.addStretch()
        # Add groupbox to horizontal box layout
        self.OpenCollectionHBL1.addWidget(self.ThumbnailGroupBox)

        # Add horizontal box layout to main layout
        self.OpenCollectionVBL1.addLayout(self.OpenCollectionHBL1)

    # This function is executed when the itemSelectionChanged signal is emitted
    # It performs a simple search on all columns in the SQL table based on what the user has inputted in the search bar
    def SimpleSearch(self):
        # Get search string from search bar
        SearchRequest = self.SearchBarTB.text()
        # SearchResult stores the rows of the table widget which contain the items that have fulfilled the terms of the search
        SearchResult = []
        # Presence check
        if SearchRequest == "":
            self.CollectionTable.clearSelection()
        else:
            # Clear all previous selections
            self.CollectionTable.clearSelection()
            self.CollectionTable.setSelectionMode(QAbstractItemView.MultiSelection)
            # Retrieve all column names from SQL table
            self.MyCursor.execute("SHOW COLUMNS FROM " + self.OpenCollectionTable)
            MyResult4 = self.MyCursor.fetchall()
            # Concatenate strings together to form a SQL query that will search the table for target items and return their primary key
            SQLStatement = 'SELECT PK_Table' + str(self.OpenCollectionID) + ' FROM ' + self.OpenCollectionTable + ' WHERE '
            # The function searches all columns in the table except the Thumbnail column
            for x in range(1, len(MyResult4) - 2):
                # Uses LIKE statements to find instances of the string inputted in the search bar in all fields of the database
                SQLStatement += MyResult4[x][0] + ' LIKE "%' + SearchRequest + '%" OR '
            SQLStatement += MyResult4[len(MyResult4) - 2][0] + ' LIKE "%' + SearchRequest + '%"'
            self.MyCursor.execute(SQLStatement)
            print(SQLStatement)
            # Retrieve results of SQL query
            MyResult5 = list(set(self.MyCursor.fetchall()))

            # For each element in the result of the SQL query, find their corresponding row in the table widget by comparing their primary keys
            for z in range(0, self.CollectionTable.rowCount()):
                for x in range(0, len(MyResult5)):
                    if self.CollectionTable.item(z, 0).text() == str(MyResult5[x][0]):
                        # Add each tableItem object to the list
                        SearchResult.append(self.CollectionTable.item(z, 0))

            # Highlight/Select each row stored in SearchResult to relay the results of the search to the user
            for z in range(0, len(SearchResult)):
                    self.CollectionTable.selectRow(SearchResult[z].row())
            self.CollectionTable.setSelectionMode(QAbstractItemView.ExtendedSelection)

    # This function is executed when the user selects an item in CollectionTable
    # It displays the thumbnail for the selected item alongside the data stored about them in the SQL table
    # The thumbnails of items which are marked as rare get a rare tag overlayed over their thumbnail
    def DisplayImage(self):
        # Get currently selected row
        Row = self.CollectionTable.selectionModel().currentIndex()
        # Get the primary key of that row by reading the valus stored in the first (hidden) column
        PKValue = Row.sibling(Row.row(), 0).data()

        if len(self.CollectionTable.selectionModel().selectedRows()) > 1:
            self.StatusLBL.setText(str(len(self.CollectionTable.selectionModel().selectedRows())) + " of " + str(self.RowCount) + " items")
        else:
            self.StatusLBL.setText(str(self.RowCount) + " items")

        # Presence check
        if PKValue:
            # Retrieve the SQL entry which matches the currently selected row
            self.MyCursor.execute("SELECT * FROM " + self.OpenCollectionTable + " WHERE PK_" + self.OpenCollectionTable + " = " + PKValue)
            MyResult3 = self.MyCursor.fetchall()[0]
            # If a binary large object has been stored in the Thumbnail column...
            if MyResult3[len(MyResult3) - 1]:
                # Load image as QImage from raw binary data
                ThumbnailImage = QImage.fromData(MyResult3[len(MyResult3) - 1])
                # Convert QImage into QPixmap
                ThumbnailPixmap = QPixmap.fromImage(ThumbnailImage)
                # Resize image
                ThumbnailPixmap = ThumbnailPixmap.scaledToWidth(120, Qt.SmoothTransformation)
                # Check if item is tagged as Rare
                if MyResult3[len(MyResult3) - 3] == 1:
                    # If image is rare, load overlay image
                    OverlayPixmap = QPixmap("Resources/RareTag.png")
                    # Initialise QPainter object
                    Painter = QPainter(ThumbnailPixmap)
                    # Draw rare tag over item thumbnail
                    Painter.drawPixmap(0, 0, OverlayPixmap)
                    # End paint event
                    Painter.end()
            # If there is nothing in the Thumbnail column, display a generic 'No Image Available' image
            else:
                ThumbnailPixmap = QPixmap("Resources/NoImageAvailable.png")
                ThumbnailPixmap = ThumbnailPixmap.scaledToWidth(120, Qt.SmoothTransformation)
            # Load pixmap into ThumbnailLabel
            self.ThumbnailImageLabel.setPixmap(ThumbnailPixmap)

            # Iterate through list of thumbnail labels and set each one's text to the corresponding data stored in the field for that item
            for x in range(0, len(self.ThumbnailLabelsArray)):
                self.ThumbnailLabelsArray[x].setText(str(MyResult3[x + 1]))
            ThumbnailRatingPixmap = QPixmap("Resources/{0} stars.png".format(str(MyResult3[len(MyResult3) - 2])))
            ThumbnailRatingPixmap = ThumbnailRatingPixmap.scaledToWidth(100, Qt.SmoothTransformation)
            self.ThumbnailRatingLBL.setPixmap(ThumbnailRatingPixmap)

    # This function populates the PyQt table widget with data from the SQL table
    def PopulateTable(self):
        # Get columns from SQL table
        self.MyCursor.execute("SHOW COLUMNS FROM " + self.OpenCollectionTable)
        MyResult1 = self.MyCursor.fetchall()
        ColumnNames = []
        ColumnCounter = 0
        # LargestArray stores the size of each column
        # As the function progresses, LargestArray finds the size of the alrgest string for each column and appends it
        LargestArray = []
        # Iterate through the result of the SQL query and get amount of columns as well as column names
        for x in range(0, len(MyResult1) - 1):
            ColumnNames.append(MyResult1[x][0])
            ColumnCounter += 1
            Temp = QLabel(MyResult1[x][0])
            Temp.setFixedWidth(QFontMetrics(Temp.font()).width(Temp.text()))
            LargestArray.append(Temp.width())
        LargestArray[len(MyResult1) - 2] = 100
        # Set column count of table widget to column count of SQL table
        self.CollectionTable.setColumnCount(ColumnCounter)
        # Set the horizontal headings of the table widget to the headings of the SQL columns
        self.CollectionTable.setHorizontalHeaderLabels(ColumnNames)
        # Hide the first column as it stores the primary key for each item
        self.CollectionTable.setColumnHidden(0, True)

        self.CollectionTable.horizontalHeader().setObjectName("hHeader")

        # Clear table of rows before repopulating table
        self.CollectionTable.setRowCount(0)
        # Get number of entries in table
        self.MyCursor.execute("SELECT COUNT(*) FROM " + self.OpenCollectionTable)
        self.RowCount = self.MyCursor.fetchall()[0][0]
        # Set number of rows in table widget to number of entries in SQL table
        self.CollectionTable.setRowCount(self.RowCount)
        # Set label in status bar to display the number of items in the collection
        self.StatusLBL.setText(str(self.RowCount) + " items")
        # Select which order the items should be displayed in based on the value in OrderCB
        if self.OrderCB.currentText() == "Ascending":
            # Order items in ascending alphabetical order based on the first column (excluding the primary key)
            self.MyCursor.execute("SELECT * FROM " + self.OpenCollectionTable + " ORDER BY " + str(MyResult1[1][0]) + " ASC")
        elif self.OrderCB.currentText() == "Descending":
            # Order items in descending order based on the first column
            self.MyCursor.execute("SELECT * FROM " + self.OpenCollectionTable + " ORDER BY " + str(MyResult1[1][0]) + " DESC")
        else:
            # Order items in the order that they have been added to the collection
            self.MyCursor.execute("SELECT * FROM " + self.OpenCollectionTable)

        # Retrieve results of SQL query
        MyResult2 = self.MyCursor.fetchall()
        # Iterate through each entry in the table
        for x in range(0, len(MyResult2)):
            # Store the primary key in the first (hidden) column of the table widget
            self.CollectionTable.setItem(x, 0, QTableWidgetItem(str(MyResult2[x][0])))
            # For loop here begins at 1 because we have already stored the primary key in a table cell
            # len(MyResult2[x]) - 3 excludes the Rare, Rating and Thumbnail columns as they are displayed in special widgets
            for y in range(1, len(MyResult2[x]) - 3):
                # Create a label and set label text to text value of current field the loop is on
                Temp = QLabel(str(MyResult2[x][y]))
                # Add label to corresponding cell in the table widget
                self.CollectionTable.setCellWidget(x, y, Temp)
                # If the width of the label is greater than the width currently stored in LargestArray, change the value at that index to the new largest width
                if int(Temp.width()) > LargestArray[y]:
                    LargestArray[y] = int(Temp.width())

            # If the item is tagged as rare...
            if MyResult2[x][len(MyResult2[x]) - 3] == 1:
                # Create an instance of RareWidget and add to table widget
                RarityCell = RareWidget()
                self.CollectionTable.setCellWidget(x, (len(MyResult2[x]) - 3), RarityCell)

            # Create an instance of RatingWidget, passing in the rating of the current item as a parameter
            RatingCell = RatingWidget(Rating = MyResult2[x][len(MyResult2[x]) - 2])
            self.CollectionTable.setCellWidget(x, (len(MyResult2[x]) - 2), RatingCell)

        # Set size of each column to the corresponding width in LargestArray
        for x in range(0, len(LargestArray)):
            self.CollectionTable.setColumnWidth(x, LargestArray[x] + 40)

        self.CheckTableScrollBar(False)

        # If the sorting tree widget is not hidden, populate it
        if not self.SortingTree.isHidden():
            # 3D list containing each parent and its corresponding children
            self.SortingTreeKey = []
            # Clear the tree's contents before repopulating it
            self.SortingTree.clear()
            # Iterate through the list containing each column in the table
            for x in range (1, len(MyResult1) - 1):
                # Create a parent item for each column in the table (excluding the thumbnail and primary key columns) and add them to the tree widget
                Temp1 = QTreeWidgetItem(self.SortingTree, [MyResult1[x][0]])
                # Add the parent to the list
                self.SortingTreeKey.append([Temp1])
                # SQL query which returns each entry under the specified column along with the amount of times it occurs in the table
                self.MyCursor.execute("SELECT `" + str(MyResult1[x][0]) + "`, COUNT(*) FROM " + self.OpenCollectionTable + " GROUP BY `" + str(MyResult1[x][0]) + "`")
                MyResult3 = self.MyCursor.fetchall()
                # Iterate through the results of the query, creating a child item for each entry and adding it to the tree widget
                for y in range(0, len(MyResult3)):
                    # Create child item and add to tree widget, the string passed in is the name with the number of time it occurs appended to the end
                    Temp2 = QTreeWidgetItem(self.SortingTreeKey[x - 1][0], [str(MyResult3[y][0]) + " (" + str(MyResult3[y][1]) + ")"])
                    Temp2.setData(0, Qt.UserRole, MyResult3[y][0])
                    # Add child to 3D list in the same index as its parent
                    self.SortingTreeKey[x - 1].append(Temp2)

    # This slot is executed whenever a new item is selected in SortingTree
    # It highlights all the items which correspond with the user's selection
    def SortingTreeClicked(self):
        # Get the current selected item
        SelectedItem = self.SortingTree.currentItem()
        # If the currently selected item is a parent item do not proceed
        if SelectedItem.parent() is None:
            pass
        # If the selected item is a child item, proceed
        else:
            # Get the child item's parent
            SelectedItemParent = SelectedItem.parent()
            # Select the primary key of all entries where the contents of the parent column is the same as the selected child
            self.MyCursor.execute("SELECT PK_" + self.OpenCollectionTable + " FROM " + self.OpenCollectionTable + " WHERE " + str(SelectedItemParent.text(0)) + " = '" + str(SelectedItem.data(0, Qt.UserRole)) + "'")
            # Reassign query result as list, not tuple
            MyResult1 = list(set(self.MyCursor.fetchall()))

            # List for storing all the rows in the frontend table which correspond with the results of the SQL query
            SearchResult = []
            # Clear selection
            self.CollectionTable.clearSelection()
            # Set the table's selection mode so that multiple rows can be selected at once
            self.CollectionTable.setSelectionMode(QAbstractItemView.MultiSelection)

            # Iterate through all the rows in the frontend table and add each row which corresponds with the SQL query results to the list
            for z in range(0, self.CollectionTable.rowCount()):
                for x in range(0, len(MyResult1)):
                    if self.CollectionTable.item(z, 0).text() == str(MyResult1[x][0]):
                        SearchResult.append(self.CollectionTable.item(z, 0))

            # Iterate through the contents of SearchResult and highlight the rows
            for z in range(0, len(SearchResult)):
                    self.CollectionTable.selectRow(SearchResult[z].row())

            # Return table's selection mode to default
            self.CollectionTable.setSelectionMode(QAbstractItemView.ExtendedSelection)

    # Method executed when ShowThumbnailAction in the View menu is pressed
    def ShowThumbnail(self):
        if self.ShowThumbnailAction.isChecked():
            self.ThumbnailGroupBox.show()
        else:
            self.ThumbnailGroupBox.hide()

    # Method executed when ShowThumbnailAction in the View menu is pressed
    def ShowSorting(self):
        if self.ShowSortingAction.isChecked():
            self.SortingGroupBox.show()
        else:
            self.SortingGroupBox.hide()

    # Initialise window toolbar
    def InitToolbar(self):
        # Toolbar buttons are displayed in a horizontal box layout
        self.ToolBarHBL = QHBoxLayout()
        self.OpenCollectionVBL1.addLayout(self.ToolBarHBL)

        # Each Toolbar button is an instance of the ToolBarBTN class
        # AddItemBTN is used for adding new items to the collection
        self.AddItemBTN = ToolBarBTN(Text = "Add Item", IconPath = "Resources/AddItemIcon.png")
        self.AddItemBTN.clicked.connect(self.AddItemMethod)
        self.ToolBarHBL.addWidget(self.AddItemBTN)

        # DeleteItemBTN deletes the selected item(s) from the collection
        self.DeleteItemBTN = ToolBarBTN(Text = "Delete Item", IconPath = "Resources/DeleteItemIcon.png")
        self.DeleteItemBTN.clicked.connect(self.DeleteItemMethod)
        self.ToolBarHBL.addWidget(self.DeleteItemBTN)

        # EditItemBTN allows the user to edit the data stored about the selected item
        self.EditItemBTN = ToolBarBTN(Text = "Edit Item", IconPath = "Resources/EditItemIcon.jpg")
        self.EditItemBTN.clicked.connect(self.EditItemMethod)
        self.ToolBarHBL.addWidget(self.EditItemBTN)

        # DeleteDuplicatesBTN deletes duplicate items from the collection
        self.DeleteDuplicatesBTN = ToolBarBTN(Text = "Delete Duplicates", IconPath = "Resources/DeleteDuplicatesIcon.png")
        self.DeleteDuplicatesBTN.clicked.connect(self.DeleteDuplicatesMethod)
        self.ToolBarHBL.addWidget(self.DeleteDuplicatesBTN)

        # AdvancedSearchBTN opens the advanced search window for constructing complex queries
        self.AdvancedSearchBTN = ToolBarBTN(Text = "Advanced Search", IconPath = "Resources/AdvancedSearchIcon.png")
        self.AdvancedSearchBTN.clicked.connect(self.AdvancedSearchMethod)
        self.ToolBarHBL.addWidget(self.AdvancedSearchBTN)

        # LoanItemBTN is for loaning out items
        self.LoanItemBTN = ToolBarBTN(Text = "Loan Item", IconPath = "Resources/LoanItemIcon.png")
        self.LoanItemBTN.clicked.connect(self.LoanItemMethod)
        self.ToolBarHBL.addWidget(self.LoanItemBTN)

        # ExportBTN exports the current collection
        self.ExportBTN = ToolBarBTN(Text = "Export Collection", IconPath = "Resources/ExportTxtIcon.png")
        self.ExportBTN.clicked.connect(self.ExportCollectionMethod)
        self.ToolBarHBL.addWidget(self.ExportBTN)

        # BarcodeSearchBTN opens the barcode search window which allows users to add items to collections using their barcode
        self.BarcodeSearchBTN = ToolBarBTN(Text = "Search Barcode", IconPath = "Resources/BarcodeSearchIcon.png")
        self.BarcodeSearchBTN.clicked.connect(self.BarcodeSearchMethod)
        self.ToolBarHBL.addWidget(self.BarcodeSearchBTN)

        # GenerateGraphsBTN generates and displays graphs based on the user's collection
        self.GenerateGraphsBTN = ToolBarBTN(Text = "Generate Graphs", IconPath = "Resources/GenerateGraphsIcon.png")
        self.GenerateGraphsBTN.clicked.connect(self.GenerateGraphsMethod)
        self.ToolBarHBL.addWidget(self.GenerateGraphsBTN)

        self.ToolBarHBL.addStretch()

    # This function is executed when the advanced search is complete
    def SearchCompleteSlot(self, SearchItems):
        # This method of highlighting search results is similar to the one used for the simple search, with a few minor adjustments made
        SearchResult = []
        self.CollectionTable.clearSelection()
        # Set the selection colour for the table to light red in order to differentiate search results from normal selection
        self.CollectionTable.setStyleSheet("QWidget::item:selected { background: #FF6961; }")
        self.CollectionTable.setSelectionMode(QAbstractItemView.MultiSelection)
        for z in range(0, self.CollectionTable.rowCount()):
            for x in range(0, len(SearchItems)):
                if self.CollectionTable.item(z, 0).text() == str(SearchItems[x][0]):
                    SearchResult.append(self.CollectionTable.item(z, 0))
        for z in range(0, len(SearchResult)):
            self.CollectionTable.selectRow(SearchResult[z].row())
        self.CollectionTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Connect the signal emitted when the table is clicked to the slot
        self.CollectionTable.clicked.connect(self.CollectionTableClickedSlot)
        # Show message to user in status bar
        self.StatusBar.showMessage("Search results are highlighted in red", 3000)
        self.CheckTableScrollBar(AdvancedSearch = True)

    # This slot is executed when the table is clicked after an advanced search is completed
    # It sets the selection colour in the table back to pastel green instead of red
    def CollectionTableClickedSlot(self):
        self.CollectionTable.setStyleSheet("QWidget::item:selected {background: #D5E8D4}")
        self.CollectionTable.clicked.disconnect()

    def CheckTableScrollBar(self, AdvancedSearch):
        if (self.CollectionTable.rowHeight(0) * self.RowCount) > self.CollectionTable.height():
            if AdvancedSearch:
                self.CollectionTable.setStyleSheet("QTableWidget { border-right: 0px; } QWidget::item:selected { background: #FF6961; }")
            else:
                self.CollectionTable.setStyleSheet("QTableWidget { border-right: 0px; } QWidget::item:selected { background: #D5E8D4; }")
        else:
            if AdvancedSearch:
                self.CollectionTable.setStyleSheet("QTableWidget { border-right: 1px solid rgb(90,90,90); } QWidget::item:selected { background: #FF6961; }")
            else:
                self.CollectionTable.setStyleSheet("QTableWidget { border-right: 1px solid rgb(90,90,90); } QWidget::item:selected { background: #D5E8D4; }")

    def BarcodeSearchMethod(self):
        self.BarcodeSearchInstance = BarcodeSearch.BarcodeSearch(widget = self.BarcodeSearchBTN)

    # This function is executed when the user selects Close Collection from the file menu
    # It closes the current window and reopens the collection window
    def CloseCollection(self):
        self.MainMenu.clear()
        self.CollectionWindowInstance = CollectionWindow.CollectionWindow(MyCursor = self.MyCursor, MyDB = self.MyDB, ActiveUserID = self.Yes)
        self.close()

    # This method is executed when the user presses GenerateGraphsBTN
    def GenerateGraphsMethod(self):
        self.GraphWindowInstance = GraphWindow.GraphWidget(MyCursor=self.MyCursor, MyDB=self.MyDB, ActiveUserID=self.ActiveUserID,
                                                           OpenCollectionID=self.OpenCollectionID, OpenCollectionTable=self.OpenCollectionTable, widget = self.GenerateGraphsBTN)

    # This method is executed when the user presses AddItemBTN
    def AddItemMethod(self):
        self.AddItemWindowInstance = AddItemWindow.AddItemWindow(MyCursor=self.MyCursor, MyDB=self.MyDB, ActiveUserID=self.ActiveUserID,
                                    OpenCollectionID=self.OpenCollectionID, OpenCollectionTable=self.OpenCollectionTable, widget = self.AddItemBTN)
        self.AddItemWindowInstance.ItemAddedSignal.connect(self.ItemAddedSlot)

    # This method is executed when the user presses LoanItemBTN
    def LoanItemMethod(self):
        self.LoanItemWindowInstance = LoanItem.LoanItemWindow(MyCursor=self.MyCursor, MyDB=self.MyDB, ActiveUserID=self.ActiveUserID,
                                    OpenCollectionID=self.OpenCollectionID, OpenCollectionTable=self.OpenCollectionTable, widget = self.LoanItemBTN)

    # This method is executed when the user presses AdvancedSearchBTN
    def AdvancedSearchMethod(self):
        self.AdvancedSearchInstance = AdvancedSearch.AdvancedSearch(MyCursor=self.MyCursor, MyDB=self.MyDB, ActiveUserID=self.ActiveUserID,
                                    OpenCollectionID=self.OpenCollectionID, OpenCollectionTable=self.OpenCollectionTable, widget = self.AdvancedSearchBTN)
        self.AdvancedSearchInstance.SearchCompleteSignal.connect(self.SearchCompleteSlot)

    # This method is executed when the user presses ExportCollectionBTN
    def ExportCollectionMethod(self):
        self.ExportSubMenuInstance = ExportCollection.ExportSubMenu(MyCursor=self.MyCursor, MyDB=self.MyDB, ActiveUserID=self.ActiveUserID,
                                    OpenCollectionID=self.OpenCollectionID, OpenCollectionTable=self.OpenCollectionTable, widget = self.ExportBTN)
        self.ExportSubMenuInstance.Success.connect(lambda: self.StatusBar.showMessage("Your collection was successfully exported!", 3000))
        self.ExportSubMenuInstance.Failed.connect(lambda: self.StatusBar.showMessage("There was an issue exporting your collection, please try again", 3000))

    # This function is executed when the user presses EditItemBTN
    # It retrieves the selected row from CollectionTable and passes it into a new instance of EditItemWindow as an argument
    def EditItemMethod(self):
        # Stores the selected row
        SelectedRowsArray = []
        # Stores the id corresponding to each selected row
        SelectedRowsIDArray = []
        # Iterate through selected rows in CollectionTable and append them to the list
        for x in self.CollectionTable.selectionModel().selectedRows():
            SelectedRowsArray.append(x.row())
        # Iterate through the contents of SelectedRowsArray and retrieve the corresponding primary key by getting the contents of the first (hidden) column
        for y in range(0, len(SelectedRowsArray)):
            SelectedRowsIDArray.append(self.CollectionTable.item(SelectedRowsArray[y], 0).text())
        # If the user hasn't selected an item don't continue
        if len(SelectedRowsIDArray) == 0:
            pass
        else:
            # Create EditItemWindow instance
            # EditItemWindow takes the same parameters of AddItemWindow as well as ItemsForEditing which in this case is the first value in SelectedRowsIDArray
            self.EditItemWindowInstance = EditItemWindow.EditItemWindow(MyCursor=self.MyCursor, MyDB=self.MyDB, ActiveUserID=self.ActiveUserID,
                                    OpenCollectionID=self.OpenCollectionID, OpenCollectionTable=self.OpenCollectionTable, widget = self.EditItemBTN, ItemsForEditing = SelectedRowsIDArray[0])
            # Connect signal to slot
            self.EditItemWindowInstance.ItemAddedSignal.connect(self.ItemAddedSlot)

    # This function is executed when the signal ItemAddedSignal is emitted
    def ItemAddedSlot(self, Message):
        # Message is a boolean value passed into ItemAddedSignal
        # The value of Message is passed to this slot when the signal is emitted
        # Message is set to False if the window is an edit item window, so the program shows the according message in the status bar
        if not Message:
            self.StatusBar.showMessage("Item has been edited", 3000)
        # Message is set to True if the window is an add item window
        else:
            self.StatusBar.showMessage("New item has been added to collection", 3000)

        self.UpdateSizes()

        # Refresh front end table
        self.PopulateTable()

    # This function is called when DeleteItemBTN is pressed
    # It deletes the selected items in CollectionTable from the database
    def DeleteItemMethod(self):
        # List stores all the rows in CollectionTable the user has selected
        SelectedRowsArray = []
        # List will store the primary keys of the items the user has selected
        SelectedRowsIDArray = []

        # Iterate through all the selected rows and add them to the list
        for x in self.CollectionTable.selectionModel().selectedRows():
            SelectedRowsArray.append(x.row())

        # Iterate through the array of selected rows and add their primary key to the second list
        for y in range(0, len(SelectedRowsArray)):
            # The primary key of each item is stored in the first column, which is hidden
            SelectedRowsIDArray.append(self.CollectionTable.item(SelectedRowsArray[y], 0).text())
        # If the user hasn't selected any items before they pressed the button, their is no point in proceeding
        if len(SelectedRowsIDArray) == 0:
            pass
        else:
            # Data has to be passed into a SQL command as a tuple
            SelectedRowsIDTuple = tuple(SelectedRowsIDArray)
            # Delete each item in the tuple from the database
            for z in range(0, len(SelectedRowsIDArray)):
                self.MyCursor.execute("DELETE FROM " + self.OpenCollectionTable + " WHERE PK_" + self.OpenCollectionTable + " = %s" % (SelectedRowsIDTuple[z]))
            # Save changes to database
            self.MyDB.commit()

            self.UpdateSizes()

            # Refresh table to get rid of deleted items
            self.PopulateTable()
            # Display temporary message to user informing them that operation was successful
            self.StatusBar.showMessage("Selected items have been deleted", 3000)

    # This function is executed when DeleteDuplicatesBTN is pressed
    # It deletes all duplicate items from the database
    def DeleteDuplicatesMethod(self):
        # Get columns from open collection table
        self.MyCursor.execute("SHOW COLUMNS FROM " + self.OpenCollectionTable)
        MyResult6 = self.MyCursor.fetchall()

        # Construct a SQL command which will select all the duplicate entries in the table using the COUNT(*) command
        SQLStatement = "SELECT "
        for x in range(1, len(MyResult6) - 4):
            SQLStatement += "`" + MyResult6[x][0] + "`, "
        SQLStatement += MyResult6[len(MyResult6) - 4][0] + " FROM " + self.OpenCollectionTable + " GROUP BY "
        for x in range(1, len(MyResult6) - 4):
            SQLStatement += "`" + MyResult6[x][0] + "`, "
        SQLStatement += MyResult6[len(MyResult6) - 4][0] + " HAVING COUNT(*) > 1"
        self.MyCursor.execute(SQLStatement)
        MyResult7 = self.MyCursor.fetchall()

        # Iterate through duplicate entries
        for x in range(0, len(MyResult7)):
            # Construct a SQL command which returns the primary key of each duplicate record
            SQLStatement2 = "SELECT PK_" + self.OpenCollectionTable + " FROM " + self.OpenCollectionTable + " WHERE "
            # For loop starts at 1 because the first instance of the duplicate entry isn't deleted
            for y in range(1, len(MyResult6) - 4):
                SQLStatement2 += "`" + str(MyResult6[y][0]) + "` = '" + str(MyResult7[x][y - 1]) + "' AND "
            SQLStatement2 += "`" + str(MyResult6[len(MyResult6) - 4][0]) + "` = '" + str(MyResult7[x][len(MyResult7[x]) - 1]) + "' ORDER BY PK_" + self.OpenCollectionTable + " DESC"
            self.MyCursor.execute(SQLStatement2)
            # MyResult8 stores all the duplicate entry primary keys
            MyResult8 = self.MyCursor.fetchall()

            # For each duplicate record (there may be more than one duplicate) delete it from the SQL table
            for z in range(0, len(MyResult8) - 1):
                self.MyCursor.execute("DELETE FROM " + self.OpenCollectionTable + " WHERE PK_" + self.OpenCollectionTable + " = " + str(MyResult8[z][0]))
                # Save changes to database
                self.MyDB.commit()

        self.UpdateSizes()

        # Refresh table to get rid of deleted items
        self.PopulateTable()
        # Display temporary message to user informing them that operation was successful
        self.StatusBar.showMessage("Duplicate items have been deleted", 3000)

    # Executed when the size of the collection changes (i.e. when items are added or deleted)
    def UpdateSizes(self):
        # Get the size of the collection
        self.MyCursor.execute("SELECT COUNT(*) FROM " + self.OpenCollectionTable)
        MyResult9 = self.MyCursor.fetchall()
        # Store the size in the database alongside the date that size was recorded at
        self.MyCursor.execute("INSERT INTO Sizes (TimeRecorded, Magnitude, FK_Collections_Sizes) VALUES ('" + str(datetime.now()) + "', " + str(MyResult9[0][0]) + ", " + str(self.OpenCollectionID) + ")")
        # Save changes to database
        self.MyDB.commit()


# Inherits from QToolButton
# Used to create toolbar buttons in InitToolbar()
class ToolBarBTN(QToolButton):
    # Takes the arguments Text and IconPath
    # IconPath is the file path for the icon the button displays
    def __init__(self, Text, IconPath):
        super(ToolBarBTN, self).__init__()
        self.setText(Text)
        self.setIcon(QIcon(IconPath))
        self.setIconSize(QSize(50, 50))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setFixedWidth(90)

# RareWidget is a styled QLabel enclosed within a QWidget
# It is displayed in the table widget for any item that is tagged as rare
class RareWidget(QWidget):
    def __init__(self):
        super(RareWidget, self).__init__()
        RarityLBL = QLabel("Rare")
        RarityLBL.setStyleSheet("background: #7C5295; color: white; font-weight: bold; font-size: 12px; border-radius: 5px;")
        RarityLBL.setAlignment(Qt.AlignCenter)
        RarityLBL.setFixedSize(40, 20)
        self.setObjectName("BorderlessWidget")
        self.setStyleSheet("background-color: rgba(0,0,0,0%)")
        RarityLayout = QHBoxLayout(self)
        RarityLayout.addWidget(RarityLBL)
        RarityLayout.setAlignment(Qt.AlignVCenter)
        RarityLayout.setContentsMargins(0, 0, 0, 0)

# RatingWidget displays an image of stars out of five based on the value stored in the Rating column
class RatingWidget(QWidget):
    # Takes the argument Rating, this is just an integer out of five
    def __init__(self, Rating):
        super(RatingWidget, self).__init__()
        RatingLBL = QLabel()
        RatingPixmap = QPixmap()
        # Format value of Rating into file path to get correct picture
        RatingPixmap.load("Resources/{0} stars.png".format(Rating))
        RatingLBL.setPixmap(RatingPixmap.scaledToHeight(20))
        RatingLBL.setAlignment(Qt.AlignCenter)
        self.setObjectName("BorderlessWidget")
        self.setStyleSheet("background-color: rgba(0,0,0,0%)")
        RatingLayout = QHBoxLayout(self)
        RatingLayout.addWidget(RatingLBL)
        RatingLayout.setAlignment(Qt.AlignVCenter)
        RatingLayout.setContentsMargins(0, 0, 0, 0)