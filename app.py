from flask import Flask, render_template

app = Flask(__name__)

# Liste simulée de produits agricoles avec images
products = [
    {"name": "Tomates", "price": 1000, "location": "Sénégal", "stock": 100, "image": "static\img\Tomate.png"},
    {"name": "Pommes de terre", "price": 800, "location": "Mali", "stock": 50, "image": "static\img\PommeDeTerre.png"},
    {"name": "Oignons", "price": 750, "location": "Côte d'Ivoire", "stock": 75, "image": "static\img\Oignon.png"},
    {"name": "Carottes", "price": 600, "location": "Burkina Faso", "stock": 200, "image": "static\img\carrote.png"},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products_page():
    return render_template('products.html', products=products)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
