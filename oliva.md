\## 1. What the task was



I received a denormalized CSV file containing retail sales data from multiple stores in Munich. The file included transactional information together with store data, product details, customer information, supplier data, promotions, and sales staff information all combined into one flat structure. The goal was to analyze the dataset, design a proper dimensional data model, deploy it to a relational database, and build a Python ETL pipeline to clean, transform, and load the data into the warehouse.





\## 2. What you built



I built a small retail sales data warehouse using PostgreSQL as the database. PostgreSQL was deployed locally using Docker to create a reproducible and portable setup without requiring a manual database installation.



I implemented the ETL pipeline in Python using Pandas for data transformation and cleaning operations. SQLAlchemy was used **(Without SQLAlchemy, pandas cannot easily write to PostgreSQL. I used SQLAlchemy because it provides a clean abstraction layer between Python and PostgreSQL and integrates very well with pandas.)**
as the connection layer between Python and PostgreSQL, allowing the pipeline to create connections and load data into the warehouse tables.



I also created a SQL schema script 
(**idempotent -- drop if )**
that defines the warehouse structure, including fact and dimension tables, primary keys, foreign keys, and constraints. Finally, the entire solution was documented and uploaded to GitHub for version control and submission.





\## 3. Data analysis and issues discovered



The first step was inspecting the raw CSV structure and analyzing the quality of the data. During this process, several data quality issues were identified.



The dataset contained mixed date formats inside the transaction date column, which initially caused parsing errors during transformation. Some customer-related fields contained missing values because not every transaction was associated with a registered customer. Promotion information was also missing for many transactions, which indicated purchases without active promotions.



In addition, some business entities contained inconsistent text formatting. For example, store types and categories appeared with different casing formats such as uppercase, lowercase, and mixed case. This created duplicate dimension entries during loading.



Another issue involved datatype inconsistencies between pandas and PostgreSQL, especially around ID columns and discount fields. During testing, it became clear that `discount\_applied` represented a boolean flag rather than a numeric amount, so the schema and transformation logic were adjusted accordingly.



These issues were handled during the transformation stage through standardization, deduplication, null handling, datatype conversion, and validation logic.





\## 4. Data model design



After analyzing the dataset, I separated the data into business entities and designed a dimensional star schema optimized for analytical reporting.



I chose a star schema because the dataset and reporting requirements were relatively straightforward. A star schema simplifies analytical querying and is commonly preferred for BI workloads due to its simplicity and performance advantages.



Snowflaking would increase normalization and reduce redundancy slightly, but it would also increase query complexity without significant benefit for this use case.



The central table is the `fact\_sales` table, which stores the transactional sales events and measurable business metrics such as quantity, unit price, discounts, total amount, and tax values.



Around the fact table, several dimension tables were created to store descriptive business information. These included dimensions for stores, customers, products, suppliers, sales staff, promotions, and dates.



This design reduces redundancy, improves maintainability, and supports efficient analytical querying and reporting workloads.





\## 5. Why a star schema was used



I chose a star schema because the assignment focuses on retail analytics and reporting. A star schema is well suited for business intelligence workloads because it simplifies queries, improves readability, and separates descriptive business entities from measurable transactional events.



Compared to a fully normalized transactional model, the star schema provides a simpler and more efficient structure for reporting and aggregation.





\## 6. ETL pipeline process



The ETL pipeline was implemented in Python and follows the standard Extract, Transform, Load process.



During extraction, the CSV file is read into pandas dataframes. During transformation, the pipeline performs duplicate removal, mixed date conversion, text standardization, null handling, datatype correction, and dimension deduplication.



The pipeline then creates surrogate key relationships by loading dimension tables first and reading back generated keys before building the final fact table.



Finally, the cleaned and transformed data is loaded into PostgreSQL tables through SQLAlchemy connections.





\## 7. Database deployment and validation

Docker was used to create a reproducible PostgreSQL environment that can be started consistently on any machine without requiring manual database installation or configuration.



PostgreSQL was deployed locally using Docker Compose. This allowed the database environment to be started quickly and consistently using a simple container configuration.



After loading the warehouse, the results were validated using DBeaver by querying the tables directly. The final fact table successfully loaded 35,612 sales records, and relationships between fact and dimension tables were verified through SQL queries.





\## 8. Improvements you could mention



With additional time, I would extend the solution by adding incremental loading support, automated testing, logging, indexing optimization, and workflow orchestration tools such as Airflow or dbt. I would also add more formal data quality validation rules and monitoring.











\# **SQL Cheat Sheet For Your Meeting**



\# 1. Show first 10 rows



SELECT \*

FROM fact\_sales

LIMIT 10;



\# 2. Count total rows





SELECT COUNT(\*)

FROM fact\_sales;



\# 3. Total revenue



SELECT SUM(total\_amount)

FROM fact\_sales;



\# 4. Average transaction value



SELECT AVG(total\_amount)

FROM fact\_sales;



\# 5. Revenue by store



SELECT

&#x20;   ds.store\_name,

&#x20;   SUM(fs.total\_amount) AS revenue

FROM fact\_sales fs

JOIN dim\_store ds

&#x20;   ON fs.store\_key = ds.store\_key

GROUP BY ds.store\_name

ORDER BY revenue DESC;



\# 6. Top selling products



SELECT

&#x20;   dp.product\_name,

&#x20;   SUM(fs.quantity) AS total\_quantity

FROM fact\_sales fs

JOIN dim\_product dp

&#x20;   ON fs.product\_key = dp.product\_key

GROUP BY dp.product\_name

ORDER BY total\_quantity DESC

LIMIT 10;



\# 7. Sales by payment method



SELECT

&#x20;   payment\_method,

&#x20;   COUNT(\*) AS transactions

FROM fact\_sales

GROUP BY payment\_method

ORDER BY transactions DESC;



\# 8. Revenue by month



SELECT

&#x20;   dd.year,

&#x20;   dd.month,

&#x20;   SUM(fs.total\_amount) AS revenue

FROM fact\_sales fs

JOIN dim\_date dd

&#x20;   ON fs.date\_key = dd.date\_key

GROUP BY dd.year, dd.month

ORDER BY dd.year, dd.month;



\# 9. Products ordered alphabetically



SELECT \*

FROM dim\_product

ORDER BY product\_name;



\# 10. Find suspicious “Copy of” products



SELECT \*

FROM dim\_product

WHERE product\_name ILIKE '%copy%';



\# Most Important SQL Keywords



| Keyword  | Meaning        |

| -------- | -------------- |

| SELECT   | choose columns |

| FROM     | choose table   |

| WHERE    | filter rows    |

| GROUP BY | aggregate data |

| ORDER BY | sort           |

| JOIN     | combine tables |

| SUM      | add values     |

| COUNT    | count rows     |

| AVG      | average        |

| LIMIT    | top N rows     |





\# Very Important JOIN Concept



Example:





JOIN dim\_product dp

ON fs.product\_key = dp.product\_key



Meaning:



Connect fact\_sales with dim\_product

using the shared key.



This is probably the most important warehouse concept.



During validation I identified several extreme outlier transactions caused by unusually large quantities combined with negative unit prices in the source dataset. Since the ETL logic preserved source transactional integrity, these records were loaded as-is, but in a production environment I would implement additional business validation rules or anomaly detection thresholds.





