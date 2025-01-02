# GreenCart Microservices

## Overview

GreenCart is a microservices-based e-commerce platform that allows users to manage products, orders, customers, and transactions. The platform is built using Django for the backend and FastAPI for product management and recommendations.

## Project Structure

- **django_backend**: Contains the Django backend for managing customers, orders, transactions, and more.
- **fastapi_recommendations**: Contains the FastAPI service for managing products and recommendations.

## Functionalities

### Django Backend

- **Customer Management**: Register, login, and manage customer details.
- **Cart Management**: Add, view, and manage cart items.
- **Order Management**: Create and view orders.
- **Payment Management**: Manage payment methods and transactions.
- **Invoice Management**: Generate and view invoices.

### FastAPI Service

- **Product Management**: CRUD operations for products.
- **Recommendation Management**: Manage product recommendations.
- **Stock Management**: Retrieve and update product stock levels.

## How Services are Linked

### Example Flow: Creating an Order

1. **User Adds Product to Cart (Django Backend)**

   - Endpoint: `POST /api/cart/`
   - The user adds a product to their cart.
   - The Django backend validates the product details by making a request to the FastAPI service.

2. **Django Backend Validates Product (FastAPI Service)**

   - Endpoint: `GET /products/{product_id}`
   - The Django backend sends a request to the FastAPI service to fetch product details.
   - The FastAPI service returns the product details, including stock availability.

3. **User Creates an Order (Django Backend)**

   - Endpoint: `POST /api/orders/`
   - The user creates an order with the items in their cart.
   - The Django backend validates the stock levels by making requests to the FastAPI service.

4. **Django Backend Validates and Updates Stock (FastAPI Service)**

   - Endpoint: `PUT /products/{product_id}/stock`
   - The Django backend sends a request to the FastAPI service to update the stock levels.
   - The FastAPI service updates the stock and returns the updated product details.

5. **Order is Created (Django Backend)**
   - The Django backend creates the order and associated order items.
   - The order details are saved in the Django backend database.

### Detailed Flow

1. **Add Product to Cart**

   - User sends a `POST` request to `/api/cart/` with `product_id` and `quantity`.
   - Django backend calls FastAPI service to validate product details:
     ```python
     response = requests.get(f"{FASTAPI_URL}/products/{product_id}", timeout=5)
     ```
   - FastAPI service returns product details:
     ```json
     {
       "id": 1,
       "name": "Laptop",
       "description": "A high-performance laptop",
       "price": 1500.0,
       "stock": 10,
       "category": {
         "id": 1,
         "name": "Electronics"
       }
     }
     ```
   - Django backend checks stock and adds the product to the cart.

2. **Create Order**
   - User sends a `POST` request to `/api/orders/` with `order_items`.
   - Django backend validates stock levels for each item:
     ```python
     response = requests.get(f"{FASTAPI_URL}/products/{product_id}", timeout=5)
     ```
   - FastAPI service returns product details.
   - Django backend updates stock levels:
     ```python
     stock_update_response = requests.put(
         f"{FASTAPI_URL}/products/{product_id}/stock",
         json={"stock": new_stock},
         timeout=5
     )
     ```
   - FastAPI service updates the stock and returns the updated product details.
   - Django backend creates the order and saves it in the database.

## Running the Project

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-repo/greencart-microservices.git
   cd greencart-microservices
   ```

2. **Set Up the Django Backend**:

   ```bash
   cd django_backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Set Up the FastAPI Service**:

   ```bash
   cd fastapi_recommendations
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

4. **Access the Application**:
   - Django Backend: `http://localhost:8000/`
   - FastAPI Service: `http://localhost:8001/`

## Conclusion

GreenCart provides a robust and scalable e-commerce platform with a microservices architecture. The integration of Django and FastAPI ensures efficient management of customers, orders, products, and recommendations. The detailed API documentation and modular design make it easy to extend and maintain the platform.
