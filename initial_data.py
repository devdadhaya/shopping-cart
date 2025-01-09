import sqlite3

def insert_initial_data():
    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # カテゴリデータの挿入
    categories = [
        ('Electronics',),
        ('Books',),
        ('Clothing',)
    ]
    c.executemany('INSERT INTO categories (name) VALUES (?)', categories)
    print("Categories inserted.")

    # 商品データの挿入
    products = [
        ('Laptop', 1000, 'A high-performance laptop', 1),  # Electronics
        ('Smartphone', 500, 'A powerful smartphone', 1),  # Electronics
        ('Novel', 20, 'A gripping novel', 2),             # Books
        ('T-Shirt', 15, 'A comfortable T-shirt', 3)       # Clothing
    ]
    c.executemany('INSERT INTO products (name, price, description, category_id) VALUES (?, ?, ?, ?)', products)
    print("Products inserted.")

    conn.commit()
    conn.close()
    print("Initial data inserted successfully!")

if __name__ == '__main__':
    insert_initial_data()
