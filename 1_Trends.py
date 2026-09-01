import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

import nutrition_tracker as nt
from nutrients_data import NUTRIENT_CATEGORIES

st.set_page_config(page_title="Nutrition Trends", page_icon="📊", layout="centered")

# --- Look & feel: dark navy background, bold Arial, colorful lines ---
DARK_BG = "#111827"
CARD_BG = "#1c2434"
GRID_COLOR = "#2d3748"
FONT_FAMILY = "Arial Black, Arial, sans-serif"

CAL_COLOR = "#FF6B6B"      # calories
PROTEIN_COLOR = "#A78BFA"  # protein
CARBS_COLOR = "#FB923C"    # carbs
FAT_COLOR = "#38BDF8"      # fat
SODIUM_COLOR = "#F4B33B"   # orange-yellow
POTASSIUM_COLOR = "#E6A8E0"  # light purple-pink

CATEGORY_COLORS = [
    "#F87171", "#FBBF24", "#34D399", "#60A5FA",
    "#A78BFA", "#F472B6", "#4ADE80", "#38BDF8",
]

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {DARK_BG}; }}
    h1, h2, h3, h4, p, .stMarkdown, .stMetric label, .stRadio label {{
        font-family: {FONT_FAMILY} !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: {FONT_FAMILY} !important;
        font-weight: 900 !important;
    }}
    .stat-card {{
        background-color: {CARD_BG};
        border-radius: 18px;
        padding: 20px 24px;
        margin-top: 12px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Nutrition Trends")

# --- Time range picker ---
range_choice = st.radio(
    "Time range",
    ["Last 7 Days", "Last 30 Days", "Last Year", "Custom"],
    horizontal=True,
)

today = date.today()
if range_choice == "Last 7 Days":
    start_date, end_date = today - timedelta(days=6), today
elif range_choice == "Last 30 Days":
    start_date, end_date = today - timedelta(days=29), today
elif range_choice == "Last Year":
    start_date, end_date = today - timedelta(days=364), today
else:
    picked = st.date_input(
        "Pick a range", value=(today - timedelta(days=6), today)
    )
    if isinstance(picked, tuple) and len(picked) == 2:
        start_date, end_date = picked
    else:
        start_date, end_date = today - timedelta(days=6), today

all_dates = list(pd.date_range(start_date, end_date).date)
x_labels = [f"{d.month}/{d.day}" for d in all_dates]


def base_layout(y1_title, y2_title=None):
    layout = dict(
        plot_bgcolor=DARK_BG,
        paper_bgcolor=DARK_BG,
        font=dict(family=FONT_FAMILY, color="white", size=13),
        legend=dict(orientation="h", y=-0.25, font=dict(size=13)),
        margin=dict(t=20, b=20, l=10, r=10),
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(title=y1_title, gridcolor=GRID_COLOR),
    )
    if y2_title:
        layout["yaxis2"] = dict(
            title=y2_title, overlaying="y", side="right", gridcolor=GRID_COLOR
        )
    return layout


# =========================================================
# MACRONUTRIENTS
# =========================================================
st.header("Macronutrients")

macro_rows = nt.get_daily_macro_totals(str(start_date), str(end_date))
macro_by_date = {r[0]: r for r in macro_rows}

cal, prot, carb, fat = [], [], [], []
for d in all_dates:
    row = macro_by_date.get(str(d))
    _, c, p, cb, f = row if row else (None, 0, 0, 0, 0)
    cal.append(c or 0)
    prot.append(p or 0)
    carb.append(cb or 0)
    fat.append(f or 0)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x_labels, y=cal, name="Calories", yaxis="y2",
    line=dict(color=CAL_COLOR, dash="dash", width=3),
    marker=dict(size=6),
))
fig.add_trace(go.Scatter(
    x=x_labels, y=prot, name="Protein",
    line=dict(color=PROTEIN_COLOR, width=3),
))
fig.add_trace(go.Scatter(
    x=x_labels, y=carb, name="Carbs",
    line=dict(color=CARBS_COLOR, width=3),
))
fig.add_trace(go.Scatter(
    x=x_labels, y=fat, name="Fat",
    line=dict(color=FAT_COLOR, width=3),
))
fig.update_layout(**base_layout("grams (g)", "Calories (cal)"))
st.plotly_chart(fig, use_container_width=True)

n_days = max(len(all_dates), 1)
st.markdown('<div class="stat-card">', unsafe_allow_html=True)
st.caption(f"📅 {n_days}-Day Average")
c1, c2 = st.columns(2)
c1.metric("Calories", f"{sum(cal)/n_days:.0f}", help=f"Max: {max(cal):.0f}" if cal else None)
c2.metric("Protein", f"{sum(prot)/n_days:.0f}g", help=f"Max: {max(prot):.0f}g" if prot else None)
c3, c4 = st.columns(2)
c3.metric("Carbs", f"{sum(carb)/n_days:.0f}g", help=f"Max: {max(carb):.0f}g" if carb else None)
c4.metric("Fat", f"{sum(fat)/n_days:.0f}g", help=f"Max: {max(fat):.0f}g" if fat else None)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# SODIUM : POTASSIUM
# =========================================================
st.header("Sodium : Potassium")

nutrient_by_date = nt.get_daily_nutrient_totals_range(str(start_date), str(end_date))
sodium, potassium = [], []
for d in all_dates:
    day_vals = nutrient_by_date.get(str(d), {})
    sodium.append(day_vals.get("sodium", 0))
    potassium.append(day_vals.get("potassium", 0))

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=x_labels, y=sodium, name="Sodium",
    line=dict(color=SODIUM_COLOR, width=3), fill="tozeroy",
    fillcolor="rgba(244,179,59,0.15)",
))
fig2.add_trace(go.Scatter(
    x=x_labels, y=potassium, name="Potassium",
    line=dict(color=POTASSIUM_COLOR, width=3), fill="tozeroy",
    fillcolor="rgba(230,168,224,0.15)",
))
fig2.update_layout(**base_layout("mg"))
st.plotly_chart(fig2, use_container_width=True)

total_sodium, total_potassium = sum(sodium), sum(potassium)
st.markdown('<div class="stat-card">', unsafe_allow_html=True)
if total_potassium > 0:
    ratio = total_sodium / total_potassium
    st.metric("Average Sodium : Potassium Ratio", f"{ratio:.2f} : 1")
else:
    st.caption("Log sodium and potassium to see your ratio here.")
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# OTHER MICRONUTRIENTS (by category)
# =========================================================
st.header("Micronutrients")

category_names = [c for c in NUTRIENT_CATEGORIES if c != "Carb & Fat Detail"]
selected_category = st.selectbox("Category", category_names)

fig3 = go.Figure()
any_data = False
for i, (key, label, unit) in enumerate(NUTRIENT_CATEGORIES[selected_category]):
    series = [nutrient_by_date.get(str(d), {}).get(key, 0) for d in all_dates]
    if any(series):
        any_data = True
    fig3.add_trace(go.Scatter(
        x=x_labels, y=series, name=f"{label} ({unit})",
        line=dict(color=CATEGORY_COLORS[i % len(CATEGORY_COLORS)], width=3),
    ))

fig3.update_layout(**base_layout("amount"))
if any_data:
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info(f"No {selected_category.lower()} logged in this range yet.")
