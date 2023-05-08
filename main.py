import discord
import requests
import MiseEnForme
import formatageHeure
import APIs
import json
import sys
import discord.ui 

datajson = open("data.json", "w", encoding="UTF-8")
GaresID = open("gares_et_ids.txt", "r", encoding="UTF-8")

IDgare = GaresID

API_KEY = APIs.APISNCF

client = discord.Client(intents=discord.Intents.all())

toutesLesGares = [eachgare.split("|")[0] for eachgare in IDgare]


nombreresultat = ""


def getTrain(gare_depart, gare_arrivee, nombreOutput: int) -> list[str]:
    time = formatageHeure.timeToFormat()
    dataBaseGareNomId = MiseEnForme.MiseenForme("gares_et_ids.txt")
    if gare_depart in dataBaseGareNomId:
        idGareDepart = dataBaseGareNomId[dataBaseGareNomId.index(gare_depart)+1]
    else:
        return ["Erreur", "Problème avec la gare de départ"]
    if gare_arrivee in dataBaseGareNomId:
        idGareArrivee = dataBaseGareNomId[dataBaseGareNomId.index(gare_arrivee)+1]
    else:
        return ["Erreur", "problème avec la gare d'arriver"]
    listeDepart = []
    memoire = ""
    url = f"https://api.sncf.com/v1/coverage/sncf/journeys?from=stop_area:SNCF:{idGareDepart}&to=stop_area:SNCF:{idGareArrivee}&count={nombreOutput}&datetime={time}&key={API_KEY}"
    response = requests.get(url, auth=(API_KEY, ''))
    if response.status_code == 200:
        data = response.json()
        json.dump(data,datajson)
        # datajson.close()
        if "journeys" in data and len(data["journeys"]) > 0:
            for i in range(nombreOutput):
                try:
                    journey = data["journeys"][i]# type:ignore
                    horaireDepart = journey["departure_date_time"]
                    horaireArrivee = journey["arrival_date_time"]
                except IndexError:
                    global nombreresultat
                    nombreresultat = f"Nombre de résultat ajusté à {i}"
                try:
                    modeDeTransport: str = journey["sections"][1]["links"][3]["id"].split(":")[1]  # type:ignore
                    if modeDeTransport == "OUI":
                        modeDeTransport = "INOUI"
                    modeDeTransport = "("+modeDeTransport+")"
                except IndexError:
                    modeDeTransport = "(AUTRE)"
                # type:ignore
                if formatageHeure.formatToTimeDate(horaireDepart) != memoire:# type:ignore
                    dateDepart = formatageHeure.formatToTimeDate(
                        horaireDepart)  # type:ignore
                    listeDepart.append(dateDepart+":")
                    memoire = formatageHeure.formatToTimeDate(horaireDepart)  # type:ignore
                heureDepart = formatageHeure.formatToTimeHeure(horaireDepart)  # type:ignore
                heureArrivee = formatageHeure.formatToTimeHeure(horaireArrivee)  # type:ignore
                listeDepart.append(f"{heureDepart}-->{heureArrivee} {modeDeTransport}")  # type:ignore
            return listeDepart
    return ["Impossible de trouvée des horaires"]


def getGare(gare: str) -> str:
    resRecherche = [g.capitalize() for g in toutesLesGares if g.startswith(gare)]
    return MiseEnForme.horaireForme(resRecherche)


def createEmbed(titre: str, descriptions: str = ""):
    Embed = discord.Embed(title=titre, description=descriptions, color=discord.Colour(0xE9055E))
    return Embed

def createButtonRetour(text:str):
    return discord.ui.Button(label=text,style=discord.ButtonStyle.green,emoji="🚅")

def createButtonHelp(text:str):
    return discord.ui.Button(label=text,style=discord.ButtonStyle.blurple,emoji="💡")

def countDate(datehoraire:list[str])->int:
    return datehoraire.count("/")//2

def isDate(datehoraire:str)->bool:
    return datehoraire.count("/")==2

#finir ça voir le miseenformehoraire pour voir des horaires avec des fields en fonction du nombre d'output

def createEmbedWithField(nom:str,horaire:str):
    embeds=discord.Embed(title=nom,color=discord.Colour(0xE9055E))
    listehoraire=horaire.split("\n")
    listeheure=[]
    for i in range(len(listehoraire)):
        if isDate(listehoraire[i]):
            date=listehoraire[i]
        else:
            listeheure.append(listehoraire[i])
            try:
                if isDate(listehoraire[i+1]):
                    embeds.add_field(name=str(date),value=MiseEnForme.horaireForme(listeheure),inline=False)#type:ignore
            except IndexError:
                embeds.add_field(name=str(date),value=MiseEnForme.horaireForme(listeheure),inline=False)#type:ignore
    return embeds

@client.event
async def on_ready():
    print('Bot prêt')
    guilds=client.guilds
    for guild in guilds:
        print(guild)

