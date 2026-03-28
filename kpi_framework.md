# KPI Framework — Amman Digital Market

---

## KPI 1 — Monthly Revenue (Time-Based)

- **Name:** Monthly Total Revenue
- **Definition:** The total revenue generated from all non-cancelled orders in a given calendar month, excluding items with suspicious quantities (> 100 units).
- **Formula:** `SUM(quantity × unit_price)` grouped by `YEAR-MONTH(order_date)`
- **Data Source:** `order_items.quantity`, `products.unit_price`, `orders.order_date`, `orders.status`
- **Baseline Value:** Ranges from 2,021.00 JOD (May 2025) to 5,086.50 JOD (June 2025); the 2024 average is approximately 2,489 JOD/month.
- **Interpretation:** Monthly revenue is broadly stable through 2024 (2,100–2,720 JOD), with two notable spikes in March 2025 (+79%) and June 2025 (+152%). These spikes likely reflect seasonal demand or promotional activity and should be investigated to understand whether they are repeatable.

---

## KPI 2 — Month-over-Month Revenue Growth Rate (Time-Based)

- **Name:** Month-over-Month (MoM) Revenue Growth Rate
- **Definition:** The percentage change in total revenue from one month to the previous month, indicating acceleration or deceleration in business activity.
- **Formula:** `(current_month_revenue − previous_month_revenue) / previous_month_revenue × 100`
- **Data Source:** Derived from KPI 1 monthly revenue series (`orders.order_date`, `order_items`, `products.unit_price`)
- **Baseline Value:** MoM growth across the period ranges from −39.4% (April 2025) to +151.7% (June 2025). The 2024 average MoM change is approximately −0.5%, indicating a near-flat trend through the year.
- **Interpretation:** 2024 is characterised by low-volatility oscillations around zero growth — the market is stable but not expanding. The large positive spikes in early and mid-2025 are followed by sharp drops, suggesting irregular demand events rather than sustained growth. Consistent positive MoM growth above 5% would indicate a healthy expansion trajectory.

---

## KPI 3 — Revenue by City (Cohort-Based)

- **Name:** Total Revenue by Customer City
- **Definition:** The total revenue attributed to customers in each city, segmented as a cohort by their registered city. Customers with NULL city are excluded.
- **Formula:** `SUM(quantity × unit_price)` grouped by `customers.city`
- **Data Source:** `customers.city`, `order_items.quantity`, `products.unit_price`, `orders.order_id`
- **Baseline Value:**

  | City   | Revenue (JOD) |
  |--------|--------------|
  | Amman  | 15,719.00    |
  | Irbid  | 7,250.50     |
  | Zarqa  | 4,842.00     |
  | Madaba | 4,691.00     |
  | Salt   | 4,477.00     |
  | Aqaba  | 4,167.50     |

- **Interpretation:** Amman generates more than twice the revenue of Irbid, the second-ranked city, and roughly 3.4× more than Aqaba. This is partly explained by Amman's larger customer base. However, a Welch's t-test (t = 0.63, p = 0.527) shows that the **per-order** revenue between Amman and Irbid is not statistically different (Cohen's d = 0.094, negligible effect size) — meaning Amman's total revenue advantage comes from **order volume**, not higher-value individual orders. Growing the customer base in smaller cities represents a clear expansion opportunity.

  **Statistical Validation — Amman vs. Irbid Per-Order Revenue:**
  - H₀: Mean per-order revenue is the same in Amman and Irbid
  - H₁: Mean per-order revenue differs between Amman and Irbid
  - Test: Welch's independent samples t-test (chosen because group sizes and variances differ)
  - t = 0.63, p = 0.527 → **Fail to reject H₀**
  - Cohen's d = 0.094 (negligible effect size)
  - **Interpretation:** Customers in Amman and Irbid spend similar amounts per order. Amman's revenue dominance is driven by customer volume, not spending behaviour.

---

## KPI 4 — Average Order Value by Product Category

- **Name:** Average Order Value by Product Category
- **Definition:** The mean revenue per order, broken down by product category, measuring how much a typical order contributes to revenue in each category.
- **Formula:** `MEAN( SUM(quantity × unit_price) per order )` grouped by `products.category`
- **Data Source:** `order_items.quantity`, `products.unit_price`, `products.category`, `orders.order_id`
- **Baseline Value:**

  | Category        | Avg Order Value (JOD) |
  |-----------------|-----------------------|
  | Books           | 70.46                 |
  | Electronics     | 52.40                 |
  | Clothing        | 48.01                 |
  | Home & Garden   | 45.33                 |
  | Sports          | 27.70                 |
  | Food & Beverage | 27.26                 |

- **Interpretation:** Books yield the highest average order value at 70.46 JOD — 2.6× higher than Food & Beverage (27.26 JOD). A one-way ANOVA confirms this difference is statistically significant (F(5, 1061) = 56.79, p < 0.0001, η² = 0.211), with category explaining 21% of the variance in order revenue. This is a strong, actionable signal: promoting high-value categories (Books, Electronics) increases revenue per transaction without requiring more customers.

  **Statistical Validation — ANOVA on Order Value by Category:**
  - H₀: Mean order value is equal across all product categories
  - H₁: At least one category has a different mean order value
  - Test: One-way ANOVA (appropriate for comparing means across 6 independent groups)
  - F(5, 1061) = 56.79, p < 0.0001 → **Reject H₀**
  - Eta-squared (η²) = 0.2111 (large effect size — ~21% of variance explained by category)
  - **Interpretation:** Product category is a strong predictor of order value. The difference between Books (70.46 JOD) and Food & Beverage (27.26 JOD) is not random. Strategies that shift the product mix toward Books and Electronics should measurably increase average revenue per transaction.

---

## KPI 5 — Total Units Sold by Product Category

- **Name:** Total Units Sold by Product Category
- **Definition:** The total number of product units sold (after removing data entry errors) in each category, indicating volume demand regardless of price.
- **Formula:** `SUM(quantity)` grouped by `products.category`
- **Data Source:** `order_items.quantity`, `products.category`, `products.product_id`
- **Baseline Value:**

  | Category        | Units Sold |
  |-----------------|-----------|
  | Clothing        | 252        |
  | Electronics     | 252        |
  | Food & Beverage | 225        |
  | Sports          | 208        |
  | Books           | 192        |
  | Home & Garden   | 188        |

- **Interpretation:** Clothing and Electronics tie for the highest unit volume (252 each), yet Books — which sells fewer units (192) — generates the highest average order value. This volume/value split has direct inventory and margin implications: Books should be prioritised for revenue, while Clothing and Electronics require sufficient stock depth to sustain volume. Food & Beverage ranks third in volume but last in order value, indicating a high-frequency, low-margin category suited to basket-building promotions.