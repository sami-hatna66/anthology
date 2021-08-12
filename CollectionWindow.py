from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import math
import Login
import OpenCollection
from datetime import datetime

# This object stores the window which displays collections belonging to the logged in user and allows them to create new collections
class CollectionWindow(QMainWindow):
    def __init__(self, MyCursor, ActiveUserID, MyDB):
        super(CollectionWindow, self).__init__()

        # The database connection, cursor and the id of the user currently logged in are passed into this object as arguments
        # The database connection, cursor and the id of the user currently logged in are passed into this object as arguments
        self.ActiveUserID = ActiveUserID
        self.MyCursor = MyCursor
        self.MyDB = MyDB

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Set window widget and initialise main layouts
        self.CentralWidget = QWidget()
        self.setCentralWidget(self.CentralWidget)
        self.CollectionVBL1 = QVBoxLayout()
        self.CollectionVBL1.setContentsMargins(0, 0, 0, 0)
        self.CollectionGL1 = QGridLayout()
        self.CentralWidget.setLayout(self.CollectionVBL1)

        # ContainerWidget contains the status bar displayed at the top of the window
        # The status bar conatins a lgout button and a label outputting the currently logged in user
        self.ContainerWidget = QWidget()
        self.ContainerWidget.setObjectName("ContainerWidget")
        self.CollectionHBL1 = QHBoxLayout()
        self.CollectionHBL1.setContentsMargins(0, 0, 0, 0)
        LogoutBTN = QPushButton()
        LogoutBTN.clicked.connect(self.Logout)
        LogoutBTN.setIcon(QIcon("Resources/LogoutIcon.png"))
        LogoutBTN.setStyleSheet("width: 20px; padding: 5px; border-bottom: 0px; border-right: 0px;")
        self.MyCursor.execute("SELECT Email FROM Users WHERE PK_Users = " + str(self.ActiveUserID))
        SignedInUserLBL = QLabel("Logged in as " + str(self.MyCursor.fetchall()[0][0]))
        SignedInUserLBL.setStyleSheet("background-color: #D5E8D4; padding: 5px; border-top: 1px solid #5A5A5A;")
        self.CollectionHBL1.addWidget(LogoutBTN)
        self.CollectionHBL1.addWidget(SignedInUserLBL)
        self.CollectionHBL1.addStretch()
        self.ContainerWidget.setLayout(self.CollectionHBL1)
        self.CollectionVBL1.addWidget(self.ContainerWidget)

        self.InitUI()

        # Horizontal layout contains the navigation buttons and the scroll area used to display the collections
        self.CollectionHBL2 = QHBoxLayout()
        self.CollectionHBL2.setContentsMargins(10, 0, 10, 0)
        self.CollectionVBL1.addLayout(self.CollectionHBL2)

        # Initialise scroll area and set the widget which will be displayed within it
        self.CollectionScrollArea = QScrollArea()
        self.CollectionScrollArea.setObjectName("BorderlessWidget")
        # The user will navigate the scroll area using buttons, so the scroll bars are set to hidden
        self.CollectionScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.CollectionScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.CollectionScrollArea.setWidgetResizable(True)
        self.CollectionWidget = QWidget()
        self.CollectionWidget.setObjectName("BorderlessWidget")
        self.CollectionWidget.setLayout(self.CollectionGL1)
        self.CollectionScrollArea.setWidget(self.CollectionWidget)

        # LeftArrowBTN and RightArrowBTN are used to navigate left and right within the scroll are
        self.LeftArrowBTN = QPushButton()
        self.LeftArrowBTN.setIcon(QIcon("Resources/LeftArrow.png"))
        self.LeftArrowBTN.setStyleSheet("background-color: white; border: 0px;")
        self.LeftArrowBTN.clicked.connect(self.MoveLeft)
        self.LeftArrowBTN.setFixedSize(10, 300)

        self.RightArrowBTN = QPushButton()
        self.RightArrowBTN.setIcon(QIcon("Resources/RightArrow.png"))
        self.RightArrowBTN.setStyleSheet("background-color: white; border: 0px;")
        self.RightArrowBTN.clicked.connect(self.MoveRight)
        self.RightArrowBTN.setFixedSize(10, 90)

        # Add widgets to layout
        self.CollectionHBL2.addWidget(self.LeftArrowBTN)
        self.CollectionHBL2.addWidget(self.CollectionScrollArea)
        self.CollectionHBL2.addWidget(self.RightArrowBTN)

        self.setFixedSize(690, 410)
        self.CollectionVBL1.addStretch()

        # Display window
        self.show()

    # This function is called when the user wants to log out of the current account
    # It creates a new instance of the LoginWindow class and closes the current window
    def Logout(self):
        self.LoginWindowInstance = Login.LoginWindow()
        self.close()

    # MoveLeft and MoveRight are executed when the left and right navigation buttons are pressed
    # They simply move the scrollbar along by 160 pixels
    def MoveLeft(self):
        self.CollectionScrollArea.horizontalScrollBar().setValue(
            self.CollectionScrollArea.horizontalScrollBar().value() - 160)

    def MoveRight(self):
        self.CollectionScrollArea.horizontalScrollBar().setValue(
            self.CollectionScrollArea.horizontalScrollBar().value() + 160)

    # This function populates the scroll area with buttons for each collection and a button for creating collections
    def InitUI(self):
        # Remove any widgets already in the layout before repopulating it
        for i in reversed(range(self.CollectionGL1.count())):
            self.CollectionGL1.itemAt(i).widget().setParent(None)

        # Initialise create collection button and add to grid layout
        self.CreateCollectionBTN = QToolButton()
        self.CreateCollectionBTN.setIcon(QIcon("Resources/AddItemIcon.png"))
        self.CreateCollectionBTN.setIconSize(QSize(50, 50))
        self.CreateCollectionBTN.setToolTip("Create a new collection")
        self.CreateCollectionBTN.setObjectName("CollectionButton")
        self.CreateCollectionBTN.setFixedWidth(140)
        self.CreateCollectionBTN.clicked.connect(self.CreateNewCollection)
        self.CollectionGL1.addWidget(self.CreateCollectionBTN, 0, 0)

        # Retrieve all collections that belong to the currently logged in user from the database
        self.MyCursor.execute("SELECT * FROM Collections WHERE FK_Users_Collections = " + str(self.ActiveUserID))
        self.MyResult1 = self.MyCursor.fetchall()

        # The following code iterates through the result of the database query and creates a button for each collection which is added to the grid layout
        # Counters are used to keep track of which row and column the program is in
        Populated = False
        RowCounter = 0
        ResultCounter = 0
        ColumnCounter = 1
        self.CollectionBTNArray = []
        Division = math.ceil(len(self.MyResult1) / 3)
        while not Populated:
            if ResultCounter == len(self.MyResult1):
                Populated = True
            elif ColumnCounter <= Division:
                self.CollectionBTNArray.append(CollectionButton(Data = self.MyResult1[ResultCounter]))
                self.CollectionBTNArray[ResultCounter].DeleteCollectionSignal.connect(self.DeleteCollectionSlot)
                self.CollectionBTNArray[ResultCounter].OpenCollectionSignal.connect(self.OpenCollectionSlot)
                self.CollectionBTNArray[ResultCounter].EditCollectionSignal.connect(self.EditCollection)
                self.CollectionGL1.addWidget(self.CollectionBTNArray[ResultCounter], RowCounter, ColumnCounter)
                ColumnCounter += 1
                ResultCounter += 1
            else:
                RowCounter += 1
                ColumnCounter = 0

    def EditCollection(self, Sender):
        self.EditCollectionWindowInstance = AddCollectionWindow(MyCursor = self.MyCursor, ActiveUserID = self.ActiveUserID, MyDB = self.MyDB, RootPos = self.geometry(), Type = "Edit", ID = Sender)
        self.EditCollectionWindowInstance.CreateCollectionSignal.connect(self.InitUI)

    # This slot is executed when this class receives the DeleteCollection signal from the CollectionButton object
    # Its purpose is to delete the collection and its corresponding table from the database and refresh the window
    def DeleteCollectionSlot(self, IDForDeletion):
        self.MyCursor.execute("DROP TABLE Table" + str(IDForDeletion))
        self.MyCursor.execute("DELETE FROM Collections WHERE PK_Collections = " + str(IDForDeletion))
        self.MyCursor.execute("DELETE FROM Sizes WHERE FK_Collections_Sizes = " + str(IDForDeletion))
        self.MyDB.commit()
        self.InitUI()

    # This function is executed when the create collection button is pressed
    # It creates an instance of the AddCollectionWindow object
    def CreateNewCollection(self):
        self.AddCollectionWindowInstance = AddCollectionWindow(MyCursor = self.MyCursor, ActiveUserID = self.ActiveUserID, MyDB = self.MyDB, RootPos = self.geometry(), Type = "Add")
        self.AddCollectionWindowInstance.CreateCollectionSignal.connect(self.InitUI)

    # This function is executed when one of the collection buttons is pressed
    # It creates an instance of OpenCollectionInstance, passing in the relevant arguments for that collection
    def OpenCollectionSlot(self, IDForOpening):
        self.OpenCollectionInstance = OpenCollection.OpenCollectionWindow(MyCursor = self.MyCursor, ActiveUserID = self.ActiveUserID, MyDB = self.MyDB, OpenCollectionID = IDForOpening)
        self.close()

