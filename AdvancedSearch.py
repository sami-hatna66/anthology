from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# This is the object which contains the advanced search window
# It inherits from QWidget and takes the same arguments as AddItemWindow
class AdvancedSearch(QWidget):
    # This signal is emitted when a successful search has been carried out
    SearchCompleteSignal = pyqtSignal(list)
    def __init__(self, MyCursor, MyDB, ActiveUserID, OpenCollectionID, OpenCollectionTable, widget = None):
        super(AdvancedSearch, self).__init__()

        # Set arguments to attributes
        self.MyCursor = MyCursor
        self.MyDB = MyDB
        self.ActiveUserID = ActiveUserID
        self.OpenCollectionID = OpenCollectionID
        self.OpenCollectionTable = OpenCollectionTable

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Initialise main layout
        self.AdvancedSearchVBL1 = QVBoxLayout()
        self.setLayout(self.AdvancedSearchVBL1)

        # Get columns from SQL table
        self.MyCursor.execute("SHOW FIELDS FROM " + self.OpenCollectionTable)
        MyResult1 = self.MyCursor.fetchall()
        # ConditionList stores the column names
        self.ConditionList = []
        # ConditionDataTypeList stores each columns data type
        self.ConditionDataTypeList = []
        for x in range(1, len(MyResult1) - 1):
            self.ConditionList.append(MyResult1[x][0])
            self.ConditionDataTypeList.append(MyResult1[x][1])
        # Remove the rare column from the list of conditions
        self.ConditionList.remove("Rare")
        # Remove its data type from the list of datat types
        self.ConditionDataTypeList.remove(b'tinyint(1)')

        # This list stored each instance of ConditionWidget for future reference
        self.ConditionWidgetsList = []

        self.InitUI()

        # Set the window to close when the parent window closes
        self.setAttribute(Qt.WA_QuitOnClose, False)
        # Give the window a transparent background so the outline image can be used as the window background
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Make window modal
        self.setWindowModality(Qt.ApplicationModal)
        # Make window frameless and keep it on top of all other windows
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint))

        # Determine where window should be positioned based on the widget which is passed in as an argument
        x = widget.mapToGlobal(QPoint(0, 0)).x()
        y = widget.mapToGlobal(QPoint(0, 0)).y() + widget.height()
        # The window should appear on the screen just below the AddItemBTN which is clicked to create it
        self.move(x, y)

        # Show window
        self.show()

    # This method initialises widgets and arranges them in layouts
    def InitUI(self):
        # Header label informs the user of the purpose of the window
        HeaderLBL = QLabel("Advanced Search")
        HeaderLBL.setStyleSheet("font-size: 16px;")
        HeaderLBL.setAlignment(Qt.AlignCenter)
        self.AdvancedSearchVBL1.addWidget(HeaderLBL)

        # Users will add conditions to this scroll area
        self.AdvancedSearchScrollArea = QScrollArea()
        # Add scroll area to main layout
        self.AdvancedSearchVBL1.addWidget(self.AdvancedSearchScrollArea)
        self.AdvancedSearchScrollArea.setWidgetResizable(True)
        # Widget which displays within the scroll area
        self.ScrollAreaWidget = QWidget()
        self.ScrollAreaWidget.setObjectName("BorderlessWidget")
        # Initialise layout of ScrollAreaWidget
        self.ScrollAreaLayout = QVBoxLayout()
        self.ScrollAreaLayout.setAlignment(Qt.AlignTop)
        self.OuterLayout = QVBoxLayout()
        self.OuterLayout.addLayout(self.ScrollAreaLayout)
        self.ScrollAreaWidget.setLayout(self.OuterLayout)
        self.AdvancedSearchScrollArea.setWidget(self.ScrollAreaWidget)

        self.CheckBoxLayouts = QHBoxLayout()
        self.OuterLayout.addLayout(self.CheckBoxLayouts)
        # This combobox allows users to filter query results based on their rarity
        self.CheckBoxLayouts.addWidget(QLabel("Rare:"))
        self.RareCB = QComboBox()
        self.RareCB.addItems(["Both", "True", "False"])
        self.RareCB.setFixedWidth(80)
        self.CheckBoxLayouts.addWidget(self.RareCB)
        self.CheckBoxLayouts.addSpacing(50)
        self.CheckBoxLayouts.addWidget(QLabel("Thumbnail:"))
        # This combobox allows users to filter query results based on whether they have a thumbnail or not
        self.ThumbnailCB = QComboBox()
        self.ThumbnailCB.addItems(["Both", "True", "False"])
        self.ThumbnailCB.setFixedWidth(80)
        self.CheckBoxLayouts.addWidget(self.ThumbnailCB)
        self.CheckBoxLayouts.addStretch()

        # This label displays when the advanced search returns no results
        self.ErrorLBL = QLabel("Your search returned no results")
        self.ErrorLBL.setAlignment(Qt.AlignCenter)
        self.ErrorLBL.setStyleSheet("color: red; ")
        self.AdvancedSearchVBL1.addWidget(self.ErrorLBL)
        # The label is initially hidden
        self.ErrorLBL.hide()

        # This is the button the user presses when they want to add a new condition
        self.AddConditionBTN = QPushButton("Add New Condition")
        # Bind button to function
        self.AddConditionBTN.clicked.connect(self.AddCondition)
        self.AdvancedSearchVBL1.addWidget(self.AddConditionBTN)

        ActionBTNsHBL = QHBoxLayout()
        # CancelBTN closes the advanced search window when it is clicked
        self.CancelBTN = QPushButton("Cancel")
        self.CancelBTN.clicked.connect(self.close)
        # SubmitBTN carries out the advanced search
        self.SubmitBTN = QPushButton("Submit")
        self.SubmitBTN.clicked.connect(self.ConductSearch)
        ActionBTNsHBL.addWidget(self.CancelBTN)
        ActionBTNsHBL.addWidget(self.SubmitBTN)
        self.AdvancedSearchVBL1.addLayout(ActionBTNsHBL)

        # Create an initial condition widget
        # The argument First is set to True for this instance to inform the object that this is the first condition widget in the window
        ConditionWidgetInstance = ConditionWidget(Conditions = self.ConditionList, DataTypes = self.ConditionDataTypeList, First = True)
        # Add widget to list
        self.ConditionWidgetsList.append(ConditionWidgetInstance)
        # Add widget to scroll area
        self.ScrollAreaLayout.addWidget(self.ConditionWidgetsList[0])

    # This method is executed when the user clicks AddConditionBTN
    def AddCondition(self):
        # Create an instance of ConditionWidget
        # Set arguments Conditions and DataTypes to the lists of column names and data types created in the constructor
        ConditionWidgetInstance = ConditionWidget(Conditions = self.ConditionList, DataTypes = self.ConditionDataTypeList, First = False)

        # Add instance to list for future reference
        self.ConditionWidgetsList.append(ConditionWidgetInstance)
        # Bind signal emitted when the condition is deleted to the slot
        self.ConditionWidgetsList[len(self.ConditionWidgetsList) - 1].DeleteConditionSignal.connect(self.DeleteConditionSlot)

        # Add widget to scroll area
        self.ScrollAreaLayout.addWidget(ConditionWidgetInstance)

    # This slot is executed when DeleteConditionSignal is emitted
    # It removes the deleted object from the list of condition widgets
    def DeleteConditionSlot(self, Sender):
        self.ConditionWidgetsList.remove(Sender)

    # This method is executed when the user presses SubmitBTN
    # It retrieves the user's inputs and constructs a SQL query from them
    def ConductSearch(self):
        # SQLStatement stores the string of the SQL query which will be executed
        SQLStatement = "SELECT * FROM " + self.OpenCollectionTable + " WHERE "
        # Iterate through each condition widget, retrieving the user's inputs and adding the new conditions to the query
        for widget in self.ConditionWidgetsList:
            # If the widget is the first widget in the scroll area, there won't be any OR or AND statement coming after it
            if widget.First:
                SQLStatement += "`" + widget.ConditionCB.currentText() + "`"
            else:
                # Append the user's choice of operator, then the choice of column to search, then the search text to the string
                SQLStatement += widget.OperatorCB.currentText() + " `" + widget.ConditionCB.currentText() + "`"
            # Use the appropriate comparison operator based on the user's choice in the MatchType combobox
            if widget.MatchTypeCB.currentText() == "Exact Match":
                SQLStatement += " = '" + widget.ConditionTB.text() + "' "
            else:
                SQLStatement += " LIKE '%" + widget.ConditionTB.text() + "%' "
        # Execute SQL query
        self.MyCursor.execute(SQLStatement)
        MyResult2 = self.MyCursor.fetchall()

        # Filter the query results based on the user's rarity filter
        for result in MyResult2:
            # If the user wants results that are both rare and not rare, do nothing to the results
            if self.RareCB.currentText() == "Both":
                continue
            # If the user only wants rare results, delete all non-rare results
            elif self.RareCB.currentText() == "True":
                if not result[len(result) - 3]:
                    MyResult2.remove(result)
            # If the user only wants non-rare results, delete all rare results
            else:
                if result[len(result) - 3]:
                    MyResult2.remove(result)

        # Filter the query results based on the user's thumbnail
        for result in MyResult2:
            # If the user wants results that both have a thumbnail and don't, do nothing to the results
            if self.ThumbnailCB.currentText() == "Both":
                continue
            # If the user only wants results with a thumbnail, delete all results that don't have a thumbnail
            elif self.ThumbnailCB.currentText() == "True":
                if result[len(result) - 1] is None:
                    MyResult2.remove(result)
            # If the user only wants results without a thumbnail, delete all results that do have a thumbnail
            else:
                if result[len(result) - 1] is not None:
                    MyResult2.remove(result)

        # If the SQL query returns no results, display the error message
        if len(MyResult2) == 0:
            self.ErrorLBL.show()
            QTimer.singleShot(3000, self.ErrorLBL.hide)
        # If the search returns results, emit the corresponding signal
        else:
            # The signal takes the result of the query as a parameter
            self.SearchCompleteSignal.emit(MyResult2)
            self.close()

    # Inbuilt PyQt function
    # sizeHint is the preferred size of the widget
    # It has to be set so that the painter event can paint the outline image according to these dimensions
    def sizeHint(self):
        return QSize(725, 425)

    # This event runs when the window is first initialized
    # It draws the outline/background of the window as the image "AddItemOutline.png"
    # This allows me to create irregularly shaped windows
    def paintEvent(self, event):
        # Create painter
        Painter = QPainter()
        # Start painter, set painter to perform on AddItemWindow (self)
        Painter.begin(self)
        # Create pixmap to act as guide for painter
        Outline = QPixmap()
        Outline.load('Resources/AdvancedSearchOutline.png')
        # Paint window as Outline pixmap
        Painter.drawPixmap(QPoint(0, 0), Outline)
        # End paint event
        Painter.end()

