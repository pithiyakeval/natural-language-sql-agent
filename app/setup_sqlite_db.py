import sqlite3
import random
from datetime import date, timedelta

# =========================
# CONNECT DB
# =========================
conn = sqlite3.connect("business.db")
cur = conn.cursor()

# =========================
# DROP OLD TABLES
# =========================
cur.executescript("""
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;
""")

# =========================
# CREATE TABLES
# =========================
cur.executescript("""
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    city TEXT,
    signup_date DATE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    cost_price REAL,
    selling_price REAL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    order_date DATE,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
""")

# =========================
# USERS (500)
# =========================
cities = ["Vadodara", "Ahmedabad", "Surat", "Rajkot", "Mumbai", "Pune"]

users = []
for i in range(1, 501):
    users.append((
        i,
        f"User{i}",
        f"user{i}@mail.com",
        random.choice(cities),
        date(2023, 1, 1) + timedelta(days=random.randint(0, 365))
    ))

cur.executemany(
    "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
    users
)

# =========================
# PRODUCTS (120)
# =========================
categories = {
    "Electronics": (8000, 25000),
    "Accessories": (500, 4000),
    "Home": (1500, 12000),
    "Fitness": (2000, 15000)
}

products = []
pid = 1
for category, price_range in categories.items():
    for i in range(30):
        cost = random.randint(*price_range)
        selling = int(cost * random.uniform(1.25, 1.6))
        products.append((
            pid,
            f"{category}_Product_{i+1}",
            category,
            cost,
            selling
        ))
        pid += 1

cur.executemany(
    "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
    products
)

# =========================
# ORDERS (5000 across 2024)
# =========================
orders = []
order_items = []
start_date = date(2024, 1, 1)

for oid in range(1, 5001):
    user_id = random.randint(1, 500)
    order_date = start_date + timedelta(days=random.randint(0, 364))
    orders.append((oid, user_id, order_date))

    for _ in range(random.randint(1, 4)):
        product_id = random.randint(1, 120)
        qty = random.randint(1, 3)
        order_items.append((oid, product_id, qty))

cur.executemany(
    "INSERT INTO orders VALUES (?, ?, ?)",
    orders
)

cur.executemany(
    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
    order_items
)

conn.commit()
conn.close()

print("✅ business.db created successfully with realistic 1-year business data")
