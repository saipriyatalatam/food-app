import random
import numpy as np
import time
from itertools import combinations
from scipy.spatial.distance import euclidean, cdist
from tabulate import tabulate
from django.db.models import F
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from .models import FoodItem
from django.conf import settings

SIMILARITY_MATRIX = None


#Data Preprocessing
def preprocess_data(data):
    data = data.fillna(0)


    def clean_value(value):
        if isinstance(value, str):
            if 'x' in value:
                return 0
            if '±' in value:
                value = value.split('±')[0]
            try:
                return float(value)
            except ValueError:
                return 0
        return value

    data['Food Group'] = data['Food Group'].astype(str)
    data['FoodName'] = data['FoodName'].astype(str)
    numeric_columns = data.columns[3:-2]

    for column in numeric_columns:
        data[column] = data[column].apply(clean_value)

    scaler = MinMaxScaler(feature_range=(0, 10))
    data.loc[:, numeric_columns] = scaler.fit_transform(data[numeric_columns])

    if 'Estimated Price (INR per kg/liter)' in data.columns:
        price_scaler = MinMaxScaler(feature_range=(0, 10))
        data['Estimated Price (INR per kg/liter)'] = price_scaler.fit_transform(data[['Estimated Price (INR per kg/liter)']])

    return data


#Load the processed data to DB
def load_csv_to_db(csv_path):
    df = pd.read_csv(csv_path)
    df = df.drop_duplicates().reset_index(drop=True)
    df = preprocess_data(df)  #Calling the preprocessing function
    df = df[df['code']!=0]  
    print(df.columns)

    #Extract the data and load to DB
    for _, row in df.iterrows():
        print(row['code'])
        FoodItem.objects.update_or_create(
            code=row['code'],
            food_name=row['FoodName'],
            food_group=row['Food Group'],
            defaults={
                'doh25': row.get('25-OH-D3 [ug]'),
                'crypxb': row.get('?-Cryptoxanthin [ug]'),
                'ala': row.get('Alanine [g]'),
                'al': row.get('Aluminium (Al) [mg]'),
                'apigen': row.get('Apigenin [mg]'),
                'apigen7onshps': row.get('Apigenin-7-O-neohesperidoside [mg]'),
                'f20d0': row.get('Arachidic (C20:0) [mg]'),
                'arg': row.get('Arginine [g]'),
                'as_1': row.get('Arsenic (As) [ug]'),
                'f22d0': row.get('Behenic (C22:0) [mg]'),
                'cd': row.get('Cadmium (Cd) [mg]'),
                'carbs': row.get('Carbs'),
                'cholc': row.get('Cholesterol [mg]'),
                'co': row.get('Cobalt (Co) [mg]'),
                'f22d5n3': row.get('Docosa pentaenoic (C22:5n3) [mg]'),
                'f20d1_n9f': row.get('Eicosaenoic (C20:1n9) [mg]'),
                'f20d3n6': row.get('Eicosatrienoic (C20:3n6) [mg]'),
                'enerc': row.get('Energy [kJ]'),
                'fumac': row.get('Fumaric Acid [mg]'),
                'gallac': row.get('Gallic acid [mg]'),
                'glus': row.get('Glucose [g]'),
                'glu': row.get('Glutamic Acid [g]'),
                'gly': row.get('Glycine [g]'),
                'his': row.get('Histidine [g]'),
                'fe': row.get('Iron (Fe) [mg]'),
                'ile': row.get('Isoleucine [g]'),
                'f12d0': row.get('Lauric (C12:0) [mg]'),
                'pb': row.get('Lead (Pb) [mg]'),
                'tf18d2cn6': row.get('Linoleic (C18:2n6) [%]'),
                'f18d2cn6': row.get('Linoleic (C18:2n6) [mg]'),
                'li': row.get('Lithium (Li) [mg]'),
                'malac': row.get('Malic Acid [mg]'),
                'mn': row.get('Manganese (Mn) [mg]'),
                'vitk2': row.get('Menaquinones (K2) [ug]'),
                'hg': row.get('Mercury (Hg) [ug]'),
                'met': row.get('Methionine [g]'),
                'water': row.get('Moisture [g]'),
                'mo': row.get('Molybdenum (Mo) [mg]'),
                'f14d0': row.get('Myristic (C14:0) [mg]'),
                'f24d1_c': row.get('Nervonic (C24:1n9) [mg]'),
                'ni': row.get('Nickel (Ni) [mg]'),
                'rafs': row.get('Oligosaccharides - Raffinose [g]'),
                'oxals': row.get('Oxalate-Soluble [mg]'),
                'tf16d0': row.get('Palmitic (C16:0) [%]'),
                'f16d0': row.get('Palmitic (C16:0) [mg]'),
                'tf16d1c': row.get('Palmitoleic (C16:1) [%]'),
                'pantac': row.get('Pantothenic Acid (B5) [mg]'),
                'f15d0': row.get('Pentadecanoic (C15:0) [mg]'),
                'phe': row.get('Phenylalanine [g]'),
                'p': row.get('Phophorus (P) [mg]'),
                'camt': row.get('Phytosterols - Campesterol [mg]'),
                'proteins': row.get('Proteins'),
                'pcathac': row.get('Protocatechuic acid [mg]'),
                'querce3ortns': row.get('Quercetin-3-O-rutinoside [mg]'),
                'retol': row.get('Retinol [ug]'),
                'ribf': row.get('Riboflavin (B2) [mg]'),
                'sucs': row.get('Sucrose [g]'),
                'thia': row.get('Thiamine(B1) [mg]'),
                'thr': row.get('Threonine [g]'),
                'tocpha': row.get('Tocopherols (Alpha) [mg]'),
                'tocphb': row.get('Tocopherols (Beta) [mg]'),
                'toctrb': row.get('Tocotrienols (Beta) [mg]'),
                'cho': row.get('Total Available CHO [g]'),
                'cartoid': row.get('Total Carotenoids [ug]'),
                'folsum': row.get('Total Folates (B9) [ug]'),
                'fapu': row.get('Total Poly Unsaturated Fatty Acids (TPUFA) [mg]'),
                'fasat': row.get('Total Saturated Fatty Acids (TSFA) [mg]'),
                'starch': row.get('Total Starch [g]'),
                'trp': row.get('Tryptophan [g]'),
                'zn': row.get('Zinc (Zn) [mg]'),
                'estimated_price': row.get('Estimated Price (INR per kg/liter)'),
            }
        )


