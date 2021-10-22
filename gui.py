from tkinter import *
import time

# Just mucking about


class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

        menu = Menu(self.master)
        self.master.config(menu=menu)

        # widget can take all window
        self.pack(fill=BOTH, expand=1)

        # create button, link it to clickExitButton()
        #exitButton = Button(self, text="Exit", command=self.clickExitButton)
        # place button at (0,0)
        #exitButton.place(x=0, y=0)

        fileMenu = Menu(menu)
        fileMenu.add_command(label="Item")
        fileMenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="File", menu=fileMenu)

        editMenu = Menu(menu)
        editMenu.add_command(label="Undo")
        editMenu.add_command(label="Redo")
        menu.add_cascade(label="Edit", menu=editMenu)

        self.label = Label(text="", fg="Red", font=("Helvetica", 36))
        self.label.place(x=50, y=80)
        self.update_clock()
        # text.pack()

    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        self.label.configure(text=now)
        self.after(1000, self.update_clock)

    def exitProgram(self):
        exit()

    # def clickExitButton(self):
    #     exit()


root = Tk()
app = Window(root)

# title
root.wm_title("SW")
root.geometry("640x480")
# show
root.mainloop()
