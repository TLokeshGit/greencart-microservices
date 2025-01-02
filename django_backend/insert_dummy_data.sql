-- Delete existing data except for users 'john_doe' and 'jane_smith'
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM shop_customer WHERE username IN ('john_doe', 'jane_smith')) THEN
        DELETE FROM shop_transaction WHERE customer_id NOT IN (SELECT id FROM shop_customer WHERE username IN ('john_doe', 'jane_smith'));
        DELETE FROM shop_invoice WHERE customer_id NOT IN (SELECT id FROM shop_customer WHERE username IN ('john_doe', 'jane_smith'));
        DELETE FROM shop_order_item WHERE order_id IN (SELECT id FROM shop_order WHERE customer_id NOT IN (SELECT id FROM shop_customer WHERE username IN ('john_doe', 'jane_smith')));
        DELETE FROM shop_order WHERE customer_id NOT IN (SELECT id FROM shop_customer WHERE username IN ('john_doe', 'jane_smith'));
        DELETE FROM shop_payment_method WHERE customer_id NOT IN (SELECT id FROM shop_customer WHERE username IN ('john_doe', 'jane_smith'));
        DELETE FROM shop_cart_item WHERE customer_id NOT IN (SELECT id FROM shop_customer WHERE username IN ('john_doe', 'jane_smith'));
        DELETE FROM shop_product_recommendation;
        DELETE FROM shop_product_rating;
        DELETE FROM shop_address WHERE customer_id NOT IN (SELECT id FROM shop_customer WHERE username IN ('john_doe', 'jane_smith'));
        DELETE FROM shop_coupon;
    END IF;
END $$;

-- Ensure tables exist before truncating
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_product_recommendation') THEN
        TRUNCATE TABLE shop_product_recommendation RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_product_rating') THEN
        TRUNCATE TABLE shop_product_rating RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_order_item') THEN
        TRUNCATE TABLE shop_order_item RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_order') THEN
        TRUNCATE TABLE shop_order RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_product') THEN
        TRUNCATE TABLE shop_product RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_category') THEN
        TRUNCATE TABLE shop_category RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_invoice') THEN
        TRUNCATE TABLE shop_invoice RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_payment_method') THEN
        TRUNCATE TABLE shop_payment_method RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_cart_item') THEN
        TRUNCATE TABLE shop_cart_item RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_transaction') THEN
        TRUNCATE TABLE shop_transaction RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_address') THEN
        TRUNCATE TABLE shop_address RESTART IDENTITY CASCADE;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_coupon') THEN
        TRUNCATE TABLE shop_coupon RESTART IDENTITY CASCADE;
    END IF;
END $$;

-- Insert customers
INSERT INTO shop_customer (username, email, phone_number, address, password, created_at, is_superuser, is_staff, is_active, date_joined, first_name, last_name) VALUES
('john_doe', 'john@example.com', '+1234567890', '123 Main St, Anytown, USA', 'hashed_password', NOW(), false, false, true, NOW(), 'John', 'Doe')
ON CONFLICT (username) DO NOTHING;

INSERT INTO shop_customer (username, email, phone_number, address, password, created_at, is_superuser, is_staff, is_active, date_joined, first_name, last_name) VALUES
('jane_smith', 'jane@example.com', '+0987654321', '456 Elm St, Othertown, USA', 'hashed_password', NOW(), false, false, true, NOW(), 'Jane', 'Smith')
ON CONFLICT (username) DO NOTHING;

-- Insert categories
INSERT INTO shop_category (name, description, created_at) VALUES
('Fruits', 'Fresh fruits', NOW()),
('Vegetables', 'Fresh vegetables', NOW()),
('Dairy', 'Dairy products', NOW()),
('Bakery', 'Bakery items', NOW()),
('Beverages', 'Drinks and beverages', NOW())
ON CONFLICT (name) DO NOTHING;

-- Insert products
INSERT INTO shop_product (name, description, price, stock, category_id, created_at) VALUES
('Apple', 'Fresh red apples', 3.99, 100, (SELECT id FROM shop_category WHERE name = 'Fruits'), NOW()),
('Banana', 'Organic bananas', 1.99, 150, (SELECT id FROM shop_category WHERE name = 'Fruits'), NOW()),
('Carrot', 'Crunchy carrots', 2.49, 200, (SELECT id FROM shop_category WHERE name = 'Vegetables'), NOW()),
('Broccoli', 'Fresh broccoli', 2.99, 120, (SELECT id FROM shop_category WHERE name = 'Vegetables'), NOW()),
('Milk', 'Organic whole milk', 4.99, 80, (SELECT id FROM shop_category WHERE name = 'Dairy'), NOW()),
('Bread', 'Whole grain bread', 3.49, 60, (SELECT id FROM shop_category WHERE name = 'Bakery'), NOW())
ON CONFLICT (name) DO NOTHING;

-- Insert addresses
INSERT INTO shop_address (customer_id, street, city, state, postal_code, country, is_default, created_at) VALUES
((SELECT id FROM shop_customer WHERE username = 'john_doe'), '123 Main St', 'Anytown', 'Anystate', '12345', 'USA', true, NOW()),
((SELECT id FROM shop_customer WHERE username = 'jane_smith'), '456 Elm St', 'Othertown', 'Otherstate', '67890', 'USA', true, NOW())
ON CONFLICT DO NOTHING;

