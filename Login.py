import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import mysql.connector
import hashlib
from functools import partial
import re
import CollectionWindow

# This object inherits from the QMessageBox class which is used to create popup windows
# This popup is displayed when a connection with the SQL database can't be established
class SQLErrorPopup(QMessageBox):
    def __init__(self, RootWindow):
        super(SQLErrorPopup, self).__init__()
        self.RootWindow = RootWindow
        # Initialise window elements
        self.setText("Database Error")
        self.setText("There was an error connecting to the database")
        self.setInformativeText(
        """We came across an error when trying to initialise a connection with our database.
Please press the retry button to try connecting again.
If the problem persists, please contact customer support""")
        self.setIcon(QMessageBox.Critical)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        # If the user presses the retry button, the TestConnection function will be executed again
        self.button(QMessageBox.Retry).clicked.connect(self.RootWindow.TestConnection)
        # If they press the cancel button, the application will close
        self.button(QMessageBox.Cancel).clicked.connect(sys.exit)

        # Apply stylesheet to popup window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        self.exec()

# This object inherits from the QMainWindow class
# It displays the login window, validates user credentials and grants the user access if they provide valid login details
class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()

        # The central widget is a container for all the other widgets the window displays
        self.CentralWidget = QWidget()
        self.CentralWidget.setObjectName("BorderlessWidget")
        self.setCentralWidget(self.CentralWidget)
        self.setWindowTitle("Login")

        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Keeps track of how many unsuccessful login attempts have been made
        self.Attempts = 4
        # Keeps track of how many times the user has made more than 4 login attempts
        self.Magnitude = 1

        self.InitUI()
        # TestConnection has been repurposed as a method of the LoginWindow class
        self.TestConnection()

    # Tests the program's connection with the SQL database
    def TestConnection(self):
        # Try establishing a connection with the database and creating a cursor
        try:
            self.MyDB = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="Anthology"
            )
            self.MyCursor = self.MyDB.cursor()
            self.show()
        # If the program encounters an error when trying to connect, an instance of the error popup is executed
        except mysql.connector.Error:
            self.SQLErrorPopupInstance = SQLErrorPopup(RootWindow = self)

    # This method initialises all the UI elements in the window
    def InitUI(self):
        self.LoginVBL1 = QVBoxLayout()

        # # Displays an image of the app logo
        # LogoLBL = QLabel()
        # LogoPixmap = QPixmap("Resources/Logo.png")
        # LogoLBL.setPixmap(LogoPixmap)
        # LogoLBL.setAlignment(Qt.AlignCenter)
        # self.LoginVBL1.addWidget(LogoLBL)

        # Create sublayout
        InnerHBL = QHBoxLayout()
        # Align elements within layout to the left
        InnerHBL.setAlignment(Qt.AlignLeft)
        InnerHBL.setSpacing(5)
        # Create a label for displaying the logo image
        LogoLBL = QLabel()
        # Create pixmap for logo image
        LogoPixmap = QPixmap("Resources/Logo3.png").scaledToHeight(60)
        LogoLBL.setPixmap(LogoPixmap)
        LogoLBL.setAlignment(Qt.AlignCenter)
        InnerHBL.addWidget(LogoLBL)
        # Create another sublayout for the text
        InnerVBL = QVBoxLayout()
        InnerVBL.setSpacing(0)
        InnerVBL.setAlignment(Qt.AlignVCenter)
        # Create heading label
        LogoLBL1 = QLabel("Anthology")
        # Style heading
        LogoLBL1.setStyleSheet("font-size: 30px;")
        InnerVBL.addWidget(LogoLBL1)
        # Create subheading label
        LogoLBL2 = QLabel("Cataloguing Software")
        # Style subheading
        LogoLBL2.setStyleSheet("font: italic")
        # Add widgets to layout
        InnerVBL.addWidget(LogoLBL2)
        InnerHBL.addLayout(InnerVBL)
        self.LoginVBL1.addLayout(InnerHBL)

        self.WelcomeLBL = QLabel("Welcome Back!")
        self.WelcomeLBL.setStyleSheet("padding-top: 20px; padding-bottom: 20px; font-size: 15px;")
        self.LoginVBL1.addWidget(self.WelcomeLBL)

        # Text box for user to input username
        self.UsernameTB = QLineEdit()
        self.UsernameTB.setPlaceholderText("Username")
        self.LoginVBL1.addWidget(self.UsernameTB)

        # Text box for user to input password
        self.PasswordTB = QLineEdit()
        # EchoMode determines how the text will be displayed
        # In this case it will be hidden because the password is sensitive information
        self.PasswordTB.setEchoMode(QLineEdit.Password)
        self.PasswordTB.setPlaceholderText("Password")
        self.LoginVBL1.addWidget(self.PasswordTB)

        self.SignInBTN = QPushButton("Sign In")
        # Bind sign in button to CheckCredentials function
        self.SignInBTN.clicked.connect(self.CheckCredentials)
        self.LoginVBL1.addWidget(self.SignInBTN)

        # This button is used to create a new account
        self.CreateAccountBTN = QPushButton("Create An Account")
        self.CreateAccountBTN.setStyleSheet("""
        QPushButton:pressed { color: D5E8D4; }
        QPushButton:hover:!pressed { color: #96BA8A; }
        QPushButton { border: 0px; background-color: white; font-size: 10px; }
        """)
        ButtonFont = QFont()
        ButtonFont.setUnderline(True)
        self.CreateAccountBTN.setFont(ButtonFont)
        # Bind CreateAccountBTN to CreateAccountMethod function
        self.CreateAccountBTN.clicked.connect(self.CreateAccountMethod)
        self.LoginVBL1.addWidget(self.CreateAccountBTN)

        # Displays artwork alongside login form
        ArtLBL = QLabel()
        ArtPixmap = QPixmap("Resources/LoginArt.png").scaledToHeight(280)
        ArtLBL.setPixmap(ArtPixmap)

        # Combine layouts and add layouts to central widget
        self.LoginHBL1 = QHBoxLayout()
        self.LoginHBL1.addLayout(self.LoginVBL1)
        self.LoginHBL1.addWidget(ArtLBL)
        self.LoginHBL1.setContentsMargins(0, 0, 0, 0)
        self.LoginVBL1.setContentsMargins(22, 22, 0, 22)
        self.CentralWidget.setLayout(self.LoginHBL1)

        # Prevent user from being able to resize window
        self.setFixedSize(400, self.minimumHeight())

    # This function checks user inputted credentials against the credentials stored in the database
    def CheckCredentials(self):
        # If the user hasn't exceeded the maximum amount of attempts permitted...
        if self.Attempts > 1:
            self.InputUsername = self.UsernameTB.text()
            # Passwords stored in the database are hashed so the user input has to be hashed before it can be compared
            self.InputPassword = hashlib.sha224(bytes(self.PasswordTB.text(), encoding = "utf-8")).hexdigest()

            # Retrieve all entries from the Users table
            self.MyCursor.execute("SELECT * FROM Users")
            MyResult = self.MyCursor.fetchall()

            # Boolean value indicates whether a successful login has been made
            self.SuccessfulLogin = False

            # Iterate through query result and compare each username and password combination with the user inputs
            for x in range(0, len(MyResult)):
                if MyResult[x][1] == self.InputUsername:
                    if MyResult[x][2] == self.InputPassword:
                        self.SuccessfulLogin = True
                        self.ActiveUserID = MyResult[x][0]
                        break

            # If the user has inputted correct credentials, they will be logged into the application and the login window will close
            if self.SuccessfulLogin:
                self.CollectionWindow = CollectionWindow.CollectionWindow(MyCursor = self.MyCursor, MyDB = self.MyDB, ActiveUserID = self.ActiveUserID)
                self.close()
            # If their crednetials are incorrect, an error message is displayed informing them of how many attempts they have remaining
            else:
                self.Attempts -= 1
                self.WelcomeLBL.setText("Incorrect Login Credentials\nyou have " + str(self.Attempts) + " attempts remaining")
                self.WelcomeLBL.setStyleSheet("color: red; font-size: 10px; padding-top: 20px; padding-bottom: 10px;")
        # If user has exceeded max attempts, login screen is disabled for a period of time
        else:
            self.WelcomeLBL.setText("Too many incorrect login attempts\nLogin disabled for {0} seconds".format(10 * self.Magnitude))
            self.SignInBTN.setEnabled(False)
            self.UsernameTB.setEnabled(False)
            self.PasswordTB.setEnabled(False)
            self.UsernameTB.setStyleSheet("border-color: red;")
            self.PasswordTB.setStyleSheet("border-color: red;")
            self.SignInBTN.setStyleSheet("border-color: red; background-color: #ececec")
            self.setCursor(Qt.ForbiddenCursor)
            # Time period for which window is disabled is calculated by multiplying 10 seconds by the variable self.Magnitude
            # Each time the user exceeds the max, self.Magnitude is incremented so they will have to wait 10 seconds longer
            QTimer.singleShot(10000 * self.Magnitude, partial(self.TimerSlot))

    # TimerSlot is called when the QTimer is complete
    # It re-enables the login window, resets the no. of attempts and increments self.Magnitude
    def TimerSlot(self):
        self.SignInBTN.setEnabled(True)
        self.UsernameTB.setEnabled(True)
        self.PasswordTB.setEnabled(True)
        self.WelcomeLBL.setText("Welcome Back!")
        self.WelcomeLBL.setStyleSheet("padding-top: 20px; padding-bottom: 20px; font-size: 15px;")
        self.UsernameTB.setStyleSheet("border-color: black; border: 1px solid #5A5A5A;")
        self.PasswordTB.setStyleSheet("border-color: black; border: 1px solid #5A5A5A;")
        self.SignInBTN.setStyleSheet("border-color: black; border: 1px solid #5A5A5A;")
        self.setCursor(Qt.ArrowCursor)
        self.Attempts = 4
        self.Magnitude += 1

    # When the user presses the create account button, an instance of CreateAccountWindow is initialised
    def CreateAccountMethod(self):
        self.CreateAccountWindowInstance = CreateAccountWindow(RootPos = self.geometry(), MyCursor = self.MyCursor, MyDB = self.MyDB)