# Subclass of QPushButton used to create buttons for each collection
class CollectionButton(QPushButton):
    # This signal is emitted when the user selects Delete Collection in the widget's context menu
    DeleteCollectionSignal = pyqtSignal(int)
    OpenCollectionSignal = pyqtSignal(int)
    EditCollectionSignal = pyqtSignal(int)
    # The only argument passed into this object is the name and primary key of the collection it is supposed to represent
    def __init__(self, Data):
        super(CollectionButton, self).__init__()
        self.Data = Data
        self.setText(self.Data[1])
        # Properties are values attached to a widget, this will be used when the user wants to open or delete the collection by clicking on the button
        self.setProperty("Key", self.Data[0])
        self.setObjectName("CollectionButton")
        self.setFixedWidth(140)
        self.clicked.connect(self.OpenCollection)

    # This event occurs when the user right clicks on a button
    # It create a context menu with the option to delete a collection
    def contextMenuEvent(self, event):
        PropertyWidgetContextMenu = QMenu(self)
        DeleteAction = PropertyWidgetContextMenu.addAction("Delete Collection")
        EditAction = PropertyWidgetContextMenu.addAction("Edit Collection")
        Action = PropertyWidgetContextMenu.exec_(self.mapToGlobal(event.pos()))
        # If the user chooses to delete the collection, DeleteCollectionSignal emits
        if Action == DeleteAction:
            self.setParent(None)
            self.DeleteCollectionSignal.emit(self.Data[0])
        if Action == EditAction:
            self.EditCollectionSignal.emit(self.Data[0])

    # When the button is clicked, this method is called
    def OpenCollection(self):
        self.OpenCollectionSignal.emit(self.Data[0])

