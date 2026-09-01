import streamlit as st
import pandas as pd
from datetime import date

import nutrition_tracker as nt

st.set_page_config(page_title="Nutrition Tracker", page_icon="🥗", layout="centered")
st.title("🥗 Nutrition Tracker")
st.write("Track your daily calories and macros")

today = str(date.today())

# --- Input Form ---
with st.form("meal_form", clear_on_submit=True):
    st.subheader("Add a Meal")

    meal_name = st.text_input("Food / Meal name")
    calories = st.number_input("Calories", min_value=0, step=10)
    protein = st.number_input("Protein (g)", min_value=0.0, step=1.0)
    carbs = st.number_input("Carbs (g)", min_value=0.0, step=1.0)
    fat = st.number_input("Fat (g)", min_value=0.0, step=1.0)

    submitted = st.form_submit_button("Add Meal")

    if submitted and meal_name:
        nt.add_meal(meal_name, calories, protein, carbs, fat, today)
        st.success(f"Added: {meal_name}")

# --- Daily Summary ---
rows = nt.get_meals(today)

if rows:
    df = pd.DataFrame(
        rows, columns=["date", "meal", "calories", "protein", "carbs", "fat"]
    )

    st.subheader("Today's Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calories", f"{df['calories'].sum():.0f}")
    col2.metric("Protein", f"{df['protein'].sum():.1f}g")
    col3.metric("Carbs", f"{df['carbs'].sum():.1f}g")
    col4.metric("Fat", f"{df['fat'].sum():.1f}g")

    st.subheader("Meal Log")
    st.dataframe(df, use_container_width=True)

    if st.button("Clear all meals"):
        nt.clear_meals(today)
        st.rerun()
else:
    st.info("No meals logged yet. Add your first meal above!")
