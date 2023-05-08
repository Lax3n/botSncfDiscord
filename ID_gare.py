import requests
import APIs

# Définir le nom du fichier où stocker les identifiants
filename = "gares_et_ids.txt"

# Ouvrir le fichier en mode écriture
with open(filename, "w", encoding="UTF-8") as file:
    # Définir l'URL de l'API SNCF
    url = "https://api.sncf.com/v1/coverage/sncf/stop_areas"

    # Définir les paramètres de la requête
    for i in range(5):
        params = {
            "type": "stop_area",  # Type de l'objet recherché (ici, une gare)
            "count": 1000,       # Nombre maximum d'objets à renvoyer par requête
            "key": APIs.APISNCF,  # Clé API SNCF
            "start_page": i
        }

        # Envoyer la première requête à l'API SNCF et récupérer la réponse

        response = requests.get(url, params=params)

        # Vérifier si la première requête a réussi (code 200)
        if response.status_code == 200:
            # Extraire les données de la réponse au format JSON
            data = response.json()
            # Ajouter les identifiants de toutes les gares de la première page au fichier
            for stop_area in data["stop_areas"]:
                ID=stop_area['id'].split(":")[-1]
                bewrite=f"{stop_area['name']}|{ID}\n"
                bewrite=bewrite.replace(" ","-")
                bewrite=bewrite.replace("--","-")
                bewrite=bewrite.replace("---","-")
                bewrite=bewrite.replace("--","-")
                file.write(bewrite.lower())
            # Vérifier s'il y a d'autres pages de résultats
        else:
            # Afficher un message d'erreur si la première requête a échoué
            print("Erreur lors de la requête à l'API SNCF :", response.status_code)

    # Afficher un message de confirmation à la fin du script
    print("Les identifiants et noms de toutes les gares ont été stockés dans le fichier", filename)
