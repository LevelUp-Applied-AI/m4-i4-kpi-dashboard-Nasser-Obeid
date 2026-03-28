"""Integration 4 — KPI Dashboard: Amman Digital Market Analytics

Extract data from PostgreSQL, compute KPIs, run statistical tests,
and create visualizations for the executive summary.

Usage:
    python analysis.py
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine


def connect_db():
    """Create a SQLAlchemy engine connected to the amman_market database.

    Returns:
        engine: SQLAlchemy engine instance

    Notes:
        Use DATABASE_URL environment variable if set, otherwise default to:
        postgresql://postgres:postgres@localhost:5432/amman_market
    """
    url = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/amman_market")
    return create_engine(url)


def extract_data(engine):
    """Extract all required tables from the database into DataFrames.

    Args:
        engine: SQLAlchemy engine connected to amman_market

    Returns:
        dict: mapping of table names to DataFrames
              (e.g., {"customers": df, "products": df, "orders": df, "order_items": df})
    """
    customers   = pd.read_sql("SELECT * FROM customers", engine)
    products    = pd.read_sql("SELECT * FROM products", engine)
    orders      = pd.read_sql("SELECT * FROM orders", engine)
    order_items = pd.read_sql("SELECT * FROM order_items", engine)

    # Filter out cancelled orders and suspicious quantities
    orders      = orders[orders["status"] != "cancelled"].copy()
    order_items = order_items[order_items["quantity"] <= 100].copy()

    # Keep only order_items that belong to non-cancelled orders
    order_items = order_items[order_items["order_id"].isin(orders["order_id"])].copy()

    return {
        "customers":   customers,
        "products":    products,
        "orders":      orders,
        "order_items": order_items,
    }


def compute_kpis(data_dict):
    """Compute the 5 KPIs defined in kpi_framework.md.

    Args:
        data_dict: dict of DataFrames from extract_data()

    Returns:
        dict: mapping of KPI names to their computed values (or DataFrames
              for time-series / cohort KPIs)

    Notes:
        At least 2 KPIs should be time-based and 1 should be cohort-based.
    """
    customers   = data_dict["customers"]
    products    = data_dict["products"]
    orders      = data_dict["orders"]
    order_items = data_dict["order_items"]

    # Build a base joined table: orders + items + products + customers
    base = (
        order_items
        .merge(products[["product_id", "unit_price", "category"]], on="product_id")
        .merge(orders[["order_id", "customer_id", "order_date"]], on="order_id")
        .merge(customers[["customer_id", "city"]], on="customer_id")
    )
    base["revenue"] = base["quantity"] * base["unit_price"]
    base["order_date"] = pd.to_datetime(base["order_date"])
    base["month"] = base["order_date"].dt.to_period("M")

    # KPI 1 — Monthly Revenue (time-based)
    monthly_revenue = (
        base.groupby("month")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"revenue": "total_revenue"})
    )
    monthly_revenue["month_str"] = monthly_revenue["month"].astype(str)

    # KPI 2 — Month-over-Month Revenue Growth % (time-based)
    monthly_revenue["mom_growth_pct"] = (
        monthly_revenue["total_revenue"].pct_change() * 100
    )

    # KPI 3 — Revenue by City (cohort-based)
    revenue_by_city = (
        base.dropna(subset=["city"])
        .groupby("city")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"revenue": "total_revenue"})
        .sort_values("total_revenue", ascending=False)
    )

    # KPI 4 — Average Order Value by Product Category
    order_revenue = base.groupby(["order_id", "category"])["revenue"].sum().reset_index()
    avg_order_value_by_category = (
        order_revenue.groupby("category")["revenue"]
        .mean()
        .reset_index()
        .rename(columns={"revenue": "avg_order_value"})
        .sort_values("avg_order_value", ascending=False)
    )

    # KPI 5 — Top Product Categories by Units Sold
    units_by_category = (
        base.groupby("category")["quantity"]
        .sum()
        .reset_index()
        .rename(columns={"quantity": "total_units"})
        .sort_values("total_units", ascending=False)
    )

    return {
        "monthly_revenue":             monthly_revenue,
        "revenue_by_city":             revenue_by_city,
        "avg_order_value_by_category": avg_order_value_by_category,
        "units_by_category":           units_by_category,
        "base":                        base,   # shared for stat tests & charts
    }


def run_statistical_tests(data_dict):
    """Run hypothesis tests to validate patterns in the data.

    Args:
        data_dict: dict of DataFrames from extract_data()

    Returns:
        dict: mapping of test names to results (test statistic, p-value,
              interpretation)

    Notes:
        Run at least one test. Consider:
        - Does average order value differ across product categories?
        - Is there a significant trend in monthly revenue?
        - Do customer cities differ in purchasing behavior?
    """
    customers   = data_dict["customers"]
    products    = data_dict["products"]
    orders      = data_dict["orders"]
    order_items = data_dict["order_items"]

    base = (
        order_items
        .merge(products[["product_id", "unit_price", "category"]], on="product_id")
        .merge(orders[["order_id", "customer_id", "order_date"]], on="order_id")
        .merge(customers[["customer_id", "city"]], on="customer_id")
    )
    base["revenue"] = base["quantity"] * base["unit_price"]

    results = {}

    # Test 1 — ANOVA: Does average order value differ across product categories?
    # H0: mean order revenue is equal across all categories
    # H1: at least one category has a different mean
    order_by_cat = base.groupby(["order_id", "category"])["revenue"].sum().reset_index()
    groups = [group["revenue"].values for _, group in order_by_cat.groupby("category")]
    f_stat, p_anova = stats.f_oneway(*groups)

    # Effect size: eta-squared
    grand_mean = order_by_cat["revenue"].mean()
    ss_between = sum(
        len(g) * (g.mean() - grand_mean) ** 2 for g in groups
    )
    ss_total = sum((order_by_cat["revenue"] - grand_mean) ** 2)
    eta_sq = ss_between / ss_total

    results["anova_order_value_by_category"] = {
        "h0": "Mean order value is equal across all product categories",
        "h1": "At least one product category has a different mean order value",
        "test": "One-way ANOVA",
        "f_stat": round(f_stat, 4),
        "p_value": round(p_anova, 4),
        "eta_squared": round(eta_sq, 4),
        "interpretation": (
            f"F({len(groups)-1}, {len(order_by_cat)-len(groups)}) = {f_stat:.2f}, "
            f"p = {p_anova:.4f}. "
            + ("Reject H0: revenue differs significantly across categories."
               if p_anova < 0.05 else
               "Fail to reject H0: no significant difference across categories.")
            + f" Eta-squared = {eta_sq:.4f} (proportion of variance explained)."
        ),
    }

    # Test 2 — Independent t-test: Amman vs Irbid revenue per order
    # H0: mean per-order revenue is the same in Amman and Irbid
    # H1: means are different
    order_revenue_city = base.dropna(subset=["city"]).groupby(["order_id", "city"])["revenue"].sum().reset_index()
    amman = order_revenue_city[order_revenue_city["city"] == "Amman"]["revenue"]
    irbid = order_revenue_city[order_revenue_city["city"] == "Irbid"]["revenue"]
    t_stat, p_ttest = stats.ttest_ind(amman, irbid, equal_var=False)

    # Effect size: Cohen's d
    pooled_std = np.sqrt((amman.std() ** 2 + irbid.std() ** 2) / 2)
    cohens_d = (amman.mean() - irbid.mean()) / pooled_std if pooled_std > 0 else 0

    results["ttest_amman_vs_irbid"] = {
        "h0": "Mean per-order revenue is the same in Amman and Irbid",
        "h1": "Mean per-order revenue differs between Amman and Irbid",
        "test": "Welch's independent samples t-test",
        "t_stat": round(t_stat, 4),
        "p_value": round(p_ttest, 4),
        "cohens_d": round(cohens_d, 4),
        "amman_mean": round(amman.mean(), 2),
        "irbid_mean": round(irbid.mean(), 2),
        "interpretation": (
            f"t = {t_stat:.2f}, p = {p_ttest:.4f}. "
            + ("Reject H0: order revenue differs significantly between Amman and Irbid."
               if p_ttest < 0.05 else
               "Fail to reject H0: no significant revenue difference between cities.")
            + f" Cohen's d = {cohens_d:.4f}."
        ),
    }

    return results


def create_visualizations(kpi_results, stat_results):
    """Create publication-quality charts for all 5 KPIs.

    Args:
        kpi_results: dict from compute_kpis()
        stat_results: dict from run_statistical_tests()

    Returns:
        None

    Side effects:
        Saves at least 5 PNG files to the output/ directory.
        Each chart should have a descriptive title stating the finding,
        proper axis labels, and annotations where appropriate.
    """
    sns.set_palette("colorblind")
    os.makedirs("output", exist_ok=True)

    monthly_revenue             = kpi_results["monthly_revenue"]
    revenue_by_city             = kpi_results["revenue_by_city"]
    avg_order_value_by_category = kpi_results["avg_order_value_by_category"]
    units_by_category           = kpi_results["units_by_category"]
    base                        = kpi_results["base"]

    # ── Chart 1 & 2: Multi-panel — Monthly Revenue + MoM Growth ──────────────
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle("Revenue Grows Steadily with Mid-Year Acceleration", fontsize=14, fontweight="bold")

    months = monthly_revenue["month_str"]
    x = range(len(months))

    axes[0].bar(x, monthly_revenue["total_revenue"], color=sns.color_palette("colorblind")[0])
    axes[0].set_ylabel("Total Revenue (JOD)")
    axes[0].set_title("KPI 1 — Monthly Revenue")
    axes[0].tick_params(axis="x", rotation=45)
    plt.setp(axes[0].get_xticklabels(), visible=False)

    growth = monthly_revenue["mom_growth_pct"].iloc[1:]
    colors = ["green" if v >= 0 else "red" for v in growth]
    axes[1].bar(range(1, len(months)), growth, color=colors)
    axes[1].axhline(0, color="black", linewidth=0.8, linestyle="--")
    axes[1].set_ylabel("MoM Growth (%)")
    axes[1].set_title("KPI 2 — Month-over-Month Revenue Growth")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(months, rotation=45, ha="right")

    fig.tight_layout()
    fig.savefig("output/kpi1_kpi2_monthly_revenue_growth.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ── Chart 3: Revenue by City (cohort) ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(
        revenue_by_city["city"],
        revenue_by_city["total_revenue"],
        color=sns.color_palette("colorblind", len(revenue_by_city)),
    )
    ax.set_xlabel("Total Revenue (JOD)")
    ax.set_title("KPI 3 — Amman Dominates Revenue; Irbid and Zarqa Follow", fontweight="bold")
    ax.bar_label(bars, fmt="%.0f", padding=4)
    fig.tight_layout()
    fig.savefig("output/kpi3_revenue_by_city.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ── Chart 4: Avg Order Value by Category (Seaborn boxplot) ───────────────
    order_by_cat = base.groupby(["order_id", "category"])["revenue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(
        data=order_by_cat,
        x="category",
        y="revenue",
        palette="colorblind",
        ax=ax,
    )
    ax.set_xlabel("Product Category")
    ax.set_ylabel("Order Revenue (JOD)")
    ax.set_title("KPI 4 — Electronics and Books Drive Highest Order Values", fontweight="bold")

    # Annotate with ANOVA result
    anova = stat_results["anova_order_value_by_category"]
    ax.annotate(
        f"ANOVA: F = {anova['f_stat']}, p = {anova['p_value']}",
        xy=(0.98, 0.97), xycoords="axes fraction",
        ha="right", va="top", fontsize=8,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray"),
    )
    fig.tight_layout()
    fig.savefig("output/kpi4_avg_order_value_by_category.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ── Chart 5: Units Sold by Category ──────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        units_by_category["category"],
        units_by_category["total_units"],
        color=sns.color_palette("colorblind", len(units_by_category)),
    )
    ax.set_xlabel("Product Category")
    ax.set_ylabel("Total Units Sold")
    ax.set_title("KPI 5 — Food & Beverage and Sports Lead in Volume", fontweight="bold")
    ax.bar_label(bars, padding=3)
    fig.tight_layout()
    fig.savefig("output/kpi5_units_sold_by_category.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ── Chart 6: Heatmap — Revenue by City × Category ────────────────────────
    pivot = (
        base.dropna(subset=["city"])
        .groupby(["city", "category"])["revenue"]
        .sum()
        .unstack(fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(
        pivot,
        annot=True, fmt=".0f",
        cmap="YlOrRd",
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("Revenue Heatmap: Amman Leads Across All Categories", fontweight="bold")
    ax.set_xlabel("Product Category")
    ax.set_ylabel("City")
    fig.tight_layout()
    fig.savefig("output/kpi3_heatmap_city_category.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    """Orchestrate the full analysis pipeline."""
    os.makedirs("output", exist_ok=True)

    engine      = connect_db()
    data_dict   = extract_data(engine)
    kpi_results = compute_kpis(data_dict)
    stat_results = run_statistical_tests(data_dict)
    create_visualizations(kpi_results, stat_results)

    # ── Summary printout ──────────────────────────────────────────────────────
    monthly = kpi_results["monthly_revenue"]
    print("=" * 55)
    print("KPI SUMMARY — Amman Digital Market")
    print("=" * 55)

    print("\nKPI 1 & 2 — Monthly Revenue & MoM Growth:")
    for _, row in monthly.iterrows():
        growth = f"{row['mom_growth_pct']:+.1f}%" if pd.notna(row["mom_growth_pct"]) else "  n/a "
        print(f"  {row['month_str']}  Revenue: {row['total_revenue']:>8,.2f} JOD   MoM: {growth}")

    print("\nKPI 3 — Revenue by City:")
    for _, row in kpi_results["revenue_by_city"].iterrows():
        print(f"  {row['city']:<12}  {row['total_revenue']:>8,.2f} JOD")

    print("\nKPI 4 — Avg Order Value by Category:")
    for _, row in kpi_results["avg_order_value_by_category"].iterrows():
        print(f"  {row['category']:<18}  {row['avg_order_value']:>7,.2f} JOD")

    print("\nKPI 5 — Units Sold by Category:")
    for _, row in kpi_results["units_by_category"].iterrows():
        print(f"  {row['category']:<18}  {row['total_units']:>5} units")

    print("\nStatistical Tests:")
    for name, res in stat_results.items():
        print(f"\n  [{name}]")
        print(f"  {res['interpretation']}")

    print("\nCharts saved to output/")
    print("=" * 55)


if __name__ == "__main__":
    main()