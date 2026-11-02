# Online Retail Sales Analysis
### Data Analytics Portfolio Project

**Author:** Haider  
**Tools:** Python, Pandas, Power BI  
**Project:** Project Ecom First

## 1. Project Overview
This project analyzes an online retail transaction dataset to understand sales patterns, product performance, country-level sales, and business trends.

The objective is to transform raw transactional data into meaningful business insights that can support data-driven decision-making.

## 2. Business Objectives
- Understand overall sales performance.
- Analyze monthly sales trends.
- Identify top-performing products.
- Compare sales across countries.
- Investigate unusual manual transactions.
- Build an interactive Power BI dashboard.

## 3. Dataset Overview
The project uses the Online Retail dataset containing transactions from December 2010 to December 2011.

The original dataset contains 541,909 rows and 8 columns.

**Main columns:**
- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country

## 4. Tools and Technologies
- **Python:** Data inspection and analysis.
- **Pandas:** Data manipulation and cleaning.
- **Power BI:** Interactive dashboard and visualization.
- **CSV:** Storage of analysis outputs.

## 5. Data Cleaning
The cleaning process included:
- Identifying and removing exact duplicate rows.
- Inspecting missing values.
- Checking invalid dates.
- Investigating negative quantities.
- Examining zero and negative unit prices.
- Creating a LineAmount calculation using Quantity × UnitPrice.

After removing 5,268 extra duplicate rows, the cleaned dataset contained 536,641 rows.

## 6. Exploratory Data Analysis
The analysis explored:
- Monthly sales trends.
- Country-level sales performance.
- Product-level sales performance.
- Manual transaction patterns.
- May and June transaction comparisons.

## 7. Business Insights
The analysis identified:
- The United Kingdom had the largest sales contribution.
- November 2011 had the highest monthly net sales in the dataset.
- Product-level analysis highlighted the highest-value product descriptions.
- Manual transactions required further investigation and business context.

## 8. Power BI Dashboard
An interactive dashboard was created to explore:
- Net Sales
- Total Transactions
- Unique Customers
- Monthly Net Sales
- Top 10 Countries
- Top 10 Products
- Country and Date filters

The dashboard screenshot is included in this repository.

## 9. Important Data Limitations
- The dataset ends on 9 December 2011, so December represents a partial month.
- Missing CustomerID values limit customer-level analysis.
- Negative quantities and manual transactions require business context.
- A discrepancy was identified between Python/Power Query and Power BI product counts. The unique product KPI was therefore excluded from the final dashboard pending validation.
- Net LineAmount should not automatically be interpreted as profit.

## 10. Project Conclusion
This project demonstrates a practical data analytics workflow, from raw data inspection and cleaning to exploratory analysis, business insights, and interactive dashboard development.

It represents my first end-to-end Data Analytics portfolio project.

## 11. Project Files
The repository includes:
- Python data inspection script.
- Phase 4 business analysis CSV outputs.
- Additional analysis output CSV files.
- Power BI dashboard screenshot.
- Project analysis report.

---

**Project Ecom First | Data Analytics Portfolio | Haider**