# This object creates the window which allows users to create new collections
class AddCollectionWindow(QMainWindow):
    # This signal is emitted to inform the CollectionWindow class that a new collection has been added to the database and the display needs to be refreshed
    CreateCollectionSignal = pyqtSignal()
    def __init__(self, ActiveUserID, MyCursor, MyDB, RootPos, Type, ID = None):
        super(AddCollectionWindow, self).__init__()

        self.ActiveUserID = ActiveUserID
        self.MyCursor = MyCursor
        self.MyDB = MyDB
        self.Type = Type
        self.ID = ID
        self.ForDeletion = []

        # Instances of PropertyWidget are created dynamically, so they will be stored in this array
        self.PropertyWidgetArray = []
        # Counter keeps track of how many instances of PropertyWidget exist
        self.PropertyWidgetCounter = 0
        self.PropertyWidgetCounter2 = 0

        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint))
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowModality(Qt.ApplicationModal)

        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Set central widget and initialise vertical box layout
        self.CentralWidget = QWidget()
        self.setCentralWidget(self.CentralWidget)
        self.CreateCollectionVBL1 = QVBoxLayout()
        self.CentralWidget.setLayout(self.CreateCollectionVBL1)

        self.InitUI()

        self.setFixedSize(450, 400)
        self.move(int(RootPos.x() + 112), int(RootPos.y()))

        self.show()

    def InitUI(self):
        # Create header and add to layout
        if self.Type == "Add":
            HeaderLBL = QLabel("Create New Collection")
        else:
            HeaderLBL = QLabel("Edit Collection")
        HeaderLBL.setStyleSheet("font-size: 16px;")
        HeaderLBL.setAlignment(Qt.AlignCenter)
        self.CreateCollectionVBL1.addWidget(HeaderLBL)

        # The first text input box is for inputting the name of the collection
        self.CreateCollectionHBL1 = QHBoxLayout()
        self.CreateCollectionHBL1.addWidget(QLabel("Name"))
        self.NameTB = QLineEdit()
        self.CreateCollectionHBL1.addWidget(self.NameTB)
        self.CreateCollectionVBL1.addLayout(self.CreateCollectionHBL1)

        # The user creates collections by adding named properties, these property widgets are displayed in a scroll area
        self.CreateCollectionScrollArea = QScrollArea()
        self.CreateCollectionScrollArea.setWidgetResizable(True)
        self.CreateCollectionScrollArea.verticalScrollBar().setStyleSheet("QScrollBar { border-right: 0px; border-top: 0px; border-bottom: 0px; } QScrollBar::handle { border-top: 0px; border-bottom: 0px; }")
        self.ScrollAreaWidget = QWidget()
        self.ScrollAreaWidget.setObjectName("BorderlessWidget")
        self.ScrollAreaLayout = QVBoxLayout()
        self.ScrollAreaLayout.setAlignment(Qt.AlignTop)
        self.ScrollAreaWidget.setLayout(self.ScrollAreaLayout)
        self.CreateCollectionScrollArea.setWidget(self.ScrollAreaWidget)
        self.CreateCollectionVBL1.addWidget(self.CreateCollectionScrollArea)

        # Button for adding a new property
        self.AddNewPropertyBTN = QPushButton("Add New Property")
        self.AddNewPropertyBTN.clicked.connect(self.AddNewProperty)
        self.CreateCollectionVBL1.addWidget(self.AddNewPropertyBTN)

        # Two buttons, one for cancelling the operation and one for submitting the new collections
        self.CreateCollectionHBL2 = QHBoxLayout()
        self.CancelBTN = QPushButton("Cancel")
        self.CancelBTN.clicked.connect(self.close)
        self.CreateCollectionHBL2.addWidget(self.CancelBTN)
        if self.Type == "Add":
            self.CreateCollectionBTN = QPushButton("Create Collection")
            self.CreateCollectionBTN.clicked.connect(self.CreateCollection)
        else:
            self.CreateCollectionBTN = QPushButton("Edit Collection")
            self.CreateCollectionBTN.clicked.connect(self.SubmitEdits)
        self.CreateCollectionHBL2.addWidget(self.CreateCollectionBTN)
        self.CreateCollectionVBL1.addLayout(self.CreateCollectionHBL2)

        if self.Type == "Add":
            self.AddNewProperty()
        else:
            self.InitForEdit()

    def SubmitEdits(self):
        for deletions in self.ForDeletion:
            self.MyCursor.execute("ALTER TABLE Table" + str(self.ID) + " DROP COLUMN `" + deletions + "`")
        for x in range(0, len(self.PropertiesCorresponding)):
            self.MyCursor.execute("ALTER TABLE Table" + str(self.ID) + " RENAME COLUMN `" + self.Columns[x] + "` TO `" + self.PropertiesCorresponding[x].PropertyNameTB.text() + "`")
        for y in range(0, len(self.PropertyWidgetArray)):
            if self.PropertyWidgetArray[y].TypeCB.currentText() == "Text":
                DataType = "Varchar (500)"
            else:
                DataType = "Integer (255)"
            self.MyCursor.execute("ALTER TABLE Table" + str(self.ID) + " ADD COLUMN `" + self.PropertyWidgetArray[y].PropertyNameTB.text() + "` " + DataType + " AFTER " + self.Columns[len(self.Columns) - 1])
        self.MyCursor.execute("UPDATE Collections SET CollectionName = '" + self.NameTB.text() + "' WHERE PK_Collections = " + str(self.ID))
        self.MyDB.commit()
        self.CreateCollectionSignal.emit()
        self.close()

    def InitForEdit(self):
        self.MyCursor.execute("SELECT * FROM Collections WHERE PK_Collections = " + str(self.ID))
        self.NameTB.setText(self.MyCursor.fetchall()[0][1])
        self.MyCursor.execute("SHOW FIELDS FROM Table" + str(self.ID))
        self.Columns = self.MyCursor.fetchall()
        self.Columns = [columns[0] for columns in self.Columns[1:len(self.Columns) - 3]]
        self.PropertiesCorresponding = []
        for x in range(0, len(self.Columns)):
            self.PropertiesCorresponding.append(PropertyWidget(Number=self.PropertyWidgetCounter2 + 1))
            self.ScrollAreaLayout.addWidget(self.PropertiesCorresponding[self.PropertyWidgetCounter2])
            self.PropertiesCorresponding[self.PropertyWidgetCounter2].DeletePropertySignal.connect(self.DeletePropertySlot2)
            self.PropertiesCorresponding[self.PropertyWidgetCounter2].PropertyNameTB.setText(self.Columns[x])
            self.PropertyWidgetCounter2 += 1

    def DeletePropertySlot2(self, Sender):
        self.ForDeletion.append(Sender.PropertyNameTB.text())
        Index = self.PropertiesCorresponding.index(Sender)
        self.Columns.pop(Index)
        self.PropertiesCorresponding.pop(Index)

    # This function adds a new property widget to the scroll area
    def AddNewProperty(self):
        self.PropertyWidgetArray.append(PropertyWidget(Number = self.PropertyWidgetCounter + 1))
        self.ScrollAreaLayout.addWidget(self.PropertyWidgetArray[self.PropertyWidgetCounter])
        self.PropertyWidgetArray[self.PropertyWidgetCounter].DeletePropertySignal.connect(self.DeletePropertySlot)
        self.PropertyWidgetCounter += 1

    # This function stores a new entry in the Collections table and create the collection's corresponding table
    # See database design section of report for more info (page 36)
    def CreateCollection(self):
        # Presence check to ensure all fields are filled in
        EmptyString = False
        EmptyPropertyWidgetIndexes = []
        for x in range(0, len(self.PropertyWidgetArray)):
            if self.PropertyWidgetArray[x].PropertyNameTB.text() == "":
                EmptyString = True
                EmptyPropertyWidgetIndexes.append(x)

        # If presence check flags an unfilled field, execute error function
        if EmptyString or self.NameTB.text() == "":
            self.CreateCollectionError(EmptyPropertyWidgetIndexes)
        else:
            # Get name of new collections
            Name = self.NameTB.text()
            # Insert new entry into Collections table
            self.MyCursor.execute("INSERT INTO Collections (CollectionName, FK_Users_Collections) VALUES ('{0}', '{1}')".format(Name, self.ActiveUserID))
            self.MyCursor.execute("SELECT MAX(PK_Collections) FROM Collections")
            self.MyResult1 = self.MyCursor.fetchall()
            # New table name consists of "table" + primary key of the entry that has just been stored in Collections table
            SQLStatement = "CREATE TABLE Table" + str(self.MyResult1[0][0]) + " (PK_Table" + str(self.MyResult1[0][0]) + " INTEGER(255) NOT NULL AUTO_INCREMENT PRIMARY KEY, "
            # Piece together SQL statement for creation of new table
            for x in range(0, len(self.PropertyWidgetArray)):
                # Get property name and datatype and use as column in new table
                PropertyName = self.PropertyWidgetArray[x].PropertyNameTB.text()
                DataType = self.PropertyWidgetArray[x].TypeCB.currentText()
                if DataType == "Number":
                    DataType = "Integer"
                    SQLStatement = SQLStatement + "`" + PropertyName + "` " + DataType + "(255), "
                else:
                    DataType = "Varchar"
                    SQLStatement = SQLStatement + "`" + PropertyName + "` " + DataType + "(500), "
            # All collections will have a Rare column, a Rating column and a Thumbnail column
            SQLStatement = SQLStatement + " Rare BOOLEAN, Rating INTEGER(20), Thumbnail LONGBLOB)"
            self.MyCursor.execute(SQLStatement)
            # Add new table name to the entry in Collections
            self.MyCursor.execute("UPDATE Collections SET TableName = 'Table" + str(self.MyResult1[0][0]) + "' WHERE PK_Collections = " + str(self.MyResult1[0][0]))

            # When a new collection is created, an entry into Sizes is made with the starting size of 0
            self.MyCursor.execute("INSERT INTO Sizes (TimeRecorded, Magnitude, FK_Collections_Sizes) VALUES ('" + str(datetime.now()) + "', 0, " + str(self.MyResult1[0][0]) + ")")

            # Save changes to database
            self.MyDB.commit()
            # Emit signal to inform CollectionWindow that a new collection has been created and it needs to be refreshed
            self.CreateCollectionSignal.emit()
            self.close()

    # Function is executed when a field has been left empty
    # It takes a list containing the indexes of the empty widgets as a parameter and sets the border of these widgets to red
    def CreateCollectionError(self, OffendingWidgets):
        for x in OffendingWidgets:
            self.PropertyWidgetArray[x].PropertyNameTB.setStyleSheet("border: 1px solid #FF0000")

    # This function is executed when the Delete Property signal is received
    # It deletes the specified property widget
    def DeletePropertySlot(self, Sender):
        self.PropertyWidgetArray.remove(Sender)
        self.PropertyWidgetCounter -= 1
        for x in range(0, len(self.PropertyWidgetArray)):
            self.PropertyWidgetArray[x].PropertyLBL.setText("Property " + str(x + 1))

