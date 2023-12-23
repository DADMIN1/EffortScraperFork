import tkinter
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import FileDialog

GridVarSelect = "Column"
CurrentRow = 0
CurrentColumn = 2

def NextCoord():
    if GridVarSelect == "Row":
        global CurrentRow
        CurrentRow += 1
    else:
        global CurrentColumn
        CurrentColumn += 1
    return CurrentRow, CurrentColumn


class TkApp(tkinter.Frame):
    def __init__(self, master=None, title="NoTitle"):
        super().__init__(master)
        self.master.title(title)
        self.grid()

        # Dropdown menu
        self.stats_var = tkinter.StringVar()
        self.stats_var.set("Select Stats Type")
        self.stats_dropdown = ttk.Combobox(self.master, textvariable=self.stats_var,
                                           values=["Rebounding", "Passing"])
        self.stats_dropdown.grid(row=0, column=0, padx=10, pady=10)

        # Textbox to display data
        self.data_textbox = ScrolledText(self.master, width=200)
        self.data_textbox.grid(row=1, column=1, padx=10, pady=10)

    def ExpandTextbox(self, xdelta=5, ydelta=5):
        self.data_textbox["width"] += xdelta
        self.data_textbox["height"] += ydelta


def CreateButton(parent, text, command):
    newbutton = tkinter.Button(parent, text=text, command=command)
    row, column = NextCoord()
    newbutton.grid(row=row, column=column, padx=10, pady=10)
    return newbutton



if __name__ == "__main__":
    root = tkinter.Tk()
    NBAStatsApp = TkApp(root)
    CreateButton(root, "expand textbox", NBAStatsApp.ExpandTextbox)
    #CreateButton(root, "ChooseCSV", OpenFileDialog_NoPandas)

    #choice = pickFile(NBAStatsApp, 0)
    #if choice is not None:
    #    loadedCSV = loadCSV(choice)
    #else:
    #    loadedCSV = loadCSV("passing_data")
    #if loadedCSV is not None:
    #    print(loadedCSV)
    #    saveCSV(loadedCSV, "resaved")
    #    # how the fuck do we select columns/rows?
    #    NBAStatsApp.data_textbox.insert(tkinter.END, loadedCSV.to_string(index=False))

    NBAStatsApp.mainloop()
