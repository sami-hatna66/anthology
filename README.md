<p align="center">
  <img src="screenshots/header.png?raw=true" alt="Anthology logo" width=350/>
</p>

# Anthology

Anthology is a cataloguing application for amateur collectors. Users can create collections, add items, view statistics, export collections and loan out items, among other things. The application has a Python/Qt frontend and a MySQL backend. Anthology was programmed for my A Level computer science coursework. I have also uploaded a copy of the report I wrote for that project to this repository.

## Installation
Anthology requires the following dependencies to be installed via pip
* PyQt5
* mysql-connector-python
* pyDrive (for Google Drive API)
* matplotlib
* opencv-python-headless
* pyzbar
* tabulate

Anthology also requires MySQL to be installed on your computer. You can install MySQL [here](https://dev.mysql.com/downloads/mysql/).

You will also need [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) to run the setup code.

Once MySQL has been installed and setup, run the following code on your SQL server (or open and run AnthologySetup.sql)

```bash
CREATE DATABASE Anthology;
USE Anthology;
CREATE TABLE Users (PK_Users INTEGER(255) NOT NULL AUTO_INCREMENT PRIMARY KEY, Email VARCHAR(320), PasswordHash VARCHAR(200));
CREATE TABLE Collections (PK_Collections INTEGER(255) NOT NULL AUTO_INCREMENT PRIMARY KEY, CollectionName VARCHAR(320), TableName VARCHAR(320), FK_Users_Collections INTEGER(255));
CREATE TABLE Sizes (PK_Sizes INTEGER(255) NOT NULL AUTO_INCREMENT PRIMARY KEY, TimeRecorded DATETIME, Magnitude INTEGER(255), FK_Collections_Users INTEGER(500));
CREATE TABLE Loans (PK_Loans INTEGER(255) NOT NULL AUTO_INCREMENT PRIMARY KEY, DueDate DATE, FK_Collections_Loans INTEGER(255), FK_Users_Loans INTEGER(255), KeyInCorrespondingTable INTEGER(255), Email BOOLEAN, Push BOOLEAN)
```

Anthology should now be ready to use!

(NOTE: the Google Drive backups won't work as they require a Google developer account and the loaning feature won't work as it needs a script to be scheduled with CRONTAB, however you are welcome to peruse the source code and get these things working on your computer if you want)

## Screenshots
<p float="left">
  <img src="/screenshots/screenshot1.png" width="400" />
  <img src="/screenshots/screenshot2.png" width="400" /> 
</p>
