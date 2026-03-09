"""
charts.py
Generates Plotly charts for the supply chain dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


COLORS = ["#2563eb", "#16a34a", "#dc2626", "#d97706", "#7c3aed"]


def chart_avg_delay_by_warehouse(df: pd.DataFrame) -> go.Figure:
    if "Shipping_Delay_Days" not in df.columns:
        return go.Figure()

    data = (
        df.groupby("Warehouse")["Shipping_Delay_Days"]
        .mean().round(2).reset_index()
        .rename(columns={"Shipping_Delay_Days": "Avg_Delay_Days"})
        .sort_values("Avg_Delay_Days", ascending=False)
    )

    fig = px.bar(
        data, x="Warehouse", y="Avg_Delay_Days", color="Warehouse",
        color_discrete_sequence=COLORS,
        title="Average Shipping Delay by Warehouse (days)",
        labels={"Avg_Delay_Days": "Avg Delay (days)"},
    )
    fig.update_layout(showlegend=False)
    return fig


def chart_processing_time_by_product(df: pd.DataFrame) -> go.Figure:
    if "Processing_Time_Days" not in df.columns:
        return go.Figure()

    data = (
        df.groupby("Product")["Processing_Time_Days"]
        .mean().round(2).reset_index()
        .rename(columns={"Processing_Time_Days": "Avg_Processing_Days"})
        .sort_values("Avg_Processing_Days")
    )

    fig = px.bar(
        data, x="Product", y="Avg_Processing_Days", color="Product",
        color_discrete_sequence=COLORS,
        title="Average Processing Time by Product (days)",
        labels={"Avg_Processing_Days": "Avg Processing Time (days)"},
    )
    fig.update_layout(showlegend=False)
    return fig


def chart_order_volume_by_warehouse(df: pd.DataFrame) -> go.Figure:
    if "Warehouse" not in df.columns:
        return go.Figure()

    data = df["Warehouse"].value_counts().reset_index()
    data.columns = ["Warehouse", "Order_Count"]

    return px.pie(
        data, names="Warehouse", values="Order_Count",
        color_discrete_sequence=COLORS,
        title="Order Volume Distribution by Warehouse",
    )


def chart_delay_distribution(df: pd.DataFrame) -> go.Figure:
    if "Shipping_Delay_Days" not in df.columns:
        return go.Figure()

    return px.histogram(
        df, x="Shipping_Delay_Days", nbins=15,
        color_discrete_sequence=["#2563eb"],
        title="Distribution of Shipping Delay (days)",
        labels={"Shipping_Delay_Days": "Shipping Delay (days)"},
    )


def chart_lead_time_trend(df: pd.DataFrame) -> go.Figure:
    if "Order_Date" not in df.columns or "Total_Lead_Time_Days" not in df.columns:
        return go.Figure()

    data = (
        df.groupby("Order_Date")["Total_Lead_Time_Days"]
        .mean().round(2).reset_index().sort_values("Order_Date")
    )

    fig = px.line(
        data, x="Order_Date", y="Total_Lead_Time_Days",
        color_discrete_sequence=["#2563eb"],
        title="Average Total Lead Time Over Time (days)",
        labels={"Total_Lead_Time_Days": "Avg Lead Time (days)", "Order_Date": "Order Date"},
    )
    fig.update_traces(mode="lines+markers")
    return fig


def chart_warehouse_product_heatmap(df: pd.DataFrame) -> go.Figure:
    if not all(c in df.columns for c in ["Processing_Time_Days", "Warehouse", "Product"]):
        return go.Figure()

    pivot = df.pivot_table(
        values="Processing_Time_Days",
        index="Warehouse",
        columns="Product",
        aggfunc="mean",
    ).round(2)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Blues",
        text=pivot.values.round(1),
        texttemplate="%{text}",
        showscale=True,
    ))
    fig.update_layout(
        title="Avg Processing Time (days): Warehouse x Product",
        xaxis_title="Product",
        yaxis_title="Warehouse",
    )
    return fig
