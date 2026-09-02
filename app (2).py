import streamlit as st
from datetime import date

import nutrition_tracker as nt
from nutrients_data import NUTRIENT_CATEGORIES
from health_score import compute_meal_health_score

st.set_page_config(page_title="Nutrition Tracker", page_icon="🥗", layout="centered")

DARK_BG = "#0d1220"
CARD_BG = "#161d30"
RING_TRACK = "#232c46"
FONT_FAMILY = "Arial Black, Arial, sans-serif"

PROTEIN_COLOR = "#A78BFA"
CARBS_COLOR = "#FB923C"
FAT_COLOR = "#38BDF8"
CAL_COLOR = "#4ADE80"
SCORE_GOOD = "#4ADE80"
SCORE_MID = "#FBBF24"
SCORE_LOW = "#F87171"

SUGAR_CUBE_SVG = """
<svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="1" y="12" width="9" height="9" rx="1.5" fill="{c}" opacity="0.55"/>
  <rect x="10" y="7" width="9" height="9" rx="1.5" fill="{c}" opacity="0.8"/>
  <rect x="16" y="14" width="9" height="9" rx="1.5" fill="{c}"/>
</svg>
"""

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {DARK_BG}; }}
    h1, h2, h3, h4, .stMarkdown p {{ font-family: {FONT_FAMILY} !important; }}
    .card {{
        background-color: {CARD_BG};
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 16px;
    }}
    .ring-label {{ text-align: center; font-family: {FONT_FAMILY}; color: white; margin-top: 8px; }}
    .ring-sub {{ text-align: center; color: #8b95ab; font-size: 13px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def ring_html(pct, size, color, center_html):
    pct = max(0, min(100, pct))
    deg = pct * 3.6
    return f"""
    <div style="
        width:{size}px; height:{size}px; border-radius:50%;
        background: conic-gradient({color} {deg}deg, {RING_TRACK} {deg}deg);
        display:flex; align-items:center; justify-content:center; margin:auto;">
      <div style="
          width:{size - 18}px; height:{size - 18}px; border-radius:50%;
          background:{CARD_BG}; display:flex; flex-direction:column;
          align-items:center; justify-content:center; text-align:center;">
        {center_html}
      </div>
    </div>
    """


today = str(date.today())

# --- Goals (editable) ---
with st.expander("⚙️ Daily Goals"):
    c1, c2, c3, c4 = st.columns(4)
    calorie_goal = c1.number_input("Calories", value=int(nt.get_setting("calorie_goal")), step=50)
    protein_goal = c2.number_input("Protein (g)", value=int(nt.get_setting("protein_goal")), step=5)
    carb_goal = c3.number_input("Carbs (g)", value=int(nt.get_setting("carb_goal")), step=5)
    fat_goal = c4.number_input("Fat (g)", value=int(nt.get_setting("fat_goal")), step=5)
    if st.button("Save Goals"):
        nt.set_setting("calorie_goal", calorie_goal)
        nt.set_setting("protein_goal", protein_goal)
        nt.set_setting("carb_goal", carb_goal)
        nt.set_setting("fat_goal", fat_goal)
        st.rerun()

calorie_goal = int(nt.get_setting("calorie_goal"))
protein_goal = int(nt.get_setting("protein_goal"))
carb_goal = int(nt.get_setting("carb_goal"))
fat_goal = int(nt.get_setting("fat_goal"))

st.markdown(f"<h1>🥗 Nutrition Tracker</h1>", unsafe_allow_html=True)

# --- Today's totals ---
meals_today = nt.get_meals(today)
total_cal = sum(m[3] for m in meals_today)
total_protein = sum(m[4] for m in meals_today)
total_carbs = sum(m[5] for m in meals_today)
total_fat = sum(m[6] for m in meals_today)
scores_today = [m[7] for m in meals_today if m[7] is not None]
avg_score = sum(scores_today) / len(scores_today) if scores_today else None

nutrient_totals_today = nt.get_daily_nutrient_totals(today)
vitamin_keys = [k for k, l, u in NUTRIENT_CATEGORIES["Fat-Soluble Vitamins"] + NUTRIENT_CATEGORIES["Water-Soluble Vitamins"]]
mineral_keys = [k for k, l, u in NUTRIENT_CATEGORIES["Electrolytes & Macrominerals"] + NUTRIENT_CATEGORIES["Trace Minerals"]]
vitamins_logged = len([k for k in vitamin_keys if k in nutrient_totals_today])
minerals_logged = len([k for k in mineral_keys if k in nutrient_totals_today])

# --- Calories + Health Score ring row ---
st.markdown('<div class="card">', unsafe_allow_html=True)
r1, r2 = st.columns(2)
with r1:
    cal_left = max(0, calorie_goal - total_cal)
    cal_pct = (total_cal / calorie_goal * 100) if calorie_goal else 0
    st.markdown(
        ring_html(
            cal_pct, 170, CAL_COLOR,
            f"<div style='font-size:26px;font-weight:900;color:white;'>{cal_left:.0f}</div>"
            f"<div style='color:#8b95ab;font-size:12px;'>left</div>",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='ring-label'>Calories</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ring-sub'>eaten {total_cal:.0f} of {calorie_goal}</div>", unsafe_allow_html=True)

with r2:
    if avg_score is not None:
        score_color = SCORE_GOOD if avg_score >= 70 else SCORE_MID if avg_score >= 40 else SCORE_LOW
        score_display = f"{avg_score:.0f}"
    else:
        score_color = RING_TRACK
        score_display = "—"
    st.markdown(
        ring_html(
            avg_score or 0, 170, score_color,
            f"<div style='font-size:32px;font-weight:900;color:white;'>{score_display}</div>"
            f"<div style='color:#8b95ab;font-size:12px;'>/ 100</div>",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='ring-label'>Health Score</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ring-sub'>today's average</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Macro rings ---
st.markdown('<div class="card">', unsafe_allow_html=True)
m1, m2, m3 = st.columns(3)
macro_defs = [
    (m1, "💪", "Protein", total_protein, protein_goal, PROTEIN_COLOR),
    (m2, None, "Carbs", total_carbs, carb_goal, CARBS_COLOR),
    (m3, "🛢️", "Fat", total_fat, fat_goal, FAT_COLOR),
]
for col, emoji, label, value, goal, color in macro_defs:
    with col:
        pct = (value / goal * 100) if goal else 0
        icon_html = SUGAR_CUBE_SVG.format(c=color) if emoji is None else f"<div style='font-size:22px;'>{emoji}</div>"
        st.markdown(
            ring_html(pct, 110, color, f"{icon_html}<div style='color:white;font-weight:900;'>{value:.0f}g</div>"),
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='ring-label'>{label}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ring-sub'>{goal}g goal</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Micronutrient summary ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("<h3>Essential Micronutrients</h3>", unsafe_allow_html=True)
v1, v2 = st.columns(2)
with v1:
    pct = vitamins_logged / len(vitamin_keys) * 100 if vitamin_keys else 0
    st.markdown(
        ring_html(pct, 110, "#818CF8", f"<div style='color:white;font-weight:900;font-size:22px;'>{vitamins_logged}</div><div style='color:#8b95ab;font-size:11px;'>of {len(vitamin_keys)}</div>"),
        unsafe_allow_html=True,
    )
    st.markdown("<div class='ring-label'>Vitamins</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ring-sub'>{pct:.0f}% Score</div>", unsafe_allow_html=True)
with v2:
    pct = minerals_logged / len(mineral_keys) * 100 if mineral_keys else 0
    st.markdown(
        ring_html(pct, 110, "#F87171", f"<div style='color:white;font-weight:900;font-size:22px;'>{minerals_logged}</div><div style='color:#8b95ab;font-size:11px;'>of {len(mineral_keys)}</div>"),
        unsafe_allow_html=True,
    )
    st.markdown("<div class='ring-label'>Minerals</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ring-sub'>{pct:.0f}% Score</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# AI MEAL LOGGING
# =========================================================
st.markdown("<h3>🤖 Log a Meal with AI</h3>", unsafe_allow_html=True)
st.caption("Describe your meal, attach a photo, or both. Requires an ANTHROPIC_API_KEY — see ai_helper.py.")

description = st.text_input("Describe your meal", placeholder="e.g. grilled chicken, white rice, and broccoli")
photo = st.file_uploader("Or attach a food photo", type=["jpg", "jpeg", "png"])

if st.button("Analyze & Log Meal", type="primary"):
    if not description and not photo:
        st.warning("Add a description or a photo first.")
    else:
        try:
            import ai_helper
            with st.spinner("Analyzing meal..."):
                if photo:
                    mime = "image/png" if photo.type == "image/png" else "image/jpeg"
                    result = ai_helper.analyze_image(photo.getvalue(), mime, description)
                else:
                    result = ai_helper.analyze_text(description)

            food_items = result.get("food_items", [])
            health_score, breakdown = compute_meal_health_score(food_items)

            meal_id = nt.add_meal(
                result.get("meal_name", "AI-logged meal"),
                result.get("calories", 0),
                result.get("protein", 0),
                result.get("carbs", 0),
                result.get("fat", 0),
                today,
                health_score,
            )
            nt.add_nutrients(meal_id, result.get("nutrients", {}))

            st.success(f"Logged: {result.get('meal_name')}")
            if health_score is not None:
                st.write(f"Health Score: **{health_score:.0f}**")
                for name, s, tier in breakdown:
                    st.caption(f"• {name} — {tier} ({s})")
            st.rerun()
        except Exception as e:
            st.error(f"Couldn't analyze meal: {e}")

st.page_link("pages/1_Log_Meal.py", label="Prefer to enter it manually?", icon="✍️")
