import sqlite3
from pathlib import Path
from datetime import date

# Data is stored in a single file in your home folder, so it survives
# closing the app, restarting your PC, and (later) rebuilding the .exe.
DB_PATH = Path.home() / ".nutrition_tracker" / "data.db"

DEFAULT_GOALS = {
    "calorie_goal": "2293",
    "protein_goal": "111",
    "carb_goal": "251",
    "fat_goal": "86",
}


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
            fat REAL NOT NULL,
            health_score REAL
        )
        """
    )
    # Older databases created before health_score existed won't have the
    # column yet — add it if missing so upgrades don't break.
    existing_cols = [row[1] for row in conn.execute("PRAGMA table_info(meals)")]
    if "health_score" not in existing_cols:
        conn.execute("ALTER TABLE meals ADD COLUMN health_score REAL")

    # One row per (meal, nutrient) pair. This lets you log any subset of
    # the 60+ nutrients per meal without the meals table needing a
    # column for every single one.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meal_nutrients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER NOT NULL,
            nutrient_key TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (meal_id) REFERENCES meals (id)
        )
        """
    )
    # Simple key/value store for daily goals (calories, protein, etc.)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    return conn


def add_meal(meal_name, calories, protein, carbs, fat, meal_date=None, health_score=None):
    """Inserts the meal and returns its new id, so nutrients can be
    attached to it with add_nutrients()."""
    meal_date = meal_date or str(date.today())
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO meals (date, meal, calories, protein, carbs, fat, health_score) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (meal_date, meal_name, calories, protein, carbs, fat, health_score),
    )
    meal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meal_id


def add_nutrients(meal_id, nutrients):
    """nutrients: dict of {nutrient_key: amount}. Zero/empty amounts are
    skipped so totals aren't cluttered with values nobody entered."""
    conn = get_connection()
    for key, amount in nutrients.items():
        if amount:
            conn.execute(
                "INSERT INTO meal_nutrients (meal_id, nutrient_key, amount) "
                "VALUES (?, ?, ?)",
                (meal_id, key, amount),
            )
    conn.commit()
    conn.close()


def get_meals(for_date=None):
    conn = get_connection()
    if for_date:
        cursor = conn.execute(
            "SELECT id, date, meal, calories, protein, carbs, fat, health_score "
            "FROM meals WHERE date = ? ORDER BY id",
            (for_date,),
        )
    else:
        cursor = conn.execute(
            "SELECT id, date, meal, calories, protein, carbs, fat, health_score "
            "FROM meals ORDER BY id"
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_daily_nutrient_totals(for_date):
    """Returns {nutrient_key: total_amount} summed across every meal
    logged on the given date."""
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT mn.nutrient_key, SUM(mn.amount)
        FROM meal_nutrients mn
        JOIN meals m ON mn.meal_id = m.id
        WHERE m.date = ?
        GROUP BY mn.nutrient_key
        """,
        (for_date,),
    )
    totals = dict(cursor.fetchall())
    conn.close()
    return totals


def clear_meals(for_date=None):
    """Deletes meals and their attached nutrient rows."""
    conn = get_connection()
    if for_date:
        conn.execute(
            "DELETE FROM meal_nutrients WHERE meal_id IN "
            "(SELECT id FROM meals WHERE date = ?)",
            (for_date,),
        )
        conn.execute("DELETE FROM meals WHERE date = ?", (for_date,))
    else:
        conn.execute("DELETE FROM meal_nutrients")
        conn.execute("DELETE FROM meals")
    conn.commit()
    conn.close()


def get_daily_macro_totals(start_date, end_date):
    """Returns a list of (date, calories, protein, carbs, fat) rows,
    one per day that has at least one logged meal in the range."""
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT date, SUM(calories), SUM(protein), SUM(carbs), SUM(fat)
        FROM meals
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """,
        (start_date, end_date),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_daily_health_scores(start_date, end_date):
    """Returns a list of (date, avg_health_score) for days that have at
    least one scored meal."""
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT date, AVG(health_score)
        FROM meals
        WHERE date BETWEEN ? AND ? AND health_score IS NOT NULL
        GROUP BY date
        ORDER BY date
        """,
        (start_date, end_date),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_daily_nutrient_totals_range(start_date, end_date):
    """Returns {date: {nutrient_key: amount}} for every day with logged
    nutrients in the range."""
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT m.date, mn.nutrient_key, SUM(mn.amount)
        FROM meal_nutrients mn
        JOIN meals m ON mn.meal_id = m.id
        WHERE m.date BETWEEN ? AND ?
        GROUP BY m.date, mn.nutrient_key
        """,
        (start_date, end_date),
    )
    rows = cursor.fetchall()
    conn.close()
    result = {}
    for d, key, amount in rows:
        result.setdefault(d, {})[key] = amount
    return result


def get_setting(key, default=None):
    conn = get_connection()
    cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return DEFAULT_GOALS.get(key, default)


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )
    conn.commit()
    conn.close()
