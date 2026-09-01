import customtkinter as ctk
import json
import os
from datetime import date

# Appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DATA_FILE = "meals.json"

class NutritionTracker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nutrition Tracker")
        self.geometry("700x600")
        self.resizable(False, False)

        # Load saved meals
        self.meals = self.load_meals()

        # Title
        self.title_label = ctk.CTkLabel(self, text="🥗 Nutrition Tracker", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=15)

        # --- Input Frame ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.input_frame, text="Add a Meal", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Food name
        self.name_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Food / Meal name", width=400)
        self.name_entry.pack(pady=5)

        # Numbers frame
        self.numbers_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.numbers_frame.pack(pady=5)

        self.cal_entry = ctk.CTkEntry(self.numbers_frame, placeholder_text="Calories", width=90)
        self.cal_entry.grid(row=0, column=0, padx=5)

        self.protein_entry = ctk.CTkEntry(self.numbers_frame, placeholder_text="Protein (g)", width=90)
        self.protein_entry.grid(row=0, column=1, padx=5)

        self.carbs_entry = ctk.CTkEntry(self.numbers_frame, placeholder_text="Carbs (g)", width=90)
        self.carbs_entry.grid(row=0, column=2, padx=5)

        self.fat_entry = ctk.CTkEntry(self.numbers_frame, placeholder_text="Fat (g)", width=90)
        self.fat_entry.grid(row=0, column=3, padx=5)

        # Add button
        self.add_button = ctk.CTkButton(self.input_frame, text="Add Meal", command=self.add_meal)
        self.add_button.pack(pady=12)

        # --- Summary ---
        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.pack(pady=10, padx=20, fill="x")

        self.summary_label = ctk.CTkLabel(self.summary_frame, text="Today's Totals: 0 kcal | P: 0g | C: 0g | F: 0g",
                                          font=ctk.CTkFont(size=14))
        self.summary_label.pack(pady=10)

        # --- Meal List ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.meal_listbox = ctk.CTkTextbox(self.list_frame, width=640, height=220)
        self.meal_listbox.pack(pady=10, padx=10)
        self.meal_listbox.configure(state="disabled")

        # Clear button
        self.clear_button = ctk.CTkButton(self, text="Clear All Meals", fg_color="#c0392b", hover_color="#e74c3c",
                                          command=self.clear_meals)
        self.clear_button.pack(pady=10)

        self.update_display()

    def load_meals(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_meals(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.meals, f, indent=2)

    def add_meal(self):
        name = self.name_entry.get().strip()
        if not name:
            return

        try:
            calories = float(self.cal_entry.get() or 0)
            protein = float(self.protein_entry.get() or 0)
            carbs = float(self.carbs_entry.get() or 0)
            fat = float(self.fat_entry.get() or 0)
        except ValueError:
            return

        meal = {
            "date": str(date.today()),
            "name": name,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }

        self.meals.append(meal)
        self.save_meals()

        # Clear inputs
        self.name_entry.delete(0, "end")
        self.cal_entry.delete(0, "end")
        self.protein_entry.delete(0, "end")
        self.carbs_entry.delete(0, "end")
        self.fat_entry.delete(0, "end")

        self.update_display()

    def clear_meals(self):
        self.meals = []
        self.save_meals()
        self.update_display()

    def update_display(self):
        # Update summary
        total_cal = sum(m["calories"] for m in self.meals)
        total_p = sum(m["protein"] for m in self.meals)
        total_c = sum(m["carbs"] for m in self.meals)
        total_f = sum(m["fat"] for m in self.meals)

        self.summary_label.configure(
            text=f"Today's Totals: {total_cal:.0f} kcal | P: {total_p:.1f}g | C: {total_c:.1f}g | F: {total_f:.1f}g"
        )

        # Update list
        self.meal_listbox.configure(state="normal")
        self.meal_listbox.delete("1.0", "end")

        if not self.meals:
            self.meal_listbox.insert("end", "No meals logged yet.\n")
        else:
            for m in self.meals:
                line = f"• {m['name']}  —  {m['calories']:.0f} kcal | P: {m['protein']:.1f}g | C: {m['carbs']:.1f}g | F: {m['fat']:.1f}g\n"
                self.meal_listbox.insert("end", line)

        self.meal_listbox.configure(state="disabled")

if __name__ == "__main__":
    app = NutritionTracker()
    app.mainloop()
