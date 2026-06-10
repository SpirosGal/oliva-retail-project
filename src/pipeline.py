import pandas as pd
from sqlalchemy import create_engine, text
import logging
pd.set_option('future.no_silent_downcasting', True)

# Database connection
DB_URL = "postgresql://oliva:oliva@localhost:5432/retail_dw"
engine = create_engine(DB_URL)
logging.basicConfig(
    filename="etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("ETL pipeline started")
# -----------------------------
# EXTRACT
# -----------------------------
df = pd.read_csv("data/munich_retail_sales_raw.csv")
print("CSV loaded successfully.")
logging.info("CSV loaded successfully.")

# -----------------------------
# TRANSFORM: BASIC CLEANING
# -----------------------------
df = df.drop_duplicates()

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    format="mixed",
    errors="coerce"
)

df = df.dropna(subset=["transaction_date"])
df["discount_applied"] = (
    df["discount_applied"]
    .fillna(False)
    .infer_objects(copy=False)
)
df["customer_loyalty_status"] = df["customer_loyalty_status"].fillna("Unknown")
df["product_department"] = df["product_department"].fillna("Unknown")
df["promotion_id"] = df["promotion_id"].fillna(0)
df["promotion_name"] = df["promotion_name"].fillna("No Promotion")

# Fill missing numeric values
df["quantity"] = df["quantity"].fillna(0)

# If unit_price is missing, derive it from base_price and discount_rate.
# Existing unit_price values are preserved.
df["unit_price"] = df["unit_price"].fillna(
    df["base_price"] * (1 - df["discount_rate"])
)

# If total_amount is missing, derive it from quantity and unit_price.
# Existing total_amount values are preserved.
df["total_amount"] = df["total_amount"].fillna(
    df["quantity"] * df["unit_price"]
)

# -----------------------------
# DATA QUALITY VALIDATION
# -----------------------------
df["calculated_total_amount"] = df["quantity"] * df["unit_price"]

suspicious_rows = df[
    (df["quantity"] < 0) |
    (df["quantity"] > 1000) |
    (df["unit_price"] < -1000) |
    (df["unit_price"] > 10000) |
    (df["total_amount"].abs() > 10000)
].copy()

print(f"Suspicious rows found: {len(suspicious_rows)}")
logging.info("Suspicious rows found: {len(suspicious_rows)}")
# -----------------------------
# STANDARDIZE ID TYPES
# -----------------------------
id_columns = [
    "customer_id",
    "product_id",
    "supplier_id",
    "sales_staff_id",
    "promotion_id",
    "store_id"
]

for col in id_columns:
    df[col] = df[col].astype("Int64").astype(str)
    df[col] = df[col].replace("<NA>", None)

# -----------------------------
# TRANSFORM: STANDARDIZE TEXT
# -----------------------------
text_columns = [
    "store_name",
    "store_location",
    "store_type",
    "district_name",
    "customer_name",
    "customer_email",
    "customer_loyalty_status",
    "product_name",
    "product_category",
    "product_subcategory",
    "product_brand",
    "product_department",
    "supplier_name",
    "sales_staff_name",
    "promotion_name",
    "payment_method",
    "transaction_status"
]

for col in text_columns:
    df[col] = df[col].astype(str).str.strip()

df["store_type"] = df["store_type"].str.upper()
df["product_category"] = df["product_category"].str.upper()
df["product_brand"] = df["product_brand"].str.upper()
df["customer_loyalty_status"] = df["customer_loyalty_status"].str.upper()

print("Data cleaned.")
logging.info("Data cleaned.")
# -----------------------------
# LOAD: CREATE SCHEMA
# -----------------------------
with open("sql/schema.sql", "r") as file:
    schema_sql = file.read()

with engine.connect() as conn:
    conn.execute(text(schema_sql))
    conn.commit()

print("Schema created.")
logging.info("Schema created")
suspicious_rows.to_sql(
    "data_quality_issues",
    engine,
    if_exists="replace",
    index=False
)

print("Data quality issues table loaded.")
logging.info("Data quality issues table loaded.")
# -----------------------------
# CREATE DIMENSION TABLES
# -----------------------------

# Date dimension
dim_date = pd.DataFrame({
    "full_date": df["transaction_date"].dt.date
}).drop_duplicates()

dim_date["date_key"] = dim_date["full_date"].apply(
    lambda x: int(x.strftime("%Y%m%d"))
)

