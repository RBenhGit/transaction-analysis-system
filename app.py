"""
Transaction Analysis System - Main Streamlit Application

A comprehensive securities trading analysis dashboard for IBI broker data.
Displays all 13 transaction fields including stock names, fees, and multi-currency amounts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime
import requests

# Import our modules
from src.input.excel_reader import ExcelReader
from src.input.file_discovery import FileDiscovery
from src.json_adapter import JSONAdapter
from src.adapters.ibi_adapter import IBIAdapter
from src.modules.portfolio_dashboard import (
    PortfolioBuilder,
    display_portfolio_by_currency
)


# Page configuration
st.set_page_config(
    page_title="Transaction Analysis System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_current_exchange_rate():
    """Get current ILS/USD exchange rate from API."""
    try:
        # Using exchangerate-api.com (free tier)
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        if response.status_code == 200:
            data = response.json()
            ils_rate = data['rates'].get('ILS', 3.6)  # Default fallback
            return ils_rate
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")

    # Fallback to approximate rate if API fails
    return 3.6


@st.cache_data
def load_ibi_data(file_path: str):
    """Load and process IBI Excel file."""
    try:
        # Read Excel file
        reader = ExcelReader()
        df_raw = reader.read(file_path)

        # Transform using IBI adapter
        adapter = IBIAdapter()
        df_transformed = adapter.transform(df_raw)

        # Convert to Transaction objects
        json_adapter = JSONAdapter()
        transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

        return df_transformed, transactions

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None, None


def main():
    """Main application function."""

    # Header
    st.markdown('<div class="main-header">🏦 Transaction Analysis System</div>', unsafe_allow_html=True)
    st.markdown("**Securities Trading Analysis Dashboard** - Complete IBI Broker Format Support")

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1f77b4/FFFFFF?text=IBI+Broker", use_container_width=True)
        st.markdown("### 📁 File Selection")

        # Discover available files
        discovery = FileDiscovery()
        files = discovery.discover_excel_files()

        if not files:
            st.warning("No Excel files found in Data_Files/")
            st.info("Please add IBI transaction Excel files to the Data_Files directory.")
            return

        # File selection
        file_options = {f.name: str(f) for f in files}
        selected_file_name = st.selectbox(
            "Select Transaction File",
            options=list(file_options.keys()),
            index=len(file_options) - 1  # Select most recent
        )

        selected_file_path = file_options[selected_file_name]

        st.markdown("---")
        st.markdown("### ⚙️ Options")

        show_raw_data = st.checkbox("Show Raw Data", value=False)
        show_statistics = st.checkbox("Show Statistics", value=True)
        show_charts = st.checkbox("Show Charts", value=True)

        st.markdown("---")
        st.markdown("### 💾 Export")

        if st.button("Export to JSON"):
            st.info("Export functionality will save data to output/ folder")

    # Main content
    if selected_file_path:
        # Load data
        with st.spinner("Loading transaction data..."):
            df, transactions = load_ibi_data(selected_file_path)

        if df is None or transactions is None:
            return

        # Display summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Transactions", len(transactions))

        with col2:
            unique_securities = df['security_name'].nunique()
            st.metric("Unique Securities", unique_securities)

        with col3:
            final_balance = df['balance'].iloc[-1]
            st.metric("Current Balance", f"₪{final_balance:,.2f}")

        with col4:
            total_fees = df['transaction_fee'].sum() + df['additional_fees'].sum()
            st.metric("Total Fees Paid", f"₪{total_fees:,.2f}")

        with col5:
            buys = sum(1 for t in transactions if t.is_buy)
            sells = sum(1 for t in transactions if t.is_sell)
            st.metric("Buy/Sell Ratio", f"{buys}/{sells}")

        # Second row: Investment totals
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        # Calculate total invested (buy transactions only)
        buy_df = df[df['transaction_type'].str.contains('קניה', na=False)]

        # Total in shekels (negative amounts mean money spent)
        total_invested_nis = abs(buy_df['amount_local_currency'].sum())

        # Get current exchange rate
        current_rate = get_current_exchange_rate()
        total_invested_usd = total_invested_nis / current_rate if current_rate > 0 else 0

        with col1:
            st.metric("💰 Total Invested (NIS)", f"₪{total_invested_nis:,.2f}")

        with col2:
            st.metric("💵 Total Invested (USD)", f"${total_invested_usd:,.2f}")

        with col3:
            st.metric("📊 Current Rate (USD→ILS)", f"$1 = ₪{current_rate:.3f}")

        st.markdown("---")

        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Transactions", "📊 Analytics", "💹 Securities", "📈 Charts", "🏦 Portfolio"])

        with tab1:
            st.subheader("Transaction History")

            # Filters
            col1, col2, col3 = st.columns(3)

            with col1:
                # Date range filter
                min_date = df['date'].min()
                max_date = df['date'].max()
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )

            with col2:
                # Transaction type filter
                all_types = ['All'] + sorted(df['transaction_type'].unique().tolist())
                selected_type = st.selectbox("Transaction Type", all_types)

            with col3:
                # Security filter
                all_securities = ['All'] + sorted(df['security_name'].unique().tolist())
                selected_security = st.selectbox("Security", all_securities)

            # Apply filters
            df_filtered = df.copy()

            if len(date_range) == 2:
                df_filtered = df_filtered[
                    (df_filtered['date'] >= pd.Timestamp(date_range[0])) &
                    (df_filtered['date'] <= pd.Timestamp(date_range[1]))
                ]

            if selected_type != 'All':
                df_filtered = df_filtered[df_filtered['transaction_type'] == selected_type]

            if selected_security != 'All':
                df_filtered = df_filtered[df_filtered['security_name'] == selected_security]

            # Display transactions
            st.write(f"Showing {len(df_filtered)} transactions")

            # Format for display
            df_display = df_filtered[[
                'date', 'transaction_type', 'security_name', 'security_symbol',
                'quantity', 'execution_price', 'currency',
                'amount_local_currency', 'balance', 'transaction_fee'
            ]].copy()

            df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d')

            st.dataframe(
                df_display,
                use_container_width=True,
                height=400
            )

        with tab2:
            st.subheader("Transaction Analytics")

            col1, col2 = st.columns(2)

            with col1:
                # Transaction type distribution
                st.markdown("#### Transaction Type Distribution")
                type_counts = df['transaction_type'].value_counts().head(10)

                fig_types = px.bar(
                    x=type_counts.values,
                    y=type_counts.index,
                    orientation='h',
                    labels={'x': 'Count', 'y': 'Transaction Type'},
                    title="Top 10 Transaction Types"
                )
                st.plotly_chart(fig_types, use_container_width=True)

            with col2:
                # Monthly transaction volume
                st.markdown("#### Monthly Transaction Volume")
                df['month'] = df['date'].dt.to_period('M').astype(str)
                monthly_counts = df.groupby('month').size()

                fig_monthly = px.line(
                    x=monthly_counts.index,
                    y=monthly_counts.values,
                    labels={'x': 'Month', 'y': 'Transactions'},
                    title="Transactions per Month"
                )
                st.plotly_chart(fig_monthly, use_container_width=True)

        with tab3:
            st.subheader("Securities Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # Most traded securities
                st.markdown("#### Most Traded Securities")
                security_counts = df['security_name'].value_counts().head(10)

                fig_securities = px.pie(
                    names=security_counts.index,
                    values=security_counts.values,
                    title="Top 10 Securities by Transaction Count"
                )
                st.plotly_chart(fig_securities, use_container_width=True)

            with col2:
                # Securities by total volume
                st.markdown("#### Securities by Total Amount")
                security_amounts = df.groupby('security_name')['amount_local_currency'].sum().abs().sort_values(ascending=False).head(10)

                fig_amounts = px.bar(
                    x=security_amounts.values,
                    y=security_amounts.index,
                    orientation='h',
                    labels={'x': 'Total Amount (NIS)', 'y': 'Security'},
                    title="Top 10 Securities by Total Amount"
                )
                st.plotly_chart(fig_amounts, use_container_width=True)

        with tab4:
            st.subheader("Balance & Performance Charts")

            # Balance over time
            st.markdown("#### Account Balance Over Time")

            # Sort by date to ensure chronological order
            df_balance = df.sort_values('date')[['date', 'balance']].copy()

            fig_balance = go.Figure()
            fig_balance.add_trace(go.Scatter(
                x=df_balance['date'],
                y=df_balance['balance'],
                mode='lines',
                name='Balance',
                line=dict(color='#1f77b4', width=2)
            ))

            fig_balance.update_layout(
                title="Account Balance History",
                xaxis_title="Date",
                yaxis_title="Balance (NIS)",
                hovermode='x unified',
                showlegend=False
            )

            st.plotly_chart(fig_balance, use_container_width=True)

            # Fees over time
            st.markdown("#### Fees Over Time")
            df['total_fees'] = df['transaction_fee'] + df['additional_fees']

            fig_fees = px.bar(
                df[df['total_fees'] > 0],
                x='date',
                y='total_fees',
                labels={'date': 'Date', 'total_fees': 'Fees (NIS)'},
                title="Transaction Fees"
            )
            st.plotly_chart(fig_fees, use_container_width=True)

        with tab5:
            st.subheader("Assets Portfolio Dashboard")

            # Check if transactions are available
            if transactions is None or len(transactions) == 0:
                st.warning("⚠️ No transactions loaded. Please select a transaction file from the sidebar.")
            else:
                # Build portfolio from transaction history
                st.markdown("**Current holdings calculated from transaction history**")

                # Build portfolio from transaction data with current prices
                with st.spinner("Building portfolio and fetching current prices..."):
                    builder = PortfolioBuilder()
                    positions_by_currency = builder.build_by_currency(transactions, fetch_prices=True)

                # Get current exchange rate for proper currency conversion
                exchange_rate = get_current_exchange_rate()

                # Display portfolio separated by currency with conversion info
                display_portfolio_by_currency(
                    positions_by_currency,
                    show_market_data=False,
                    exchange_rate=exchange_rate
                )

                # Show data source info
                st.markdown("---")
                st.caption(f"📊 Portfolio calculated from **{len(transactions)} transactions** | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.caption(f"📁 Data source: {selected_file_name}")
                st.caption(f"💱 Exchange rate: $1 = ₪{exchange_rate:.3f}")
                st.caption(f"📈 Current prices: US stocks from Yahoo Finance (cached 10 min, rate-limited) | TASE stocks: not available")

        # Raw data view
        if show_raw_data:
            st.markdown("---")
            st.subheader("Raw Data View")
            st.dataframe(df, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        Transaction Analysis System | Built with Streamlit | IBI Broker Format Support
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
