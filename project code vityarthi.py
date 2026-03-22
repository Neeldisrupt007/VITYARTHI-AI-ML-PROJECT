import sqlite3
from datetime import datetime, timedelta

# ---------------- DATABASE SETUP ---------------- #
conn = sqlite3.connect("fridge.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    storage TEXT,
    purchase_date TEXT,
    expiry_days REAL
)
""")
conn.commit()

# ---------------- TRAINING DATA (ML) ---------------- #
# This acts as your dataset

training_data = [
    ("milk", "fridge", 5),
    ("milk", "fridge", 6),
    ("bread", "room", 3),
    ("bread", "room", 2),
    ("fruit", "fridge", 10),
    ("fruit", "room", 7),
    ("vegetable", "fridge", 6),
    ("vegetable", "room", 4)
]

# ---------------- ML PREDICTION FUNCTION ---------------- #
def predict_expiry(category, storage):
    values = []

    for item, store, days in training_data:
        if item == category and store == storage:
            values.append(days)

    # fallback if no match
    if not values:
        return 5

    return sum(values) / len(values)


# ---------------- RECIPE DATABASE ---------------- #
recipes = {
    "Omelette": ["egg", "milk"],
    "Fruit Salad": ["fruit", "banana"],
    "Sandwich": ["bread", "butter"],
    "Veg Curry": ["vegetable", "salt"]
}


# ---------------- FUNCTIONS ---------------- #

def add_item():
    name = input("Enter item name: ").lower()
    category = input("Enter category (milk/bread/fruit/vegetable): ").lower()
    storage = input("Storage (fridge/room): ").lower()

    if category not in ["milk", "bread", "fruit", "vegetable"]:
        print("❌ Invalid category!")
        return

    if storage not in ["fridge", "room"]:
        print("❌ Invalid storage!")
        return

    purchase_date = datetime.now()

    expiry_days = predict_expiry(category, storage)

    cursor.execute("""
    INSERT INTO items (name, category, storage, purchase_date, expiry_days)
    VALUES (?, ?, ?, ?, ?)
    """, (name, category, storage,
          purchase_date.strftime("%Y-%m-%d"), expiry_days))

    conn.commit()

    print(f"✅ Item added successfully!")
    print(f"📅 Predicted expiry in {round(expiry_days)} days")


def view_items():
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()

    if not rows:
        print("📭 No items found.")
        return

    print("\n📦 Your Fridge Items:\n")

    for row in rows:
        item_id, name, category, storage, purchase_date, expiry_days = row

        purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d")
        expiry_date = purchase_date + timedelta(days=expiry_days)
        days_left = (expiry_date - datetime.now()).days

        print(f"ID: {item_id} | {name}")
        print(f"Category: {category} | Storage: {storage}")
        print(f"⏳ Days left: {days_left}")

        if days_left <= 2:
            print("⚠️ Expiring soon!")

        print("-" * 35)


def delete_item():
    item_id = input("Enter item ID to delete: ")

    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()

    print("🗑️ Item deleted successfully!")


def suggest_recipes():
    cursor.execute("SELECT name FROM items")
    items = [row[0] for row in cursor.fetchall()]

    print("\n🍳 Recipe Suggestions:\n")

    found = False

    for recipe, ingredients in recipes.items():
        if all(ingredient in items for ingredient in ingredients):
            print(f"✅ {recipe}")
            found = True

    if not found:
        print("❌ No matching recipes found.")


def menu():
    while True:
        print("\n====== Invisible Waste Optimizer ======")
        print("1. Add Item")
        print("2. View Items")
        print("3. Delete Item")
        print("4. Suggest Recipes")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_item()
        elif choice == "2":
            view_items()
        elif choice == "3":
            delete_item()
        elif choice == "4":
            suggest_recipes()
        elif choice == "5":
            print("👋 Exiting program...")
            break
        else:
            print("❌ Invalid choice!")


# ---------------- RUN PROGRAM ---------------- #
if __name__ == "__main__":
    menu()