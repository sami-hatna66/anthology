from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# This class is the window for managing loaned items
class LoanItemWindow(QWidget):
    def __init__(self, MyCursor, MyDB, ActiveUserID, OpenCollectionID, OpenCollectionTable, widget = None):
        super(LoanItemWindow, self).__init__()

        # Reassign arguments as attributes
        self.MyCursor = MyCursor
        self.MyDB = MyDB
        self.ActiveUserID = ActiveUserID
        self.OpenCollectionID = OpenCollectionID
        self.OpenCollectionTable = OpenCollectionTable

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Initialise main layout
        self.LoanItemVBL1 = QVBoxLayout()
        self.setLayout(self.LoanItemVBL1)
        self.LoanItemHBL1 = QHBoxLayout()
        self.LoanItemVBL1.addLayout(self.LoanItemHBL1)

        # Set window attributes
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint))

        self.InitUI()

        # Calculate window position
        x = widget.mapToGlobal(QPoint(0, 0)).x() - 225
        y = widget.mapToGlobal(QPoint(0, 0)).y() + widget.height()
        self.move(x, y)

        self.show()
        self.setFixedWidth(905)

    # Initialise widgets
    def InitUI(self):
        # The window is split into two columns; one for items that are available to loan and one for items which have already been loaned out
        self.ToLoanListLayout = QVBoxLayout()
        self.ToLoanListLayout.addWidget(QLabel("Items Available to Loan:"))
        # ToLoanList displays all the items in the collection which haven't been loaned out yet
        self.ToLoanList = QListWidget()
        # Style widget
        self.ToLoanList.setStyleSheet("selection-color: black;")
        self.ToLoanList.verticalScrollBar().setStyleSheet("QScrollBar { border-right: 0px; border-top: 0px; border-bottom: 0px; } QScrollBar::handle { border-top: 0px; border-bottom: 0px; }")
        # Connect the signal emitted when the list's selection is changed to a slot
        self.ToLoanList.itemSelectionChanged.connect(self.ItemSelected)
        # Don't display focus rectangle when item is selected
        self.ToLoanList.setAttribute(Qt.WA_MacShowFocusRect, 0)
        # Add list to layout
        self.ToLoanListLayout.addWidget(self.ToLoanList)
        self.LoanItemHBL1.addLayout(self.ToLoanListLayout)
        self.ToLoanList.setFixedWidth(300)

        self.AlreadyLoanedListLayout = QVBoxLayout()
        self.AlreadyLoanedListLayout.addWidget(QLabel("Loaned Items:"))
        # AlreadyLoanedList displays all the items that have already been loaned out
        self.AlreadyLoanedList = QListWidget()
        # Style widget
        self.AlreadyLoanedList.setStyleSheet("selection-color: black;")
        self.AlreadyLoanedList.verticalScrollBar().setStyleSheet("QScrollBar { border-right: 0px; border-top: 0px; border-bottom: 0px; } QScrollBar::handle { border-top: 0px; border-bottom: 0px; }")
        # Don't show focus rectangle
        self.AlreadyLoanedList.setAttribute(Qt.WA_MacShowFocusRect, 0)
        # Add to layout
        self.AlreadyLoanedListLayout.addWidget(self.AlreadyLoanedList)
        self.LoanItemHBL1.addLayout(self.AlreadyLoanedListLayout)

        # Run PopulateLists method to fill both lists with items
        self.PopulateLists()

        # QDateEdit object used to input the due date of the selected item when loaning it out
        self.PickDueDate = QDateEdit()
        # Set the minimum date the user can input to the current date
        self.PickDueDate.setMinimumDate(QDate.currentDate())
        self.ToLoanListLayout.addWidget(self.PickDueDate)
        # The widget is hidden until the user selects an item in ToLoanList
        self.PickDueDate.hide()

        # OptionsWidget displays two checkboxes
        self.OptionsWidget = QWidget()
        self.OptionsWidget.setObjectName("BorderlessWidget")
        self.OptionsHBL = QHBoxLayout()
        self.OptionsHBL.setSpacing(0)
        self.OptionsHBL.setContentsMargins(0, 0, 0, 0)
        # This checkbox allows the user to choose if they would like to receive push notifications when an item is due
        self.PushNotificationCB = QCheckBox()
        self.PushNotificationCB.setFixedWidth(15)
        self.PushNotificationCB.setStyleSheet("padding-right: 0px;")
        self.PushNotificationCB.setChecked(True)
        self.OptionsHBL.addWidget(self.PushNotificationCB)
        PushLBL = QLabel("Push Notifications")
        PushLBL.setStyleSheet("padding-bottom: 1px; padding-left: 0px;")
        self.OptionsHBL.addWidget(PushLBL)
        # This checkbox allows the user to choose if they would like to receive email notifications when an item is due
        self.EmailNotificationCB = QCheckBox()
        self.EmailNotificationCB.setFixedWidth(15)
        self.EmailNotificationCB.setStyleSheet("padding-right: 0px;")
        self.EmailNotificationCB.setChecked(True)
        self.OptionsHBL.addWidget(self.EmailNotificationCB)
        EmailLBL = QLabel("Email Notifications")
        EmailLBL.setStyleSheet("padding-bottom: 1px; padding-left: 0px;")
        self.OptionsHBL.addWidget(EmailLBL)
        self.OptionsWidget.setLayout(self.OptionsHBL)
        self.ToLoanListLayout.addWidget(self.OptionsWidget)
        # These checkboxes are hidden until the user selects an item in ToLoanList
        self.OptionsWidget.hide()

        # This button allows the user to loan out the selected item in ToLoanList with the due date specified in PickDueDate
        self.SubmitLoanBTN = QPushButton("Loan Item")
        # Bind button to function
        self.SubmitLoanBTN.clicked.connect(self.SubmitLoanMethod)
        self.ToLoanListLayout.addWidget(self.SubmitLoanBTN)
        # Hide button until an item is selected in ToLoanList
        self.SubmitLoanBTN.hide()

        # Button for closing the window
        self.CloseWindowBTN = QPushButton("Close")
        self.CloseWindowBTN.setFixedWidth(50)
        self.CloseWindowBTN.clicked.connect(self.close)
        self.LoanItemVBL1.addWidget(self.CloseWindowBTN)

    # This method populates ToLoanList with items which haven't been loaned out yet and fills AlreadyLoanedList with the items in that collection which have already been loaned out
    def PopulateLists(self):
        # Clear both lists of their contents before repopulating them
        self.ToLoanList.clear()
        self.AlreadyLoanedList.clear()
        # Get the primary key of every item in the current collection's table
        self.MyCursor.execute("SELECT PK_" + self.OpenCollectionTable + " FROM " + self.OpenCollectionTable)
        MyResult1 = self.MyCursor.fetchall()
        # Presence check: if there are no items in the collection, do not proceed
        if len(MyResult1) == 0:
            pass
        # If there are items in the collection, go on to populate the lists
        else:
            # Get every entry into Loans which corresponds with the primary key of the current collection
            self.MyCursor.execute("SELECT KeyInCorrespondingTable FROM Loans WHERE FK_Collections_Loans = " + str(self.OpenCollectionID))
            MyResult2 = self.MyCursor.fetchall()

            # Remove all items from MyResult1 which are also in MyResult2
            # This should leave us with all the loaned items in MyResult2 and all the unloaned items in MyResult1
            MyResult1 = list(set(MyResult1) - set(MyResult2))
            # Repopulate tuple as list
            MyResult1 = [item[0] for item in MyResult1]
            # Sort items into ascending order
            MyResult1.sort()
            # If all the items in the collection have already been loaned out, don't proceed with populating ToLoanList
            if len(MyResult1) == 0:
                pass
            else:
                # Construct a query to select all the items in the SQL table with primary keys in MyResult1
                if len(MyResult1) > 1:
                    SQLStatement = "SELECT * FROM " + self.OpenCollectionTable + " WHERE "
                    for x in range(0, len(MyResult1) - 1):
                        SQLStatement += "PK_" + self.OpenCollectionTable + " = " + str(MyResult1[x]) + " OR "
                    SQLStatement += "PK_" + self.OpenCollectionTable + " = " + str(MyResult1[len(MyResult1) - 1])
                    self.MyCursor.execute(SQLStatement)
                else:
                    self.MyCursor.execute("SELECT * FROM " + self.OpenCollectionTable + " WHERE PK_" + self.OpenCollectionTable + " = " + str(MyResult1[0]))
                # Execute query to get a tuple of all the items which need to go into ToLoanList
                MyResult3 = self.MyCursor.fetchall()

                # Populate ToLoanList with the results of the SQL query
                for item in MyResult3:
                    ListItem = QListWidgetItem(str(item[1]))
                    # setData attaches a hidden value to each list item which can be accessed by calling data() on the item object
                    # In this case, the program attaches the primary key of each item to its corresponding list item
                    ListItem.setData(Qt.UserRole, item[0])
                    self.ToLoanList.addItem(ListItem)

            # Repopulate tuple as list
            MyResult2 = [item[0] for item in MyResult2]
            # If no items have been loaned out, don't proceed with populating AlreadyLoanedList
            if len(MyResult2) == 0:
                pass
            else:
                # Get all the entries into the Loans table which correspond with the current collection
                self.MyCursor.execute("SELECT * FROM Loans WHERE FK_Collections_Loans = " + str(self.OpenCollectionID))
                MyResult5 = self.MyCursor.fetchall()
                # Iterate through query result
                for x in range(0, len(MyResult5)):
                    try:
                        # For each item in the query result, get the corresponding entry into the collection's table
                        self.MyCursor.execute("SELECT * FROM " + self.OpenCollectionTable + " WHERE PK_" + self.OpenCollectionTable + " = " + str(MyResult5[x][3]))
                        MyResult6 = self.MyCursor.fetchall()
                        # Create a list item to enclose the custom list widget
                        ListItem = QListWidgetItem(self.AlreadyLoanedList)
                        # Create an instance of CustomListItem, passing in the results of the SQL query as parameters
                        ListWidgetContents = CustomListItem(Name = MyResult6[0][1], DueDate = MyResult5[x][1].strftime("%d/%m/%Y"), ID = MyResult5[x][0])
                        # Connect the CancelLoanSignal emitted by CustomListItem when CancelLoanBTN is pressed to the corresponding slot
                        ListWidgetContents.CancelLoanSignal.connect(self.CancelLoanSlot)
                        ListItem.setSizeHint(ListWidgetContents.minimumSizeHint())
                        # Set the layout of the container ListItem to the instance of CustomListItem
                        self.AlreadyLoanedList.setItemWidget(ListItem, ListWidgetContents)
                    except:
                        pass

    # This slot is executed when CancelLoanSignal is emitted
    # It takes the parameter Sender which is the instance of CustomListItem which emitted the signal
    def CancelLoanSlot(self, Sender):
        # Delete the corresponding item from the Loans SQL table
        self.MyCursor.execute("DELETE FROM Loans WHERE PK_Loans = " + str(Sender.ID))
        # Save changes to database
        self.MyDB.commit()
        # Repopulate lists
        self.PopulateLists()

    # This slot is executed when an item is selected in ToLoanList
    def ItemSelected(self):
        # If no items are selected, hide PickDueDate, OptionsWidget and SubmitLoanBTN
        if len(self.ToLoanList.selectedItems()) == 0:
            self.PickDueDate.hide()
            self.SubmitLoanBTN.hide()
            self.OptionsWidget.hide()
        # If an item in the list has been selected, show these widgets
        else:
            self.PickDueDate.show()
            self.SubmitLoanBTN.show()
            self.OptionsWidget.show()

    # This method is executed when the user presses SubmitLoanBTN
    # It writes the new loan to the Loans table
    def SubmitLoanMethod(self):
        # Get the primary key corresponding with the item selected in ToLoanList
        SelectedItemID = self.ToLoanList.selectedItems()[0].data(Qt.UserRole)
        # Get the due date the user has inputted
        DueDate = self.PickDueDate.date().toPyDate()
        # Insert new entry into Loans table
        self.MyCursor.execute("INSERT INTO Loans (DueDate, FK_Collections_Loans, KeyInCorrespondingTable, Email, Push) VALUES ('" + str(DueDate) + "', " + str(self.OpenCollectionID) + ", " + str(SelectedItemID) + ", " + str(self.EmailNotificationCB.isChecked()) + ", " + str(self.PushNotificationCB.isChecked()) + ")")
        # Save changes to database
        self.MyDB.commit()
        # Repopulate lists
        self.PopulateLists()

    def sizeHint(self):
        return QSize(910, 505)

    def paintEvent(self, event):
        Painter = QPainter()
        Painter.begin(self)
        Outline = QPixmap()
        Outline.load('Resources/LoanOutline.png')
        Painter.drawPixmap(QPoint(0, 0), Outline)
        Painter.end()

