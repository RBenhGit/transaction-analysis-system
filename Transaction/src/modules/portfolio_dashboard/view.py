"""
Portfolio Dashboard View.

Streamlit display components for showing current portfolio holdings.
Displays ACTUAL values from real transaction data.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict
from .position import Position


def display_portfolio(positions: List[Position]):
    """
    Display current portfolio holdings in Streamlit.

    Shows ACTUAL values:
    - Actual quantities owned
    - Actual average costs paid
    - Actual money invested

    Args:
        positions: List of Position objects from real transaction data
    """
    st.subheader("📊 Current Portfolio Holdings")

    if not positions or len(positions) == 0:
        st.info("No current positions. Portfolio is empty or all positions have been closed.")
        return

    # Convert positions to DataFrame for display
    data = []
    for pos in positions:
        data.append({
            "Security": pos.security_name,
            "Symbol": pos.security_symbol,
            "Quantity": f"{pos.quantity:.2f}",
            "Avg Cost": f"{pos.currency}{pos.average_cost:.2f}",
            "Total Invested": f"{pos.currency}{pos.total_invested:,.2f}",
        })

    df = pd.DataFrame(data)

    # Display holdings table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Security": st.column_config.TextColumn("Security", width="large"),
            "Symbol": st.column_config.TextColumn("Symbol", width="small"),
            "Quantity": st.column_config.TextColumn("Quantity", width="small"),
            "Avg Cost": st.column_config.TextColumn("Avg Cost", width="medium"),
            "Total Invested": st.column_config.TextColumn("Total Invested", width="medium"),
        }
    )

    # Summary metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Positions", len(positions))

    with col2:
        # Calculate total invested across all positions
        total_invested = sum(pos.total_invested for pos in positions)
        st.metric("Total Invested", f"₪{total_invested:,.2f}")

    with col3:
        # Count unique securities
        unique_securities = len(set(pos.security_symbol for pos in positions))
        st.metric("Unique Securities", unique_securities)

    # Export functionality
    st.markdown("---")
    if st.button("📥 Export Portfolio to Excel"):
        export_portfolio_to_excel(positions)


def export_portfolio_to_excel(positions: List[Position]):
    """
    Export portfolio to Excel file.

    Args:
        positions: List of Position objects
    """
    # Create DataFrame
    data = [pos.to_dict() for pos in positions]
    df = pd.DataFrame(data)

    # Convert to Excel in memory
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Portfolio', index=False)

    output.seek(0)

    # Download button
    st.download_button(
        label="📥 Download Portfolio.xlsx",
        data=output,
        file_name="portfolio_holdings.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("Portfolio exported successfully!")


def display_portfolio_by_currency(positions_by_currency: Dict[str, List[Position]], show_market_data: bool = True):
    """
    Display portfolio separated by currency with optional market data.

    Args:
        positions_by_currency: Dict mapping currency to positions
                              Example: {"₪": [pos1, pos2], "$": [pos3, pos4]}
        show_market_data: If True, display market values and P&L (default: True)
    """
    st.subheader("📊 Current Portfolio Holdings")

    if not positions_by_currency or len(positions_by_currency) == 0:
        st.info("No current positions. Portfolio is empty or all positions have been closed.")
        return

    # Check if any position has market data
    has_any_market_data = any(
        pos.has_market_data
        for positions in positions_by_currency.values()
        for pos in positions
    )

    # Display summary metrics first
    total_positions = sum(len(positions) for positions in positions_by_currency.values())
    total_currencies = len(positions_by_currency)

    # Calculate totals by currency
    if has_any_market_data and show_market_data:
        col1, col2, col3, col4 = st.columns(4)
    else:
        col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Positions", total_positions)
    with col2:
        st.metric("Currencies", total_currencies)

    if has_any_market_data and show_market_data:
        # Calculate total market value and P&L across all currencies
        total_market_value_by_curr = {}
        total_pnl_by_curr = {}

        for currency, positions in positions_by_currency.items():
            market_val = sum(pos.market_value for pos in positions if pos.market_value is not None)
            pnl = sum(pos.unrealized_pnl for pos in positions if pos.unrealized_pnl is not None)
            total_market_value_by_curr[currency] = market_val
            total_pnl_by_curr[currency] = pnl

        with col3:
            # Show market value for each currency
            mv_display = " + ".join([f"{curr}{val:,.0f}" for curr, val in total_market_value_by_curr.items() if val > 0])
            st.metric("Total Market Value", mv_display)

        with col4:
            # Show total P&L for each currency
            pnl_display = " + ".join([
                f"{curr}{val:+,.0f}" for curr, val in total_pnl_by_curr.items() if val != 0
            ])
            total_pnl_sum = sum(total_pnl_by_curr.values())
            delta_color = "normal" if total_pnl_sum >= 0 else "inverse"
            st.metric("Total Unrealized P&L", pnl_display, delta_color=delta_color)

    st.markdown("---")

    # Display each currency portfolio separately
    for currency in sorted(positions_by_currency.keys()):
        positions = positions_by_currency[currency]

        # Currency section header
        currency_name = "Shekel (NIS)" if currency == "₪" else "Dollar (USD)" if currency == "$" else currency
        st.markdown(f"### {currency} {currency_name} Portfolio")

        # Convert to DataFrame
        data = []
        for pos in positions:
            row = {
                "Security": pos.security_name,
                "Symbol": pos.security_symbol,
                "Quantity": pos.quantity,
                "Avg Cost": pos.average_cost,
                "Cost Basis": pos.total_invested,
            }

            # Add market data if available
            if pos.has_market_data and show_market_data:
                row["Current Price"] = pos.current_price
                row["Market Value"] = pos.market_value
                row["P&L"] = pos.unrealized_pnl
                row["P&L %"] = pos.unrealized_pnl_pct

            data.append(row)

        df = pd.DataFrame(data)

        # Configure column display
        column_config = {
            "Security": st.column_config.TextColumn("Security", width="large"),
            "Symbol": st.column_config.TextColumn("Symbol", width="small"),
            "Quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
            "Avg Cost": st.column_config.NumberColumn("Avg Cost", format=f"{currency}%.2f"),
            "Cost Basis": st.column_config.NumberColumn("Cost Basis", format=f"{currency}%,.2f"),
        }

        if has_any_market_data and show_market_data:
            column_config.update({
                "Current Price": st.column_config.NumberColumn("Current Price", format=f"{currency}%.2f"),
                "Market Value": st.column_config.NumberColumn("Market Value", format=f"{currency}%,.2f"),
                "P&L": st.column_config.NumberColumn("P&L", format=f"{currency}%,.2f"),
                "P&L %": st.column_config.NumberColumn("P&L %", format="%.1f%%"),
            })

        # Display table with conditional styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )

        # Currency-specific totals
        total_invested = sum(pos.total_invested for pos in positions)
        num_positions = len(positions)

        if has_any_market_data and show_market_data:
            col1, col2, col3 = st.columns(3)
        else:
            col1, col2 = st.columns(2)

        with col1:
            st.metric(f"{currency} Positions", num_positions)
        with col2:
            st.metric(f"{currency} Cost Basis", f"{currency}{total_invested:,.2f}")

        if has_any_market_data and show_market_data:
            total_market_val = sum(pos.market_value for pos in positions if pos.market_value is not None)
            total_pnl = sum(pos.unrealized_pnl for pos in positions if pos.unrealized_pnl is not None)
            total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

            with col3:
                st.metric(
                    f"{currency} Market Value",
                    f"{currency}{total_market_val:,.2f}",
                    delta=f"{total_pnl:+,.2f} ({total_pnl_pct:+.1f}%)"
                )

        st.markdown("---")

    # Export functionality
    if st.button("📥 Export All Portfolios to Excel"):
        export_currency_portfolios_to_excel(positions_by_currency)


def export_currency_portfolios_to_excel(positions_by_currency: Dict[str, List[Position]]):
    """
    Export currency-separated portfolios to Excel file with separate sheets.

    Args:
        positions_by_currency: Dict mapping currency to positions
    """
    from io import BytesIO

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Create a sheet for each currency
        for currency, positions in positions_by_currency.items():
            data = [pos.to_dict() for pos in positions]
            df = pd.DataFrame(data)

            sheet_name = "NIS_Portfolio" if currency == "₪" else "USD_Portfolio" if currency == "$" else f"{currency}_Portfolio"
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Create a summary sheet
        summary_data = []
        for currency, positions in positions_by_currency.items():
            total_invested = sum(pos.total_invested for pos in positions)
            summary_data.append({
                "Currency": currency,
                "Positions": len(positions),
                "Total Invested": total_invested
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

    output.seek(0)

    # Download button
    st.download_button(
        label="📥 Download Portfolio.xlsx",
        data=output,
        file_name="portfolio_by_currency.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("Portfolio exported successfully!")
