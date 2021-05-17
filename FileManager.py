import os
from datetime import datetime
from tkinter import messagebox as mbox
import sys
import re

class FileManager():
    """
    Module that handles all file related task.

    - Getting file permission
    - Renaming the files
    - Formating the returned data from os calls in order to make it user readable
    - Getting all file names from a directory 
    """
    def __init__(self):
        """only certain data attributes initialization"""
        # INVALID CHAR -> chars not allowed to use in filenames
        # RESERVED_FILENAMES -> Reserved words not allowed to use in filename 
        self.INVALID_CHAR = ['<', '>', '/',
                             '\\', ':', '"',
                             '|', '?', '*'
                             ]
        self.RESERVED_FILENAMES = ['CON', 'PRN', 'AUX', 'NUL',
                                   'COM1', 'COM2', 'COM3', 'COM4',
                                   'COM5', 'COM6', 'COM7', 'COM8',
                                   'COM9', 'LPT1', 'LPT2', 'LPT3',
                                   'LPT4', 'LPT5', 'LPT6', 'LPT7',
                                   'LPT8', 'LPT9'
                                    ]


    def getDate(self, ctime):
        """
        Method that returns date in format of 'date month year' 
        
        parameters:
        ctime :In milliseconds 
        """
        date = datetime.fromtimestamp(ctime).strftime('%d %b %Y')
        return date

    def getDirFiles(self, dir):
        """Method responsible for getting files list names from the given directory"""
        self.path = dir
        try:
            self.allFiles = os.listdir(self.path)
        except:
            self.display_error("Directory Not Selected")
            return []
        fileList = []
        for file in self.allFiles:
            filePath = os.path.join(self.path, file)
            if os.path.isdir(filePath):
                pass
            else:
                size = round(os.path.getsize(filePath) / 1000)
                if size <= 0:
                    size = 0
                size = str(size) + ' kb'
                ctime = os.path.getctime(filePath)
                ctime = self.getDate(ctime)
                item = (file, size, ctime, 0)
                fileList.append(item)
        return fileList

    def display_error(self, msg, type = "Error"):
        """utility method to print any error during exception caught."""
        mbox.showerror(type, msg)

    def checkFilePermission(self, path):
        """Method that checks read/write permission of a directory"""
        if os.access(path, os.R_OK) and os.access(path, os.W_OK) and os.access(path, os.X_OK | os.W_OK):
            return 1
        else:
            return 0

    def isValidFileName(self, fileName):
        """Method to check user specified filename is correct and meet the requirements."""
        s = fileName.lstrip().rstrip()
        for item in self.RESERVED_FILENAMES:
            if item.lower() == s.lower():
                return 0
        res = [ele for ele in self.INVALID_CHAR if(ele in s)] 
        if bool(res) == True:
            return 0
        return 1

    def renameFile(self, source, dest):
        """Method to rename files given the source and destination filename path"""
        try:
            os.rename(source, dest)
            return 1
        except (FileExistsError):
            return 0

    def combinePath(self, path, filename):
        """utility method that combines appends file to a given path"""
        return os.path.join(path, filename)
    
    def getExtentionList(self, list):
        """Method that separates the file extention names from a comma string input"""
        l = list.split(',')
        l1 = []
        for item in l:
            l1.insert(0, "f1" + item.strip())
        valid = []
        for e in l1:
            ex = e.lower()
            f, e = os.path.splitext(ex)
            if e == "":
                pass
            else:
                valid.insert(0, e)
        return valid

    def isValidRegex(self, regex):
        """Method to check the given string is a valid regex expression"""
        try:
            re.compile(regex)
            return 1
        except:
            return 0

    def createCount(self, num, zeros):
        """Method to increment a counter and pad with zeros"""
        zerosToAdd = zeros - len(str(num))
        numString = str(num)
        for i in range(zerosToAdd):
            numString = "0" + numString
        return numString

