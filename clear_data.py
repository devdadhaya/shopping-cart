import sqlite3

def clear_all_data():
    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # データ削除クエリ
    tables = ['members', 'products', 'categories', 'cart', 'purchase_history']
    for table in tables:
        c.execute(f'DELETE FROM {table}')
        c.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}"')  # IDのリセット

    conn.commit()
    conn.close()
    print("All data cleared successfully!")

if __name__ == '__main__':
    clear_all_data()
