import csv
import time
from datetime import datetime as dt
from os import read
daten = []
with open("..\..\Downloads\py_umsatz.csv", "r", newline='',) as file:
    # create a csv reader object for storing our computed result
    reader = csv.reader(file)
    # remove the header from the reader object
    header = next(reader)
    # iterate on the reader object to extract all line
  
    # change datatyp for the new csv-file 
    # daten[datum,beguenstiger,betrag]
    for line in reader:
        zeile = line
        datum = dt.strptime(zeile[0], "%d.%m.%Y")
        betrag_str = ""
        a = (zeile[2].split(" ")[0]).split(",")
        if len(a[0]) >= 4:
            a[0] = a[0].replace(".", "")
            betrag_str = (".").join(a)
        else:
            betrag_str = (".").join(a)
        betrag = float(betrag_str)
        beguenstigter = "" 
        if "/" in zeile[1] and not " " in zeile[1]:
            b = zeile[1].split("/")
            beguenstigter = b[0] + " " + b[1]
        elif "," in zeile[1] and not " " in zeile[1]:
            b = zeile[1].split(",")
            beguenstigter = b[0] + " " + b[1]
        elif zeile[1] == "":
            beguenstigter = "Bargeld Einzahkung"
        elif len(zeile[1].split(" ")) == 1:
            beguenstigter = zeile[1].split(" ")[0]
        else:
            b = zeile[1].split(" ")
            beguenstigter = b[0] + " " + b[1]
        daten.append([datum,beguenstigter,betrag])
    print(header)
    print(daten[0])