@client.event
async def on_message(message):
    try:
        if message.content.startswith("!help"):
            embeds = createEmbed("!help")
            embeds.add_field(name="!train <Gare-de-départ> <Gare-d'arrivé> <Nombre d'horaire>",value="!train permet de connaitre les trains entre 2 positions A et B les prompts des gares doivent forcément avoir des tirets dedans pour en savoir plus vous pouvez faire !gare <nom de gare recherche> pour trouver le nom de certaines gare toujours avec des tirets",inline=False)  
            embeds.add_field(name="!gare <Gare-rechercher>",value="!gare permet de connaitre les gares possibles à rentrer dans le prompt de !train (ne fait pas de requête à l'API)",inline=False)
            embeds.add_field(name="Information",value="L'API est limité par la SNCF à 90 000 Requêtes par mois, dans la limite de 3 000 Requêtes par jour (on a de la marge)",inline=False)
            await message.channel.send(embed=embeds)
            
        if message.content.startswith("!gare"):
            command_parts = message.content.split()
            if len(command_parts) != 2:
                embed = createEmbed(
                    "Erreur", "La commande !gare est une commande de recherche elle s'utilise de cette façon !gare <nom-de-gare>")
                await message.channel.send(embed=embed)
            else:
                gare = command_parts[1].lower()
                # gare:str=f"Voici les résultats de gare pour {command_parts[1]}:\n{getGare(gare)}"
                embeds = createEmbed(f'Voici les résultats de gare pour "{command_parts[1]}":', f'{getGare(gare)}')
                if nombreresultat != "":
                    embeds.add_field(name="Limitation", value=nombreresultat)
                await message.channel.send(embed=embeds)

        if message.content.startswith('!train'):
            command_parts = message.content.split()
            if len(command_parts) != 4:
                if len(command_parts) != 3:
                    embeds = createEmbed("Utilisation:", "!train <gare_depart> <gare_arrivee> <nombre_d'horaire>")
                    await message.channel.send(embed=embeds)
                    return
            if len(command_parts) == 3:
                nombreOutput: int = 1
            else:
                nombreOutput: int = int(command_parts[3])

            gare_depart = command_parts[1].lower()
            gare_arrivee = command_parts[2].lower()

            train: list[str] = getTrain(gare_depart, gare_arrivee, nombreOutput)  # data
            horaire: str = MiseEnForme.horaireForme(train)
            if train is None:
                embeds = createEmbed(f"Aucun train trouvé entre {gare_depart} et {gare_arrivee}.")
                await message.channel.send(embed=embeds)
                # await message.channel.send(f"Aucun train trouvé entre {gare_depart} et {gare_arrivee}.")
            else:
                embeds = createEmbedWithField(f"Horaires de train entre {gare_depart.capitalize()} et {gare_arrivee.capitalize()} :", f"{horaire}")
                try:
                    async def buttonCallbackRetour(interaction,gareA=gare_arrivee,gareD=gare_depart):
                        embeds=createEmbedWithField(f"Retour entre {gareA.capitalize()} et {gareD.capitalize()}",f"{MiseEnForme.horaireForme(getTrain(gareA,gareD,nombreOutput))}")
                        views=discord.ui.View()
                        bouttonHelp=createButtonHelp("Help")
                        views.add_item(bouttonHelp)
                        bouttonHelp.callback=bouttonCallbackHelp
                        await interaction.response.send_message(embed=embeds,view=views)
                    async def bouttonCallbackHelp(interaction):
                        embeds=createEmbed("Help")
                        embeds.add_field(name="!train <Gare-de-départ> <Gare-d'arrivé> <Nombre d'horaire>",value="!train permet de connaitre les trains entre 2 positions A et B les prompts des gares doivent forcément avoir des tirets dedans pour en savoir plus vous pouvez faire !gare <nom de gare recherche> pour trouver le nom de certaines gare toujours avec des tirets",inline=False)  
                        embeds.add_field(name="!gare <Gare-rechercher>",value="!gare permet de connaitre les gares possibles à rentrer dans le prompt de !train (ne fait pas de requête à l'API)",inline=False)
                        embeds.add_field(name="Information",value="L'API est limité par la SNCF à 90 000 Requêtes par mois, dans la limite de 3 000 Requêtes par jour (on a de la marge)",inline=False)
                        await interaction.response.send_message(embed=embeds)
                        
                    bouttonRetour=createButtonRetour(f"Retour")
                    bouttonHelp=createButtonHelp("Help")
                    views=discord.ui.View()
                    views.add_item(bouttonRetour)
                    views.add_item(bouttonHelp)
                    bouttonRetour.callback=buttonCallbackRetour
                    bouttonHelp.callback=bouttonCallbackHelp
                    await message.channel.send(embed=embeds,view=views) 
                except:
                    print(str(sys.exc_info()))
                    embeds = createEmbed("Quantité d'ouput impossible à satisfaire (essaie un nombre inférieur à 50)")
                    await message.channel.send(embed=embeds)
    except:
        # embeds = createEmbed("Error", str(sys.exc_info()))
        print(str(sys.exc_info()))
        embeds = createEmbed("Error")
        await message.channel.send(embed=embeds)

client.run(APIs.APIDISCORD)
