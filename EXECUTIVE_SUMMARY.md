# Executive Summary — Amman Digital Market Analytics

## Overview

This analysis covers sales activity on the Amman Digital Market from January 2024 to June 2025, drawing on approximately 500 orders placed by 112 registered customers across six Jordanian cities. After removing cancelled orders (~10% of the dataset) and correcting data entry errors (3 order items with quantities of 175–450 units), five KPIs were computed across four dimensions: monthly revenue trends, city-level revenue cohorts, product category order value, and units sold volume. Two statistical tests were conducted to validate the key patterns.

---

## Finding 1 — Books Generate 2.6× More Revenue Per Order Than Food & Beverage

Books produce the highest average order value at 70.46 JOD, compared to 52.40 JOD for Electronics and just 27.26 JOD for Food & Beverage. This difference is not due to chance: a one-way ANOVA across all six product categories returned F(5, 1061) = 56.79 (p < 0.0001), with product category explaining 21% of the variance in order revenue (η² = 0.21).

**Supporting data:** KPI 4 — Avg Order Value by Category. See `output/kpi4_avg_order_value_by_category.png`.

---

## Finding 2 — Amman's Revenue Lead Comes From Customer Volume, Not Higher Spending

Amman accounts for 15,719 JOD in total revenue — more than double Irbid (7,250.50 JOD) and nearly 3.8× more than Aqaba (4,167.50 JOD). However, a Welch's t-test comparing per-order revenue between Amman and Irbid found no statistically significant difference (t = 0.63, p = 0.527, Cohen's d = 0.094). Customers in both cities spend roughly the same per order; Amman simply has more of them.

**Supporting data:** KPI 3 — Revenue by City. See `output/kpi3_revenue_by_city.png` and `output/kpi3_heatmap_city_category.png`.

---

## Finding 3 — Revenue is Stable Through 2024 but Shows Unplanned Spikes in 2025

Monthly revenue across 2024 averaged approximately 2,489 JOD with low volatility (−26.6% to +22.6% MoM), indicating a mature, steady market. Two large spikes occurred in March 2025 (+79.1%) and June 2025 (+151.7%), followed immediately by sharp reversals (−39.4% and not yet recovered). These are not signs of sustained growth — they are isolated demand events with no evident cause in the data.

**Supporting data:** KPI 1 & KPI 2 — Monthly Revenue and MoM Growth. See `output/kpi1_kpi2_monthly_revenue_growth.png`.

---

## Recommendations

1. **Shift promotional focus toward Books and Electronics.** Since product category drives 21% of order value variance, increasing the share of Books and Electronics in the product mix — through featured placements, bundles, or targeted campaigns — is the most direct lever for raising revenue per transaction. A 10% shift in order mix toward Books could increase average order value by an estimated 5–8 JOD per transaction.

2. **Invest in customer acquisition outside Amman.** Because per-order spending is statistically similar across cities, every new customer in Irbid, Zarqa, or Aqaba produces roughly the same revenue as a new Amman customer. Targeted outreach in these cities — where the current customer base is thin — offers the highest volume growth opportunity at no sacrifice to order quality.

3. **Investigate the 2025 revenue spikes before planning around them.** The March and June 2025 surges (79% and 152% MoM) should be traced to specific orders, customers, or campaigns before being treated as a trend. If they are attributable to a single large buyer or a one-time promotion, forecasting and inventory planning must not assume they will repeat. Understanding the root cause will determine whether they represent a replicable growth pattern or an anomaly to be smoothed out.