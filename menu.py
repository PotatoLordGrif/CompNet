import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from client import FTP 
import os
 
LARGEFONT =("Verdana", 35)
ftp_connection = FTP()
class tkinterApp(tk.Tk):
     
    def __init__(self, *args, **kwargs): 
         
        tk.Tk.__init__(self, *args, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.window_close)
        container = tk.Frame(self)  
        container.pack(side = "top", fill = "both", expand = True) 
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
  
        self.frames = {}  
  
        for F in (StartPage, FileExp):
  
            frame = F(container, self)
  
            self.frames[F] = frame 
  
            frame.grid(row = 0, column = 0, sticky ="nsew")
  
        self.show_frame(StartPage)
  
    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        if ftp_connection.connected == True:
            try:
                frame.list_files()
            except:
                pass
        frame.tkraise()
    
    def window_close(self):
        global ftp_connection
        if ftp_connection.connected == True:
            ftp_connection.quit()
            self.destroy()
        else:
            self.destroy()
  
# first window frame startpage
  
class StartPage(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        # label of frame Layout 2
        label = ttk.Label(self, text ="Connection", font = LARGEFONT)
         
        # putting the grid in its place by using
        # grid
        label.grid(row = 0, column = 2) 
        #Create Server Address/Port box
        self.serverLabel = tk.Label(self,text="Address: ").grid(row=1,column=0)
        self.serverEntry = tk.Entry(self,bd=2)
        self.serverEntry.grid(row=1,column=1)

        #Create port/password labels and text boxes.
        self.portLabel = tk.Label(self,text="Port: ").grid(row=2,column=0)
        self.portEntry = tk.Entry(self,bd=2)
        self.portEntry.grid(row=2,column=1)

        #Create Login Button, used to connect and confirm connection.
        self.login_button = tk.Button(self, text="Login", command= lambda : self.validate_login(controller))
        self.login_button.grid(row = 3, column = 1, padx = 10, pady = 10)
        button1 = ttk.Button(self, text ="Page 1",
        command = lambda : controller.show_frame(FileExp))
     
    def validate_login(self, controller):
        global ftp_connection
        addr = self.serverEntry.get()
        port = self.portEntry.get()
        try:
            #print(f"Attempting to create connection to {addr} with port {port}")
            if ftp_connection.connected == False:
                test_con = FTP(addr,int(port))
                #print(f'Sending QUIT Command')
                test_con.quit()
            else:
                return
        except:
            messagebox.showerror('Connection Error', 'Error: Failed to Connect')
            return
        ftp_connection = FTP(addr,int(port))
        controller.show_frame(FileExp)  
  
# third window frame page2
class FileExp(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.local_path = "./Client/"
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row=1,column = 1)
        label = ttk.Label(self, text ="File Server", font = LARGEFONT)
        label.grid(row = 0, column = 0, padx = 10, pady = 10)
        # Remote File Viewer
        self.remote_view = ttk.Treeview(self, columns=("Files",), show="headings", selectmode="browse")
        self.remote_view.heading("Files", text="Server Files")
        self.remote_view.grid(row=1,column=2, padx = 10, pady = 10)
        # Local File Viewer
        self.local_view = ttk.Treeview(self, columns=("Files",), show="headings", selectmode="browse")
        self.local_view.heading("Files", text="Local Files")
        self.local_view.grid(row=1,column=0, padx = 10, pady = 10)

        self.list_files()
        #Create Center buttons
        uploadButton = ttk.Button(buttonFrame, text ="Upload ->",command = lambda : self.upload())
        uploadButton.pack()
        downloadButton = ttk.Button(buttonFrame, text ="<- Download",command = lambda : self.download())
        downloadButton.pack()
        deleteButton = ttk.Button(buttonFrame,text="Delete Remote File",command= lambda: self.deletefile())
        listButton = ttk.Button(buttonFrame, text ="Refresh List",command = lambda : self.list_files())
        listButton.pack()

        quitButton = ttk.Button(self, text ="Quit",command = lambda : self.quit())
        quitButton.grid(row=0,column=1)

        pathButton = ttk.Button(self, text="Change Directory", command = self.updateDir)
        pathButton.grid(row=2,column=0)
        self.pathLabel = ttk.Label(self,text=self.local_path)
        self.pathLabel.grid(row=3,column=0)
    
    #Quit the FTP connection, return to loginScreen
    def quit(self):
        global ftp_connection
        print(ftp_connection.connected, ftp_connection.timedout)
        if ftp_connection.connected == True:
            ftp_connection.checkTime()
            if ftp_connection.connected == True:
                ftp_connection.quit()
        ftp_connection = FTP()
        self.controller.show_frame(StartPage)
    #List files in both local and remote directories
    def list_files(self):
        global ftp_connection
        if ftp_connection.connected == True:
            ftp_connection.checkTime()
            if ftp_connection.connected == True:
                for item in self.remote_view.get_children():
                    self.remote_view.delete(item)
                files = ftp_connection.list_files()
                for file in files:
                    self.remote_view.insert("", "end", values=(file,))
            elif ftp_connection.timedout == True:
                messagebox.showerror('Connection Error', 'Connection Timed Out!')
                self.quit()
        for item in self.local_view.get_children():
            self.local_view.delete(item)
    
        for filename in os.listdir(self.local_path):
            if os.path.isfile(os.path.join(self.local_path, filename)):
                self.local_view.insert("", "end", values=(filename,))
    #Change local file directory
    def updateDir(self):
        self.local_path = filedialog.askdirectory() + "/"
        self.list_files()
        self.pathLabel['text'] = self.local_path
    #Use FTP class's upload function to upload file to remote
    def upload(self):
        global ftp_connection
        if ftp_connection.connected == True:
            ftp_connection.checkTime()
            if ftp_connection.connected == True:
                file = self.local_view.item(self.local_view.focus())['values'][0]
                ftp_connection.upload(self.local_path, file)
                self.list_files()
            elif ftp_connection.timedout == True:
                messagebox.showerror('Connection Error', 'Connection Timed Out!')
                self.quit()
    #Use the FTP class's download function to download file from remote
    def download(self):
        global ftp_connection
        if ftp_connection.connected == True:
            ftp_connection.checkTime()
            if ftp_connection.connected == True:
                file = self.remote_view.item(self.remote_view.focus())['values'][0]
                ftp_connection.download(self.local_path, file)
                self.list_files()
            elif ftp_connection.timedout == True:
                messagebox.showerror('Connection Error', 'Connection Timed Out!')
                self.quit()
    #Use FTP delete function to delfile remote file
    def deletefile(self):
        global ftp_connection
        if ftp_connection.connected == True:
            ftp_connection.checkTime()
            if ftp_connection.connected == True:
                file = self.remote_view.item(self.remote_view.focus())['values'][0]
                ftp_connection.delfile(file)
                self.list_files()
            elif ftp_connection.timedout == True:
                messagebox.showerror('Connection Error', 'Connection Timed Out!')
                self.quit()
    

  
# Driver Code
app = tkinterApp()
app.mainloop()