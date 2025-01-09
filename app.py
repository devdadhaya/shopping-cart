from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from auth_utils import register_user, check_password  # auth_utilsからインポート

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
        password = request.form['password']

        # データベースからユーザー情報を取得
        conn = sqlite3.connect('shopping_cart.db')
        c = conn.cursor()
        c.execute('SELECT password FROM members WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        # ユーザーが存在し、パスワードが一致する場合
        if user and check_password(password, user[0]):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('products'))
        else:
            # エラーメッセージを表示
            flash('Invalid username or password. Please try again.', 'danger')

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

# カートページ
@app.route('/cart')
def view_cart():
    if 'username' not in session:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # ユーザーIDを取得
    c.execute('SELECT id FROM members WHERE username = ?', (session['username'],))
    user_id = c.fetchone()[0]

    # カート内容を取得
    c.execute('''
        SELECT products.name, cart.quantity, products.price
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    ''', (user_id,))
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
    if 'username' not in session:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # ユーザーIDを取得
    c.execute('SELECT id FROM members WHERE username = ?', (session['username'],))
    user_id = c.fetchone()[0]

    # カート内容を購入履歴に追加
    c.execute('''
        INSERT INTO purchase_history (user_id, product_id, quantity)
        SELECT user_id, product_id, quantity FROM cart WHERE user_id = ?
    ''', (user_id,))
    conn.commit()

    # カートを空にする
    c.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

    flash('Purchase successful!', 'success')
    return redirect(url_for('thank_you'))

# サンキューページ
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

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
    if 'username' not in session:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    product_id = request.form['product_id']

    conn = sqlite3.connect('shopping_cart.db')
    c = conn.cursor()

    # ユーザーIDを取得
    c.execute('SELECT id FROM members WHERE username = ?', (session['username'],))
    user_id = c.fetchone()[0]

    # カートに商品を追加
    c.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
              (user_id, product_id, 1))
    conn.commit()
    conn.close()

    flash('Product added to cart!', 'success')
    return redirect(url_for('products'))

if __name__ == '__main__':
    app.run(debug=True)

