import time
import requests
import pandas as pd
import random
import json
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

import statsmodels.api as sm
import statsmodels.formula.api as smf
import analyse_candide as ac

#Here we create a dictionary to map category IDs to genders

gender_dict = {
    # HOMME — vêtements
    "32": "homme",
    "1206": "homme",
    "34": "homme",
    "85": "homme",
    "84": "homme",
    "92": "homme",
    "257": "homme",
    "76": "homme",
    "79": "homme",
    "80": "homme",
    "2910": "homme",
    "30": "homme",

    # HOMME — chaussures
    "1233": "homme",
    "2657": "homme",
    "1238": "homme",
    "2659": "homme",
    "1242": "homme",
    "2656": "homme",
    "2970": "homme",
    "2969": "homme",
    "2968": "homme",
    "1452": "homme",

    # FEMME — vêtements
    "13": "femme",
    "10": "femme",
    "12": "femme",
    "9": "femme",
    "1035": "femme",
    "29": "femme",
    "73": "femme",
    "1037": "femme",
    "8": "femme",
    "11": "femme",
    "183": "femme",
    "15": "femme",
    "28": "femme",
    "1176": "femme",
    "1782": "femme",

    # FEMME — chaussures
    "2954": "femme",
    "2623": "femme",
    "2955": "femme",
    "1049": "femme",
    "2953": "femme",
    "543": "femme",
    "2950": "femme",
    "215": "femme",
    "2632": "femme",
    "2952": "femme",
    "2951": "femme",
    "2949": "femme",
    "2630": "femme",
}

#Here we create a dictionary to map category IDs to super categories that can be considered similar for men and women 

category_dict = {
    # HOMME — vêtements
    "32": "suits and blazers",
    "1206": "outerwear",
    "34": "trousers",
    "85": "socks and underwear",
    "84": "swimwear",
    "92": "costumes and special outfits",
    "257": "jeans",
    "76": "tops and t-shirts",
    "79": "jumpers and sweaters",
    "80": "shorts",
    "2910": "sleepwear",
    "30": "activewear",

    # HOMME — chaussures
    "1233": "boots",
    "2657": "espadrilles",
    "1238": "formal shoes",
    "2659": "slippers",
    "1242": "trainers",
    "2656": "boat shoes, loafers and moccasins",
    "2970": "clogs and mules",
    "2969": "flip-flops and slides",
    "2968": "sandals",
    "1452": "sports shoes",

    # FEMME — vêtements
    "13": "jumpers and sweaters",
    "10": "dresses",
    "12": "tops and t-shirts",
    "9": "trousers and leggings",
    "1035": "jumpsuits and playsuits",
    "29": "lingerie and nightwear",
    "73": "activewear",
    "1037": "outerwear",
    "8": "suits and blazers",
    "11": "skirts",
    "183": "jeans",
    "15": "shorts and cropped trousers",
    "28": "swimwear",
    "1176": "maternity clothes",
    "1782": "costumes and special outfits",

    # FEMME — chaussures
    "2954": "boat shoes, loafers and moccasins",
    "2623": "clogs and mules",
    "2955": "ballerinas",
    "1049": "boots",
    "2953": "espadrilles",
    "543": "heels",
    "2950": "mary janes and t-bar shoes",
    "215": "slippers",
    "2632": "trainers",
    "2952": "flip-flops and slides",
    "2951": "lace-up shoes",
    "2949": "sandals",
    "2630": "sports shoes",
}
#Here we create a dictionary to map category titles to super categories that can be considered similar for men and women
super_category_dict = {
    # Pants / trousers / leggings
    "trousers": "trousers",
    "trousers and leggings": "trousers",
    "jeans": "jeans",
    "shorts": "shorts",
    "shorts and cropped trousers": "shorts",

    # Tops / T-shirts / jumpers
    "tops and t-shirts": "t-shirts",
    "jumpers and sweaters": "jumpers",
    "sweatshirts": "jumpers",
    
    # Dresses / skirts
    "dresses": "dresses",
    "skirts": "skirts",
    "jumpsuits and playsuits": "jumpsuits",

    # Outerwear
    "outerwear": "outerwear",
    
    # Suits / blazers
    "suits and blazers": "suits and blazers",
    
    # Swimwear / lingerie / activewear
    "swimwear": "swimwear",
    "lingerie and nightwear": "lingerie",
    "activewear": "activewear",
    "sleepwear": "sleepwear",
    "maternity clothes": "maternity clothes",
    "costumes and special outfits": "special outfits",
    
    # Shoes (all types merged)
    "boots": "shoes",
    "espadrilles": "shoes",
    "formal shoes": "shoes",
    "slippers": "shoes",
    "trainers": "shoes",
    "boat shoes, loafers and moccasins": "shoes",
    "clogs and mules": "shoes",
    "flip-flops and slides": "shoes",
    "sandals": "shoes",
    "sports shoes": "shoes",
    "ballerinas": "shoes",
    "heels": "shoes",
    "mary janes and t-bar shoes": "shoes",
    "lace-up shoes": "shoes"
}

