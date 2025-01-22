<script type="text/babel">
    const Cart = () => {
        const [cartItems, setCartItems] = React.useState([]);
        const [total, setTotal] = React.useState(0);
    
        React.useEffect(() => {
            fetch('/cart-data')
                .then(response => response.json())
                .then(data => {
                    setCartItems(data);
                    const totalAmount = data.reduce((sum, item) => sum + item.quantity * item.price, 0);
                    setTotal(totalAmount);
                });
        }, []);
    
        if (cartItems.length === 0) {
            return <p>カートは空です。</p>;
        }
    
        return (
            <div>
                <h1>カート</h1>
                <table>
                    <thead>
                        <tr>
                            <th>商品名</th>
                            <th>数量</th>
                            <th>価格</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cartItems.map((item, index) => (
                            <tr key={index}>
                                <td>{item.name}</td>
                                <td>{item.quantity}</td>
                                <td>¥{item.price}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <p>合計: ¥{total}</p>
            </div>
        );
    };
    
    ReactDOM.render(<Cart />, document.getElementById('cart-root'));
    </script>
    