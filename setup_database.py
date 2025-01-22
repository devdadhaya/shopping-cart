import sqlite3

def drop_all_tables(conn):
    """データベース内のすべてのテーブルを削除"""
    c = conn.cursor()

    # ビュー一覧を取得して削除
    c.execute("SELECT name FROM sqlite_master WHERE type='view';")
    views = c.fetchall()
    for view_name in views:
        c.execute(f"DROP VIEW IF EXISTS {view_name[0]}")
        print(f"View {view_name[0]} dropped.")

    # テーブル一覧を取得
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    tables = c.fetchall()
    for table_name in tables:
        c.execute(f"DROP TABLE IF EXISTS {table_name[0]}")
        print(f"Table {table_name[0]} dropped.")

    # sqlite_sequenceの内容をリセット
    c.execute("DELETE FROM sqlite_sequence;")
    print("sqlite_sequence reset.")

    conn.commit()

def setup_database():
    conn = sqlite3.connect('shopping_cart.db')

    # 既存のテーブルを削除
    drop_all_tables(conn)

    c = conn.cursor()

    # 新しいテーブルを作成
    c.executescript('''
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        description TEXT,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );

    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS purchase_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        session_id TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE VIEW cart_view AS
    SELECT 
        products.name, 
        SUM(cart.quantity) AS total_quantity, 
        products.price, 
        SUM(cart.quantity * products.price) AS subtotal,
        cart.session_id,
        cart.product_id
    FROM cart
    JOIN products ON cart.product_id = products.id
    GROUP BY products.name, products.price, cart.session_id, cart.product_id;

    ''')

    conn.commit()
    conn.close()
    print("Database setup complete!")

if __name__ == '__main__':
    setup_database()
