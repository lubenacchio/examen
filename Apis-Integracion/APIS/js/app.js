document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    setupCustomerForm();
});
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ecommerce_user:admin123@localhost/ecommerce'

function fetchProducts() {
    fetch('http://localhost:8000/products')
        .then(response => response.json())
        .then(products => {
            const productList = document.getElementById('product-list');
            productList.innerHTML = products.map(product => `
                <div class="product">
                    <h2>${product.name}</h2>
                    <p>${product.description}</p>
                    <p>${product.price}</p>
                    <button onclick="addToCart(${product.id})">Añadir al carrito</button>
                </div>
            `).join('');
        });
}

function setupCustomerForm() {
    const customerForm = document.getElementById('customer-form');
    if (customerForm) {
        customerForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const customerData = {
                razonSocial: document.getElementById('razonSocial').value,
                rut: document.getElementById('rut').value,
                direccion: document.getElementById('direccion').value
            };
            const result = await createCustomer(customerData);
            if (result && result.message) {
                alert(result.message);
                customerForm.reset();
            } else {
                alert('Error al crear cliente');
            }
        });
    }
}

function addToCart(productId) {
    fetch('http://localhost:8000/cart', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ productId }),
    })
    .then(response => response.json())
    .then(data => {
        alert('Producto añadido al carrito');
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
