from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, render_template
import time
import sqlite3
from auth_utils import register_user, check_password  # auth_utilsからインポート
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        try:
            register_user(username, password)  # ユーザー登録
            flash('User registered successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        plain_password = request.form['password']

        # ユーザーの認証処理
        conn = sqlite3.connect('shopping_cart.db')
        c = conn.cursor()
        c.execute('SELECT username, password FROM members WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user:
            db_username, db_hashed_password = user
            if check_password(plain_password, db_hashed_password):  # パスワードを突合
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('products'))  # ログイン成功後のリダイレクト
            else:
                flash('Invalid username or password.', 'danger')
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

# 商品一覧ページ
@app.route('/products')
def products():
    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # 商品情報を取得
    c.execute('SELECT id, name, price FROM products')
    product_list = c.fetchall()
    conn.close()

    # テンプレートに渡して表示
    return render_template('products.html', products=product_list)

@app.route('/cart')
def view_cart():
    if 'session_id' not in session:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    session_id = session['session_id']
    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()
    c.execute('''
        SELECT products.name, cart.quantity, products.price
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.session_id = ?
    ''', (session_id,))
    cart_items = c.fetchall()
    conn.close()

    if not cart_items:
        flash('Your cart is empty!', 'danger')
        return redirect(url_for('products'))

    total = sum(item[1] * item[2] for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total=total)

# 購入確認ページ
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'session_id' not in session:
        return jsonify({'error': 'You need to log in first!'}), 401

    session_id = session['session_id']
    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # cart_view を使用して購入履歴に追加
    c.execute('''
        INSERT INTO purchase_history (session_id, product_id, quantity)
        SELECT session_id, product_id, total_quantity
        FROM cart_view
        WHERE session_id = ?
    ''', (session_id,))
    conn.commit()

    # カートを空にする
    c.execute('DELETE FROM cart WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Purchase successful!'})

# サンキューページ
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # セッションからユーザー名を削除
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))  # キャッシュ対策はヘッダーで対応

@app.route('/products-db')
def products_from_db():
    # SQLiteデータベース接続
    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # 商品情報を取得
    c.execute('SELECT id, name, price FROM products')
    product_list = c.fetchall()

    conn.close()

    # デバッグ用ログ（確認用）
    print("Product List:", product_list)

    # 商品情報をテンプレートに渡す
    return render_template('products.html', products=product_list)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'username' not in session or 'session_id' not in session:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    product_id = request.form['product_id']
    session_id = session['session_id']

    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # カートに商品を追加
    c.execute('INSERT INTO cart (session_id, product_id, quantity) VALUES (?, ?, ?)',
              (session_id, product_id, 1))
    conn.commit()
    conn.close()

    flash('Product added to cart!', 'success')
    return redirect(url_for('products'))

@app.route('/cart-data')
def cart_data():
    if 'session_id' not in session:
        return jsonify([])

    session_id = session['session_id']
    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # cart_view を使用してカートデータを取得
    c.execute('''
        SELECT name, total_quantity, price, subtotal
        FROM cart_view
        WHERE session_id = ?
    ''', (session_id,))
    cart_items = c.fetchall()
    conn.close()

    # JSON形式でデータを返す
    return jsonify([
        {'name': item[0], 'quantity': item[1], 'price': item[2], 'subtotal': item[3]}
        for item in cart_items
    ])

if __name__ == '__main__':
    environment = os.environ.get('ENV', 'local')  # デフォルトは'local'
    if environment == 'render':
        port = int(os.environ.get('PORT', 5000))
        print(f"Running on Render with port {port}")
        app.run(host='0.0.0.0', port=port)
    else:
        print("Running locally")
        app.run(debug=True)