-- Insert coupons
INSERT INTO shop_coupon (code, description, discount_amount, valid_from, valid_to, active) VALUES
('DISCOUNT10', '10% off', 10.00, NOW() - INTERVAL '1 DAY', NOW() + INTERVAL '30 DAYS', true),
('DISCOUNT20', '20% off', 20.00, NOW() - INTERVAL '1 DAY', NOW() + INTERVAL '30 DAYS', true)
ON CONFLICT (code) DO NOTHING;

-- Insert orders
INSERT INTO shop_order (customer_id, total_amount, status, created_at) VALUES
((SELECT id FROM shop_customer WHERE username = 'john_doe'), 19.97, 'PENDING', NOW()),
((SELECT id FROM shop_customer WHERE username = 'jane_smith'), 9.98, 'PENDING', NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert order items
INSERT INTO shop_order_item (order_id, product_id, quantity, price) VALUES
((SELECT id FROM shop_order WHERE customer_id = (SELECT id FROM shop_customer WHERE username = 'john_doe') AND status = 'PENDING' LIMIT 1), (SELECT id FROM shop_product WHERE name = 'Apple' LIMIT 1), 3, 3.99),
((SELECT id FROM shop_order WHERE customer_id = (SELECT id FROM shop_customer WHERE username = 'john_doe') AND status = 'PENDING' LIMIT 1), (SELECT id FROM shop_product WHERE name = 'Milk' LIMIT 1), 1, 4.99),
((SELECT id FROM shop_order WHERE customer_id = (SELECT id FROM shop_customer WHERE username = 'jane_smith') AND status = 'PENDING' LIMIT 1), (SELECT id FROM shop_product WHERE name = 'Banana' LIMIT 1), 5, 1.99)
ON CONFLICT DO NOTHING;

-- Insert payment methods
INSERT INTO shop_payment_method (customer_id, method_type, number, added_at) VALUES
((SELECT id FROM shop_customer WHERE username = 'john_doe'), 'CREDIT_CARD', '12345678', NOW()),
((SELECT id FROM shop_customer WHERE username = 'jane_smith'), 'DEBIT_CARD', '87654321', NOW())
ON CONFLICT DO NOTHING;

-- Insert transactions without uuid_generate_v4()
INSERT INTO shop_transaction (order_id, payment_method_id, customer_id, transaction_id, amount, transaction_date, stripe_payment_intent_id) VALUES
((SELECT id FROM shop_order WHERE customer_id = (SELECT id FROM shop_customer WHERE username = 'john_doe') AND status = 'PENDING' LIMIT 1),
 (SELECT id FROM shop_payment_method WHERE customer_id = (SELECT id FROM shop_customer WHERE username = 'john_doe') AND method_type = 'CREDIT_CARD' LIMIT 1),
 (SELECT id FROM shop_customer WHERE username = 'john_doe'),
 '11111111-1111-1111-1111-111111111111', 19.97, NOW(), 'pi_123456789'),
((SELECT id FROM shop_order WHERE customer_id = (SELECT id FROM shop_customer WHERE username = 'jane_smith') AND status = 'PENDING' LIMIT 1),
 (SELECT id FROM shop_payment_method WHERE customer_id = (SELECT id FROM shop_customer WHERE username = 'jane_smith') AND method_type = 'DEBIT_CARD' LIMIT 1),
 (SELECT id FROM shop_customer WHERE username = 'jane_smith'),
 '22222222-2222-2222-2222-222222222222', 9.98, NOW(), 'pi_987654321')
ON CONFLICT (transaction_id) DO NOTHING;

-- Insert product ratings
INSERT INTO shop_product_rating (customer_id, product_id, rating, rated_at) VALUES
((SELECT id FROM shop_customer WHERE username = 'john_doe'), (SELECT id FROM shop_product WHERE name = 'Apple' LIMIT 1), 5, NOW()),
((SELECT id FROM shop_customer WHERE username = 'jane_smith'), (SELECT id FROM shop_product WHERE name = 'Milk' LIMIT 1), 4, NOW())
ON CONFLICT DO NOTHING;

-- Insert product recommendations
INSERT INTO shop_product_recommendation (product_id, recommended_product_id) VALUES
((SELECT id FROM shop_product WHERE name = 'Apple' LIMIT 1), (SELECT id FROM shop_product WHERE name = 'Banana' LIMIT 1)),
((SELECT id FROM shop_product WHERE name = 'Milk' LIMIT 1), (SELECT id FROM shop_product WHERE name = 'Bread' LIMIT 1))
ON CONFLICT (product_id, recommended_product_id) DO NOTHING;

-- Insert cart items
INSERT INTO shop_cart_item (customer_id, product_id, quantity, added_at) VALUES
    ((SELECT id FROM shop_customer WHERE username = 'john_doe'), 
     (SELECT id FROM shop_product WHERE name = 'Apple' LIMIT 1), 
     2, NOW()),
     
    ((SELECT id FROM shop_customer WHERE username = 'john_doe'), 
     (SELECT id FROM shop_product WHERE name = 'Milk' LIMIT 1), 
     1, NOW()),
     
    ((SELECT id FROM shop_customer WHERE username = 'jane_smith'), 
     (SELECT id FROM shop_product WHERE name = 'Banana' LIMIT 1), 
     3, NOW())
ON CONFLICT DO NOTHING;

-- Execute the script using psql
-- psql -U postgres -d greencart -f /Users/lokesh/Desktop/greencart-microservices/django_backend/insert_dummy_data.sql
