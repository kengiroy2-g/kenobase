import csv
import time
from datetime import datetime as dt
from os import read
daten = []
with open("..\..\Downloads\py_umsatz.csv", "r") as file:
    header = next(file)
    print(header)
    for line in file:
        betrag_str = ""
        zeile = line.strip().split(";")
        # datum = dt.strptime(zeile[0], "%d.%m.%Y")
        datum = zeile[0]
        a = (zeile[2].split(" ")[0]).split(",")
        if len(a[0]) >= 4:
            a[0] = a[0].replace(".", "")
            betrag_str = (".").join(a)
        else:
            betrag_str = (".").join(a)
        # betrag = float(betrag_str)
        betrag = betrag_str + " " + " EUR"
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
    with open("..\..\Downloads\py_umsatz_new.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(["datum","beguenstigter","betrag"])
        for element in daten:
            writer.writerow(element)