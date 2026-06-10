# Munich Retail Sales Data Warehouse

## Project Overview

This project implements a dimensional data warehouse model for retail sales data from Munich stores.

The solution includes:

- Dimensional star schema design
- PostgreSQL database deployment
- Python ETL pipeline
- Data cleaning and transformation
- Dockerized database setup

---

## Architecture

```text
CSV File → Python ETL Pipeline → PostgreSQL Data Warehouse
```

---

## Technologies Used

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Docker
- DBeaver

---

## Data Model

The warehouse follows a star schema design optimized for analytical reporting and business intelligence workloads.

### Fact Table

#### `fact_sales`

Contains transactional sales records and measurable business metrics.

Main measures include:

- quantity
- unit_price
- discount_rate
- total_amount
- tax_amount

The fact table references all dimension tables through foreign keys.

---

### Dimension Tables

#### `dim_date`

Stores calendar and date-related attributes.

#### `dim_store`

Stores store information including:
- store name
- location
- district
- store type

#### `dim_customer`

Stores customer and loyalty information.

#### `dim_product`

Stores product hierarchy and classification data including:
- category
- subcategory
- brand
- department

#### `dim_supplier`

Stores supplier information.

#### `dim_sales_staff`

Stores sales employee information.

#### `dim_promotion`

Stores promotion and campaign information.

---

## Entity Relationship Diagram (ERD)

The ERD diagram is located in:

```text
docs/ERD.png
```

---

## Project Structure

```text
oliva-retail-project/
│
├── data/
│   └── munich_retail_sales_raw.csv
│
├── docs/
│   └── ERD.png
│
├── sql/
│   └── schema.sql
│
├── src/
│   └── pipeline.py
│
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Database Setup

PostgreSQL is deployed using Docker.

### Start PostgreSQL Container

```bash
docker compose up -d
```

---

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Run ETL Pipeline

```bash
python src/pipeline.py
```

The ETL pipeline performs:

1. CSV extraction
2. Data cleaning and transformation
3. Dimension table creation
4. Fact table creation
5. Data loading into PostgreSQL

---

## Data Cleaning & Transformation

The following transformations were applied:

- Duplicate removal
- Null value handling
- Mixed date format conversion
- Text standardization
- Dimension deduplication
- Surrogate key generation

---

## Assumptions

The following assumptions were made during implementation:

- Missing loyalty status values were set to `"Unknown"`
- Missing promotions were set to `"No Promotion"`
- Missing discount flags were set to `False`
- Duplicate business entities were standardized and deduplicated
- Invalid transaction dates were removed

---

## Database Connection

| Parameter | Value |

| Host | localhost |
| Port | 5432 |
| Database | retail_dw |
| Username | oliva |

---

## Verification

The warehouse was validated by:

- Successful ETL execution
- Verification of dimension and fact table loads
- SQL validation queries executed in DBeaver

Example validation query:

```sql
SELECT COUNT(*) FROM fact_sales;
```

Result:

```text
35612 rows loaded
```

---

## Future Improvements

Potential future improvements include:

- Incremental loading support
- Additional indexing optimization
- Automated testing
- Workflow orchestration
- Enhanced logging

## Power BI Dashboard

A Power BI dashboard file is included in the repository:

- MunichRetailDashboard.pbix

The dashboard connects to the PostgreSQL warehouse and provides example retail analytics visualizations.

## Improvments made:
- Suspicious transactions are flagged into a separate `data_quality_issues` table for review without deleting source records.