#This script converts the raw JSONL data obtained from Vinted scraping into a cleaned JSON file with selected fields.

#The input_path path may need to be changed to your local paths obtained with the scrapping
input_path = r"vinted_products_api.jsonl"
output_path = r"vinted_test_candide_clean.json" 

converted_items = []

with open(input_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue  # skip empty lines
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Skipping line {i} due to JSON error: {e}")
            continue

        query = str(item.get("query")) if item.get("query") is not None else None #the query gives us the category ID

#Here is the description of the data that we collected or inferred from the raw data
        converted_item = {
            "item_id": item.get("id"),
            "price": float(item["prix"]["amount"]) if item.get("prix") else None,
            "currency": item["prix"]["currency_code"] if item.get("prix") else None,
            "gender": gender_dict.get(query),
            "category_title": category_dict.get(query),
            "category_id": query,
            "brand": item.get("marque"),
            "title": item.get("titre"),
            "url": item.get("url"),
            "user_id": item.get("vendeur_id"),
            "username": item.get("vendeur_nom"),
            "country": item.get("country"),
            "desc" : item.get("item_box")["accessibility_label"] if item.get("item_box") else "",
            "status" : item.get("status")
        }

        converted_items.append(converted_item)

# Save as JSON array
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(converted_items, f, ensure_ascii=False, indent=4)


df = pd.read_json(output_path)

df["super_category"] = df["category_title"].map(super_category_dict)
df = df.dropna(subset=["super_category"])

# counts_score = [0,0,0,0,0,0,0]
# counts_urgency = 0

# for item in df["brand"] :
#     brand = ac.classify_brand(item)
#     if brand == "Luxe" :
#         counts_score[0] +=1
#     elif brand == "Premium" :
#         counts_score[1] +=1
#     elif brand == "Sport" :
#         counts_score[2] +=1
#     elif brand == "Mass Market" :
#         counts_score[3] +=1
#     elif brand == "Discount" :
#         counts_score[4] +=1
#     elif brand == "Unknown" :
#         counts_score[5] +=1
#     else :
#         counts_score[6] +=1
# print (counts_score)

# counts_status = [0,0,0,0,0,0]

# print(df["status"][0:50])

# for etat in df["status"] :
#     if etat == "Neuf avec étiquette" or etat == "New with tags" :
#         counts_status[0] += 1
#     elif etat == "Neuf sans étiquette" or etat == "New without tags" :
#         counts_status[1] += 1
#     elif etat == "Très bon état" or etat == "Very good" :
#         counts_status[2] += 1
#     elif etat == "Bon état" or etat == "Good" :
#         counts_status[3] += 1
#     elif etat == "Satisfaisant" or etat == "Satisfactory" :
#         counts_status[4] += 1
#     else :
#         counts_status[5] += 1

# score = [0,0,0,0,0,0,0,0,0,0,0,0]

# for desc in df["desc"] :
#     if desc == "" :
#         score[0] +=1
#     else :
#         i = ac.damage_grade(ac.desc_nlp(desc))
#         score[i+1] +=1

# for desc in df["desc"][0:100]:
#     if desc != "" :
#         print(desc)
#         print(ac.desc_nlp(desc))
#         print(ac.damage_grade(ac.desc_nlp(desc)))


# print(counts_status)
# print(score)

n = len(df)
men_meansNWT = [0,0,0,0,0,0]
men_countNWT = [0,0,0,0,0,0]
women_meansNWT = [0,0,0,0,0,0]
women_countNWT = [0,0,0,0,0,0]
men_meansNST = [0,0,0,0,0,0]
men_countNST = [0,0,0,0,0,0]
women_meansNST = [0,0,0,0,0,0]
women_countNST = [0,0,0,0,0,0]
men_meansTB = [0,0,0,0,0,0]
men_countTB = [0,0,0,0,0,0]
women_meansTB = [0,0,0,0,0,0]
women_countTB = [0,0,0,0,0,0]
men_meansB = [0,0,0,0,0,0]
men_countB = [0,0,0,0,0,0]
women_meansB = [0,0,0,0,0,0]
women_countB = [0,0,0,0,0,0]
men_meansS = [0,0,0,0,0,0]
men_countS = [0,0,0,0,0,0]
women_meansS = [0,0,0,0,0,0]
women_countS= [0,0,0,0,0,0]
men_means = [0,0,0,0,0,0]
men_count = [0,0,0,0,0,0]
women_means = [0,0,0,0,0,0]
women_count = [0,0,0,0,0,0]


for i in range (n) :
    if df["gender"].get(i) == "femme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Neuf avec étiquette" or etat == "New with tags" or etat == "Nuevo con etiquetas" or etat == "Novo com etiquetas":
            if brand == "Luxe" :
                women_meansNWT[0] += df["price"].get(i)
                women_countNWT[0] += 1
            elif brand == "Premium" :
                women_meansNWT[1] += df["price"].get(i)
                women_countNWT[1] += 1
            elif brand == "Sport" :
                women_meansNWT[2] += df["price"].get(i)
                women_countNWT[2] += 1
            elif brand == "Mass Market" :
                women_meansNWT[3] += df["price"].get(i)
                women_countNWT[3] += 1
            elif brand == "Discount" :
                women_meansNWT[4] += df["price"].get(i)
                women_countNWT[4] += 1
            else : 
                women_meansNWT[5] += df["price"].get(i)
                women_countNWT[5] += 1
    if df["gender"].get(i) == "homme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Neuf avec étiquette" or etat == "New with tags" or etat == "Nuevo con etiquetas" or etat == "Novo com etiquetas":
            if brand == "Luxe" :
                men_meansNWT[0] += df["price"].get(i)
                men_countNWT[0] += 1
            elif brand == "Premium" :
                men_meansNWT[1] += df["price"].get(i)
                men_countNWT[1] += 1
            elif brand == "Sport" :
                men_meansNWT[2] += df["price"].get(i)
                men_countNWT[2] += 1
            elif brand == "Mass Market" :
                men_meansNWT[3] += df["price"].get(i)
                men_countNWT[3] += 1
            elif brand == "Discount" :
                men_meansNWT[4] += df["price"].get(i)
                men_countNWT[4] += 1
            else : 
                men_meansNWT[5] += df["price"].get(i)
                men_countNWT[5] += 1

for i in range (n) :
    if df["gender"].get(i) == "femme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Neuf sans étiquette" or etat == "New without tags" or etat == "Nuevo sin etiquetas" or etat == "Novo sem etiquetas":
            if brand == "Luxe" :
                women_meansNST[0] += df["price"].get(i)
                women_countNST[0] += 1
            elif brand == "Premium" :
                women_meansNST[1] += df["price"].get(i)
                women_countNST[1] += 1
            elif brand == "Sport" :
                women_meansNST[2] += df["price"].get(i)
                women_countNST[2] += 1
            elif brand == "Mass Market" :
                women_meansNST[3] += df["price"].get(i)
                women_countNST[3] += 1
            elif brand == "Discount" :
                women_meansNST[4] += df["price"].get(i)
                women_countNST[4] += 1
            else : 
                women_meansNST[5] += df["price"].get(i)
                women_countNST[5] += 1
    if df["gender"].get(i) == "homme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Neuf sans étiquette" or etat == "New without tags" or etat == "Nuevo sin etiquetas" or etat == "Novo sem etiquetas":
            if brand == "Luxe" :
                men_meansNST[0] += df["price"].get(i)
                men_countNST[0] += 1
            elif brand == "Premium" :
                men_meansNST[1] += df["price"].get(i)
                men_countNST[1] += 1
            elif brand == "Sport" :
                men_meansNST[2] += df["price"].get(i)
                men_countNST[2] += 1
            elif brand == "Mass Market" :
                men_meansNST[3] += df["price"].get(i)
                men_countNST[3] += 1
            elif brand == "Discount" :
                men_meansNST[4] += df["price"].get(i)
                men_countNST[4] += 1
            else : 
                men_meansNST[5] += df["price"].get(i)
                men_countNST[5] += 1

for i in range (n) :
    if df["gender"].get(i) == "femme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Très bon état" or etat == "Very good" or etat == "Muito bom" or etat == "Muy bueno":
            if brand == "Luxe" :
                women_meansTB[0] += df["price"].get(i)
                women_countTB[0] += 1
            elif brand == "Premium" :
                women_meansTB[1] += df["price"].get(i)
                women_countTB[1] += 1
            elif brand == "Sport" :
                women_meansTB[2] += df["price"].get(i)
                women_countTB[2] += 1
            elif brand == "Mass Market" :
                women_meansTB[3] += df["price"].get(i)
                women_countTB[3] += 1
            elif brand == "Discount" :
                women_meansTB[4] += df["price"].get(i)
                women_countTB[4] += 1
            else : 
                women_meansTB[5] += df["price"].get(i)
                women_countTB[5] += 1
    if df["gender"].get(i) == "homme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Très bon état" or etat == "Very good" or etat == "Muito bom" or etat == "Muy bueno":
            if brand == "Luxe" :
                men_meansTB[0] += df["price"].get(i)
                men_countTB[0] += 1
            elif brand == "Premium" :
                men_meansTB[1] += df["price"].get(i)
                men_countTB[1] += 1
            elif brand == "Sport" :
                men_meansTB[2] += df["price"].get(i)
                men_countTB[2] += 1
            elif brand == "Mass Market" :
                men_meansTB[3] += df["price"].get(i)
                men_countTB[3] += 1
            elif brand == "Discount" :
                men_meansTB[4] += df["price"].get(i)
                men_countTB[4] += 1
            else : 
                men_meansTB[5] += df["price"].get(i)
                men_countTB[5] += 1

for i in range (n) :
    if df["gender"].get(i) == "femme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Bon état" or etat == "Good" or etat == "Bom" or etat == "Bueno":
            if brand == "Luxe" :
                women_meansB[0] += df["price"].get(i)
                women_countB[0] += 1
            elif brand == "Premium" :
                women_meansB[1] += df["price"].get(i)
                women_countB[1] += 1
            elif brand == "Sport" :
                women_meansB[2] += df["price"].get(i)
                women_countB[2] += 1
            elif brand == "Mass Market" :
                women_meansB[3] += df["price"].get(i)
                women_countB[3] += 1
            elif brand == "Discount" :
                women_meansB[4] += df["price"].get(i)
                women_countB[4] += 1
            else : 
                women_meansB[5] += df["price"].get(i)
                women_countB[5] += 1
    if df["gender"].get(i) == "homme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Bon état" or etat == "Good" or etat == "Bom" or etat == "Bueno":
            if brand == "Luxe" :
                men_meansB[0] += df["price"].get(i)
                men_countB[0] += 1
            elif brand == "Premium" :
                men_meansB[1] += df["price"].get(i)
                men_countB[1] += 1
            elif brand == "Sport" :
                men_meansB[2] += df["price"].get(i)
                men_countB[2] += 1
            elif brand == "Mass Market" :
                men_meansB[3] += df["price"].get(i)
                men_countB[3] += 1
            elif brand == "Discount" :
                men_meansB[4] += df["price"].get(i)
                men_countB[4] += 1
            else : 
                men_meansB[5] += df["price"].get(i)
                men_countB[5] += 1

for i in range (n) :
    if df["gender"].get(i) == "femme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Satisfaisant" or etat == "Satisfactory" or etat == "Satisfatório" or etat == "Satisfactorio":
            if brand == "Luxe" :
                women_meansS[0] += df["price"].get(i)
                women_countS[0] += 1
            elif brand == "Premium" :
                women_meansS[1] += df["price"].get(i)
                women_countS[1] += 1
            elif brand == "Sport" :
                women_meansS[2] += df["price"].get(i)
                women_countS[2] += 1
            elif brand == "Mass Market" :
                women_meansS[3] += df["price"].get(i)
                women_countS[3] += 1
            elif brand == "Discount" :
                women_meansS[4] += df["price"].get(i)
                women_countS[4] += 1
            else : 
                women_meansS[5] += df["price"].get(i)
                women_countS[5] += 1
    if df["gender"].get(i) == "homme" :
        brand = ac.classify_brand(df["brand"].get(i))
        etat = df["status"].get(i)
        if etat == "Satisfaisant" or etat == "Satisfactory" or etat == "Satisfatório" or etat == "Satisfactorio":
            if brand == "Luxe" :
                men_meansS[0] += df["price"].get(i)
                men_countS[0] += 1
            elif brand == "Premium" :
                men_meansS[1] += df["price"].get(i)
                men_countS[1] += 1
            elif brand == "Sport" :
                men_meansS[2] += df["price"].get(i)
                men_countS[2] += 1
            elif brand == "Mass Market" :
                men_meansS[3] += df["price"].get(i)
                men_countS[3] += 1
            elif brand == "Discount" :
                men_meansS[4] += df["price"].get(i)
                men_countS[4] += 1
            else : 
                men_meansS[5] += df["price"].get(i)
                men_countS[5] += 1

for i in range (n) :
    if df["gender"].get(i) == "femme" :
        brand = ac.classify_brand(df["brand"].get(i))
        if brand == "Luxe" :
            women_means[0] += df["price"].get(i)
            women_count[0] += 1
        elif brand == "Premium" :
            women_means[1] += df["price"].get(i)
            women_count[1] += 1
        elif brand == "Sport" :
            women_means[2] += df["price"].get(i)
            women_count[2] += 1
        elif brand == "Mass Market" :
            women_means[3] += df["price"].get(i)
            women_count[3] += 1
        elif brand == "Discount" :
            women_means[4] += df["price"].get(i)
            women_count[4] += 1
        else : 
            women_means[5] += df["price"].get(i)
            women_count[5] += 1
    if df["gender"].get(i) == "homme" :
        brand = ac.classify_brand(df["brand"].get(i))
        if brand == "Luxe" :
            men_means[0] += df["price"].get(i)
            men_count[0] += 1
        elif brand == "Premium" :
            men_means[1] += df["price"].get(i)
            men_count[1] += 1
        elif brand == "Sport" :
            men_means[2] += df["price"].get(i)
            men_count[2] += 1
        elif brand == "Mass Market" :
            men_means[3] += df["price"].get(i)
            men_count[3] += 1
        elif brand == "Discount" :
            men_means[4] += df["price"].get(i)
            men_count[4] += 1
        else : 
            men_means[5] += df["price"].get(i)
            men_count[5] += 1

for i in range (6) :
    men_means[i] = men_means[i]/men_count[i]
    women_means[i] = women_means[i]/women_count[i]
    men_meansNWT[i] = men_meansNWT[i]/men_countNWT[i]
    women_meansNWT[i] = women_meansNWT[i]/women_countNWT[i]
    men_meansNST[i] = men_meansNST[i]/men_countNST[i]
    women_meansNST[i] = women_meansNST[i]/women_countNST[i]
    men_meansTB[i] = men_meansTB[i]/men_countTB[i]
    women_meansTB[i] = women_meansTB[i]/women_countTB[i]
    men_meansB[i] = men_meansB[i]/men_countB[i]
    women_meansB[i] = women_meansB[i]/women_countB[i]
    men_meansS[i] = men_meansS[i]/men_countS[i]
    women_meansS[i] = women_meansS[i]/women_countS[i]

mat = np.zeros((12,12))

for i in range (6) :
    mat[0][i] = men_meansNWT[i]
    mat[0][2*i] = men_countNWT[i]
    mat[2][i] = men_meansNST[i]
    mat[2][2*i] = men_countNST[i]
    mat[4][i] = men_meansTB[i]
    mat[4][2*i] = men_countTB[i]
    mat[6][i] = men_meansB[i]
    mat[6][2*i] = men_countB[i]
    mat[8][i] = men_meansS[i]
    mat[8][2*i] = men_countS[i]
    mat[10][i] = men_means[i]
    mat[10][2*i] = men_count[i]
    mat[1][i] = women_meansNWT[i]
    mat[1][2*i] = women_countNWT[i]
    mat[3][i] = women_meansNST[i]
    mat[3][2*i] = women_countNST[i]
    mat[5][i] = women_meansTB[i]
    mat[5][2*i] = women_countTB[i]
    mat[7][i] = women_meansB[i]
    mat[7][2*i] = women_countB[i]
    mat[9][i] = women_meansS[i]
    mat[9][2*i] = women_countS[i]
    mat[11][i] = women_means[i]
    mat[11][2*i] = women_count[i]

np.transpose(mat)
# 2. Convertissez-la en DataFrame Pandas
df = pd.DataFrame(mat)

# 3. Copiez-la dans votre presse-papier
# index=False et header=False évitent de copier les numéros de lignes/colonnes
print(df.to_csv(sep='\t', index=False, header=False))