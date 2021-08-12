from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import dates as matplotlibdates
from math import log10, floor
from datetime import datetime
import os

# This object is the window which displays the graphs generated from the user's collection
# It uses matplotlib to plot the graphs
class GraphWidget(QWidget):
    def __init__(self, MyCursor, MyDB, ActiveUserID, OpenCollectionID, OpenCollectionTable, widget = None):
        super(GraphWidget, self).__init__()

        # Reassign arguments as attributes
        self.MyCursor = MyCursor
        self.MyDB = MyDB
        self.ActiveUserID = ActiveUserID
        self.OpenCollectionID = OpenCollectionID
        self.OpenCollectionTable = OpenCollectionTable

        # Apply stylesheet to window
        with open("Stylesheet/Stylesheet.txt", "r") as ss:
            self.setStyleSheet(ss.read())

        # Set window attributes (same as AddItemWindow)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint))

        # Initialise main window layout
        self.GraphWidgetVBL1 = QVBoxLayout()
        self.setLayout(self.GraphWidgetVBL1)

        # Retrieve column names from table
        self.MyCursor.execute("SHOW FIELDS FROM " + self.OpenCollectionTable)
        self.GraphTypes = self.MyCursor.fetchall()
        # Remove thumbnails from list
        self.GraphTypes.pop(len(self.GraphTypes) - 1)
        # Add Collection Size category to list
        self.GraphTypes.append(("Collection Size", ))
        # Index keeps track of which graph is currently being displayed
        self.GraphTypesIndex = 1

        # Horizontal layout for displaying the graph/chart and its legend
        self.FigureHBL = QHBoxLayout()

        self.FigureWidget = QWidget()
        self.FigureWidget.setObjectName("BorderlessWidget")
        self.FigureWidgetLayout = QVBoxLayout()
        self.FigureWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.FigureWidget.setLayout(self.FigureWidgetLayout)
        # Create MatPlotLib figure for displaying the graph/chart
        self.Figure = Figure()
        # Create MatPlotLib canvas and pass figure in as argument
        self.Canvas = FigureCanvas(self.Figure)
        # Add canvas to layout
        self.FigureWidgetLayout.addWidget(self.Canvas)
        self.FigureHBL.addWidget(self.FigureWidget)
        self.GraphWidgetVBL1.addLayout(self.FigureHBL)

        # Create MatPlotLib figure for displaying the legend
        self.LegendFigure = Figure()
        # Create MatPlotLib canvas and pass figure in as argument
        self.LegendCanvas = FigureCanvas(self.LegendFigure)
        self.FigureHBL.addWidget(self.LegendCanvas)

        # Horizontal box layout for displaying the navigation and action buttons
        self.NavigationHBL = QHBoxLayout()
        # BackBTN is used to navigate to the previous graph
        self.BackBTN = QPushButton()
        self.BackBTN.setIcon(QIcon("Resources/LeftArrow2.png"))
        self.BackBTN.clicked.connect(self.PreviousGraph)
        self.BackBTN.setFixedWidth(40)
        # ForwardBTN is used to naviagte to the next graph
        self.ForwardBTN = QPushButton()
        self.ForwardBTN.setIcon(QIcon("Resources/RightArrow2.png"))
        self.ForwardBTN.clicked.connect(self.NextGraph)
        self.ForwardBTN.setFixedWidth(40)
        # CloseBTN closes the window
        self.CloseBTN = QPushButton("Close")
        self.CloseBTN.clicked.connect(self.close)
        self.CloseBTN.setFixedWidth(50)
        # ExportBTN is used to export the graph as a png
        self.ExportBTN = QPushButton("Save as Image")
        self.ExportBTN.clicked.connect(self.ExportGraph)
        self.ExportBTN.setFixedWidth(100)
        # Label displays message to user when graph is successfully exported as image
        self.ExportStatusLBL = QLabel("Successfully Exported graph as 'AnthologyExport.png'")
        self.ExportStatusLBL.hide()
        # Add buttons to layout
        self.NavigationHBL.addWidget(self.BackBTN)
        self.NavigationHBL.addWidget(self.ForwardBTN)
        self.NavigationHBL.addWidget(self.CloseBTN)
        self.NavigationHBL.addWidget(self.ExportBTN)
        self.NavigationHBL.addWidget(self.ExportStatusLBL)
        self.GraphWidgetVBL1.addLayout(self.NavigationHBL)
        # Push buttons to the left hand side of the layout
        self.NavigationHBL.addStretch()

        # Execute ChooseGraph method to display the first graph
        self.ChooseGraph(self.GraphTypes[self.GraphTypesIndex][0])

        # Position window below GenerateGraphsBTN using widget argument
        x = widget.mapToGlobal(QPoint(0, 0)).x() - 720
        y = widget.mapToGlobal(QPoint(0, 0)).y() + widget.height()
        self.move(x, y)

        # Show window
        self.show()

    # Executed when the user clicks ExportBTN
    # It exports the graph currently being displayed as a png
    def ExportGraph(self):
        # Open file dialog and allow user to select a directory to export to
        # The file path of this directory is stored under the variable FilePath
        self.FilePath = QFileDialog.getExistingDirectory(None, "Select Export Directory", os.path.abspath(os.sep))
        # If the graph being exported is a line chart, the legend is not required
        if self.GraphTypes[self.GraphTypesIndex] == ("Collection Size",):
            # Save the image to the user-specified directory with the name AnthologyExport.png
            try:
                self.Figure.savefig(self.FilePath + "/AnthologyExport.png")
            except:
                pass
        # If the graph is a pie chart and has an index, QPainter is used to place the two images together and export them as a single image
        else:
            # Save graph and legend as separate images in Temp directory
            # They need to be joined together to produce the final export image
            self.Figure.savefig("Temp/Export1.png")
            self.LegendFigure.savefig("Temp/Export2.png")
            # Now load both images as QImage objects
            GraphImage = QImage("Temp/Export1.png")
            LegendImage = QImage("Temp/Export2")
            # Create a new QPixmap for the export
            # The width of the new image is the sum of the width of the graph image and the legend image
            FinalExport = QPixmap(QSize(GraphImage.width() + LegendImage.width(), GraphImage.height()))
            # Start painter, set painter to perform on FinalExport
            Painter = QPainter(FinalExport)
            # Draw the graph image starting at point (0, 0)
            Painter.drawImage(QPoint(0, 0), GraphImage)
            # Draw the legend image alongside the graph image
            Painter.drawImage(QPoint(GraphImage.width(), 0), LegendImage)
            # End painter
            Painter.end()
            # Save image
            FinalExport.save(self.FilePath + "/AnthologyExport.png")
            # Remove images from Temp directory
            os.remove("Temp/Export1.png")
            os.remove("Temp/Export2.png")
            # -----------------------------------------------------------------------------------------------------------
            # # Get dimensions of pie chart canvas
            # GraphSize = self.Canvas.size()
            # # Convert graph convas into QImage
            # GraphImage = QImage(self.Canvas.buffer_rgba(), GraphSize.width(), GraphSize.height(), QImage.Format_RGBX8888)
            # # Get dimensions of legend canvas
            # LegendSize = self.LegendCanvas.size()
            # # Convert legend canvas into QImage
            # LegendImage = QImage(self.LegendCanvas.buffer_rgba(), LegendSize.width(), LegendSize.height(), QImage.Format_RGBX8888)
            # # Create a new QPixmap for the export
            # # The width of the new image is the sum of the width of the graph image and
            # FinalExport = QPixmap(QSize(GraphImage.width() + LegendImage.width(), GraphImage.height()))
            # # Start painter, set painter to perform on FinalExport
            # Painter = QPainter(FinalExport)
            # # Draw the graph image starting at point (0, 0)
            # Painter.drawImage(QPoint(0, 0), GraphImage)
            # # Draw the legend image alongside the graph image
            # Painter.drawImage(QPoint(GraphImage.width(), 0), LegendImage)
            # # End painter
            # Painter.end()
            # # Save image
            # FinalExport.save(self.FilePath + "/AnthologyExport.png")
            # -----------------------------------------------------------------------------------------------------------

        # Display message to user informing them that the image has been successfully imported
        self.ExportStatusLBL.show()
        # Set message to disappear after 3 seconds
        QTimer.singleShot(3000, self.ExportStatusLBL.hide)

    # This method determines whether the program needs to draw a line graph or a pie chart
    def ChooseGraph(self, Type):
        if Type == "Collection Size":
            self.DrawLineGraph()
        else:
            self.DrawPieChart(Type)

    # This function plots a pie chart and creates a legend
    # It takes the parameter Type, which is the collection field that it is plotting
    def DrawPieChart(self, Type):
        self.FigureWidget.setFixedWidth(380)
        # Clear figure of previous graph
        self.Figure.clear()
        # Group values stored under the current column and return the number in each group
        self.MyCursor.execute("SELECT " + Type + ", COUNT(*) AS c FROM " + self.OpenCollectionTable + " GROUP BY " + Type)
        MyResult1 = self.MyCursor.fetchall()
        # Total is the total number of items being plotted (used to calculate percentages)
        self.Total = 0
        # GraphLabels is a list containing each category in the pie chart
        self.GraphLabels = []
        # Percentages is a list containing the percentage of each category
        self.Percentages = []
        # Count number of items by incrementing Total for each value in MyResult1
        for x in range(0, len(MyResult1)):
            self.Total += MyResult1[x][1]
        # Iterate through MyResult1, calculating the percentage of each category and adding category labels to the list
        for y in range(0, len(MyResult1)):
            # Calculate category's percentage of the Total
            self.Percentages.append((MyResult1[y][1] / self.Total) * 100)
            # If the category name is longer than 17 characters, cut it down and add an ellipses to the end
            if len(str(MyResult1[y][0])) > 17:
                Label = str(MyResult1[y][0][:17]) + "..."
            else:
                Label = str(MyResult1[y][0])
            # If we are plotting the rarity, we have to replace 1 and 0 with True and False for our legend
            if Type == "Rare":
                if MyResult1[y][0]:
                    Label = "True"
                else:
                    Label = "False"
            # Add the label to the list, percentages are round to the nearest whole number
            self.GraphLabels.append(Label + " (" + str(round(self.Percentages[y], -int(floor(log10(abs(self.Percentages[y])))))) + "%)")
        # Create axis object for plotting values
        self.Axis = self.Figure.add_axes((0, 0, 1, 1))
        # Set the background colour of the figure to white
        self.Figure.set_facecolor("#FFFFFF")
        # Plot pie chart using values stored in Percentages list
        self.patches, texts = self.Axis.pie(self.Percentages, startangle = 90)
        # Set the graph's aspect ration to "equal" to display the pie chart as a perfect circle rather than an ellipse
        self.Axis.axis("equal")

        # Clear figure of previous legend
        self.LegendFigure.clear()
        self.LegendFigure.tight_layout()
        # Create legend
        self.Legend = self.LegendFigure.legend(self.patches, self.GraphLabels, prop = {"size": 7}, ncol = 2)
        # Set legend title to Type parameter
        self.Legend.set_title(Type, prop = {"size": 10})

        # Call draw() method on both canvases to display new graphs
        self.Canvas.draw()
        self.LegendCanvas.draw()
        self.LegendCanvas.show()

    # The method plots a line chart
    # It is called when the user wants to view the collection sizes chart
    def DrawLineGraph(self):
        self.FigureWidget.setFixedWidth(750)
        # The line chart doesn't need a legend so its canvas is hidden
        self.LegendCanvas.hide()
        # Clear figure of previous graph
        self.Figure.clear()
        # Get all entries into the sizes table where the foreign key corresponds with the primary key of the currently open collection
        self.MyCursor.execute("SELECT * FROM Sizes WHERE FK_Collections_Sizes = " + str(self.OpenCollectionID))
        MyResult2 = self.MyCursor.fetchall()
        # Dates is a list storing the date when each size was recorded
        self.Dates = []
        # Magnitudes stores the size of the collection at each date
        self.Magnitudes = []
        # Iterate through the results of SQL query and append them to the appropriate list
        for x in range(0, len(MyResult2)):
            self.Dates.append(MyResult2[x][1])
            self.Magnitudes.append(MyResult2[x][2])
        # Convert MySQL date values to python-compatible datetime objects
        self.Dates = [datetime.strptime(str(d), "%Y-%m-%d %H:%M:%S") for d in self.Dates]
        # Convert python datetime objects to MatPlotLib compatible values
        self.Dates = matplotlibdates.date2num(self.Dates)
        # Create a formatter for the x axis to correctly display the time values
        self.DatesFormat = matplotlibdates.DateFormatter("%Y-%m-%d\n%H:%M:%S")
        # Create axis object for plotting values
        self.Axis = self.Figure.add_subplot()
        self.Figure.set_facecolor("#FFFFFF")
        self.Figure.tight_layout()
        # Set the formatter of the x axis to the newly created formatter
        self.Axis.xaxis.set_major_formatter(self.DatesFormat)
        # Plot dates against sizes as a line chart
        self.Axis.plot(self.Dates, self.Magnitudes, marker = "x", markersize = 5, linewidth = 1)
        # Set the graph's title
        self.Axis.set_title("Collecton Size", size = 12)
        # Set the x axis label
        self.Axis.set_xlabel("Date", size = 10)
        # Set the y axis label
        self.Axis.set_ylabel("Size", size = 10)
        self.Axis.tick_params(axis = "both", labelsize = 6)
        self.Figure.tight_layout()

        # Call draw() method on both canvases to display new graphs
        self.LegendFigure.clear()
        self.Canvas.draw()
        self.LegendCanvas.draw()

    # Executed when ForwardBTN is clicked
    def NextGraph(self):
        # If the index is at the end of the list, set the index to the beginning of the list
        if self.GraphTypesIndex >= len(self.GraphTypes) - 1:
            self.GraphTypesIndex = 1
        # Otherwise, increment the index by 1
        else:
            self.GraphTypesIndex += 1
        # Draw the new graph
        self.ChooseGraph(self.GraphTypes[self.GraphTypesIndex][0])

    # Executed when BackBTN is clicked
    def PreviousGraph(self):
        # If the index is at the start of the list, set the index to the end of the list
        if self.GraphTypesIndex <= 1:
            self.GraphTypesIndex = len(self.GraphTypes) - 1
        # Otherwise, decrement the index by 1
        else:
            self.GraphTypesIndex -= 1
        # Draw the new graph
        self.ChooseGraph(self.GraphTypes[self.GraphTypesIndex][0])


    def sizeHint(self):
        return QSize(815, 415)

    def paintEvent(self, event):
        Painter = QPainter()
        Painter.begin(self)
        Outline = QPixmap()
        Outline.load('Resources/GraphOutline.png')
        Painter.drawPixmap(QPoint(0, 0), Outline)
        Painter.end()