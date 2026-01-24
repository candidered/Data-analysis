import requests
import json
import time
import random

def fetch_vinted_items(query=["32"], pages=1, country = "fr"):
    # 1. Configuration de la session
    session = requests.Session()
    
    # Il est CRITIQUE d'avoir un User-Agent réaliste pour ne pas être rejeté immédiatement
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": f"https://www.vinted.{country}/"
    }
    session.headers.update(headers)

    try:
        # 2. Étape Initiale : Visiter la page d'accueil pour obtenir les cookies (CSRF, session)
        print("Initialisation de la session (récupération des cookies)...")
        response_home = session.get(f"https://www.vinted.{country}/")
        
        if response_home.status_code != 200:
            print(f"Erreur lors de l'accès à la page d'accueil: {response_home.status_code}")
            return

        # Pause aléatoire pour imiter un humain
        time.sleep(random.uniform(1, 3))
        all_items = []

        # 3. Requête vers l'API interne
        api_url = f"https://www.vinted.{country}/api/v2/catalog/items"

        random.shuffle(query)

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
                
                print(f"Scraping page {page} pour '{q}' in {country}...")
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
                            "status": item.get("status"),
                            "status_id": item.get("status_id"),
                            "item_box": item.get("item_box"),
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
                time.sleep(random.uniform(5, 12))

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
    """Ajoute les items nouveaux ou remplace ceux sans catégorie 'état'.
    Renvoie le nombre d'items effectivement ajoutés/modifiés."""
    if not items:
        return 0

    # Charger tous les objets existants
    existing_items = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        existing_items.append(obj)
                    except json.JSONDecodeError:
                        pass
    except FileNotFoundError:
        pass

    # Créer un dict id -> index pour les existants
    existing_dict = {str(item.get("id")): i for i, item in enumerate(existing_items) if item.get("id") is not None}

    modified = False
    for item in items:
        _id = item.get("id")
        if _id is None:
            continue
        _id_str = str(_id)
        if _id_str in existing_dict:
            # Vérifier si l'existant a la catégorie "état"
            idx = existing_dict[_id_str]
            existing_status = existing_items[idx].get("status")
            if existing_status != "état":
                existing_items[idx] = item
                modified = True
        else:
            existing_items.append(item)
            modified = True

    if not modified:
        return 0

    # Réécrire le fichier entier d'un coup
    with open(file_path, "w", encoding="utf-8") as f:
        for item in existing_items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return len(items)

            

if __name__ == "__main__":
    liste = ["32", "1206", "34", "85", "84", "92", "257", "76", "79", "80", "2910", "30", "13", "10", "12", "9", "1035", "29", "73", "1037", "8", "11", "183", "15", "28", "1176", "1782",
            "1233", "2657", "1238", "2659", "1242", "2656", "2970", "2969", "2968", "1452", "2954", "2623", "2955", "1049", "2953", "543", "2950", "215", "2632", "2952", "2951", "2949", "2630"]  # Liste des catalog_ids à rechercher
    country = [ "co.uk", "sk", "si", "ro", "lv", "lt", "hu", "de", "fr", "pt", "es", "com", "it", "nl", "be", "at", "pl", "cz", "lu", "dk", "ee", "se", "gr", "ie", "hr"]
    country2 = ["fr"]
    for ctry in country[8::]:
        resultats = fetch_vinted_items(query=liste, pages=2, country=ctry)  # Ajouter d'autres pays si nécessaire
        total = len(resultats) if resultats else 0
        print(f"\nTotal articles récupérés : {total}")
        # Écrire les résultats dans le fichier vinted_products_api.jsonl (ajout sans doublons)
        if resultats:
            added = append_to_jsonl("vinted_products_api.jsonl", resultats)
            skipped = total - added
            print(f"Résultats ajoutés à 'vinted_products_api.jsonl' ({added} nouvelles lignes).")
            if skipped:
                print(f"{skipped} items ignorés (déjà présents ou sans id).")