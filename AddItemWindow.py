from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os

# This class is the window which users add items to the collection from
# It inherits from QWidget rather than QMainWindow because I need to access its painEvent
class AddItemWindow(QWidget):
    # This signal is emitted when the user has successfully added an item to the collection
    # When the OpenCollection object receives this signal, it will execute the function PopulateTable()
    ItemAddedSignal = pyqtSignal(bool)
    # Takes the same arguments as OpenCollectionWindow except for widget which is the toolbar button which is pressed to open the window
    # Widget is an argument because it is used to determine the position of this new window on the screen
    def __init__(self, MyCursor, MyDB, ActiveUserID, OpenCollectionID, OpenCollectionTable, widget = None):
        super(AddItemWindow, self).__init__()

        # Reassign arguments as attributes
        self.ActiveUserID = ActiveUserID
        self.MyCursor = MyCursor
        self.MyDB = MyDB
        self.OpenCollectionID = OpenCollectionID
        self.OpenCollectionTable = OpenCollectionTable
        # Boolean for keeping track of if the user has uploaded a thumbnail or not
        self.ContainsImage = False

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Initialise main window layout
        self.AddItemVBL1 = QVBoxLayout()
        self.setLayout(self.AddItemVBL1)

        self.InitUI()

        # Set this window so that it closes when its parent window is closed
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Modal windows force the user to interact with it before they can go back to using the parent application
        self.setWindowModality(Qt.ApplicationModal)
        # Get rid of window frame and ensure this window always stays on top of other applicaton windows
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint))

        # Determine where window should be positioned based on the widget which is passed in as an argument
        x = widget.mapToGlobal(QPoint(0, 0)).x()
        y = widget.mapToGlobal(QPoint(0, 0)).y() + widget.height()
        # The window should appear on the screen just below the AddItemBTN which is clicked to create it
        self.move(x, y)

        # Show window
        self.show()

    # Initialise and display window widgets
    def InitUI(self):
        # Header label informs users exactly what the window's purpose is
        self.HeaderLBL = QLabel()
        self.HeaderLBL.setText("Add Item")
        self.HeaderLBL.setStyleSheet("font-size: 16px;")
        self.HeaderLBL.setAlignment(Qt.AlignCenter)
        self.AddItemVBL1.addWidget(self.HeaderLBL)

        # The widgets which users use to input data about the item are presented in a scroll area
        self.AddItemScrollArea = QScrollArea()
        self.AddItemScrollArea.verticalScrollBar().setStyleSheet("QScrollBar { border-right: 0px; border-top: 0px; border-bottom: 0px; } QScrollBar::handle { border-top: 0px; border-bottom: 0px; }")
        self.AddItemVBL1.addWidget(self.AddItemScrollArea)
        self.AddItemScrollArea.setWidgetResizable(True)
        # This is the widget the scroll area displays
        self.ScrollAreaWidget = QWidget()
        self.ScrollAreaWidget.setObjectName("BorderlessWidget")
        # This is the grid layout of the widget in the scroll area
        self.ScrollAreaLayout = QGridLayout()
        self.ScrollAreaLayout.setAlignment(Qt.AlignTop)
        self.ScrollAreaWidget.setLayout(self.ScrollAreaLayout)
        self.AddItemScrollArea.setWidget(self.ScrollAreaWidget)

        # Two buttons in this Horizontal layout, one for adding the new item to the collection, and one for cancelling the operation
        ActionBTNsHBL = QHBoxLayout()
        self.CancelBTN = QPushButton("Cancel")
        self.CancelBTN.clicked.connect(self.close)
        self.SubmitBTN = QPushButton("Submit")
        self.SubmitBTN.clicked.connect(self.AddItem)
        ActionBTNsHBL.addWidget(self.CancelBTN)
        ActionBTNsHBL.addWidget(self.SubmitBTN)
        self.AddItemVBL1.addLayout(ActionBTNsHBL)

        self.PopulateScrollArea()

    # This function populates the scroll area with input fields for entering the data about the new item
    def PopulateScrollArea(self):
        # Get all column names and their datatypes from the current collectin's table
        self.MyCursor.execute("SHOW FIELDS FROM " + self.OpenCollectionTable)
        MyResult1 = self.MyCursor.fetchall()
        # Because there will be a variable number of input boxes, they have to be stored in a list for future access
        self.FieldTextBoxes = []

        # Iterate through over each column, creating a new input box for each one (excluding primary key, rare, rating and thumbnail columns)
        for x in range(1, len(MyResult1) - 3):
            # Add a label to the grid layout displaying the column name
            self.ScrollAreaLayout.addWidget(QLabel(MyResult1[x][0]), x, 0)
            # Create a text input box for the current column
            Temp = QLineEdit()
            Temp.setFixedWidth(250)
            # If the datatype of the current column is integer, apply a QIntValidator to that text box
            if MyResult1[x][1] == b'int':
                # QValidators limit the input into a text box, in this case it limits the input to only accepts integers
                Temp.setValidator(QIntValidator())
            # Add text box to grid layout
            self.ScrollAreaLayout.addWidget(Temp, x, 1)
            # Add text box to list
            self.FieldTextBoxes.append(Temp)

        # Add Rare label
        self.ScrollAreaLayout.addWidget(QLabel("Rare"), len(MyResult1) - 2, 0)
        # The user marks an item as rare by checking a check box
        self.RareCheckBox = QCheckBox()
        self.RareCheckBox.setFixedWidth(15)
        # Add check box to grid layout
        self.ScrollAreaLayout.addWidget(self.RareCheckBox, len(MyResult1) - 2, 1)

        # The user uses a slider to select a value from one to five for the item's rating
        self.RatingSlider = QSlider()
        self.RatingSlider.setOrientation(Qt.Horizontal)
        self.RatingSlider.setTickInterval(1)
        self.RatingSlider.setMinimum(1)
        self.RatingSlider.setMaximum(5)
        # When the value of the slider is changed, the signal valueChanged is emitted
        # This signal is triggers the function ChangeRatingImage, which changes the pixmap in RatingImageLBL to display the amount of star corresponding with the value of the slider
        self.RatingSlider.valueChanged.connect(self.ChangeRatingImage)
        self.ScrollAreaLayout.addWidget(self.RatingSlider, len(MyResult1) - 1, 0)
        # This is the label which displays the image of the rating the user has selected
        self.RatingImageLBL = QLabel()
        self.ChangeRatingImage()
        self.ScrollAreaLayout.addWidget(self.RatingImageLBL, len(MyResult1) - 1, 1)

        # The user presses this button to open their system's file explorer
        self.UploadImageBTN = QPushButton("Add Thumbnail")
        self.UploadImageBTN.clicked.connect(self.UploadImage)
        self.UploadImageBTN.setFixedWidth(100)
        self.ScrollAreaLayout.addWidget(self.UploadImageBTN, len(MyResult1), 0)
        # If the user chooses a thumbnail image, this label will be changed to show the name of the currently selected image
        self.UploadedImageLBL = QLabel("No Image Selected")
        self.UploadedImageLBL.setFixedWidth(250)
        self.ScrollAreaLayout.addWidget(self.UploadedImageLBL, len(MyResult1), 1)

    # This function is executed when the valueChange signal is emitted
    # It displays an image of 1 to 5 stars, dependent on the value of RatingSlider
    def ChangeRatingImage(self):
        # Get value of slider
        SliderValue = self.RatingSlider.value()
        # Set label pixmap to corresponding image
        self.RatingImageLBL.setPixmap(QPixmap("Resources/" + str(SliderValue) + " stars.png").scaledToHeight(20, Qt.SmoothTransformation))

    # This function is executed when the user presses UploadImageBTN
    def UploadImage(self):
        # Open file dialog
        # "Image files (*.jpg *.png) limits user selection to only Jpeg or png files
        # This function returns the file path of the selected image
        self.FileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", os.path.abspath(os.sep), "Image files (*.jpg *.png)")
        # If the user selects a file...
        if self.FileName:
            # Change the label text to the name of the selected file
            self.UploadedImageLBL.setText("selected " + os.path.basename(self.FileName))
            # Set boolean value created in __init__ method to true
            self.ContainsImage = True
            # Convert selected image into raw binary data and store under variable self.BinaryData
            with open(self.FileName, "rb") as file:
                self.BinaryData = file.read()

    # This function performs a presence check on the input fields before the item is added to the collection
    def PresenceCheck(self):
        # First perform presence check to ensure that no input fields have been left empty
        EmptyTextBoxes = []
        FilledTextBoxes = []
        Error = False
        # Iterate over each text box and check if they are empty
        for x in range(0, len(self.FieldTextBoxes)):
            if self.FieldTextBoxes[x].text() == "":
                # Append all empty text boxes to this list
                EmptyTextBoxes.append(self.FieldTextBoxes[x])
                # Boolean indicates whether the program has encountered an empty text box yet
                Error = True
            else:
                # Append all filled text boxes to this list
                FilledTextBoxes.append(self.FieldTextBoxes[x])
        # If there are any empty text boxes, run this error handling function
        if Error:
            self.AddItemError(EmptyTextBoxes, FilledTextBoxes)
        else:
            return True

    # This function is executed when the user presses SubmitBTN
    # It collects all the user inputs and formats them into a SQL statement which it then executes
    def AddItem(self):
        if self.PresenceCheck():
            # SQLStatement is a dynamically generated string which stores the SQL command
            SQLStatement = "INSERT INTO " + self.OpenCollectionTable + " ("
            # Get column names from database
            self.MyCursor.execute("SHOW FIELDS FROM " + self.OpenCollectionTable)
            MyResult2 = self.MyCursor.fetchall()
            # Add each column name to the SQL statement
            # The loop starts from 1 because the primary key column should automatically increment itself
            for x in range(1, len(MyResult2) - 3):
                SQLStatement += "`" + MyResult2[x][0] + "`, "
            # If the user has uploaded a thumbnail, add the Thumbnail column to the list of columns in which we are inserting data
            if self.ContainsImage:
                SQLStatement += "Rare, Rating, Thumbnail) VALUES ("
                Count = len(MyResult2) - 1
            # If the user hasn't uploaded a thumbnail, there is no data to insert into Thumbnail column, so its is left out of the command
            else:
                SQLStatement += "Rare, Rating) VALUES ("
                Count = len(MyResult2) - 2
            # %s operator is used to substitute values from DataForInsertion tuple into statement when it is executed
            for x in range(1, Count):
                SQLStatement += "%s, "
            SQLStatement += "%s)"

            # DataForInsertion is the tuple which stores all the data we have retrieved from the user input fields
            DataForInsertion = ()
            # Get the contents of each text box in the window and add it to the tuple
            for x in range(0, len(self.FieldTextBoxes)):
                DataForInsertion += (self.FieldTextBoxes[x].text(), )
            # If user has checked the rare check box, set boolean value of Rare column to TRUE
            if self.RareCheckBox.isChecked():
                DataForInsertion += (True, )
            # Otherwise, the boolean value will be FALSE
            else:
                DataForInsertion += (False, )
            # Add the value of the slider for the Rating column
            DataForInsertion += (self.RatingSlider.value(), )
            # If the user has uploaded an image, add the binary data to the tuple
            if self.ContainsImage:
                DataForInsertion += (self.BinaryData, )
            # Execute the SQL command, substituting the contents of the tuple in for each of the %s operators
            self.MyCursor.execute(SQLStatement, DataForInsertion)
            # Save changes to database
            self.MyDB.commit()
            # Emit signal telling root window to repopulate CollectionTable
            self.ItemAddedSignal.emit(True)
            # Close AddItemWindow
            self.close()

    # This function is executed when the user submits an item but has left one of the input fields blank
    # It highlights each empty text box with a red border
    # It takes two parameters: a list of empty text boxes and a list of filled text boxes
    def AddItemError(self, OffendingWidgets, NonOffendingWidgets):
        # Iterate through list of empty text boxes and set their border to red
        for TextBox in OffendingWidgets:
            TextBox.setStyleSheet("border: 1px solid #FF0000")
        # Iterate through list of filled text boxes and set their border to black
        for TextBox in NonOffendingWidgets:
            TextBox.setStyleSheet("border: 1px solid black")

    # Inbuilt PyQt function
    # sizeHint is the preferred size of the widget
    # It has to be set so that the painter event can paint the outline image according to these dimensions
    def sizeHint(self):
        return QSize(450, 365)

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
        Outline.load('Resources/AddItemOutline.png')
        # Paint window as Outline pixmap
        Painter.drawPixmap(QPoint(0, 0), Outline)
        # End paint event
        Painter.end()