# Subclass of QWidget
# Each property widget consists of a text input for the name of the property and a combobox for its datatype
class PropertyWidget(QWidget):
    # This signal is emitted when the user wants to delete a property
    DeletePropertySignal = pyqtSignal(QObject)
    def __init__(self, Number):
        super(PropertyWidget, self).__init__()

        self.setObjectName("BorderlessWidget")
        # Initialise widget layout
        self.PropertyWidgetHBL1 = QHBoxLayout()
        self.setLayout(self.PropertyWidgetHBL1)

        self.PropertyLBL = QLabel("Property " + str(Number))
        self.PropertyWidgetHBL1.addWidget(self.PropertyLBL)

        # Text box for inputting property name
        self.PropertyNameTB = QLineEdit()
        self.PropertyWidgetHBL1.addWidget(self.PropertyNameTB)

        TypeLBL = QLabel("Type")
        self.PropertyWidgetHBL1.addWidget(TypeLBL)

        # Combo box for specifiying if property datatype is text or numerical
        self.TypeCB = QComboBox()
        self.TypeCB.addItems(["Text", "Number"])
        self.PropertyWidgetHBL1.addWidget(self.TypeCB)

    # Event executed when user right clicks on property widget
    def contextMenuEvent(self, event):
        PropertyWidgetContextMenu = QMenu(self)
        DeleteAction = PropertyWidgetContextMenu.addAction("Delete Property")
        Action = PropertyWidgetContextMenu.exec_(self.mapToGlobal(event.pos()))
        # If user clicks Delete Property, emit signal
        if Action == DeleteAction:
            self.setParent(None)
            self.DeletePropertySignal.emit(self)