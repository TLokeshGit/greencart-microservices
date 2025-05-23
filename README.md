# GreenCart Backend

This is the backend service for the GreenCart application, built using Django and Django REST Framework. It provides APIs for managing products, categories, customers, orders, payments, and more.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Deployment on Render.com](#deployment-on-rendercom)

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

## Deployment on Render.com

1. Create a new service on Render with the following settings:

   - Environment: Python
   - Build Command: `./build.sh`
   - Start Command: `gunicorn django_backend.wsgi:application`

2. Add environment variables:

   - `DJANGO_SETTINGS_MODULE` set to `django_backend.settings`
   - `PYTHONPATH` set to `django_backend`
   - `DEBUG` set to `False`
   - `DATABASE_URL` from your Render PostgreSQL database
   - `SECRET_KEY`, `ALLOWED_HOSTS`, and any other variables your Django app needs

3. Push your code to the repository connected with Render. Render will automatically build and deploy.

4. After the build, visit the provided URL to confirm your Django application is running.
