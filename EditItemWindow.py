import AddItemWindow

# This object inherits from the AddItemWindow class I programmed in Iteration 7
# This subclass takes the new argument ItemsForEditing which is the primary key of the item the user has selected in CollectionTable
# Its appearance is the same as the add item window, but each input field is populated with the item's data, for the user to edit
class EditItemWindow(AddItemWindow.AddItemWindow):
    def __init__(self, MyCursor, MyDB, ActiveUserID, OpenCollectionID, OpenCollectionTable, ItemsForEditing, widget = None):
        # super calls the __init__ method of the parent object
        super(EditItemWindow, self).__init__(MyCursor = MyCursor, ActiveUserID = ActiveUserID, MyDB = MyDB, OpenCollectionID = OpenCollectionID, OpenCollectionTable = OpenCollectionTable, widget = widget)

        # Reassign arguments as attributes
        self.ItemsForEditing = ItemsForEditing

        self.PopulateForEditing()
        # In the init method of the parent object, SubmitBTN was connected to the function AddItem()
        # For editing items, this button has to be disconnected from AddItem() and connected to EditItem()
        self.SubmitBTN.clicked.disconnect()
        self.SubmitBTN.clicked.connect(self.EditItem)
        # Change window header
        self.HeaderLBL.setText("Edit Item")

    # This function fills input fields with the selected item's data
    # The user can then edit the item's data before pressing submit to save their changes to the database
    def PopulateForEditing(self):
        # Get data from db for selected item using its primary key
        self.MyCursor.execute("SELECT * FROM " + self.OpenCollectionTable + " WHERE PK_" + self.OpenCollectionTable + " = " + self.ItemsForEditing)
        MyResult3 = self.MyCursor.fetchall()[0]
        # Iterate through each field (excluding the primary key, Rating, Rare and Thumbnail columns) and set the contents of each text input to the field's contents
        for x in range(1, len(MyResult3) - 3):
            self.FieldTextBoxes[x - 1].setText(str(MyResult3[x]))
        # Tick the rare checkbox if the item is rare
        if MyResult3[len(MyResult3) - 3]:
            self.RareCheckBox.setChecked(True)
        # Set the rating slider's value to the integer stored in the Rating column
        self.RatingSlider.setValue(MyResult3[len(MyResult3) - 2])
        # Change text of label showing which image has been selected
        # This object uses the UploadImage method of the parent object
        self.UploadedImageLBL.setText("Change Image")

    # This method is called when the user presses SubmitBTN
    # It fetches the editted data for the item and updates the corresponding entry in the SQL DB to save the changes
    def EditItem(self):
        # Proceed if the presence check returns TRUE
        if self.PresenceCheck():
            # Get column names
            self.MyCursor.execute("SHOW FIELDS FROM " + self.OpenCollectionTable)
            MyResult4 = self.MyCursor.fetchall()
            # Construct UPDATE statement
            SQLStatement = "UPDATE " + self.OpenCollectionTable + " SET "
            # Loop through list of column names and add to SQL statement
            for x in range(1, len(MyResult4) - 3):
                # %s operator is used for string substitution
                SQLStatement += "`" + MyResult4[x][0] + "` = %s, "
            SQLStatement += "Rare = %s, Rating = %s"
            # If the image has been changed, add that to the UPDATE statement
            if self.ContainsImage:
                SQLStatement += ", Thumbnail = %s"
            # Limit SQL operation to selected item using its primary key
            SQLStatement += " WHERE PK_" + self.OpenCollectionTable + " = " + self.ItemsForEditing

            # DataForInsertion is the tuple which stores all the data retrieved from the user input fields
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
            self.ItemAddedSignal.emit(False)
            # Close EditItemWindow
            self.close()