# This class inherits from QWidget
# It is the widget which allows users to input search terms, select the column to be searched, selects the comparison operator and choose AND or OR
class ConditionWidget(QWidget):
    # This signal is emitted when the user chooses to delete the widget through its context menu
    DeleteConditionSignal = pyqtSignal(QObject)
    def __init__(self, Conditions, DataTypes, First):
        super(ConditionWidget, self).__init__()

        # Set arguments to attributes
        # Conditions is a list of all the columns in the collection's SQL table
        self.Conditions = Conditions
        # DataTypes is a list of each column's data type
        self.DataTypes = DataTypes
        # First is a boolean value conveying if the widget is the first condition widget or not
        self.First = First

        self.setObjectName("BorderlessWidget")

        # Initialise and set widget layout
        self.ConditionWidgetLayout = QHBoxLayout()
        self.setLayout(self.ConditionWidgetLayout)

        # If the widget isn't the first widget, it will contains an OperatorCB for selecting the condition's logical operator
        if not First:
            self.OperatorCB = QComboBox()
            self.OperatorCB.addItems(["or", "and"])
            self.OperatorCB.setFixedWidth(70)
            self.ConditionWidgetLayout.addWidget(self.OperatorCB)

        # This text box is for inputting the search term for this widget
        self.ConditionTB = QLineEdit()
        self.ConditionWidgetLayout.addWidget(self.ConditionTB)

        self.ConditionWidgetLayout.addWidget(QLabel("in"))

        # This combobox contains the name of each column in the table as an option to choose from
        # It is used to select the column the user would like to query
        self.ConditionCB = QComboBox()
        self.ConditionCB.addItems(self.Conditions)
        self.ConditionCB.currentTextChanged.connect(self.CurrentTextChangedSlot)
        self.ConditionCB.setFixedWidth(130)
        self.ConditionWidgetLayout.addWidget(self.ConditionCB)

        # THe user has a choice between exact matches using the = operator, or partial matches using the LIKE operator
        self.MatchTypeCB = QComboBox()
        self.MatchTypeCB.addItems(["Exact Match", "Partial Match"])
        self.MatchTypeCB.setFixedWidth(130)
        self.ConditionWidgetLayout.addWidget(self.MatchTypeCB)

    # This method is executed when the user selects another item in the combobox
    def CurrentTextChangedSlot(self):
        # If the selected item's data type is integer, a validator is set for the input box to ensure only integers are inputted
        if self.DataTypes[self.ConditionCB.currentIndex()] == b'int':
            self.ConditionTB.setText("")
            self.ConditionTB.setValidator(QIntValidator())
        # If the datatype is anything else, the validator is not needed
        else:
            self.ConditionTB.setValidator(None)

    # This event occurs when the user right-clicks on the widget
    # It displays a contextMenu with the option to delete the condition widget
    def contextMenuEvent(self, event):
        # If the widget is the first one, it can't be deleted as each search query needs at least one condition to be successful
        if self.First:
            pass
        # Every other widget can be deleted
        else:
            # Initialise context menu
            ConditionWidgetContextMenu = QMenu(self)
            # Add action to context menu
            DeleteAction = ConditionWidgetContextMenu.addAction("Delete Condition")
            Action = ConditionWidgetContextMenu.exec_(self.mapToGlobal(event.pos()))
            # If the user selects the delete option from the context menu...
            if Action == DeleteAction:
                # Emit the delete signal which is received by the AdvancedSearch parent class
                self.DeleteConditionSignal.emit(self)
                # Setting the widget's parent to None deletes it
                self.setParent(None)