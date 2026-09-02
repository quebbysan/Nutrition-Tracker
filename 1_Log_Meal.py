import streamlit as st
import pandas as pd
from datetime import date

import nutrition_tracker as nt
from nutrients_data import NUTRIENT_CATEGORIES
from health_score import compute_meal_health_score

st.set_page_config(page_title="Log Meal", page_icon="✍️", layout="centered")
st.title("✍️ Manual Meal Entry")
st.write("For logging a meal by hand instead of using AI on the home screen.")

today = str(date.today())

with st.form("meal_form", clear_on_submit=True):
    st.subheader("Add a Meal")

    meal_name = st.text_input("Food / Meal name")
    food_items_raw = st.text_input(
        "Individual foods in this meal (comma separated)",
        placeholder="e.g. grilled chicken, white rice, broccoli",
        help="Used only to calculate the health score against your tier list.",
    )
    calories = st.number_input("Calories", min_value=0, step=10)
    protein = st.number_input("Protein (g)", min_value=0.0, step=1.0)
    carbs = st.number_input("Carbs (g)", min_value=0.0, step=1.0)
    fat = st.number_input("Total Fat (g)", min_value=0.0, step=1.0)

    st.caption("Optional: add specific nutrients below. Leave anything at 0 to skip it.")

    nutrient_inputs = {}
    for category, nutrients in NUTRIENT_CATEGORIES.items():
        with st.expander(category):
            for key, label, unit in nutrients:
                nutrient_inputs[key] = st.number_input(
                    f"{label} ({unit})",
                    min_value=0.0,
                    step=0.1,
                    key=f"nutrient_{key}",
                )

    submitted = st.form_submit_button("Add Meal")

    if submitted and meal_name:
        food_items = [f.strip() for f in food_items_raw.split(",") if f.strip()]
        health_score, breakdown = compute_meal_health_score(food_items)

        meal_id = nt.add_meal(
            meal_name, calories, protein, carbs, fat, today, health_score
        )
        nt.add_nutrients(meal_id, nutrient_inputs)

        if health_score is not None:
            st.success(f"Added: {meal_name} — Health Score: {health_score:.0f}")
        else:
            st.success(f"Added: {meal_name}")
            st.caption(
                "No recognized foods for scoring — list individual foods above "
                "(e.g. 'chicken, rice') to get a health score."
            )

# --- Today's meal log ---
rows = nt.get_meals(today)
if rows:
    df = pd.DataFrame(
        rows,
        columns=["id", "date", "meal", "calories", "protein", "carbs", "fat", "health_score"],
    )
    st.subheader("Today's Meal Log")
    st.dataframe(
        df.drop(columns=["id", "date"]).rename(columns={"health_score": "score"}),
        use_container_width=True,
    )
    if st.button("Clear all meals"):
        nt.clear_meals(today)
        st.rerun()
else:
    st.info("No meals logged yet today.")
