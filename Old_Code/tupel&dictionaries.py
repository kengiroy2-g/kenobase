##########Dictionary
#  d = {"orange": "fruit", "concombre": "legume", "pamplemous":"citrus"}
def add_entry(x,y):
    if x in d:
        print(x +" ist bereit in Dictionary")
        print(23 * "=")
    else:
        d[x]= y
    return d
# print(add_entry("patate","tubercule"))
# print(d["patate"])
        
######Tupel entpacken
# student = ("Max Müller", 22, "Informatik")
# def get_student(l):
#     name, age, subject = l
#     print(name + " ist " + str(age) +" alt" + " und studiere " + subject)
    
# get_student(student)

####### Schleife in Dictionary
d = {"orange": "fruit", "concombre": "legume", "pamplemous":"citrus"}
def showdictionary_antrag(dico):
    
    for plante, genre in dico.items():
        print(plante + " est du genre " + genre )
    print( "\n" + 23*".")
showdictionary_antrag(d)
add_entry("patate", "tubercules")
add_entry("patate", "tubercules")
showdictionary_antrag(d)