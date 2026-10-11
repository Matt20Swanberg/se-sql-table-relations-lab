"""
SQL Table Relations Lab

This project demonstrates how to query a relational SQLite database
using SQL and Pandas.

The exercises cover:
- INNER JOIN and LEFT JOIN operations
- Filtering records with WHERE
- Identifying unmatched records with IS NULL
- Sorting results with ORDER BY
- Aggregate functions (COUNT, SUM, AVG)
- Grouping and filtering with GROUP BY and HAVING
- Counting unique values with DISTINCT
- Using subqueries to filter related records

Each query stores its results in a Pandas DataFrame for further analysis.
"""

# STEP 0: Database Setup
# ------------------------------------------------------------

# Import SQLite for database connections and Pandas for SQL queries.
import sqlite3
import pandas as pd

# Establish a connection to the SQLite database.
conn = sqlite3.connect('data.sqlite')

# Retrieve database metadata, including tables and indexes.
# Useful for inspecting the database structure during development.
data = pd.read_sql("""SELECT * FROM sqlite_master""", conn)
# print(data)


# STEP 1: Find Employees Working in Boston
# ------------------------------------------------------------

# Use INNER JOIN to connect employees with their office locations.
# Filter the results to include only employees working in Boston.
# Return each employee's first and last name.
df_boston = pd.read_sql("""
SELECT firstName, lastName
FROM employees
INNER JOIN offices
ON employees.officeCode = offices.officeCode
WHERE offices.city = 'Boston'
""", conn)
# For Debugging
# print(df_boston)


# STEP 2: Find Offices Without Employees
# ------------------------------------------------------------

# Use LEFT JOIN to include all offices, even those without employees.
# Filter for NULL employee office codes to identify offices with
# no matching employee records.
# Return the office code and city.
df_zero_emp = pd.read_sql("""
SELECT offices.officeCode, city FROM offices
LEFT JOIN employees
ON offices.officeCode = employees.officeCode
WHERE employees.officeCode IS NULL
""", conn)
# For Debugging
# print(df_zero_emp)


# STEP 3: Retrieve Employees and Their Office Locations
# ------------------------------------------------------------

# Use LEFT JOIN to retrieve all employees and their office details,
# including employees who may not have a matching office record.
# Return employee names, office city, and state.
# Sort alphabetically by first name, followed by last name.
df_employee = pd.read_sql("""
SELECT firstName, lastName, offices.city, offices.state from employees
LEFT JOIN offices
ON employees.officeCode = offices.officeCode
ORDER BY firstName ASC, lastName ASC
""", conn)
# For Debugging
# print(df_employee)


# STEP 4: Identify Customers Without Orders
# ------------------------------------------------------------

# Use LEFT JOIN to include all customers regardless of order history.
# Filter for NULL order numbers to identify customers who have
# never placed an order.
# Return customer contact information and assigned sales representative.
# Sort the results alphabetically by contact last name.
df_contacts = pd.read_sql("""
SELECT contactFirstName, contactLastName, phone, salesRepEmployeeNumber FROM customers
LEFT JOIN orders
ON customers.customerNumber = orders.customerNumber
WHERE orders.orderNumber IS NULL
ORDER BY contactLastName ASC
""", conn)
# For Debugging
# print(df_contacts)

# Further debugging: Verify the number of customers without orders.
# print(len(df_contacts))

# STEP 5: Retrieve Customer Payment Information
# ------------------------------------------------------------

# Use INNER JOIN to connect customer records with their payments.
# Return contact names, payment amounts, and payment dates.
# Cast payment amounts to REAL to ensure numeric sorting.
# Sort payments from highest to lowest amount.
df_payment = pd.read_sql("""
SELECT contactFirstName, contactLastName, payments.amount, payments.paymentDate
FROM customers
INNER JOIN payments
ON customers.customerNumber = payments.customerNumber
ORDER BY CAST(payments.amount AS REAL) DESC
""", conn)
# For Debugging
# print(df_payment)


# STEP 6: Identify Sales Representatives with High-Credit Customers
# ------------------------------------------------------------

# Use INNER JOIN to connect employees with their assigned customers.
# Group customers by their assigned sales representative.
# COUNT calculates the total number of customers per employee.
# HAVING filters for employees whose customers have an average
# credit limit greater than 90,000.
# Sort employees by customer count in descending order.
df_credit = pd.read_sql("""
SELECT employeeNumber, firstName, lastName, COUNT(customers.customerNumber) AS customer_total
FROM employees
INNER JOIN customers
ON employees.employeeNumber = customers.salesRepEmployeeNumber
GROUP BY employeeNumber
HAVING AVG(creditLimit) > 90000
ORDER BY customer_total DESC
""", conn)
# For Debugging
# print(df_credit)


