import mysql.connector
import datetime
import sys
import os
import base64
import smtplib, ssl

try:
    MyDB = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Anthology"
    )
    MyCursor = MyDB.cursor()
    Connected = True
except:
    sys.exit(1)

# Get current date
CurrentTime = datetime.date.today()
# List for storing all loans which are overdue
LoansRequiringAction = []
# Get all entries into Loans table
MyCursor.execute("SELECT * FROM Loans")
MyResult1 = MyCursor.fetchall()
# Iterate through query results
for item in MyResult1:
    # If an item's due date is older than or the same as the current date, add it to the list
    if item[1] <= CurrentTime:
        LoansRequiringAction.append(item)

# Iterate through the list of overdue loans
for item in LoansRequiringAction:
    # Get conents of table that current item belongs to
    MyCursor.execute("SELECT * FROM Table" + str(item[2]) + " WHERE PK_Table" + str(item[2]) + " = " + str(item[3]))
    MyResult2 = MyCursor.fetchall()
    # Get entry into Collections table of collection which current item belongs to
    MyCursor.execute("SELECT * FROM Collections WHERE PK_Collections = " + str(item[2]))
    MyResult3 = MyCursor.fetchall()
    # Get the entry into the Users table for the user which the collection belongs to
    MyCursor.execute("SELECT * FROM Users WHERE PK_Users = " + str(MyResult3[0][3]))
    Recipient = MyCursor.fetchall()[0][1]
    # If the boolean value for Push notifications is set to true...
    if item[5]:
        # Display a notification, formatting the appropriate data in
        NotificationString = str(MyResult2[0][1]) + " is due today"
        os.system("""
        osascript -e 'display notification "{0}" with title "{1}"'
        """.format(NotificationString, "Anthology"))
    # If the boolean value for Email notifications if set to true...
    if item[4]:
	// Email password
	Credential = ""

        # This text will make up the body of the email
        EmailText = """Subject: Item Due
        
The item '{0}' which you loaned out from your {1} collection is due back today
        
From the Anthology team
        """.format(str(MyResult2[0][1]), str(MyResult3[0][1]))

        # Start email server instance, using port 465
        with smtplib.SMTP_SSL("smtp.gmail.com", port = 465, context = ssl.create_default_context()) as Server:
            # Login to dev email account
            Server.login("", Credential)
            # Send email
            Server.sendmail("", Recipient, EmailText)
            # Quit server instance
            Server.quit()

    # Delete entry into Loans item once notification has been sent
    MyCursor.execute("DELETE FROM Loans WHERE PK_Loans = " + str(item[0]))
    # Save changes to database
    MyDB.commit()




