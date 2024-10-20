from flask import Flask, render_template
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update if needed
db = client['product_info_db']  # Database name
collection = db['extracted_data']  # Collection name

@app.route('/')
def display_products():
    # Fetch all documents from the collection
    first_product = collection.find_one()  # Get only the first document

    # Initialize invoice_id as None
    invoice_id = None

    # Check if first_product is not None and extract invoice_id
    if first_product and 'Invoice Id' in first_product:
        invoice_id = first_product['Invoice Id']
    products = list(collection.find())
    total_products = len(products)
    is_verified = all(product.get('final_result') == 'Approved' for product in products)
    return render_template('bill.html', products=products, invoice_id=invoice_id, total_products=total_products, is_verified=is_verified)
if __name__ == '__main__':
    app.run(debug=True)