# This object is used to display items in AlreadyLoanedList
# Unlike standard list items, this widget can display multiple lables and buttons
class CustomListItem(QWidget):
    # This signal is emitted when CancelLoanBTN is pressed
    CancelLoanSignal = pyqtSignal(QObject)
    def __init__(self, Name, DueDate, ID):
        super(CustomListItem, self).__init__()

        # Reassign arguments as attribute
        # ID is the primary key of the item
        self.ID = ID
        # Name is the name of the item
        self.Name = Name
        # DueDate is the due date of the item
        self.DueDate = DueDate

        # Initialise horizontal layout
        self.RowHBL = QHBoxLayout()
        self.RowHBL.setContentsMargins(0, 0, 0, 1)
        self.setLayout(self.RowHBL)

        # If the length of the item's name is greater than 26 characters, shorten it and place ellipses at the end of the string
        if len(Name) >= 26:
            self.Name = self.Name[:26] + "..."

        # Create a label displaying the item's name and add it to the layout
        self.NameLBL = QLabel(self.Name)
        self.NameLBL.setFixedWidth(213)
        self.NameLBL.setContentsMargins(5, 0, 0, 0)
        self.RowHBL.addWidget(self.NameLBL)

        # Create a label displaying the item's due date and add it to the layout
        DateLBL = QLabel(self.DueDate)
        DateLBL.setFixedWidth(213)
        DateLBL.setContentsMargins(0, 0, 0, 0)
        self.RowHBL.addWidget(DateLBL)

        # CancelLoanBTN is used to delete loans
        self.CancelLoanBTN = QPushButton("Cancel Loan")
        self.CancelLoanBTN.setContentsMargins(0, 0, 0, 0)
        # Style button
        self.CancelLoanBTN.setStyleSheet("""
        QPushButton:pressed { color: black; }
        QPushButton:hover:!pressed { color: #D5E8D4; }
        QPushButton { border: 0px; background-color: rgba(0, 0, 0, 0); font-size: 13px; color: #96BA8A }
        """)
        ButtonFont = QFont()
        ButtonFont.setUnderline(True)
        self.CancelLoanBTN.setFont(ButtonFont)
        # Connect button's clicked signal so that it emits CancelLoanSignal when pressed
        self.CancelLoanBTN.clicked.connect(lambda: self.CancelLoanSignal.emit(self))
        self.RowHBL.addWidget(self.CancelLoanBTN)

        self.RowHBL.addStretch()