dim_date["year"] = pd.to_datetime(dim_date["full_date"]).dt.year
dim_date["month"] = pd.to_datetime(dim_date["full_date"]).dt.month
dim_date["day"] = pd.to_datetime(dim_date["full_date"]).dt.day
dim_date["weekday"] = pd.to_datetime(dim_date["full_date"]).dt.day_name()

# Store dimension
dim_store = df[
    [
        "store_id",
        "store_name",
        "store_location",
        "store_type",
        "store_size_sqm",
        "district_id",
        "district_name",
        "postal_code"
    ]
].drop_duplicates(subset=["store_id"])

# Customer dimension
dim_customer = df[
    [
        "customer_id",
        "customer_name",
        "customer_email",
        "customer_loyalty_status"
    ]
].drop_duplicates(subset=["customer_id"])

dim_customer = dim_customer.dropna(subset=["customer_id"])

# Product dimension
dim_product = df[
    [
        "product_id",
        "product_name",
        "product_category",
        "product_subcategory",
        "product_brand",
        "product_department"
    ]
].drop_duplicates(subset=["product_id"])

# Supplier dimension
dim_supplier = df[
    [
        "supplier_id",
        "supplier_name"
    ]
].drop_duplicates(subset=["supplier_id"])

# Sales staff dimension
dim_sales_staff = df[
    [
        "sales_staff_id",
        "sales_staff_name"
    ]
].drop_duplicates(subset=["sales_staff_id"])

# Promotion dimension
dim_promotion = df[
    [
        "promotion_id",
        "promotion_name"
    ]
].drop_duplicates(subset=["promotion_id"])

print("Dimension tables created.")
logging.info("Dimension tables created.")
# -----------------------------
# LOAD DIMENSIONS
# -----------------------------
dim_date.to_sql("dim_date", engine, if_exists="append", index=False)
dim_store.to_sql("dim_store", engine, if_exists="append", index=False)
dim_customer.to_sql("dim_customer", engine, if_exists="append", index=False)
dim_product.to_sql("dim_product", engine, if_exists="append", index=False)
dim_supplier.to_sql("dim_supplier", engine, if_exists="append", index=False)
dim_sales_staff.to_sql("dim_sales_staff", engine, if_exists="append", index=False)
dim_promotion.to_sql("dim_promotion", engine, if_exists="append", index=False)

print("Dimensions loaded.")
logging.info("Dimensions loaded.")
# -----------------------------
# READ BACK SURROGATE KEYS
# -----------------------------
store_keys = pd.read_sql("SELECT store_key, store_id FROM dim_store", engine)
customer_keys = pd.read_sql("SELECT customer_key, customer_id FROM dim_customer", engine)
product_keys = pd.read_sql("SELECT product_key, product_id FROM dim_product", engine)
supplier_keys = pd.read_sql("SELECT supplier_key, supplier_id FROM dim_supplier", engine)
staff_keys = pd.read_sql("SELECT sales_staff_key, sales_staff_id FROM dim_sales_staff", engine)
promotion_keys = pd.read_sql("SELECT promotion_key, promotion_id FROM dim_promotion", engine)

# -----------------------------
# BUILD FACT TABLE
# -----------------------------
fact_sales = df.copy()

fact_sales["date_key"] = fact_sales["transaction_date"].apply(
    lambda x: int(pd.to_datetime(x).strftime("%Y%m%d"))
)

fact_sales = fact_sales.merge(store_keys, on="store_id", how="left")
fact_sales = fact_sales.merge(customer_keys, on="customer_id", how="left")
fact_sales = fact_sales.merge(product_keys, on="product_id", how="left")
fact_sales = fact_sales.merge(supplier_keys, on="supplier_id", how="left")
fact_sales = fact_sales.merge(staff_keys, on="sales_staff_id", how="left")
fact_sales = fact_sales.merge(promotion_keys, on="promotion_id", how="left")

fact_sales = fact_sales[
    [
        "transaction_id",
        "invoice_number",
        "date_key",
        "store_key",
        "customer_key",
        "product_key",
        "supplier_key",
        "sales_staff_key",
        "promotion_key",
        "transaction_time",
        "transaction_status",
        "quantity",
        "unit_price",
        "base_price",
        "discount_rate",
        "discount_applied",
        "total_amount",
        "tax_rate",
        "tax_amount",
        "payment_method"
    ]
]

# -----------------------------
# LOAD FACT TABLE
# -----------------------------
fact_sales.to_sql(
    "fact_sales",
    engine,
    if_exists="append",
    index=False
)

print("Fact table loaded.")
logging.info("Fact table loaded.")
print("ETL pipeline completed successfully.")
logging.info("ETL pipeline completed successfully.")
