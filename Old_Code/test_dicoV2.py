# with    open("../../Downloads/names.csv", "r") as files:

    # dico = {}
    # for line in files:
    #     prenom = line.strip().split(",")
    #     name = prenom[1]
    #     if name == "Name":
    #         continue
    #     elif name in dico:
    #         dico[name] = int(dico[name]) + int(prenom[5])
    #     else:
    #         dico[name] = int(prenom[5])
    # print(dico["James"])
    # max_value = 0
    # name1 = " "
    # for key, value in dico.items():
    #     if max_value < value:
    #         max_value = value
    #         name1 = key
    # print(name1 + ", "+ str(max_value))

with open("pythonlesen2.txt", "w") as files:
    f = "ich möchte essen, ich möchte tanzen, ich möchte fliegen"
    inhalt = f.split(",")
    for element in inhalt:
        print(element.strip(), file=files)
# with open("pythonlesen.txt", "r") as file:
#     f1 = file.read()
#     print(f1)
