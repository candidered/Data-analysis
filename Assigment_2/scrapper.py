import requests
import json
import time
import random

"""Scraper pour Vinted utilisant l'API interne du site."""
"""
La fonction principale fetch_vinted_items interroge l'API interne de Vinted pour récupérer des articles
en fonction de critères spécifiés (catégories, nombre de pages, pays). Elle gère les sessions, les en-têtes,
et les erreurs courantes comme les blocages par Datadome ou les limitations de taux.

Les fonctions auxiliaires read_existing_ids et append_to_jsonl permettent de gérer l'écriture des résultats
dans un fichier JSONL tout en évitant les doublons basés sur l'ID des articles.

Paramètres de fetch_vinted_items:
- query: Liste des catalog_ids (catégories) à rechercher.
- pages: Nombre de pages à scraper pour chaque catégorie.
- country: Code du pays pour adapter l'URL de Vinted (ex: "fr" pour France).

Retourne une liste de dictionnaires contenant les informations des articles récupérés.

La boucle principale à la fin du script permet de lancer le scraper pour une liste de catégories et de pays,
et d'écrire les résultats dans un fichier nommé vinted_products_api.jsonl
"""

def fetch_vinted_items(query=["32"], pages=1, country = "fr"):
    # 1. Configuration de la session
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.vinted.{country}/"
    }
    session.headers.update(headers)

    try:
        # Visiter la page d'accueil pour obtenir les cookies
        print("Initialisation de la session (récupération des cookies)...")
        response_home = session.get(f"https://www.vinted.{country}/")
        
        if response_home.status_code != 200:
            print(f"Erreur lors de l'accès à la page d'accueil: {response_home.status_code}")
            return

        # Pause aléatoire pour imiter un humain
        time.sleep(random.uniform(1, 3))
        all_items = []

        # Requête vers l'API interne
        api_url = f"https://www.vinted.{country}/api/v2/catalog/items"

        for q in query:
        
            for page in range(1, pages + 1):
                params = {
                    # "search_text": query,
                    "page": page, # Numéro de la page
                    "per_page": 96,  # Nombre d'articles par page
                    "order": "newest_first", # Ordre des résultats
                    "catalog_ids" : q # catégorie
                    # brand_ids ex "1"
                }
                
                print(f"Scraping page {page} pour '{q}' in {country}...")
                response_api = session.get(api_url, params=params)

                # Gestion des erreurs (notamment les blocages 403/429)
                if response_api.status_code == 200:
                    data = response_api.json()
                    items = data.get("items", [])
                    
                    for item in items:
                        item_info = {
                            "id": item.get("id"), # id de l'article
                            "titre": item.get("title"), # titre de l'article
                            "prix": item.get("price"), # prix affiché
                            "service_fee": item.get("service_fee"), # frais de service
                            "prix_total": item.get("total_item_price"), # prix total (avec frais)
                            "devise": item.get("currency"), # devise
                            "discount": item.get("discount"), # réduction éventuelle
                            "taille": item.get("size_title"), # taille
                            "marque": item.get("brand_title"), # marque
                            "url": item.get("url"), # url de l'article
                            "status_id": item.get("status_id"), # statut (disponible, vendu, etc.)
                            "vendeur_id": item.get("user", {}).get("id"), # id du vendeur
                            "vendeur_nom": item.get("user", {}).get("login"), # nom du vendeur
                            "favoris": item.get("favorites_count"),  # nombre de fois en favoris
                            "vues": item.get("views_count"), # nombre de vues
                            "query": q, # requête utilisée
                            "country": country # pays
                        }
                        all_items.append(item_info)
                                            
                elif response_api.status_code == 403:
                    print("ERREUR 403: Accès refusé par Datadome/Cloudflare. Bot détecté.")
                    break
                elif response_api.status_code == 429:
                    print("ERREUR 429: Trop de requêtes (Rate Limit).")
                    break
                else:
                    print(f"Erreur inconnue: {response_api.status_code}")
                
                # Pause entre les pages pour réduire le risque de ban
                time.sleep(random.uniform(2, 5))

        return all_items

    except Exception as e:
        print(f"Une erreur est survenue: {e}")

def read_existing_ids(file_path):
    """Lit un .jsonl et retourne un set d'ids (sous forme de str)."""
    ids = set()
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    _id = obj.get("id")
                    if _id is not None:
                        ids.add(str(_id))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        # Aucun fichier existant => aucun id connu
        pass
    return ids

def append_to_jsonl(file_path, items):
    """Ajoute uniquement les items dont l'id n'est pas déjà présent.
    Renvoie le nombre d'items effectivement ajoutés."""
    if not items:
        return 0

    existing_ids = read_existing_ids(file_path)
    to_write = []
    for item in items:
        _id = item.get("id")
        # Ignorer items sans id
        if _id is None:
            continue
        if str(_id) not in existing_ids:
            to_write.append(item)
            existing_ids.add(str(_id))

    if not to_write:
        return 0

    with open(file_path, "a", encoding="utf-8") as f:
        for item in to_write:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return len(to_write)

if __name__ == "__main__":
    liste = ["32", "1206", "34", "85", "84", "92", "257", "76", "79", "80", "2910", "30", "13", "10", "12", "9", "1035", "29", "73", "1037", "8", "11", "183", "15", "28", "1176", "1782",
             "1233", "2657", "1238", "2659", "1242", "2656", "2970", "2969", "2968", "1452", "2954", "2623", "2955", "1049", "2953", "543", "2950", "215", "2632", "2952", "2951", "2949", "2630"]  # Liste des catalog_ids à rechercher
    # liste est la liste des catalog_ids (catégories) à scraper
    # Les correspondances catalog_id <-> catégorie sont dans le fichier correspondance.txt
    
    country = ["de", "fr", "es", "com", "it", "nl", "be", "pt", "at", "pl", "cz", "lu", "dk", "ee", "se", "gr", "ie", "hr", "co.uk", "sk", "si", "ro", "lv", "lt", "hu"]
    # country est la liste des pays à scraper. Elle a été établie en fonction des extensions de domaine utilisées par Vinted.

    # On boucle sur les pays pour recréer une session propre à chaque pays (pour les cookies)
    for ctry in country:
        resultats = fetch_vinted_items(query=liste, pages=1, country=ctry)  
        total = len(resultats) if resultats else 0 # nombre total d'articles récupérés
        print(f"\nTotal articles récupérés : {total}")

        # Écrire les résultats dans le fichier vinted_products_api.jsonl (ajout sans doublons)
        if resultats:
            added = append_to_jsonl("vinted_products_api.jsonl", resultats) # nombre d'articles ajoutés
            skipped = total - added # nombre d'articles ignorés (car déjà présents)
            print(f"Résultats ajoutés à 'vinted_products_api.jsonl' ({added} nouvelles lignes).") 
            if skipped:
                print(f"{skipped} items ignorés (déjà présents ou sans id).")