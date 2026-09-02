"""
Food health-tier scoring, based on the user's own tier list.

Each tier is given the midpoint of its stated range (e.g. "90-100" -> 95).
Matching is done by checking whether a keyword appears anywhere in the
food's name, checked worst-tier-first so a specific/dangerous match
(e.g. "seed oil") is never accidentally caught by a broader, better-tier
keyword (e.g. "seeds") lower down the list.

Feel free to add/edit keywords or score values below — this is the one
file that defines the entire scoring system.

SCORING RULE (this is one reasonable reading of your instructions —
adjust the math in compute_meal_health_score() if you meant something
different):
  - If every matched food in a meal is tier 50+, the meal score is the
    average of those foods' scores.
  - Each matched food BELOW tier 50 knocks a percentage off that
    baseline: (50 - food_score) / 50. A tier-45 food barely dents it
    (10%), a tier-5 food guts it (90%). These percentages stack across
    multiple low-tier foods, capped at a 95% total reduction.
"""

# (score, tier_label, [keywords]) — ordered worst tier first.
FOOD_TIERS = [
    (5, "0-10: Detrimental", [
        "chili oil", "seed oil", "soybean oil", "canola oil", "corn oil",
        "sunflower oil", "safflower oil", "vegetable oil",
        "ultra-processed", "ultra processed", "packaged snack", "cereal",
        "sugary drink", "refined sugar", "artificial sweetener",
        "aspartame", "splenda", "soda", "soft drink", "coke", "pepsi",
        "hot dog", "deli meat", "sausage", "salami", "pepperoni",
        "pastry", "donut", "doughnut", "cookie", "cake", "muffin",
        "beer", "wine", "vodka", "whiskey", "liquor", "alcohol",
    ]),
    (15, "10-20: Poor", [
        "egg white", "broccoli", "cauliflower", "brussels sprout",
        "cabbage", "oatmeal", "oats", "whole wheat", "refined grain",
        "lentil", "chickpea", "legume", "bean",
    ]),
    (35, "30-40: Less Optimal", [
        "coffee", "tofu", "vegetable", "nuts", "seeds", "almond",
        "walnut", "cashew", "peanut", "pistachio", "sunflower seed",
        "dragonfruit", "kiwi", "passionfruit", "persimmon", "pomegranate",
        "papaya", "lychee", "guava", "starfruit", "exotic fruit",
    ]),
    (55, "50-60: Acceptable", [
        "cheese", "tea", "extra virgin olive oil", "olive oil",
        "white rice", "pasteurized honey", "honey",
    ]),
    (75, "70-80: High Quality", [
        "liver", "heart", "kidney", "organ meat", "steak tartare",
        "raw ground beef", "fermented", "sauerkraut", "kimchi",
        "potato", "tomato", "pepper", "onion", "carrot", "green onion",
    ]),
    (95, "90-100: Optimal", [
        "beef", "pork", "chicken", "steak", "cooked egg", "egg yolk",
        "grass-fed butter", "butter", "tallow", "unpasteurized milk",
        "raw milk", "dairy", "milk", "wild-caught", "oyster", "fish",
        "salmon", "tuna", "shrimp", "seafood", "raw honey", "kefir",
        "apple", "banana", "orange", "grape", "strawberry", "blueberry",
        "raspberry", "peach", "pear", "watermelon", "cherry", "plum",
        "fruit",
    ]),
]


def score_single_food(food_name):
    """Returns (score, tier_label) for the first matching keyword, or
    (None, None) if the food isn't recognized."""
    name_lower = food_name.lower()
    for score, tier_label, keywords in FOOD_TIERS:
        for kw in keywords:
            if kw in name_lower:
                return score, tier_label
    return None, None


def compute_meal_health_score(food_items):
    """food_items: list of food name strings (e.g. ["grilled chicken",
    "white rice", "soda"]).

    Returns (final_score, breakdown) where breakdown is a list of
    (food_name, score, tier_label) for every food that was recognized.
    final_score is None if nothing in the list was recognized.
    """
    matched = []
    for item in food_items:
        item = item.strip()
        if not item:
            continue
        score, tier_label = score_single_food(item)
        if score is not None:
            matched.append((item, score, tier_label))

    if not matched:
        return None, []

    high_scores = [s for _, s, _ in matched if s >= 50]
    low_scores = [s for _, s, _ in matched if s < 50]

    baseline = sum(high_scores) / len(high_scores) if high_scores else 50.0

    if low_scores:
        total_reduction_pct = sum((50 - s) / 50 for s in low_scores)
        total_reduction_pct = min(total_reduction_pct, 0.95)
        final_score = baseline * (1 - total_reduction_pct)
    else:
        final_score = baseline

    final_score = round(max(0.0, min(100.0, final_score)), 1)
    return final_score, matched