def get_recommendations(input_food, selected_features=settings.SELECTED_FEATURES, top_n=10):
    """
    Generate 3-food recommendations for a given input food item using selected features.

    Parameters:
        input_food (str): Food name to generate recommendations for.
        selected_features (list): List of exactly 70 feature column names to be used.
        top_n (int): Number of top similar items to consider for subset combinations.

    Returns:
        dict: A dictionary containing the best recommended subsets and their scores.
    """
    # Convert FoodItem objects to DataFrame
    food_items = FoodItem.objects.all()
    data = []
    for item in food_items:
        row = {
            'FoodName': item.food_name,
            'Food Group': item.food_group,
            'Estimated Price (INR per kg/liter)': item.estimated_price or 0,
            '25-OH-D3 [ug]': item.doh25 or 0,
            '?-Cryptoxanthin [ug]': item.crypxb or 0,
            'Alanine [g]': item.ala or 0,
            'Aluminium (Al) [mg]': item.al or 0,
            'Apigenin [mg]': item.apigen or 0,
            'Apigenin-7-O-neohesperidoside [mg]': item.apigen7onshps or 0,
            'Arachidic (C20:0) [mg]': item.f20d0 or 0,
            'Arginine [g]': item.arg or 0,
            'Arsenic (As) [ug]': item.as_1 or 0,
            'Behenic (C22:0) [mg]': item.f22d0 or 0,
            'Cadmium (Cd) [mg]': item.cd or 0,
            'Carbs': item.carbs or 0,
            'Cholesterol [mg]': item.cholc or 0,
            'Cobalt (Co) [mg]': item.co or 0,
            'Docosa pentaenoic (C22:5n3) [mg]': item.f22d5n3 or 0,
            'Eicosaenoic (C20:1n9) [mg]': item.f20d1_n9f or 0,
            'Eicosatrienoic (C20:3n6) [mg]': item.f20d3n6 or 0,
            'Energy [kJ]': item.enerc or 0,
            'Fumaric Acid [mg]': item.fumac or 0,
            'Gallic acid [mg]': item.gallac or 0,
            'Glucose [g]': item.glus or 0,
            'Glutamic Acid [g]': item.glu or 0,
            'Glycine [g]': item.gly or 0,
            'Histidine [g]': item.his or 0,
            'Iron (Fe) [mg]': item.fe or 0,
            'Isoleucine [g]': item.ile or 0,
            'Lauric (C12:0) [mg]': item.f12d0 or 0,
            'Lead (Pb) [mg]': item.pb or 0,
            'Linoleic (C18:2n6) [%]': item.tf18d2cn6 or 0,
            'Linoleic (C18:2n6) [mg]': item.f18d2cn6 or 0,
            'Lithium (Li) [mg]': item.li or 0,
            'Malic Acid [mg]': item.malac or 0,
            'Manganese (Mn) [mg]': item.mn or 0,
            'Menaquinones (K2) [ug]': item.vitk2 or 0,
            'Mercury (Hg) [ug]': item.hg or 0,
            'Methionine [g]': item.met or 0,
            'Moisture [g]': item.water or 0,
            'Molybdenum (Mo) [mg]': item.mo or 0,
            'Myristic (C14:0) [mg]': item.f14d0 or 0,
            'Nervonic (C24:1n9) [mg]': item.f24d1_c or 0,
            'Nickel (Ni) [mg]': item.ni or 0,
            'Oligosaccharides - Raffinose [g]': item.rafs or 0,
            'Oxalate-Soluble [mg]': item.oxals or 0,
            'Palmitic (C16:0) [%]': item.tf16d0 or 0,
            'Palmitic (C16:0) [mg]': item.f16d0 or 0,
            'Palmitoleic (C16:1) [%]': item.tf16d1c or 0,
            'Pantothenic Acid (B5) [mg]': item.pantac or 0,
            'Pentadecanoic (C15:0) [mg]': item.f15d0 or 0,
            'Phenylalanine [g]': item.phe or 0,
            'Phophorus (P) [mg]': item.p or 0,
            'Phytosterols - Campesterol [mg]': item.camt or 0,
            'Proteins': item.proteins or 0,
            'Protocatechuic acid [mg]': item.pcathac or 0,
            'Quercetin-3-O-rutinoside [mg]': item.querce3ortns or 0,
            'Retinol [ug]': item.retol or 0,
            'Riboflavin (B2) [mg]': item.ribf or 0,
            'Sucrose [g]': item.sucs or 0,
            'Thiamine(B1) [mg]': item.thia or 0,
            'Threonine [g]': item.thr or 0,
            'Tocopherols (Alpha) [mg]': item.tocpha or 0,
            'Tocopherols (Beta) [mg]': item.tocphb or 0,
            'Tocotrienols (Beta) [mg]': item.toctrb or 0,
            'Total Available CHO [g]': item.cho or 0,
            'Total Carotenoids [ug]': item.cartoid or 0,
            'Total Folates (B9) [ug]': item.folsum or 0,
            'Total Poly Unsaturated Fatty Acids (TPUFA) [mg]': item.fapu or 0,
            'Total Saturated Fatty Acids (TSFA) [mg]': item.fasat or 0,
            'Total Starch [g]': item.starch or 0,
            'Tryptophan [g]': item.trp or 0,
            'Zinc (Zn) [mg]': item.zn or 0,
        }
        data.append(row)
    df = pd.DataFrame(data)

    # Step 1: Compute similarity matrix using only selected 70 features
    global SIMILARITY_MATRIX
    if SIMILARITY_MATRIX is None:
        nutrient_vectors = df[selected_features].values
        SIMILARITY_MATRIX = cdist(nutrient_vectors, nutrient_vectors, metric='euclidean')
    similarity_matrix = SIMILARITY_MATRIX

    # Step 2: Recommend foods (excluding those with same starting name word)
    def recommend_foods(df, similarity_matrix, top_n):
        recommendations = []
        for i, food_name in enumerate(df['FoodName']):
            food_first_word = str(food_name).split()[0].lower()
            similar_indices = np.argsort(similarity_matrix[i])
            substitutes = []

            for idx in similar_indices:
                if idx == i:
                    continue
                substitute_name = str(df.iloc[idx]['FoodName'])
                substitute_first_word = substitute_name.split()[0].lower()
                if substitute_first_word != food_first_word:
                    substitutes.append(substitute_name)
                if len(substitutes) == top_n:
                    break

            recommendations.append([food_name, '; '.join(substitutes)])
        return recommendations

    top_10_recommendations = recommend_foods(df, similarity_matrix, top_n=top_n)
    top_10_dict = {row[0]: row[1].split("; ") for row in top_10_recommendations}

    # Step 3: Create 3-food subsets for the input food
    if input_food not in top_10_dict:
        raise ValueError(f"'{input_food}' not found or no valid recommendations.")

    recommendations = top_10_dict[input_food]
    if len(recommendations) < 3:
        raise ValueError(f"Not enough recommendations for '{input_food}' to build subsets.")

    unique_subsets = list(combinations(recommendations, 3))
    all_food_subsets = {input_food: [[f"Subset {i+1}", *subset] for i, subset in enumerate(unique_subsets)]}

    # Step 4: Score all subsets
    best_recommendations = []
    numeric_columns = selected_features

    for food_item, subsets in all_food_subsets.items():
        ed_results, diversity_results, cost_results, relevance_scores = [], [], [], []

        input_vector = df.loc[df['FoodName'] == food_item, numeric_columns].values.flatten()

        for subset in subsets:
            subset_name, item1, item2, item3 = subset
            subset_items = [item1, item2, item3]

            # ED Score
            distances = [
                euclidean(df.loc[df['FoodName'] == item, numeric_columns].values.flatten(), input_vector)
                for item in subset_items
                if not df.loc[df['FoodName'] == item, numeric_columns].empty
            ]
            ed_score = np.mean(distances) if distances else 0
            ed_results.append(ed_score)

            # Diversity Score
            food_groups = df.loc[df['FoodName'].isin(subset_items), 'Food Group']
            diversity_count = len(food_groups.unique())
            diversity_score = diversity_count + np.prod([count/3 for count in food_groups.value_counts().values])
            diversity_results.append(diversity_score)

            # Cost Score
            prices = df.loc[df['FoodName'].isin(subset_items), 'Estimated Price (INR per kg/liter)'].values
            cost_score = np.mean(prices) if len(prices) > 0 else 0
            cost_results.append(cost_score)

            # Relevance Score
            relevance_score = (ed_score + cost_score) / diversity_score if diversity_score > 0 else 0
            relevance_scores.append(relevance_score)

        # Step 5: Select best subset
        best_index = np.argmin(relevance_scores)
        best_subset = subsets[best_index]
        best_recommendations.append([
            food_item,
            *best_subset,
            ed_results[best_index],
            diversity_results[best_index],
            cost_results[best_index],
            relevance_scores[best_index]
        ])

    return {
        "input_food": input_food,
        "best_recommendation": best_recommendations
    }