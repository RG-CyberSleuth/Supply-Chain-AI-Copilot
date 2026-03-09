"""
app.py
Main Streamlit application for the Supply Chain AI Copilot.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import os
import tempfile

from data_processor import (
    load_data,
    compute_metrics,
    get_summary_stats,
    get_warehouse_metrics,
    get_product_metrics,
    get_delayed_orders,
)
from ai_engine import ask_question, get_ai_insight
from charts import (
    chart_avg_delay_by_warehouse,
    chart_processing_time_by_product,
    chart_order_volume_by_warehouse,
    chart_delay_distribution,
    chart_lead_time_trend,
    chart_warehouse_product_heatmap,
)

DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "orders.csv")


def load_and_prepare(filepath: str) -> pd.DataFrame:
    df = load_data(filepath)
    df = compute_metrics(df)
    return df


st.set_page_config(
    page_title="Supply Chain AI Copilot",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Supply Chain AI Copilot")
st.caption("Analyze shipment data and ask operational questions using natural language.")

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Data Source")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.read())
            csv_path = tmp.name
        st.success(f"Loaded: {uploaded_file.name}")
    else:
        csv_path = DEFAULT_CSV
        st.info("Using default dataset: orders.csv")

    st.divider()
    st.header("Delay Threshold")
    delay_threshold = st.slider(
        "Flag orders delayed more than N days",
        min_value=1,
        max_value=14,
        value=3,
    )

# ── Load Data ─────────────────────────────────────────────────────────────────

try:
    df = load_and_prepare(csv_path)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# ── Initialize Session State ──────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_dashboard, tab_data, tab_chat, tab_insights = st.tabs(
    ["Dashboard", "Data Table", "AI Chat", "AI Insights"]
)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

with tab_dashboard:
    stats = get_summary_stats(df)

    # KPI metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Orders", stats.get("total_orders", "-"))
    col2.metric("Warehouses", stats.get("unique_warehouses", "-"))
    col3.metric("Products", stats.get("unique_products", "-"))
    col4.metric("Avg Processing Time", f"{stats.get('avg_processing_time', '-')} days")
    col5.metric("Avg Shipping Delay", f"{stats.get('avg_shipping_delay', '-')} days")

    st.divider()

    # Row 1: delay by warehouse + processing time by product
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(chart_avg_delay_by_warehouse(df), width="stretch")
    with col_right:
        st.plotly_chart(chart_processing_time_by_product(df), width="stretch")

    # Row 2: order volume + delay distribution
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(chart_order_volume_by_warehouse(df), width="stretch")
    with col_right:
        st.plotly_chart(chart_delay_distribution(df), width="stretch")

    # Row 3: lead time trend (full width)
    st.plotly_chart(chart_lead_time_trend(df), width="stretch")

    # Row 4: heatmap (full width)
    st.plotly_chart(chart_warehouse_product_heatmap(df), width="stretch")

    # Delayed orders table
    st.subheader(f"Orders Delayed More Than {delay_threshold} Days (Processing Time)")
    delayed = get_delayed_orders(df, threshold_days=delay_threshold)
    if delayed.empty:
        st.info(f"No orders exceeded the {delay_threshold}-day processing threshold.")
    else:
        display_cols = [
            c for c in
            ["Order_ID", "Product", "Warehouse", "Order_Date", "Ship_Date",
             "Processing_Time_Days", "Shipping_Delay_Days", "Status"]
            if c in delayed.columns
        ]
        st.dataframe(delayed[display_cols], width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: DATA TABLE
# ═══════════════════════════════════════════════════════════════════════════════

with tab_data:
    st.subheader("Full Dataset with Computed Metrics")
    st.dataframe(df, width="stretch")

    st.divider()

    col_wh, col_prod = st.columns(2)
    with col_wh:
        st.subheader("Warehouse Summary")
        wh_metrics = get_warehouse_metrics(df)
        st.dataframe(wh_metrics, width="stretch")
    with col_prod:
        st.subheader("Product Summary")
        prod_metrics = get_product_metrics(df)
        st.dataframe(prod_metrics, width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: AI CHAT
# ═══════════════════════════════════════════════════════════════════════════════

with tab_chat:
    st.subheader("Ask a Question About Your Supply Chain Data")

    EXAMPLE_QUESTIONS = [
        "Which warehouse has the highest shipping delay?",
        "Which product ships fastest on average?",
        "What is the average delay per warehouse?",
        "Which orders were delayed more than 3 days?",
        "Which warehouse has the most total orders?",
        "What is the worst performing product in terms of lead time?",
    ]

    st.write("Example questions:")
    cols = st.columns(3)
    for i, q in enumerate(EXAMPLE_QUESTIONS):
        if cols[i % 3].button(q, key=f"example_{i}", width="stretch"):
            st.session_state["prefill_question"] = q

    st.divider()

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    # Chat input
    prefill = st.session_state.pop("prefill_question", "")
    user_input = st.chat_input("Type your question here...")

    active_question = user_input or (prefill if prefill else None)

    if active_question:
        with st.chat_message("user"):
            st.write(active_question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                try:
                    response = ask_question(
                        df,
                        active_question,
                        st.session_state.chat_history,
                    )
                    st.write(response)

                    # Update chat history (store raw question without the injected dataset context)
                    st.session_state.chat_history.append(
                        {"role": "user", "content": active_question}
                    )
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    st.error(f"AI request failed: {e}")

    if st.session_state.chat_history:
        if st.button("Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: AI INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_insights:
    st.subheader("AI-Generated Insights")
    st.write(
        "Click a button below to generate an AI analysis of your supply chain data."
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Executive Overview**")
        st.caption("High-level summary of the dataset.")
        if st.button("Generate Overview", width="stretch"):
            with st.spinner("Generating..."):
                try:
                    result = get_ai_insight(df, "overview")
                    st.session_state["insight_overview"] = result
                except Exception as e:
                    st.error(f"Failed: {e}")
        if "insight_overview" in st.session_state:
            st.info(st.session_state["insight_overview"])

    with col_b:
        st.markdown("**Bottleneck Analysis**")
        st.caption("Identify the worst-performing areas.")
        if st.button("Identify Bottlenecks", width="stretch"):
            with st.spinner("Analyzing..."):
                try:
                    result = get_ai_insight(df, "bottlenecks")
                    st.session_state["insight_bottlenecks"] = result
                except Exception as e:
                    st.error(f"Failed: {e}")
        if "insight_bottlenecks" in st.session_state:
            st.warning(st.session_state["insight_bottlenecks"])

    with col_c:
        st.markdown("**Recommendations**")
        st.caption("Actionable steps to improve performance.")
        if st.button("Get Recommendations", width="stretch"):
            with st.spinner("Thinking..."):
                try:
                    result = get_ai_insight(df, "recommendations")
                    st.session_state["insight_recommendations"] = result
                except Exception as e:
                    st.error(f"Failed: {e}")
        if "insight_recommendations" in st.session_state:
            st.success(st.session_state["insight_recommendations"])