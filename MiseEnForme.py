def MiseenForme(name:str)->list[tuple[str,int]]:
    res=[]
    fichier=open(name,"r",encoding="UTF-8").read()
    l=fichier.split("\n")
    for each_element in l:
        nomgare,idgare=each_element.split("|")
        res.append(nomgare)
        res.append(idgare)
    return res
    
def horaireForme(horaire:list[str])->str:
    return "\n".join(horaire)