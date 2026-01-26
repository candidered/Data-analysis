import spacy
import re
# Attention, installer les paquets de spacy ne suffit pas, il faut aussi installer les paquets des modèles utilisés. Je vais tout faire en anglais car je pense que c'est le plus pertinent (spacy a des mots bizarres des fois en français)

def get_spacy_model(language):
    """
    Retourne un objet nlp spaCy selon la langue choisie.
    """
    if language=="French":
        model_name = "fr_dep_news_trf"
    else:
        model_name = "en_core_web_lg"
    nlp = spacy.load(model_name)
    nlp.max_length = 2000
    print(f"Using spaCy model: {model_name}")
    return nlp

nlp=get_spacy_model("anglais") # a setup, une fois suffit, plus besoin d'y toucher ensuite

def desc_nlp (desc) :
    """
    Renvoie la liste des tokens associés à une description
    """
    doc = nlp(desc.lower())
    tokens = [token for token in doc if not token.is_stop and token.is_alpha]
    return tokens

def classify_brand(brand_raw):
    """
    Classifie une marque en catégorie économique (Luxe, Premium, Mass Market, Sport, Discount).
    """
    if not isinstance(brand_raw, str):
        return "Unknown"
    
    brand = brand_raw.lower().strip()
    
    # Dictionnaire de classification étendu (Sources: , S_S30, S_S31, S_S43)
    brand_categories = {
        # --- LUXE (Haute Couture & Luxe Héritage) ---
        "chanel": "Luxe", "hermès": "Luxe", "hermes": "Luxe", "louis vuitton": "Luxe", "vuitton": "Luxe",
        "dior": "Luxe", "christian dior": "Luxe", "gucci": "Luxe", "prada": "Luxe",
        "yves saint laurent": "Luxe", "ysl": "Luxe", "saint laurent": "Luxe",
        "balenciaga": "Luxe", "fendi": "Luxe", "versace": "Luxe", "burberry": "Luxe",
        "cartier": "Luxe", "rolex": "Luxe", "omega": "Luxe", "moncler": "Luxe",
        "kenzo": "Luxe", "givenchy": "Luxe", "valentino": "Luxe", "bottega veneta": "Luxe",
        "loewe": "Luxe", "celine": "Luxe", "jacquemus": "Luxe", "alexander mcqueen": "Luxe",
        "chloé": "Luxe", "chloe": "Luxe", "dolce & gabbana": "Luxe", "dolce and gabbana": "Luxe",
        "jean paul gaultier": "Luxe", "off-white": "Luxe", "balmain": "Luxe",
        "carolina herrera": "Luxe",
        
        # --- PREMIUM (Luxe Accessible / Créateurs / Haut de Gamme) ---
        "maje": "Premium", "sandro": "Premium", "the kooples": "Premium", "zadig & voltaire": "Premium",
        "zadig et voltaire": "Premium", "ba&sh": "Premium", "bash": "Premium",
        "ralph lauren": "Premium", "polo ralph lauren": "Premium", "tommy hilfiger": "Premium",
        "lacoste": "Premium", "calvin klein": "Premium", "michael kors": "Premium",
        "coach": "Premium", "hugo boss": "Premium", "boss": "Premium",
        "claudie pierlot": "Premium", "sézane": "Premium", "sezane": "Premium",
        "patagonia": "Premium", "the north face": "Premium", # Souvent premium en seconde main
        "stone island": "Premium", "canada goose": "Premium", "carhartt": "Premium", "carhartt wip": "Premium",
        "dr. martens": "Premium", "doc martens": "Premium", "ugg": "Premium",
        "diesel": "Premium", "guess": "Premium", "isabel marant": "Premium",
        "a.p.c.": "Premium", "acne studios": "Premium", "ganni": "Premium",
        "des petits hauts": "Premium", "american vintage": "Premium", "veja": "Premium",
        "supreme": "Premium", "palace": "Premium", "cactus jack": "Premium", # Streetwear haut de gamme (S_S31)
        
        # --- SPORT (Performance & Lifestyle) ---
        "nike": "Sport", "adidas": "Sport", "puma": "Sport", "reebok": "Sport",
        "new balance": "Sport", "asics": "Sport", "under armour": "Sport",
        "fila": "Sport", "champion": "Sport", "converse": "Sport", "vans": "Sport",
        "columbia": "Sport", "salomon": "Sport", "gymshark": "Sport",
        "lululemon": "Sport", "quiksilver": "Sport", "roxy": "Sport", "billabong": "Sport",
        "kalenji": "Sport", "domyos": "Sport", "quechua": "Sport", # Marques Decathlon
        "decathlon": "Sport", "umbro": "Sport", "kappa": "Sport", "le coq sportif": "Sport",
        
        # --- MASS MARKET (Milieu de gamme / Standard) ---
        "zara": "Mass Market", "h&m": "Mass Market", "mango": "Mass Market", "uniqlo": "Mass Market",
        "levi's": "Mass Market", "levis": "Mass Market", "gap": "Mass Market",
        "bershka": "Mass Market", "pull & bear": "Mass Market", "stradivarius": "Mass Market",
        "oysho": "Mass Market", "massimo dutti": "Mass Market", # Positionnement hybride mais groupe Inditex
        "asos": "Mass Market", "asos design": "Mass Market",
        "topshop": "Mass Market", "river island": "Mass Market", "next": "Mass Market",
        "new look": "Mass Market", "etam": "Mass Market", "promod": "Mass Market",
        "camaïeu": "Mass Market", "camaieu": "Mass Market", "pimkie": "Mass Market",
        "naf naf": "Mass Market", "kookaï": "Mass Market", "kookai": "Mass Market",
        "morgan": "Mass Market", "jules": "Mass Market", "celio": "Mass Market", "brice": "Mass Market",
        "petit bateau": "Mass Market", "cyrillus": "Mass Market", "vertbaudet": "Mass Market",
        "okaïdi": "Mass Market", "sergent major": "Mass Market", "tape à l'œil": "Mass Market",
        "kiabi": "Mass Market", # Souvent perçu comme discount, mais structurellement Mass Market
        "la redoute": "Mass Market", "la redoute collections": "Mass Market",
        "lulu castagnette": "Mass Market", "disney": "Mass Market", # Souvent sous licence 
        "arket": "Mass Market", "cos": "Mass Market", "& other stories": "Mass Market",
        "superdry": "Mass Market", "hollister": "Mass Market", "abercrombie": "Mass Market",
        "brandy melville": "Mass Market", "urban outfitters": "Mass Market",
        
        # --- DISCOUNT / FAST FASHION (Entrée de gamme / Ultra Fast Fashion) ---
        "shein": "Discount", "primark": "Discount", "boohoo": "Discount",
        "prettylittlething": "Discount", "missguided": "Discount", "nasty gal": "Discount",
        "zeeman": "Discount", "action": "Discount", "lidl": "Discount", "aldi": "Discount",
        "tex": "Discount", # Marque Carrefour 
        "in extenso": "Discount", # Marque Auchan
        "gemo": "Discount", "gémo": "Discount", "la halle": "Discount",
        "tissaia": "Discount", # Marque Leclerc
        "lefties": "Discount", "c&a": "Discount", "jennyfer": "Discount", "don't call me jennyfer": "Discount",
        "undiz": "Discount", "atmosphere": "Discount" # Marque Primark
    }
    
    # 1. Recherche exacte
    if brand in brand_categories:
        return brand_categories[brand]
    
    # 2. Recherche de sous-marques ou variations (ex: "Zara Kids" -> "Zara")
    # On itère sur les clés pour voir si elles sont contenues dans la chaîne d'entrée
    for key, category in brand_categories.items():
        # Utilisation de regex pour matcher le mot entier (éviter que "gap" matche "agape")
        if re.search(r'\b' + re.escape(key) + r'\b', brand):
            return category
            
    # # 3. Règles heuristiques de secours (Fallback) pour les cas non listés
    # if "couture" in brand or "paris" in brand and ("maison" in brand or "atelier" in brand):
    #     # Indice faible de premium/luxe, à utiliser avec prudence ou marquer comme 'Potential Premium'
    #     pass 
        
    return "Unknown"

