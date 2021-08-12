from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from bs4 import BeautifulSoup
import pyzbar
import cv2
import requests

# This class contains the window which will display the live video feed, an instruction label and a cancel button
# The two concurrent threads are initialised in this window
# The only argument it takes is the button widget clicked to create it
class BarcodeSearch(QWidget):
    def __init__(self, widget = None):
        super(BarcodeSearch, self).__init__()

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Set window attributes
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint))

        # Initialise main layout
        self.BarcodeSearchVBL1 = QVBoxLayout()
        self.setLayout(self.BarcodeSearchVBL1)

        # This label displays each frame captured by the webcam
        self.FeedLabel = QLabel()
        # Set the image displayed by the window to a generic placeholder image whilst the webcam feed is being set up
        self.FeedLabel.setPixmap(QPixmap("Resources/WebCamConnecting.png"))
        self.BarcodeSearchVBL1.addWidget(self.FeedLabel)

        # This label will be updated to relay messages to the user
        # Currently, it is telling the user how to scan a barcode using the webcam
        self.InstructionLabel = QLabel("Position barcode in camera view")
        self.BarcodeSearchVBL1.addWidget(self.InstructionLabel)

        # The user presses this button when they want to close the window and stop the video feed
        self.CancelBTN = QPushButton("Cancel")
        # The button's clicked signal is connected to the CancelFeed method
        self.CancelBTN.clicked.connect(self.CancelFeed)
        self.BarcodeSearchVBL1.addWidget(self.CancelBTN)

        # Initialise Thread ----------------------------------------------------
        self.Worker1 = VideoFeedWorker()
        # Connect the object's signals to slots/methods in this class
        self.Worker1.ImageUpdateSignal.connect(self.ImageUpdateSlot)
        self.Worker1.BarcodeDetectedSignal.connect(self.BarcodeDetectedSlot)
        # Start the thread
        self.Worker1.start()
        # ----------------------------------------------------------------------

        # Determine where window should be positioned based on the widget which is passed in as an argument
        x = widget.mapToGlobal(QPoint(0, 0)).x() - 600
        y = widget.mapToGlobal(QPoint(0, 0)).y() + widget.height()
        # The window should appear on the screen just below the button which is clicked to create it
        self.move(x, y)

        self.show()

    # This method is executed when the user presses the cancel button
    def CancelFeed(self):
        # Stop the thread from executing
        # If this isn't carried out, the program would continue capturing video which would affect the performance of the program and raise privacy concerns
        self.Worker1.stop()
        # Close window
        self.close()

    # This method is executed when VideoFeedWorker emits BarcodeDetectedSignal
    # It initialises the second QThread object which performs the online barcode search
    def BarcodeDetectedSlot(self, Barcode):
        # Change the text of InstructionLabel to inform the user that the barcode is being searched for
        self.InstructionLabel.setText("Searching Barcode...")
        # Initialise new thread, passing in the detected barcode as an argument
        self.Worker2 = WebSearchWorker(Barcode = Barcode)
        # Connect the object's signals to slots/methods in the parent class
        self.Worker2.SearchCompleteSignal.connect(self.SearchCompleteSlot)
        self.Worker2.SearchFailedSignal.connect(self.SearchFailedSlot)
        # Start the thread
        self.Worker2.start()

    # This method is executed when VideoFeedWorker emits ImageUpdateSignal
    # It sets the image displayed in FeedLabel to the image emitted by the thread
    def ImageUpdateSlot(self, Frame):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Frame))

    # This method is executed when WebSearchWorker emits SearchCompleteSignal
    # It relays the results of the barcode search to the user
    def SearchCompleteSlot(self, Result):
        # Create an instance of the popup, passing the results of the barcode search and FeedLabel object in as arguments
        self.SearchResultPopupInstance = SearchResultPopup(Result = Result, FeedLabel = self.FeedLabel)
        # Connect signals to slots
        self.SearchResultPopupInstance.CopiedSignal.connect(self.CopiedSlot)
        self.SearchResultPopupInstance.NewSearchSignal.connect(self.NewSearchSlot)
        # Create image effect object and apply to FeedLabel
        Effect = QGraphicsColorizeEffect(self.FeedLabel)
        # This effect will change the saturation of the image displayed in the label
        Effect.setStrength(0.7)
        Effect.setColor(QColor("silver"))
        self.FeedLabel.setGraphicsEffect(Effect)

    # This method is executed when SearchResultPopupInstance emits CopiedSignal
    # It changes the text in InstructionLabel to inform the user that they have successfully copied the search results to their clipboard
    def CopiedSlot(self):
        self.InstructionLabel.setText("The search result was copied to your clipboard")
        # Message should display for 6 seconds before feedLabel returns to its usual state
        QTimer.singleShot(6000, self.RevertInstructionLabel)

    # This method is executed when SearchResultPopupInstance emits NewSearchSignal
    # It restarts the Worker1 thread, allowing the user to scan a new barcode
    def NewSearchSlot(self):
        self.FeedLabel.setGraphicsEffect(None)
        # Set FeedLabel's image to a generic placeholder image whilst the webcam feed is being restarted
        self.FeedLabel.setPixmap(QPixmap("Resources/WebCamConnecting2.png"))
        self.Worker1.start()

    # This method is executed when WebSearchWorker emits SearchFailedSignal
    def SearchFailedSlot(self):
        # Sets the text in InstructionLabel to an error message
        self.InstructionLabel.setText("We couldn't find that specific barcode")
        self.InstructionLabel.setStyleSheet("color: red")
        QTimer.singleShot(6000, self.RevertInstructionLabel)
        # Restart video feed
        self.FeedLabel.setPixmap(QPixmap("Resources/WebCamConnecting2.png"))
        self.Worker1.start()

    # This method reverts the InstructionLabel back to its original text
    # It is executed in the QTimer events
    def RevertInstructionLabel(self):
        self.InstructionLabel.setText("Position barcode in camera view")
        self.InstructionLabel.setStyleSheet("color: black")

    # This method is executed when there is an error establishing a connection with the webcam (e.g. the user has no webcam or the webcam is broken)
    def VideoCaptureErrorSlot(self):
        # Display error message
        self.InstructionLabel.setText("There was an issue capturing video, please try relaunching this window")
        self.FeedLabel.setPixmap(QPixmap("Resources/WebcamError.png"))
        self.InstructionLabel.setStyleSheet("color: red")

    # Same paint event as AddItemWindow
    def sizeHint(self):
        return QSize(690, 465)

    def paintEvent(self, event):
        Painter = QPainter()
        Painter.begin(self)
        Outline = QPixmap()
        Outline.load('Resources/BarcodeSearchOutline.png')
        Painter.drawPixmap(QPoint(0, 0), Outline)
        Painter.end()

