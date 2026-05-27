DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_promotion;
DROP TABLE IF EXISTS dim_sales_staff;
DROP TABLE IF EXISTS dim_supplier;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    weekday TEXT
);

CREATE TABLE dim_store (
    store_key SERIAL PRIMARY KEY,
    store_id TEXT UNIQUE NOT NULL,
    store_name TEXT,
    store_location TEXT,
    store_type TEXT,
    store_size_sqm INTEGER,
    district_id INTEGER,
    district_name TEXT,
    postal_code TEXT
);

CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id TEXT UNIQUE,
    customer_name TEXT,
    customer_email TEXT,
    customer_loyalty_status TEXT
);

CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id TEXT UNIQUE NOT NULL,
    product_name TEXT,
    product_category TEXT,
    product_subcategory TEXT,
    product_brand TEXT,
    product_department TEXT
);

CREATE TABLE dim_supplier (
    supplier_key SERIAL PRIMARY KEY,
    supplier_id TEXT UNIQUE NOT NULL,
    supplier_name TEXT
);

CREATE TABLE dim_sales_staff (
    sales_staff_key SERIAL PRIMARY KEY,
    sales_staff_id TEXT UNIQUE NOT NULL,
    sales_staff_name TEXT
);

CREATE TABLE dim_promotion (
    promotion_key SERIAL PRIMARY KEY,
    promotion_id TEXT UNIQUE,
    promotion_name TEXT
);

CREATE TABLE fact_sales (
    sales_key SERIAL PRIMARY KEY,
    transaction_id TEXT UNIQUE NOT NULL,
    invoice_number TEXT,
    date_key INTEGER REFERENCES dim_date(date_key),
    store_key INTEGER REFERENCES dim_store(store_key),
    customer_key INTEGER REFERENCES dim_customer(customer_key),
    product_key INTEGER REFERENCES dim_product(product_key),
    supplier_key INTEGER REFERENCES dim_supplier(supplier_key),
    sales_staff_key INTEGER REFERENCES dim_sales_staff(sales_staff_key),
    promotion_key INTEGER REFERENCES dim_promotion(promotion_key),
    transaction_time TIME,
    transaction_status TEXT,
    quantity INTEGER,
    unit_price NUMERIC(10,2),
    base_price NUMERIC(10,2),
    discount_rate NUMERIC(5,2),
    discount_applied BOOLEAN,
    total_amount NUMERIC(10,2),
    tax_rate NUMERIC(5,2),
    tax_amount NUMERIC(10,2),
    payment_method TEXT
);


