from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
from tabulate import tabulate
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# This object creates a submenu containing two new tool buttons
# One is for exporting the current collection as a TXT file, the other is for uploading the collection to Google Drive
class ExportSubMenu(QWidget):
    # This signal is emitted when the program is unable to export the collection
    Failed = pyqtSignal()
    # This signal is emitted when the program successfully exports the collection
    Success = pyqtSignal()
    def __init__(self, MyCursor, MyDB, ActiveUserID, OpenCollectionID, OpenCollectionTable, widget = None):
        super(ExportSubMenu, self).__init__()

        # Reassign arguments as attributes
        self.ActiveUserID = ActiveUserID
        self.MyCursor = MyCursor
        self.MyDB = MyDB
        self.OpenCollectionID = OpenCollectionID
        self.OpenCollectionTable = OpenCollectionTable

        # Set window attributes
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Popup))
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Initialise main layout
        self.ExportHBL1 = QHBoxLayout()
        self.setLayout(self.ExportHBL1)

        # Create button for exporting as TXT file
        self.ExportToTxtBTN = QToolButton()
        self.ExportToTxtBTN.setText("Export as TXT\nfile")
        # Set button icon
        self.ExportToTxtBTN.setIcon(QIcon("Resources/ExportTXT.png"))
        self.ExportToTxtBTN.setIconSize(QSize(45, 45))
        self.ExportToTxtBTN.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.ExportToTxtBTN.setFixedWidth(90)
        self.ExportHBL1.addWidget(self.ExportToTxtBTN)
        # Bind button to function with the string parameter "Local" to indicate the user wants a local export rather than a Google Drive export
        self.ExportToTxtBTN.clicked.connect(lambda: self.ExportToTXT(type = "Local"))

        # Create button for uploading collection to Google Drive
        self.ExportGDriveBTN = QToolButton()
        self.ExportGDriveBTN.setText("Upload to \nGoogle Drive")
        # Set button icon
        self.ExportGDriveBTN.setIcon(QIcon("Resources/GDriveIcon.png"))
        self.ExportGDriveBTN.setIconSize(QSize(45, 45))
        self.ExportGDriveBTN.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.ExportGDriveBTN.setFixedWidth(90)
        self.ExportHBL1.addWidget(self.ExportGDriveBTN)
        # Bind button to function with string parameter "GDrive" to indicate the user wants to upload the export to their Google Drive
        self.ExportGDriveBTN.clicked.connect(lambda: self.ExportToTXT(type = "GDrive"))

        # Calculate window position
        x = widget.mapToGlobal(QPoint(0, 0)).x()
        y = widget.mapToGlobal(QPoint(0, 0)).y() + widget.height()
        self.move(x, y)

        # Show window
        self.show()

    # This method is called when either of the buttons are pressed
    # The parameter type tells the program whether the user wants to create a local export or upload the export to their Google Drive
    def ExportToTXT(self, type):
        # Get the collection's column names
        self.MyCursor.execute("SHOW FIELDS FROM " + self.OpenCollectionTable)
        MyResult1 = self.MyCursor.fetchall()
        MyResult1 = [item[0] for item in MyResult1]
        # Remove first and last elements from list to get rid of primary key and thumbnails columns
        MyResult1 = MyResult1[:-1]
        del MyResult1[0]

        # Construct a SQL statement for selecting the data under all columns in the table except for the primary key and thumbnails
        SQLStatement = "SELECT "
        for x in range(0, len(MyResult1) - 1):
            SQLStatement += MyResult1[x] + ", "
        SQLStatement += MyResult1[len(MyResult1) - 1] + " FROM " + self.OpenCollectionTable
        # Execute SQL command
        self.MyCursor.execute(SQLStatement)
        MyResult2 = self.MyCursor.fetchall()
        # Use tabulate library to format query results as an ascii table
        ExportTable = tabulate(MyResult2, headers = MyResult1, tablefmt = "fancy_grid")

        # If the user wants to export locally (they pressed ExportToTxtBTN)...
        if type == "Local":
            # Create a file dialog instance, allowing the user to select the director they would like to export to
            self.DirectoryName = QFileDialog.getExistingDirectory(None, "Select Export Directory", os.path.abspath(os.sep))
            # Try/Except clause provides error checking
            try:
                # Create a new file in the user-specified directory called "AnthologyExport.txt"
                ExportFile = open(self.DirectoryName + "/AnthologyExport.txt", "w")
                # Write the contents of ExportTable to the new file
                ExportFile.write(ExportTable)
                # Close the file to prevent corruption
                ExportFile.close()
                # Emit signal, this should be received by the parent class (OpenCollectionWindow) and should display a message in the status bar informing the user that the export was successful
                self.Success.emit()
            except:
                # If there is an issue during the export, emit the Failed signal which will also display a message in the StatusBar when received
                self.Failed.emit()
        # If the user wants to upload the collection to their Google Drive (they pressed ExportGDriveBTN)...
        else:
            # Try/Except clause once again provides error checking
            try:
                # Create an object to handle authentication
                GoogleLogin = GoogleAuth()
                # Opens browser and displays login screen
                GoogleLogin.LocalWebserverAuth()
                # Create Google Drive object to handle creating and uploading files
                Drive = GoogleDrive(GoogleLogin)

                # Create a file in the Temp directory
                ExportFile = open("Temp/AnthologyExport.txt", "w")
                # Write the contents of ExportTable to the new file
                ExportFile.write(ExportTable)
                ExportFile.close()

                # Open the file in the Temp directory
                with open("Temp/AnthologyExport.txt", "r") as file:
                    # Create a new drive file object
                    FileForUpload = Drive.CreateFile({"title":os.path.basename(file.name)})
                    # Set the contents of the drive file to the contents of the file in the Temp directory
                    FileForUpload.SetContentString(ExportTable)
                    # Upload the file to Google Drive
                    FileForUpload.Upload()

                # delete the file in the Temp directory as it is no longer needed
                os.remove("Temp/AnthologyExport.txt")
                # Emit Success signal
                self.Success.emit()
            # If there is an issue whilst uploading the file to the cloud, execute the following code
            except:
                # Delete the file in the temp directory if it exists
                try:
                    os.remove("Temp/AnthologyExport.txt")
                except:
                    pass
                # Emit Failed signal
                self.Failed.emit()

    def sizeHint(self):
        return QSize(232, 132)

    def paintEvent(self, event):
        Painter = QPainter()
        Painter.begin(self)
        Outline = QPixmap()
        Outline.load('Resources/ExportOutline.png')
        Painter.drawPixmap(QPoint(0, 0), Outline)
        Painter.end()