# This object is the thread which handles displaying the openCV video feed on the user's screen
# It inherits from QThread
class VideoFeedWorker(QThread):
    # Signal for when a new frame has been captured
    # it takes the captured frame image as a parameter
    ImageUpdateSignal = pyqtSignal(QImage)
    # Signal for when a barcode is detected in the frame
    # It takes the upc of the barcode as a parameter
    BarcodeDetectedSignal = pyqtSignal(str)
    # Signal for when there is an error capturing frames
    VideoCaptureErrorSignal = pyqtSignal()
    # Method executed when start() is called on the object
    # Initialises the thread loop
    def run(self):
        # Counter keeps track of how many frames have been recorded
        Counter = 0
        # Boolean value used to signal whether the while loop capturing each frame should continue executing or not
        # This value is set to False when the user presses the cancel button
        self.ThreadActive = True
        # Initialise connection with webcam, the 0 parameter tells the program to select the first webcam connection if the computer has multiple camera inputs
        Capture = cv2.VideoCapture(0)
        # This while loop captures each frame, processes it, scans it for barcodes and sends it back to the main program loop to be displayed in FeedLabel
        # It keeps iterating until boolean is set to False
        # Because it is executing in a concurrent thread, the while loop won't freeze the main program loop
        while self.ThreadActive:
            # Capture frame
            Ret, Frame = Capture.read()
            # If the frame is successfully captured...
            if Ret:
                # Convert frame to object
                Image = cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB)
                # Flip image (OpenCV doesn't automatically mirror images)
                FlippedImage = cv2.flip(Image, 1)
                # The program scans for barcodes every 5 frames
                if Counter % 5 == 0:
                    # Use pyzbar to scan frame for barcodes
                    Barcodes = pyzbar.decode(Frame)
                    # If a barcode is present
                    if Barcodes:
                        # Get the dimensions of the barcode
                        x, y, w, h = Barcodes[0].rect
                        # Draw a red rectangle around the barcode
                        RectImage = cv2.rectangle(FlippedImage, (x, y), (x + w, y + h), (255, 0, 0), 5)
                        # Convert the frame to a format that is compatible with PyQt
                        ConvertToQtFormat = QImage(RectImage.data, RectImage.shape[1], RectImage.shape[0], QImage.Format_RGB888)
                        # Scale image
                        FinalImage = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                        # Emit signal with the captured frame passed in as a parameter
                        # When the parent object receives its signal, it will set the image displayed in FeedLabel to the frame emitted with the signal
                        self.ImageUpdateSignal.emit(FinalImage)
                        # Emit signal with the upc of the scanned barcode passed in as a parameter
                        self.BarcodeDetectedSignal.emit(Barcodes[0].data.decode("utf-8"))
                        # Stop the video feed thread
                        self.stop()
                    # If a barcode isn't detected in the frame...
                    else:
                        # Convert frame to PyQt compatible format
                        ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                        # Scale image
                        FinalImage = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                        # Emit signal
                        self.ImageUpdateSignal.emit(FinalImage)
                # This is the code executed when the number of frames isn't a multiple of 5
                else:
                    # Convert frame to PyQt compatible format
                    ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                    # Scale image
                    FinalImage = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    # Emit signal
                    self.ImageUpdateSignal.emit(FinalImage)
                # Increment counter
                Counter += 1
            # if there is an error capturing the frame, emit the error signal
            else:
                self.VideoCaptureErrorSignal.emit()

    # This method stops the thread from executing
    def stop(self):
        self.ThreadActive = False
        self.quit()

