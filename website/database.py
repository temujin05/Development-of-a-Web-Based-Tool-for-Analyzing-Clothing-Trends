import oracledb
import random

def get_db_connection():
    conn = oracledb.connect(
        user="u_R1J9ML",
        password="Telmuun@@@0819",
        dsn="codd.inf.unideb.hu/ora21cp.inf.unideb.hu"
    )
    return conn

def seed_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Connected to Oracle!")

    categories = ["Shirts", "Pants", "Dresses", "Jackets", "Shoes"]


    for c in categories:
        cursor.execute(
            "INSERT INTO Categories (name) VALUES (:1)",
            [c]
        )
    conn.commit()

    styles = ["Classic", "Casual", "Modern", "Vintage","Slim Fit", "Oversized", "Relaxed","Formal", "Urban", "Minimal"]
    colors = ["Red", "Blue", "Black", "White", "Beige","Pink", "Yellow", "Brown", "Green", "Grey"]
    materials = ["Cotton", "Wool", "Polyester", "Leather", "Silk"]
    countries = ["Italy", "France", "China", "USA", "Japan", "Hungary", "South Korea"]
    genders = ["male", "female", "unisex"]
    category_items = {
        1: ["Shirt", "Tee", "Blouse"],
        2: ["Pants", "Trousers", "Jeans"],
        3: ["Dress", "Skirt"],
        4: ["Jacket", "Coat", "Hoodie"],
        5: ["Sneakers", "Boots", "Heels", "Loafers"]
    }

    for _ in range(50):
        category_id = random.randint(1, 5)
        gender = random.choice(genders)
        material = random.choice(materials)
        item_name = f"{random.choice(styles)} {material} {random.choice(colors)} {random.choice(category_items[category_id])}"

        cursor.execute("""
            INSERT INTO clothing_item
            (name, category_id, color, material, rating, price, country, gender_target)
            VALUES (:1,:2,:3,:4,:5,:6,:7,:8)
        """, [
            item_name,
            category_id,
            random.choice(colors),
            material,
            round(random.uniform(2.5, 5), 1),
            round(random.uniform(20, 400), 2),
            random.choice(countries),
            gender
        ])

    conn.commit()
 
    seasons = ["Spring", "Summer", "Autumn", "Winter"]
    cursor.execute("SELECT id FROM clothing_item")
    clothing_ids = [row[0] for row in cursor.fetchall()]

    trend_rows = []

    for clothing_id in clothing_ids:
        for year in range(2020, 2026):
            for season in seasons:
                trend_rows.append([
                    clothing_id,
                    year,
                    season,
                    random.randint(100, 5000),
                    round(random.uniform(1, 10), 1),
                    "synthetic-data"
                ])

    print("Rows to insert:", len(trend_rows))
    cursor.executemany("""
        INSERT INTO trend_data
        (clothing_id, year, season, popularity, trend_score, data_source)
        VALUES (:1,:2,:3,:4,:5,:6)
    """, trend_rows)

    conn.commit()


    users = ["user1@example.com", "user2@example.com", "user3@example.com"]

    for u in users:
        cursor.execute("INSERT INTO app_user (email) VALUES (:1)", [u])
    conn.commit()


    type_of_styles = ["Classic", "Casual", "Modern", "Vintage","Slim Fit", "Oversized", "Relaxed","Formal", "Urban", "Minimal"]

    for user_id in range(1, 4):
        cursor.execute("""
            INSERT INTO user_preference
            (user_id, category_id, color_preference, style_preference)
            VALUES (:1,:2,:3,:4)
        """, [
            user_id,
            random.randint(1, 5),
            random.choice(colors),
            random.choice(type_of_styles)
        ])

    conn.commit()

    cursor.close()
    conn.close()
    print("Done and connection closed.")


if __name__ == "__main__":
    seed_database()