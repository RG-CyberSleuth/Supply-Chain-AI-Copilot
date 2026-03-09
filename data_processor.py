"""
data_processor.py
Loads and processes supply chain CSV data.
Computes: Processing Time, Shipping Delay, Total Lead Time.
"""

import pandas as pd
from pathlib import Path


def load_data(filepath: str) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {filepath}")

    df = pd.read_csv(filepath)

    for col in ["Order_Date", "Ship_Date", "Delivery_Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "Order_Date" in df.columns and "Ship_Date" in df.columns:
        df["Processing_Time_Days"] = (df["Ship_Date"] - df["Order_Date"]).dt.days

    if "Ship_Date" in df.columns and "Delivery_Date" in df.columns:
        df["Shipping_Delay_Days"] = (df["Delivery_Date"] - df["Ship_Date"]).dt.days

    if "Order_Date" in df.columns and "Delivery_Date" in df.columns:
        df["Total_Lead_Time_Days"] = (df["Delivery_Date"] - df["Order_Date"]).dt.days

    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    stats = {
        "total_orders": len(df),
        "unique_products": df["Product"].nunique() if "Product" in df.columns else None,
        "unique_warehouses": df["Warehouse"].nunique() if "Warehouse" in df.columns else None,
        "date_range_start": str(df["Order_Date"].min().date()) if "Order_Date" in df.columns else None,
        "date_range_end": str(df["Order_Date"].max().date()) if "Order_Date" in df.columns else None,
    }

    if "Processing_Time_Days" in df.columns:
        stats["avg_processing_time"] = round(df["Processing_Time_Days"].mean(), 2)
        stats["max_processing_time"] = int(df["Processing_Time_Days"].max())

    if "Shipping_Delay_Days" in df.columns:
        stats["avg_shipping_delay"] = round(df["Shipping_Delay_Days"].mean(), 2)
        stats["max_shipping_delay"] = int(df["Shipping_Delay_Days"].max())

    if "Total_Lead_Time_Days" in df.columns:
        stats["avg_lead_time"] = round(df["Total_Lead_Time_Days"].mean(), 2)

    return stats


def get_warehouse_metrics(df: pd.DataFrame) -> pd.DataFrame:
    agg = {"Total_Orders": ("Order_ID", "count")}

    if "Processing_Time_Days" in df.columns:
        agg["Avg_Processing_Time"] = ("Processing_Time_Days", "mean")
    if "Shipping_Delay_Days" in df.columns:
        agg["Avg_Shipping_Delay"] = ("Shipping_Delay_Days", "mean")
    if "Total_Lead_Time_Days" in df.columns:
        agg["Avg_Lead_Time"] = ("Total_Lead_Time_Days", "mean")

    return df.groupby("Warehouse").agg(**agg).reset_index().round(2)


def get_product_metrics(df: pd.DataFrame) -> pd.DataFrame:
    agg = {"Total_Orders": ("Order_ID", "count")}

    if "Processing_Time_Days" in df.columns:
        agg["Avg_Processing_Time"] = ("Processing_Time_Days", "mean")
    if "Shipping_Delay_Days" in df.columns:
        agg["Avg_Shipping_Delay"] = ("Shipping_Delay_Days", "mean")
    if "Total_Lead_Time_Days" in df.columns:
        agg["Avg_Lead_Time"] = ("Total_Lead_Time_Days", "mean")

    return df.groupby("Product").agg(**agg).reset_index().round(2)


def get_delayed_orders(df: pd.DataFrame, threshold_days: int = 3) -> pd.DataFrame:
    if "Processing_Time_Days" not in df.columns:
        return pd.DataFrame()
    return (
        df[df["Processing_Time_Days"] > threshold_days]
        .copy()
        .sort_values("Processing_Time_Days", ascending=False)
    )


def get_dataset_summary_text(df: pd.DataFrame) -> str:
    stats = get_summary_stats(df)
    wh = get_warehouse_metrics(df)
    prod = get_product_metrics(df)
    delayed = get_delayed_orders(df, threshold_days=3)

    lines = [
        " SUPPLY CHAIN DATASET SUMMARY ",
        f"Total Orders       : {stats.get('total_orders')}",
        f"Unique Products    : {stats.get('unique_products')}",
        f"Unique Warehouses  : {stats.get('unique_warehouses')}",
        f"Date Range         : {stats.get('date_range_start')} to {stats.get('date_range_end')}",
        f"Avg Processing Time: {stats.get('avg_processing_time')} days",
        f"Avg Shipping Delay : {stats.get('avg_shipping_delay')} days",
        f"Avg Lead Time      : {stats.get('avg_lead_time')} days",
        "",
        "WAREHOUSE METRICS ",
        wh.to_string(index=False),
        "",
        "PRODUCT METRICS",
        prod.to_string(index=False),
        "",
        "ORDERS DELAYED MORE THAN 3 DAYS (Processing Time) ",
        f"Count: {len(delayed)}",
        delayed[["Order_ID", "Product", "Warehouse", "Processing_Time_Days"]].to_string(index=False)
        if not delayed.empty else "None",
    ]

    return "\n".join(lines)