from spacy.tokens import Doc

def damage_grade(tklist):
    """
    Attribue une note de 0 (Neuf) à 10 (Très usé) en fonction de la description.
    """
    score = 0
    
    # Défauts majeurs (+3 points) : Trous, déchirures, grosses taches
    defauts_majeurs = {
        "hole", "tear", "rip", "broken", "damage", "stained", "stain", "spot", 
        "dirty", "mark", "flaw"
    }
    
    # Défauts mineurs (+1 point) : Usure naturelle, bouloches, décoloration
    defauts_mineurs = {
        "wear", "worn", "pilling", "bobble", "fade", "faded", "rubbing", 
        "scratch", "snag", "discoloration", "wash", "used"
    }
    
    # Termes positifs pour réduire le score (Bonus de sécurité)
    termes_neuf = {"new", "mint", "unused", "tag"}

    # 3. Parcours des tokens
    # On itère sur chaque mot de la description
    for token in tklist:
        points_a_ajouter = 0
        
        # Vérification si le mot est un défaut
        if token in defauts_majeurs:
            points_a_ajouter = 3
        elif token in defauts_mineurs:
            points_a_ajouter = 1
            
        # 4. Gestion intelligente de la négation (Amélioration spaCy)
        # Si un défaut est détecté, on vérifie s'il est nié avant d'ajouter les points.
        if points_a_ajouter > 0:
            est_nie = False
            
            # Méthode A : Vérifier les enfants syntaxiques (ex: "no" attaché à "stains")
            for child in token.children:
                if child.dep_ == "neg" or child.lemma_ in ["no", "not", "without", "sans"]:
                    est_nie = True
                    break
            
            # Méthode B : Vérifier le gouverneur (ex: "free" dans "stain free")
            if token.head.lemma_ in ["free", "without", "no"]:
                est_nie = True

            # Si le défaut n'est pas nié, on ajoute les points
            if not est_nie:
                score += points_a_ajouter
                # On peut logger ici pour le débogage si besoin
                # print(f"Défaut trouvé : {lemma} (+{points_a_ajouter})")

    score = min(score, 10)
    
    # Bonus : Si le mot "new" ou "mint" est présent sans négation, on force un score bas
    # (Ceci est une sécurité supplémentaire discutée précédemment)
    for token in tklist:
        if token.lemma_ in termes_neuf:
            # Vérifier que "new" n'est pas nié (ex: "not new")
            est_nie = any(child.dep_ == "neg" for child in token.children)
            if not est_nie:
                score = max(0, score - 2) # On réduit la note d'usure

    return score

test = "Columbia navy body warmer puffer jacket coat thick winter jacket padded gilet men’s size small, brand: Columbia, condition: New with tags, size: S, £35.00, £37.45 includes Buyer Protection Pro"
tklist = desc_nlp(test)
print(damage_grade(tklist))