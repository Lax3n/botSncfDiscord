import datetime
#YYYYMMDDTHHMMSS
def timeToFormat()->str:
    time=str(datetime.datetime.now())
    annee=time[0:4]
    mois=time[5:7]
    jour=time[8:10]
    heure=time[11:13]
    minute=time[14:16]
    seconde=time[17:19]
    return "%s%s%sT%s%s%s"%(annee,mois,jour,heure,minute,seconde)

def formatToTimeHeure(format:str)->str:
    heure=format[9:11]
    minute=format[11:13]
    return "%sh%s"%(heure,minute)


def formatToTimeDate(format:str)->str:
    annee=format[0:4]
    mois=format[4:6]
    jour=format[6:8]
    return "%s/%s/%s"%(jour,mois,annee)
