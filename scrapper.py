import requests
import json
import time
import random

def fetch_vinted_items(query="sneakers", pages=1, country = ["fr"]):
    # 1. Configuration de la session
    session = requests.Session()
    
    # Il est CRITIQUE d'avoir un User-Agent réaliste pour ne pas être rejeté immédiatement
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.vinted.fr/"
    }
    session.headers.update(headers)

    try:
        # 2. Étape Initiale : Visiter la page d'accueil pour obtenir les cookies (CSRF, session)
        print("Initialisation de la session (récupération des cookies)...")
        response_home = session.get("https://www.vinted.fr/")
        
        if response_home.status_code != 200:
            print(f"Erreur lors de l'accès à la page d'accueil: {response_home.status_code}")
            return

        # Pause aléatoire pour imiter un humain
        time.sleep(random.uniform(1, 3))
        all_items = []

        # 3. Requête vers l'API interne
        for ctry in country:
            api_url = f"https://www.vinted.{ctry}/api/v2/catalog/items"

            for q in query:
            
                for page in range(1, pages + 1):
                    params = {
                        # "search_text": query,
                        "page": page,
                        "per_page": 96,  # Nombre d'articles par page
                        "order": "newest_first", 
                        "catalog_ids" : q
                        # brand_ids ex "1"
                    }
                    
                    print(f"Scraping page {page} pour '{q}'...")
                    response_api = session.get(api_url, params=params)

                    # Gestion des erreurs (notamment les blocages 403/429)
                    if response_api.status_code == 200:
                        data = response_api.json()
                        items = data.get("items", [])
                        
                        for item in items:
                            item_info = {
                                "id": item.get("id"),
                                "titre": item.get("title"),
                                "prix": item.get("price"),
                                "service_fee": item.get("service_fee"),
                                "prix_total": item.get("total_item_price"),
                                "devise": item.get("currency"),
                                "discount": item.get("discount"),
                                "taille": item.get("size_title"),
                                "marque": item.get("brand_title"),
                                "url": item.get("url"),
                                "status_id": item.get("status_id"),
                                "vendeur_id": item.get("user", {}).get("id"),
                                "vendeur_nom": item.get("user", {}).get("login"),
                                "favoris": item.get("favorites_count"),
                                "vues": item.get("views_count"),
                                "query": q,
                                "country": country
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
    resultats = fetch_vinted_items(query=liste, pages=1, country=["fr"])
    total = len(resultats) if resultats else 0
    print(f"\nTotal articles récupérés : {total}")
    # Écrire les résultats dans le fichier vinted_products_api.jsonl (ajout sans doublons)
    if resultats:
        added = append_to_jsonl("vinted_products_api.jsonl", resultats)
        skipped = total - added
        print(f"Résultats ajoutés à 'vinted_products_api.jsonl' ({added} nouvelles lignes).")
        if skipped:
            print(f"{skipped} items ignorés (déjà présents ou sans id).")