import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Nutrition Tracker", layout="centered")

st.title("Nutrition Tracker")
st.write("Track your daily calories and macros")

# Initialize session state for storing meals
if "meals" not in st.session_state:
    st.session_state.meals = []

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
        st.session_state.meals.append({
            "date": str(date.today()),
            "meal": meal_name,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        })
        st.success(f"Added: {meal_name}")

# --- Daily Summary ---
if st.session_state.meals:
    df = pd.DataFrame(st.session_state.meals)
    
    st.subheader("Today's Summary")
    total_calories = df["calories"].sum()
    total_protein = df["protein"].sum()
    total_carbs = df["carbs"].sum()
    total_fat = df["fat"].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calories", f"{total_calories:.0f}")
    col2.metric("Protein", f"{total_protein:.1f}g")
    col3.metric("Carbs", f"{total_carbs:.1f}g")
    col4.metric("Fat", f"{total_fat:.1f}g")
    
    st.subheader("Meal Log")
    st.dataframe(df, use_container_width=True)
    
    if st.button("Clear all meals"):
        st.session_state.meals = []
        st.rerun()
else:
    st.info("No meals logged yet. Add your first meal above!")