# STEP 7: Analyze Product Sales and Order Quantities
# ------------------------------------------------------------

# Use INNER JOIN to connect products with their order details.
# Group records by product code to calculate sales activity.
# COUNT determines the number of order-detail records per product.
# SUM calculates the total quantity of units ordered.
# Sort products by total units sold, from highest to lowest.
df_product_sold = pd.read_sql("""
SELECT
    productName,
    COUNT(orderdetails.orderNumber) AS numorders,
    SUM(orderdetails.quantityOrdered) AS totalunits
FROM products
INNER JOIN orderdetails
ON products.productCode = orderdetails.productCode
GROUP BY products.productCode
ORDER BY totalunits DESC
""", conn)
# For Debugging
# print(df_product_sold)


# STEP 8: Count Unique Customers Purchasing Each Product
# ------------------------------------------------------------

# Connect products to order details and customer orders.
# Group records by product code.
# COUNT(DISTINCT) calculates the number of unique customers
# who purchased each product, avoiding duplicate customer counts.
# Sort products by the number of unique purchasers in descending order.
df_total_customers = pd.read_sql("""
SELECT
    productName, products.productCode,
    COUNT(DISTINCT orders.customerNumber) AS numpurchasers
FROM products
INNER JOIN orderdetails
ON products.productCode = orderdetails.productCode
INNER JOIN orders
ON orders.orderNumber = orderdetails.orderNumber
GROUP BY products.productCode
ORDER BY numpurchasers DESC
""", conn)
# For Debugging
# print(df_total_customers)


# STEP 9: Calculate Customer Counts by Office
# ------------------------------------------------------------

# Use LEFT JOIN to connect offices with employees and their customers.
# LEFT JOIN ensures offices remain in the results even if they
# have no assigned employees or customers.
# COUNT(customers.customerNumber) calculates the number of customers
# associated with each office, returning zero for unmatched records.
# Group the results by office code.
df_customers = pd.read_sql("""
SELECT
    COUNT(customers.customerNumber) AS n_customers,
    offices.officeCode, offices.city
FROM offices
LEFT JOIN employees
ON offices.officeCode = employees.officeCode
LEFT JOIN customers
ON employees.employeeNumber = customers.salesRepEmployeeNumber
GROUP BY offices.officeCode
""", conn)
# For Debugging
# print(df_customers)


# STEP 10: Identify Employees Associated with Underperforming Products
# ------------------------------------------------------------

# Retrieve employees associated with orders containing products
# purchased by fewer than 20 unique customers.
#
# Main Query:
# - Connect employees to customers, orders, order details, and offices.
# - Retrieve employee numbers, names, and office locations.
# - Use SELECT DISTINCT to prevent duplicate employee records.
#
# Subquery:
# - Connect products with order details and orders.
# - Group records by product code.
# - COUNT(DISTINCT) identifies the number of unique customers
#   who purchased each product.
# - HAVING filters for products purchased by fewer than 20 customers.
#
# WHERE IN:
# - Restricts the main query to orders containing product codes
#   returned by the subquery.
#
# Sort the final results alphabetically by employee last name.
df_under_20 = pd.read_sql("""
SELECT DISTINCT
    employees.employeeNumber,
    employees.firstName,
    employees.lastName,
    offices.city,
    offices.officeCode
FROM employees
INNER JOIN customers
ON employees.employeeNumber = customers.salesRepEmployeeNumber
INNER JOIN orders
ON customers.customerNumber = orders.customerNumber
INNER JOIN orderDetails
ON orders.orderNumber = orderDetails.orderNumber
INNER JOIN offices
ON employees.officeCode = offices.officeCode
WHERE orderDetails.productCode IN (
    SELECT
        products.productCode
    FROM products
    INNER JOIN orderDetails
    ON products.productCode = orderDetails.productCode
    INNER JOIN orders
    ON orderDetails.orderNumber = orders.orderNumber
    GROUP BY products.productCode
    HAVING COUNT(DISTINCT orders.customerNumber) < 20
)
ORDER BY employees.lastName ASC
""", conn)

# For Debugging: Display the final results in a readable table without DataFrame indexes.
print(df_under_20.to_string(index=False))


# DATABASE CLEANUP
# ------------------------------------------------------------

# Close the SQLite connection after completing all queries
# to release database resources.
conn.close()
