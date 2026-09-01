import sqlite3
from pathlib import Path
from datetime import date

# Data is stored in a single file in your home folder, so it survives
# closing the app, restarting your PC, and (later) rebuilding the .exe.
DB_PATH = Path.home() / ".nutrition_tracker" / "data.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal TEXT NOT NULL,
            calories INTEGER NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL
        )
        """
    )
    return conn


def add_meal(meal_name, calories, protein, carbs, fat, meal_date=None):
    meal_date = meal_date or str(date.today())
    conn = get_connection()
    conn.execute(
        "INSERT INTO meals (date, meal, calories, protein, carbs, fat) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (meal_date, meal_name, calories, protein, carbs, fat),
    )
    conn.commit()
    conn.close()


def get_meals(for_date=None):
    conn = get_connection()
    if for_date:
        cursor = conn.execute(
            "SELECT date, meal, calories, protein, carbs, fat "
            "FROM meals WHERE date = ? ORDER BY id",
            (for_date,),
        )
    else:
        cursor = conn.execute(
            "SELECT date, meal, calories, protein, carbs, fat "
            "FROM meals ORDER BY id"
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_meals(for_date=None):
    conn = get_connection()
    if for_date:
        conn.execute("DELETE FROM meals WHERE date = ?", (for_date,))
    else:
        conn.execute("DELETE FROM meals")
    conn.commit()
    conn.close()
