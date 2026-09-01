import streamlit as st
import pandas as pd
from datetime import date

import nutrition_tracker as nt
from nutrients_data import NUTRIENT_CATEGORIES, NUTRIENT_LOOKUP

st.set_page_config(page_title="Nutrition Tracker", page_icon="🥗", layout="centered")
st.title("🥗 Nutrition Tracker")
st.write("Track your daily calories, macros, and micronutrients")

today = str(date.today())

# --- Input Form ---
with st.form("meal_form", clear_on_submit=True):
    st.subheader("Add a Meal")

    meal_name = st.text_input("Food / Meal name")
    calories = st.number_input("Calories", min_value=0, step=10)
    protein = st.number_input("Protein (g)", min_value=0.0, step=1.0)
    carbs = st.number_input("Carbs (g)", min_value=0.0, step=1.0)
    fat = st.number_input("Total Fat (g)", min_value=0.0, step=1.0)

    st.caption("Optional: add specific nutrients below. Leave anything at 0 to skip it.")

    # Build one number_input per nutrient, grouped in collapsible sections,
    # keyed uniquely so Streamlit can tell 60+ fields apart.
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
        meal_id = nt.add_meal(meal_name, calories, protein, carbs, fat, today)
        nt.add_nutrients(meal_id, nutrient_inputs)
        st.success(f"Added: {meal_name}")

# --- Daily Summary ---
rows = nt.get_meals(today)

if rows:
    df = pd.DataFrame(
        rows, columns=["id", "date", "meal", "calories", "protein", "carbs", "fat"]
    )

    st.subheader("Today's Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calories", f"{df['calories'].sum():.0f}")
    col2.metric("Protein", f"{df['protein'].sum():.1f}g")
    col3.metric("Carbs", f"{df['carbs'].sum():.1f}g")
    col4.metric("Fat", f"{df['fat'].sum():.1f}g")

    st.subheader("Meal Log")
    st.dataframe(
        df.drop(columns=["id"]), use_container_width=True
    )

    # Micronutrient totals, only shown for nutrients that were actually logged.
    totals = nt.get_daily_nutrient_totals(today)
    if totals:
        st.subheader("Micronutrient Totals")
        for category, nutrients in NUTRIENT_CATEGORIES.items():
            logged = [(k, l, u) for k, l, u in nutrients if k in totals]
            if not logged:
                continue
            with st.expander(f"{category} ({len(logged)} logged)"):
                for key, label, unit in logged:
                    st.write(f"**{label}:** {totals[key]:.2f} {unit}")

    if st.button("Clear all meals"):
        nt.clear_meals(today)
        st.rerun()
else:
    st.info("No meals logged yet. Add your first meal above!")
