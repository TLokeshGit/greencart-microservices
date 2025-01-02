# GreenCart Backend

This is the backend service for the GreenCart application, built using Django and Django REST Framework. It provides APIs for managing products, categories, customers, orders, payments, and more.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Project Description

GreenCart is an e-commerce platform that allows users to browse and purchase products online. The backend service is responsible for handling all the business logic and data management for the application. It includes features such as:

- User authentication and authorization
- Product and category management
- Shopping cart and order management
- Payment processing using Stripe
- Product ratings and recommendations
- Address and payment method management
- Coupon and discount management

The backend service is built using Django and Django REST Framework, providing a robust and scalable solution for managing the application's data and business logic.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/greencart-microservices.git
   cd greencart-microservices/django_backend
   ```

2. Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```sh
   python manage.py migrate
   ```

5. Create a superuser:
   ```sh
   python manage.py createsuperuser
   ```


## Running the Application

1. Start the development server:
   ```sh
   python manage.py runserver
   ```

2. Access the application at `http://localhost:8000`.

## API Documentation

The API documentation is available at the following endpoints:

- Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- ReDoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)


