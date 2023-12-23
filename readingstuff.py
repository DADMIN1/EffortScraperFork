import csv
import json
import pprint

import tkinter
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import FileDialog
import tkinter.filedialog as tkfiledialog

def pickFile(window):
    CSV_sourcefile_paths = [*csv_nested_folders["source"].glob("*.csv")]
    selection_dict = {}
    curindex = 0
    for filepath in CSV_sourcefile_paths:
        window.data_textbox.insert(tkinter.END, f"{curindex} : {filepath.stem}\n")
        selection_dict.update({curindex: filepath.stem})
        curindex += 1
    if foundfiles is None:
        userchoice = int(input("choose a file: "))
    else:  # prevent the prompt from blocking the application
        userchoice = foundfiles
    if userchoice < len(selection_dict):
        return selection_dict[userchoice]
    return None

def OpenFileDialog_NoPandas():
    hugedict = {}
    #with tkinter.filedialog.askopenfile(defaultextension='.csv', initialdir=csv_nested_folders["source"],
    #                                    filetypes=[('CSV_file', '*.csv')]) as openedfile:
    with open(csv_nested_folders["source"] / "passing_data.csv") as openedfile:
        reader = csv.DictReader(openedfile)
        #NBAStatsApp.data_textbox.delete(1.0, tkinter.END)
        headers = reader.fieldnames
        #hugedict.update({'fields': reader.fieldnames})
        for line in reader:
            print(line)  # TODO: fix the fact that this creates invalid json
            #NBAStatsApp.data_textbox.insert(tkinter.END, str(line))
            hugedict.update({reader.line_num: line})
    return hugedict, headers


def OpenFileDialog(opts=SearchFlags.Filetypes('', True, 'csv')):
    with tkfiledialog.askopenfile(
            defaultextension='.'+opts.extension,
            initialdir=csv_subdir,
            filetypes=[('CSV_file', '*.csv')],
    ) as openedfile:
        loadedCSV = pd.read_csv(openedfile)
        print(loadedCSV)
        NBAStatsApp.data_textbox.delete(1.0, tkinter.END)
        NBAStatsApp.data_textbox.insert(tkinter.END, loadedCSV.to_string(index=False))
    return loadedCSV


def MapStatCategories(first, second):
    zipped = zip(headermap[first], headermap[second])
    statmap = {}
    for fieldone, fieldtwo in zipped:
        if fieldone not in statmap.keys():
            statmap.update({fieldone: fieldtwo})
        else:
            statmap[fieldone].append(fieldtwo)
    return statmap


def MapMulti(first, *rest):
    targetmapping = {Field: headermap[Field] for Field in rest}
    combinedtargets = zip(*[D for D in targetmapping.values()])
    somepairs = list(zip(*combinedtargets))
    zipped = zip(headermap[first], somepairs)
    #statmap = {}
    #for entry in headermap[first]:
    #    if entry not in statmap.keys():
    #        statmap.update({fieldone: fieldtwo})
    #    else:
    #        statmap[fieldone].append(fieldtwo)
    #return statmap


#MapMulti("TEAM", "PLAYER", "PotentialAssists")

def PrintJSONexample():
    for name in jsonmap.keys():
        data = jsonmap[name][0]
        dumpfilepath = json_subdir / f"{name}.json"
        jsonmap[name].append(dumpfilepath)
        # jsontext = json.dumps(data, indent=2)
        jsontext = JSON_Printer.pformat(data)
        dumpfilepath.touch()
        assert dumpfilepath.exists()
        print(f"writing {dumpfilepath.stem}")
        with open(dumpfilepath, 'w', encoding="utf-8") as outfp:
            outfp.write(jsontext)
            # outfp.writelines(jsontext.splitlines())
        # json.dump(data, outfp, indent=2)
    hugemap = MapStatCategories('PLAYER', 'PotentialAssists')
    pprint.pprint(hugemap)

if __name__ == "__main__":
    JSON_Printer = pprint.PrettyPrinter(indent=2, width=120, compact=True)
    hugedict, fields = OpenFileDialog_NoPandas()
    print(fields)
    JSON_Printer.pprint(hugedict)
    headermap = {}
    for field in fields:
        entries = [line[field] for line in hugedict.values()]
        headermap.update({field: entries})
    JSON_Printer.pprint(headermap)
    jsonmap = {
        "hugedict": [hugedict],  # line number: {fields:values}
        "headermap": [headermap],  # field:[values]
    }
    PrintJSONexample()