# This thread handles the webscraping barcode search
# Searches for the barcode in two different web databases: upcscavenger.com and upcitemdb.com
# It aslo inherits from QThread
class WebSearchWorker(QThread):
    # Signal for when the search has been successfully completed
    # It takes the string result of the search as a parameter
    SearchCompleteSignal = pyqtSignal(str)
    # Signal for when the search fails to find a result
    SearchFailedSignal = pyqtSignal()

    # Thread constructor
    def __init__(self, Barcode, parent = None):
        QThread.__init__(self, parent)
        self.Barcode = Barcode

    # Start thread
    def run(self):
        # requests.get makes a connection with the website
        # Format the barcode into the url to search for it in their database
        Response = requests.get("http://www.upcscavenger.com/barcode/" + self.Barcode + "/#page=barcode")
        # Create a parser object, passing in the HTML file from the requests.get()
        Soup = BeautifulSoup(Response.text, "html.parser")
        # Parse the file for the specific class which contains the result text, then strip any line breaks from the result
        Result = Soup.find(class_ = "us2329735521 us2445479844").find(class_ = "us1881050501").get_text().replace("\n", "")
        # If the search on the first website does not return a result, try searching the second website
        if Result == self.Barcode:
            try:
                # Connect with second website
                Response2 = requests.get("https://www.upcitemdb.com/upc/" + self.Barcode, verify = False)
                # Create second parser object
                Soup2 = BeautifulSoup(Response2.text, "html.parser")
                # Locate HTML class
                Result2 = Soup2.find(class_ = "num").find("li").get_text()
                # Emit signal
                self.SearchCompleteSignal.emit(Result2)
            # If the second search also doesn't return a result, emit SearchFailedSignal
            except:
                self.SearchFailedSignal.emit()
        # If the first search is successful, emit SearchCompleteSignal, passing in the search result as a parameter
        else:
            self.SearchCompleteSignal.emit(Result)

# This object is the window which relays the results of the barcode search to the user
# It takes the result of the search and the FeedLabel object as arguments
class SearchResultPopup(QWidget):
    # Signal for when the search result has been copied to the clipboard
    CopiedSignal = pyqtSignal()
    # Signal for when the user wants to scan a new barcode
    NewSearchSignal = pyqtSignal()
    def __init__(self, Result, FeedLabel):
        super(SearchResultPopup, self).__init__()

        # Assign arguments as attributes
        self.Result = Result
        self.FeedLabel = FeedLabel

        # Create clipboard object
        self.Clipboard = QApplication.clipboard()
        self.Clipboard.clear(mode=self.Clipboard.Clipboard)

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Set window attributes
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint))

        # Initialise main layout
        self.VBL = QVBoxLayout()
        self.setLayout(self.VBL)

        InfoLabel = QLabel("Your Search Result Is:")
        InfoLabel.setStyleSheet("font-size: 14px;")
        self.VBL.addWidget(InfoLabel)

        # Label for displaying the result of the search
        ResultLabel = QLabel(self.Result)
        ResultLabel.setStyleSheet("font-size: 18px; color: red; padding: 5px;")
        # The label will be displayed in a scroll area in case the label is longer than the width of the window
        self.ResultScrollArea = QScrollArea()
        self.ResultScrollArea.setWidget(ResultLabel)
        self.ResultScrollArea.setStyleSheet("QScrollBar:horizontal { border-bottom: 0px; border-left: 0px; border-right: 0px; } QScrollBar::handle { border-left: 0px; border-right: 0px; }")
        self.ResultScrollArea.setFixedHeight(50)
        self.VBL.addWidget(self.ResultScrollArea)

        self.ActionBTNHBL = QHBoxLayout()
        # Button for copying the search result to the clipboard
        self.CopyClickboardBTN = QPushButton("Copy to clipboard")
        self.CopyClickboardBTN.clicked.connect(self.CopyToClipboard)
        self.ActionBTNHBL.addWidget(self.CopyClickboardBTN)
        # Button for starting a new barcode search
        self.ScanAgain = QPushButton("Scan a new barcode")
        self.ScanAgain.clicked.connect(self.StartNewSearch)
        self.ActionBTNHBL.addWidget(self.ScanAgain)
        self.VBL.addLayout(self.ActionBTNHBL)

        self.setFixedSize(400, 140)

        # Position widget in the middle of FeedLabel
        x = self.FeedLabel.mapToGlobal(QPoint(0, 0)).x() + (self.FeedLabel.width() / 2) - (self.width() / 2)
        y = self.FeedLabel.mapToGlobal(QPoint(0, 0)).y() + (self.FeedLabel.height() / 2) - (self.height() / 2)
        self.move(x, y)

        self.show()

    # When the user wants to start a new barcode search, the appropriate signal is emitted and the popup window is closed
    def StartNewSearch(self):
        self.NewSearchSignal.emit()
        self.close()

    # When the user wants to copy the result, it is copied to their clipboard and the appropriate signal is emitted
    def CopyToClipboard(self):
        self.Clipboard.setText(self.Result)
        self.CopiedSignal.emit()
