with    open("../../Downloads/names.csv", "r") as files:
    d = {}
    liste_name = []
    verification = []
    nombre_total = 0
    for line in files:
        prenom = line.strip().split(",")
        if prenom[1] == "Name":
            continue
        liste_name.append(prenom[1])
    for i in range (0, 5):
        nombre_total = 0
        if not liste_name[i] in verification:
            verification.append(liste_name[i])
        else:
            continue
        with    open("../../Downloads/names.csv", "r") as file:
            for line1 in file:
                count1 = line1.strip().split(",")
                if liste_name[i] in verification and liste_name[i] in count1 :
                        nombre_total = nombre_total + int(count1[5])
        
        d[liste_name[i]] = nombre_total
    print(d)
    #     verification.append(block_liste[1])
    #     verification1.append(block_liste[1])
    # for i in range (0, len(verification) - 1):
    #     gesamt_counter = 0
    #     for j in range (0, len(verification1) - 1):
    #         if verification[i] = verification1[j]:
    #             gesamt_counter = gesamt_counter + int(liste_complet[i].[])

    #         d[block_liste[1]] = block_liste[5]
    #     gesamt_counter = 0
    # print(verification)
    # print(d)
       
    # for i in range (0, len(verification) - 1):
    #     print(d[verification[i]])
    #     counter = counter + 1
    #     if counter == 123:
    #         break
        
    