# This object inherits from the QMainWindow class
# It displays the create account window, validates user inputs and adds the new account to the database
class CreateAccountWindow(QMainWindow):
    def __init__(self, RootPos, MyCursor, MyDB):
        super(CreateAccountWindow, self).__init__()

        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # The database cursor and connection have to be passed into the object as parameters
        self.MyCursor = MyCursor
        self.MyDB = MyDB

        self.CentralWidget = QWidget()
        self.setCentralWidget(self.CentralWidget)
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint))
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowModality(Qt.ApplicationModal)

        # Position new window in top center of parent window
        self.move(int(RootPos.x() - ((250 - 400) / 2)), int(RootPos.y()))

        self.InitUI()
        self.show()
        self.setFixedSize(250, 158)

    def InitUI(self):
        # Initialise layouts
        self.CreateAccountVBL1 = QVBoxLayout()
        self.CreateAccountVBL2 = QVBoxLayout()

        self.HeaderLBL = QLabel("Let's Create Your Account!")
        self.HeaderLBL.setAlignment(Qt.AlignCenter)
        self.HeaderLBL.setStyleSheet("font-size: 14px; padding: 5px; background-color: #D5E8D4; border-left: 1px solid #5A5A5A; border-right: 1px solid #5A5A5A; border-top: 1px solid #5A5A5A;")
        self.CreateAccountVBL1.addWidget(self.HeaderLBL)
        self.CreateAccountVBL1.setContentsMargins(0, 0, 0, 0)
        self.CreateAccountVBL2.setContentsMargins(10, 0, 10, 10)

        # Text box for user to input their email address
        self.EmailTB = QLineEdit()
        self.EmailTB.setPlaceholderText("Email Address")
        self.CreateAccountVBL2.addWidget(self.EmailTB)

        # Text box for user to input their password
        self.PasswordTB = QLineEdit()
        self.PasswordTB.setPlaceholderText("Password")
        self.PasswordTB.setEchoMode(QLineEdit.Password)
        self.CreateAccountVBL2.addWidget(self.PasswordTB)

        # Text box for user to input their password a second time to make sure user doesn't mistype password
        self.ConfirmPasswordTB = QLineEdit()
        self.ConfirmPasswordTB.setPlaceholderText("Confirm Password")
        self.ConfirmPasswordTB.setEchoMode(QLineEdit.Password)
        self.CreateAccountVBL2.addWidget(self.ConfirmPasswordTB)

        self.CreateAccountBTN = QPushButton("Create Account")
        self.CreateAccountBTN.clicked.connect(self.SubmitNewAccount)

        self.CancelBTN = QPushButton("Cancel")
        self.CancelBTN.clicked.connect(self.close)

        # Combine layouts and add layouts to central widget
        self.CreateAccountHBL1 = QHBoxLayout()
        self.CreateAccountHBL1.addWidget(self.CancelBTN)
        self.CreateAccountHBL1.addWidget(self.CreateAccountBTN)
        self.CreateAccountVBL2.addLayout(self.CreateAccountHBL1)
        self.CreateAccountVBL1.addLayout(self.CreateAccountVBL2)
        self.CentralWidget.setLayout(self.CreateAccountVBL1)

    # This function validates user inputs and then adds credentials to database or displays an error message accordingly
    def SubmitNewAccount(self):
        # Use regex to verify input is a valid email address
        EmailCheck = re.match("[^z]+@[^z]+\.[^z]+", self.EmailTB.text())

        # If any text boxes are empty, the two password inputs don't match or the email address isn't valid, an error message is displayed
        if (self.ConfirmPasswordTB.text() != self.PasswordTB.text() or
            not self.ConfirmPasswordTB.text() or
                not self.PasswordTB.text() or
                not self.EmailTB.text() or
                EmailCheck == None):
            self.HeaderLBL.setStyleSheet("font-size: 10px; background-color: #FF6961; border-left: 1px solid #5A5A5A; border-right: 1px solid #5A5A5A; border-top: 1px solid #5A5A5A;")
            self.HeaderLBL.setText("There was an Error Creating Your Account\nMake sure that you are using a valid email address")

        # If user inputs are valid, they are stored in the Users table
        else:
            PasswordHash = hashlib.sha224(bytes(self.PasswordTB.text(), encoding = "utf-8")).hexdigest()
            self.MyCursor.execute("INSERT INTO Users (Email, PasswordHash) VALUES (%s, %s)", (self.EmailTB.text(), PasswordHash))
            self.MyDB.commit()
            self.close()

# Main program loop
if __name__ == "__main__":
    # A QApplication instance must be created before any windows are displayed
    App = QApplication(sys.argv)
    App.setWindowIcon(QIcon("Resources/Icon.png"))
    # Begin database connection test
    Root = LoginWindow()
    # Begin program execution
    sys.exit(App.exec())