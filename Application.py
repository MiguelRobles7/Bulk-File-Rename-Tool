from tkinter import *
import os
from FileManager import FileManager
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from tkinter import PhotoImage
from datetime import datetime
from tkinter.ttk import Progressbar, Separator
from tkinter import messagebox
from ctypes import windll
import re

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    # re-assert the new window style
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())


class Application(Frame):
    """
    This Module launches the 'BULK FILE RENAME TOOL' application gui.
    Responsible for rendering the application UI and updating it. 

    """

    def __init__(self, root):
        """Method to call draw items on the tkinter window object"""
        self.root = root
        self.initialize_user_interface()

    def get_dir(self):
        """Method responsible for getting the directory path as well as filesname list in that directory"""
        path = askdirectory(title='Select Folder')
        if path == "":
            self.dirDispLabel['text'] = " Please select a directory first."
        else:
            self.dirDispLabel['text'] = path
        self.dir = path
        self.filesList = self.fileManager.getDirFiles(self.dir)
        self.display_files()

    def clear(self, event):
        """Method responsible for selecting the text inside a entry widget whenever on focus"""
        event.widget.selection_range(0, END)

    def columnHeaderClicked(self, id):
        """
        Method responsible for sorting the filenames based on alphablet, date of creation and file size both ascending and descending order

        paramater:
        id (int): The clicked header index

        """
        files = []
        folder = []
        if id == 0:
            for entry in self.filesList:
                if entry[3] == 0:
                    files.append(entry)
                else:
                    folder.append(entry)
            # T1, T2, T3 -> Boolean varable to keep check on whether to sort files ascending or descending
            # filelist -> a list containing list of files in the current direcory [filename, filesize, dateof creation, isfile/isFolder]
            if self.T1 == True:
                files.sort(key=lambda x: x[0].lower())
                folder.sort(key=lambda x: x[0].lower())
                for f in folder:
                    files.insert(0, f)
                self.T1 = False
            else:
                files.sort(reverse=True,
                           key=lambda x: x[0].lower())
                folder.sort(reverse=True,
                            key=lambda x: x[0].lower())
                for f in folder:
                    files.insert(len(files), f)
                self.T1 = True
        elif id == 1:
            for entry in self.filesList:
                if entry[3] == 0:
                    files.append(entry)
                else:
                    folder.append(entry)
            if self.T2 == True:
                files.sort(key=lambda x: int(x[1].split(" ")[0]))
                files.sort(key=lambda x: int(x[1].split(" ")[0]))
                for f in folder:
                    files.insert(0, f)
                self.T2 = False
            else:
                files.sort(reverse=True, key=lambda x: int(x[1].split(" ")[0]))
                files.sort(reverse=True, key=lambda x: int(x[1].split(" ")[0]))
                for f in folder:
                    files.insert(len(f), f)
                self.T2 = True
        else:
            if self.T3 == True:
                files = self.filesList.sort(
                    key=lambda date: datetime.strptime(date[2], '%d %b %Y'))
                self.T3 = False
            else:
                files = self.filesList.sort(reverse=True,
                                            key=lambda date: datetime.strptime(date[2], '%d %b %Y'))
                self.T3 = True
            self.display_files()
            return
        self.filesList = files
        self.display_files()

    def checkInput(self):
        """Method to check correct options are selected yet input fields are correct."""
        if len(self.filesList) <= 0:
            self.fileManager.display_error("Please Select The Directory First")
            return 0
        # filemanager -> a FileManager object that takes care of all file related tasks and exceptions
        if self.fileManager.checkFilePermission(self.dir) == 0:
            self.fileManager.display_error(
                "File read/write permission not allowed on the current directory")
            return 0

        if (self.check1.get() == 0) and (self.check2.get() == 0):
            self.fileManager.display_error(
                "Please Select < Enter Filename > or < Enter Regex > option")
            return 0

        if (self.check3.get() == 0) and (self.check4.get() == 0):
            self.fileManager.display_error(
                "Please Select < All File Types> or < Selected File Types > option")
            return 0

        self.userInputFileName = self.namingConventionInput2.get().strip()
        if self.fileManager.isValidFileName(self.userInputFileName) == 0:
            self.fileManager.display_error(
                "Please enter a valid file name.\n chars not allowed:'<', '>', '/', '\\', ':', '\"', '|', '\?', '*' ")
            return 0

        if self.check4.get() == 1:
            self.userInputFileTypes = self.fileTypesInput.get()

        if self.userInputFileName == "":
            self.fileManager.display_error("Please Enter a File Name")
            return 0

        if self.check4.get() == 1:
            if self.userInputFileTypes == "":
                self.fileManager.display_error(
                    "Please enter atleast one extention name (.txt, .png)\n Supports multiple extentions seperated by comma: .png,.exe,.jpeg")
                return 0

        if self.check5.get() == 1:
            index = self.tree.selection()
            files = [self.tree.item(i)['values'] for i in index]
            if len(files) <= 1:
                self.fileManager.display_error(
                    "Please Select atleast two items from the file list scrollview. \n Note: press ctrl and scroll to select multiple files.")
                return 0
            else:
                self.filesRenameList = files

        if self.check4.get() == 1:
            self.extentionList = self.fileManager.getExtentionList(
                self.userInputFileTypes)
            if len(self.extentionList) <= 0:
                self.fileManager.display_error(
                    "None of the extentions specified in the textfield are valid.")
                return 0

        if self.check2.get() == 1:
            self.userInputRegexExp = self.namingConventionInput1.get().strip()
            if self.userInputRegexExp == "":
                self.fileManager.display_error(
                    "Please enter the regex expression to match file names")
                return 0
            elif self.fileManager.isValidRegex(self.userInputRegexExp) == 0:
                self.fileManager.display_error("Enter Valid Regex Expression")
                return 0

        return 1

    def renameTask(self):
        """Method responsible for carrying out the rename task based on different combination of user input"""
        check1 = self.check1.get()
        check2 = self.check2.get()

        check3 = self.check3.get()
        check4 = self.check4.get()

        check5 = self.check5.get()

        if check1 == 1 and check3 == 1 and check5 == 1:
            # rename using filename of all types and selected files only
            zCnt = len(str(len(self.filesRenameList))) + 1
            cnt = 1
            for item in self.filesRenameList:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()

        elif check1 == 1 and check3 == 1 and check5 == 0:
            # rename using filename of all types on all files
            fileList = self.fileManager.getDirFiles(self.dir)
            zCnt = len(str(len(fileList))) + 1
            cnt = 1
            for item in fileList:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()

        elif check1 == 1 and check4 == 1 and check5 == 1:
            # rename using filename of selected file types on selected files only
            fileListToRename = []
            for i, ele in enumerate(self.filesRenameList):
                filename, deli, extention = ele[0].rpartition('.')
                extention = "." + extention
                if extention in self.extentionList:
                    fileListToRename.append(self.filesRenameList[i])
            if len(fileListToRename) <= 0:
                self.fileManager.display_error(
                    "No matching file extention type found")
                return
            else:
                zCnt = len(str(len(fileListToRename))) + 1
                cnt = 1
                for item in fileListToRename:
                    src = self.fileManager.combinePath(self.dir, item[0])
                    filename, deli, extention = item[0].rpartition('.')
                    filePart = self.fileManager.createCount(cnt, zCnt)
                    newFileName = self.userInputFileName + filePart + "." + extention
                    dst = self.fileManager.combinePath(self.dir, newFileName)
                    self.fileManager.renameFile(src, dst)
                    cnt += 1
                self.filesList = self.fileManager.getDirFiles(self.dir)
                self.display_files()

        elif check1 == 1 and check4 == 1 and check5 == 0:
            # rename using filename of selected file types on all files
            fileList = self.fileManager.getDirFiles(self.dir)
            fileListToRename = []
            for i, ele in enumerate(fileList):
                filename, deli, extention = ele[0].rpartition('.')
                extention = "." + extention
                if extention in self.extentionList:
                    fileListToRename.append(fileList[i])
            if len(fileListToRename) <= 0:
                self.fileManager.display_error(
                    "No matching file extention type found")
                return
            else:
                zCnt = len(str(len(fileListToRename))) + 1
                cnt = 1
                for item in fileListToRename:
                    src = self.fileManager.combinePath(self.dir, item[0])
                    filename, deli, extention = item[0].rpartition('.')
                    filePart = self.fileManager.createCount(cnt, zCnt)
                    newFileName = self.userInputFileName + filePart + "." + extention
                    dst = self.fileManager.combinePath(self.dir, newFileName)
                    self.fileManager.renameFile(src, dst)
                    cnt += 1
                self.filesList = self.fileManager.getDirFiles(self.dir)
                self.display_files()

        elif check2 == 1 and check3 == 1 and check5 == 1:
            # rename using regex of all file types on selected files only
            regex = self.userInputRegexExp
            matchingFiles = []
            for i, ele in enumerate(self.filesRenameList):
                filename, deli, extention = ele[0].rpartition('.')
                if re.search(regex, filename):
                    matchingFiles.append(self.filesRenameList[i])
            if len(matchingFiles) <= 0:
                self.fileManager.display_error(
                    "No file name match the pattern")
                return
            zCnt = len(str(len(matchingFiles))) + 1
            cnt = 1
            for item in matchingFiles:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()

        elif check2 == 1 and check3 == 1 and check5 == 0:
            # rename using regex of all file types  on all files
            regex = self.userInputRegexExp
            matchingFiles = []
            fileList = self.fileManager.getDirFiles(self.dir)
            for i, ele in enumerate(fileList):
                filename, deli, extention = ele[0].rpartition('.')
                if re.search(regex, filename):
                    matchingFiles.append(fileList[i])
            if len(matchingFiles) <= 0:
                self.fileManager.display_error(
                    "No file name match the pattern")
                return
            zCnt = len(str(len(matchingFiles))) + 1
            cnt = 1
            for item in matchingFiles:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()

        elif check2 == 1 and check4 == 1 and check5 == 1:
            # rename using regex of selected file types on selected files
            regex = self.userInputRegexExp
            matchingFiles = []
            for i, ele in enumerate(self.filesRenameList):
                filename, deli, extention = ele[0].rpartition('.')
                if re.search(regex, filename):
                    matchingFiles.append(self.filesRenameList[i])
            if len(matchingFiles) <= 0:
                self.fileManager.display_error(
                    "No file name match the pattern")
                return
            filteredList = []
            for i, ele in enumerate(matchingFiles):
                filename, deli, extention = ele[0].rpartition('.')
                extention = "." + extention
                if extention in self.extentionList:
                    filteredList.append(matchingFiles[i])
            if len(filteredList) <= 0:
                self.fileManager.display_error(
                    "Files that match to the pattern have no matching extentions")
                return
            zCnt = len(str(len(filteredList))) + 1
            cnt = 1
            for item in filteredList:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()

        elif check2 == 1 and check4 == 1 and check5 == 0:
            # rename using regex of selected file types on all files
            regex = self.userInputRegexExp
            matchingFiles = []
            fileList = self.fileManager.getDirFiles(self.dir)
            for i, ele in enumerate(fileList):
                filename, deli, extention = ele[0].rpartition('.')
                if re.search(regex, filename):
                    matchingFiles.append(fileList[i])
            if len(matchingFiles) <= 0:
                self.fileManager.display_error(
                    "No file name match the pattern")
                return
            filteredList = []
            for i, ele in enumerate(matchingFiles):
                filename, deli, extention = ele[0].rpartition('.')
                extention = "." + extention
                if extention in self.extentionList:
                    filteredList.append(matchingFiles[i])
            if len(filteredList) <= 0:
                self.fileManager.display_error(
                    "Files that match to the pattern have no matching extentions")
                return
            zCnt = len(str(len(filteredList))) + 1
            cnt = 1
            for item in filteredList:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()

    def renameFiles(self):
        """This method responsible for checking user input as well as getting confirmation from user to proceed for rename task"""
        id = self.checkInput()
        if id == 0:
            return
        else:
            msg = messagebox.askquestion(
                'Rename Files', 'Are you sure you want to rename the files.', icon='warning')
            if msg == 'yes':
                self.renameTask()
            else:
                return

    def sel(self, id):
        """Method responsible for handling changing user input choices"""
        if id == 0:
            self.regexbtn2.deselect()
            self.check2.set(0)
            self.namingConventionInput1.delete(0, END)
            self.namingConventionInput1['state'] = 'disabled'
            self.namingConventionInput2['state'] = 'normal'
            self.namingConventionInput2.delete(0, END)
            self.namingConventionInput2.insert(0, "Enter New File Name")

        elif id == 1:
            self.regexbtn1.deselect()
            self.check1.set(0)
            self.namingConventionInput1['state'] = 'normal'
            self.namingConventionInput2['state'] = 'normal'
            self.namingConventionInput1.delete(0, END)
            self.namingConventionInput1.insert(0, "Enter Regex Exponent")
            self.namingConventionInput2.delete(0, END)
            self.namingConventionInput2.insert(0, "Enter New File Name")

        elif id == 2:
            self.selectedFilesBtn.deselect()
            self.check4.set(0)
            self.fileTypesInput.delete(0, END)
            self.fileTypesInput['state'] = 'disabled'

        else:
            self.allFilesBtn.deselect()
            self.check3.set(0)
            self.fileTypesInput['state'] = 'normal'
            self.fileTypesInput.delete(0, END)
            self.fileTypesInput.insert(
                0, " Enter Extentions(.png, .txt)")

    def initialize_user_interface(self):
        """Method responsible for drawing and postitioning widgets on the root window widget."""
        self.bgTheme1 = "#F7F8FA"
        self.bgTheme2 = "#FFF"
        self.btnFgColor = "#b7b2b2"
        self.btnBgColor = "#33333D"
        self.labelFgColor = "#6D7073"
        self.labelBgColor = self.bgTheme2
        self.defaultFg = "#2C3136"
        self.off_color = "red"
        self.on_color = "black"
        self.root.title("Bulk File Rename Tool")
        self.root.configure(background=self.bgTheme1)
        self.root.option_add("*Font", "helvetica 10")
        self.fileManager = FileManager()
        self.root.geometry("960x565")
        self.root.resizable(False, False)
        self.root.update_idletasks()
        self.root.wm_title("AppWindow Test")
        button = ttk.Button(self.root, text='Exit',
                            command=lambda: self.root.destroy())
        button.place(x=10, y=10)
        self.root.overrideredirect(True)
        self.root.after(10, lambda: set_appwindow(self.root))

        # make a frame for the title bar
        title_bar = Frame(self.root, bg='#24292E',
                          relief='raised', bd=0, highlightthickness=0, highlightbackground='#24292E', pady=15)
        # put a close button on the title bar
        close_button = Button(title_bar, text='X', command=self.root.destroy, bg="#24292E", highlightbackground='#24292E', padx=10,
                              activebackground='red', bd=0, font="bold", fg='white', highlightthickness=0)

        # pack the widgets
        title_bar.pack(expand=1, fill=X)
        close_button.pack(side=RIGHT, padx=20)
        xwin = None
        ywin = None

        self.title_label = Label(title_bar, text="Bulk File Rename Tool", fg="white",
                                 bg="#24292E", justify="center", font=("helvetica 16 bold"))
        self.title_label.place(in_=title_bar, anchor="c", relx=.5, rely=.5)

        def get_pos(event):
            xwin = self.root.winfo_x()
            ywin = self.root.winfo_y()
            startx = event.x_root
            starty = event.y_root

            ywin = ywin - starty
            xwin = xwin - startx

            def move_window(event):
                self.root.geometry(
                    "960x565" + '+{0}+{1}'.format(event.x_root + xwin, event.y_root + ywin))
            startx = event.x_root
            starty = event.y_root

            title_bar.bind('<B1-Motion>', move_window)
        title_bar.bind('<Button-1>', get_pos)

        def change_on_hovering(event):
            close_button['bg'] = 'red'

        def return_to_normalstate(event):
            close_button['bg'] = '#24292E'

        close_button.bind('<Enter>', change_on_hovering)
        close_button.bind('<Leave>', return_to_normalstate)
        # Top

        self.check1 = IntVar()
        self.check2 = IntVar()
        self.check3 = IntVar()
        self.check4 = IntVar()
        self.check5 = IntVar()

        self.T1 = True
        self.T2 = True
        self.T3 = True

        self.userInput1 = ""
        self.userInput2 = ""

        self.topFrame = LabelFrame(
            self.root, width=700, height=170, borderwidth=0.4, relief="raised")
        self.midFrame = LabelFrame(
            self.root, width=700, height=330, borderwidth=0.4, relief="raised")
        self.endFrame = LabelFrame(
            self.root, width=700, height=250, borderwidth=0.4, relief="raised")

        left_side = LabelFrame(self.root, bg='#FFF',
                               relief='raised', bd=0, highlightthickness=0, highlightbackground='#FFF', width=280, height=600)
        left_side.pack(side='left')

        right_side = LabelFrame(self.root, bg='#FFF',
                                relief='raised', bd=0, highlightthickness=0, highlightbackground='#FFF', width=675, height=600)
        right_side.pack(side='right')

        for i, frame in enumerate([self.topFrame, self.midFrame, self.endFrame]):
            if i == 0:
                frame.pack(expand=True, fill='both', padx=15, pady=(10, 0))
            elif i == 1:
                frame.pack(expand=True, fill='both', padx=15, pady=(10, 10))
            else:
                frame.pack(expand=True, fill='both', padx=15, pady=(0, 10))
            frame.pack_propagate(0)
            frame.configure(background=self.bgTheme2)

        # Right
        self.openDirectoryBtn = Button(right_side, text="📂Select", bg=self.btnBgColor,
                                       fg='white', borderwidth=0.5, relief="raised", command=self.get_dir, width=7, height=1, cursor="hand2", font=('helvetica 12 bold'))
        self.openDirectoryBtn.place(x=20, y=11)

        self.l = Label(right_side, text="Dir: ", fg=self.labelFgColor,
                       bg=self.labelBgColor, justify="left", font=("helvetica 12"))
        self.l.place(x=105, y=15)

        self.dirDispLabel = Label(right_side, text=os.getcwd(
        ), fg=self.labelFgColor, bg=self.labelBgColor, justify="left", font=("helvetica 12"))
        self.dirDispLabel.place(x=135, y=15)

        self.style1 = ttk.Style()
        self.style1.configure("Custom.Treeview.Heading",
                              background="green", foreground="black", relief="flat")
        self.style1.map("Custom.Treeview.Heading",
                        relief=[('active', 'groove'), ('pressed', 'sunken')])

        self.tree = ttk.Treeview(
            right_side, style="Custom.Treeview", height=250)
        self.tree.pack()
        self.tree.place(x=20, y=50, height=435)
        self.vsb = ttk.Scrollbar(
            right_side, orient="vertical", command=self.tree.yview)
        self.vsb.place(x=635, y=51, height=432)
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.tree['columns'] = ("FileName", "FileSize", "FileCreated")
        self.tree.column("#0", width=0, stretch=NO)

        self.icon = PhotoImage('sort_icon.png')

        self.tree.column("FileName", width=280, anchor=W)
        self.tree.column("FileSize", width=100, anchor=CENTER)
        self.tree.column("FileCreated", width=250, anchor=CENTER)

        self.tree.heading("FileName", text="File Name", anchor=CENTER,
                          command=lambda: self.columnHeaderClicked(0))
        self.tree.heading("FileSize", text="File Size", anchor=CENTER,
                          command=lambda: self.columnHeaderClicked(1))
        self.tree.heading("FileCreated", text="File Created",
                          anchor=CENTER, command=lambda: self.columnHeaderClicked(2))

        # Left
        self.regexbtn1 = Checkbutton(left_side, text="  Rename all files", onvalue=1, offvalue=0, variable=self.check1, command=lambda: self.sel(
            0), fg=self.defaultFg, bg=self.labelBgColor, justify="left", font=("helvetica 13 bold"), bd=0, highlightthickness=0)
        self.regexbtn1.place(x=15, y=20)
        self.regexbtn1.select()

        self.regexbtn2 = Checkbutton(left_side, text="  Use Regex exponent to\n  select files", onvalue=1, offvalue=0,
                                     variable=self.check2, command=lambda: self.sel(1), fg=self.defaultFg, bg=self.labelBgColor, justify="left", font=("helvetica 13 bold"))
        self.regexbtn2.place(x=15, y=50)
        self.regexbtn2.deselect()

        self.namingConventionInput1 = Entry(left_side, fg="#2C3136", state="disabled",
                                            bg=self.labelBgColor, justify="left", font=("helvetica 13 bold"), border=0.7, width=27)
        self.namingConventionInput1.insert(0, "Enter Regex Exponent")
        self.namingConventionInput1.place(x=18, y=105)
        self.namingConventionInput1.bind("<FocusIn>", self.clear)

        self.namingConventionInput2 = Entry(left_side, fg=self.defaultFg,
                                            bg=self.labelBgColor, justify="left", font=("helvetica 13 bold"), border=0.7, width=27)
        self.namingConventionInput2.insert(0, "Enter New File Name")
        self.namingConventionInput2.place(x=18, y=135)
        self.namingConventionInput2.bind("<FocusIn>", self.clear)

        self.separator = Separator(left_side, orient='horizontal')
        self.separator.place(x=14, y=175, width=255)

        self.allFilesBtn = Checkbutton(left_side, text="  Include All Files Types", onvalue=1, offvalue=0, command=lambda: self.sel(
            2), variable=self.check3, fg=self.defaultFg, bg=self.labelBgColor, justify="left", font=("helvetica 13 bold"))
        self.allFilesBtn.place(x=15, y=190)
        self.allFilesBtn.select()
        self.check3.set(1)

        self.selectedFilesBtn = Checkbutton(left_side, text="  Rename Selected File\n  Types Only", onvalue=1, offvalue=0, command=lambda: self.sel(
            3), variable=self.check4, fg=self.defaultFg, bg=self.labelBgColor, justify="left", font=("helvetica 13 bold"))
        self.selectedFilesBtn.place(x=15, y=220)
        self.selectedFilesBtn.deselect()

        self.fileTypesLabel = Label(left_side, text="Separate with a comma(' , ')",
                                    fg=self.labelFgColor, bg=self.labelBgColor, justify="left", font=("helvetica 10 bold"))
        self.fileTypesLabel.place(x=50, y=262)

        self.fileTypesInput = Entry(left_side, fg=self.labelFgColor, state="disabled",
                                    bg=self.labelBgColor, justify="left", font=("helvetica 13 bold"), border=0.7, width=27)
        self.fileTypesInput.place(x=18, y=290)
        self.fileTypesInput.insert(0, "eg: .exe,.png,.jpeg")
        self.fileTypesInput.bind("<FocusIn>", self.clear)

        self.separator1 = Separator(left_side, orient='horizontal')
        self.separator1.place(x=14, y=325, width=255)

        self.renameSelectedFilesOption = Checkbutton(left_side, text="  Rename Selected\n  Files Only",
                                                     onvalue=1, offvalue=0, variable=self.check5, fg=self.defaultFg, bg=self.labelBgColor, justify="left", font=("helvetica 13 bold"))
        self.renameSelectedFilesOption.place(x=15, y=335)
        self.renameSelectedFilesOption.deselect()
        self.fileTypesLabel1 = Label(left_side, text="CTRL + Click to select files",
                                     fg=self.labelFgColor, bg=self.labelBgColor, justify="left", font=("helvetica 10 bold"))
        self.fileTypesLabel1.place(x=50, y=377)
        self.check5.set(0)

        self.separator2 = Separator(left_side, orient='horizontal')
        self.separator2.place(x=14, y=408, width=255)

        self.renameAllFilesBtn = Button(left_side, text="Rename Files", command=self.renameFiles,
                                        bg=self.btnBgColor, fg="white", borderwidth=0, relief="raised", width=19, height=2, highlightthickness=0,  font=('helvetica 16 bold'))
        self.renameAllFilesBtn.place(x=15, y=425)

        self.style2 = ttk.Style()
        self.style2.configure(
            "black.Horizontal.TProgressbar", background='green')

        self.root.bind_all(
            "<Button-1>", lambda event: event.widget.focus_set())

        self.dir = os.getcwd()
        if self.fileManager.checkFilePermission(self.dir):
            self.filesList = self.fileManager.getDirFiles(self.dir)

        self.display_files()

    def display_files(self):
        """Method responsible for updating the items in the scrollable fileList"""
        for i in self.tree.get_children():
            self.tree.delete(i)
        if len(self.filesList) <= 0:
            return
        cnt = 0
        for file in self.filesList:
            self.tree.insert(parent='', index='end', iid=cnt,
                             text="", values=(file[0], file[1], file[2]))
            cnt += 1


if __name__ == '__main__':
    app = Application(Tk())
    app.root.mainloop()
