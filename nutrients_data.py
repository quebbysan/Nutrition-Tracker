# Reference data for every trackable nutrient.
# Each entry is (key, display_label, unit).
# Units follow current USDA/FDA labeling convention:
#   g   = grams
#   mg  = milligrams
#   mcg = micrograms (µg)
# Vitamin A and D are given in mcg (modern standard) rather than the
# older IU; 1 mcg RAE Vitamin A ≈ 3.33 IU, 1 mcg Vitamin D ≈ 40 IU,
# in case you ever need to convert from an old-style label.

NUTRIENT_CATEGORIES = {
    "Electrolytes & Macrominerals": [
        ("potassium", "Potassium", "mg"),
        ("sodium", "Sodium", "mg"),
        ("chloride", "Chloride", "mg"),
        ("calcium", "Calcium", "mg"),
        ("phosphorus", "Phosphorus", "mg"),
        ("magnesium", "Magnesium", "mg"),
    ],
    "Fat-Soluble Vitamins": [
        ("vitamin_a", "Vitamin A (Retinol/Beta-Carotene)", "mcg"),
        ("vitamin_d", "Vitamin D (Calciferol)", "mcg"),
        ("vitamin_e", "Vitamin E (Tocopherol)", "mg"),
        ("vitamin_k", "Vitamin K (Phylloquinone/Menaquinone)", "mcg"),
    ],
    "Water-Soluble Vitamins": [
        ("vitamin_b1", "Vitamin B1 (Thiamine)", "mg"),
        ("vitamin_b2", "Vitamin B2 (Riboflavin)", "mg"),
        ("vitamin_b3", "Vitamin B3 (Niacin)", "mg"),
        ("vitamin_b5", "Vitamin B5 (Pantothenic Acid)", "mg"),
        ("vitamin_b6", "Vitamin B6 (Pyridoxine)", "mg"),
        ("vitamin_b7", "Vitamin B7 (Biotin)", "mcg"),
        ("vitamin_b9", "Vitamin B9 (Folate/Folic Acid)", "mcg"),
        ("vitamin_b12", "Vitamin B12 (Cobalamin)", "mcg"),
        ("vitamin_c", "Vitamin C (Ascorbic Acid)", "mg"),
    ],
    "Trace Minerals": [
        ("iron", "Iron", "mg"),
        ("zinc", "Zinc", "mg"),
        ("iodine", "Iodine", "mcg"),
        ("selenium", "Selenium", "mcg"),
        ("copper", "Copper", "mg"),
        ("manganese", "Manganese", "mg"),
        ("fluoride", "Fluoride", "mg"),
        ("chromium", "Chromium", "mcg"),
    ],
    "Essential Amino Acids": [
        ("histidine", "Histidine", "g"),
        ("isoleucine", "Isoleucine", "g"),
        ("leucine", "Leucine", "g"),
        ("lysine", "Lysine", "g"),
        ("methionine", "Methionine", "g"),
        ("phenylalanine", "Phenylalanine", "g"),
        ("threonine", "Threonine", "g"),
        ("tryptophan", "Tryptophan", "g"),
        ("valine", "Valine", "g"),
    ],
    "Essential Fatty Acids": [
        ("omega_3", "Omega-3 (Alpha-linolenic acid)", "g"),
        ("omega_6", "Omega-6 (Linoleic acid)", "g"),
    ],
    # Carbs, Protein, and Total Fat live on the main form already —
    # this category is the more granular breakdown of those.
    "Carb & Fat Detail": [
        ("dietary_fiber", "Dietary Fiber", "g"),
        ("total_sugars", "Total Sugars", "g"),
        ("added_sugars", "Added Sugars", "g"),
        ("saturated_fat", "Saturated Fats", "g"),
        ("trans_fat", "Trans Fats", "g"),
        ("monounsaturated_fat", "Monounsaturated Fats", "g"),
        ("polyunsaturated_fat", "Polyunsaturated Fats", "g"),
        ("cholesterol", "Cholesterol", "mg"),
    ],
}

# Flat lookup: key -> (label, unit), built from the categories above.
NUTRIENT_LOOKUP = {
    key: (label, unit)
    for nutrients in NUTRIENT_CATEGORIES.values()
    for key, label, unit in nutrients
}
