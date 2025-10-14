"""
Portfolio Dashboard View.

Streamlit display components for showing current portfolio holdings.
Displays ACTUAL values from real transaction data.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from .position import Position
from .validator import PortfolioValidator, ValidationResult


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


def display_portfolio_by_currency(positions_by_currency: Dict[str, List[Position]], show_market_data: bool = True, exchange_rate: float = None):
    """
    Display portfolio separated by currency with proper currency conversion.

    Args:
        positions_by_currency: Dict mapping currency to positions
                              Example: {"₪": [pos1, pos2], "$": [pos3, pos4]}
        show_market_data: If True, display market values and P&L (default: True)
        exchange_rate: USD to ILS exchange rate for conversion (e.g., 3.6 means $1 = ₪3.6)
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
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Positions", total_positions)
    with col2:
        st.metric("Currencies", total_currencies)

    with col3:
        # Calculate total cost basis with proper currency conversion
        total_invested_by_curr = {}
        for currency, positions in positions_by_currency.items():
            total_invested_by_curr[currency] = sum(pos.total_invested for pos in positions)

        # Convert all to NIS for total
        total_in_nis = 0.0
        if "₪" in total_invested_by_curr:
            total_in_nis += total_invested_by_curr["₪"]
        if "$" in total_invested_by_curr and exchange_rate:
            total_in_nis += total_invested_by_curr["$"] * exchange_rate

        # Display breakdown
        breakdown = []
        if "₪" in total_invested_by_curr:
            breakdown.append(f"₪{total_invested_by_curr['₪']:,.0f}")
        if "$" in total_invested_by_curr:
            breakdown.append(f"${total_invested_by_curr['$']:,.0f}")

        breakdown_str = " + ".join(breakdown)
        st.metric(
            "Total Cost Basis",
            f"₪{total_in_nis:,.2f}",
            delta=breakdown_str if len(breakdown) > 1 else None
        )

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
                "Current Price": pos.current_price if pos.current_price else 0.0,
                "Cost Basis": pos.total_invested,
            }

            # Add market data if available
            if pos.has_market_data and show_market_data:
                row["Market Value"] = pos.market_value
                row["P&L"] = pos.unrealized_pnl
                row["P&L %"] = pos.unrealized_pnl_pct

            data.append(row)

        df = pd.DataFrame(data)

        # Configure column display with compact widths
        # Note: format strings cannot include currency symbols, only numeric formatting
        column_config = {
            "Security": st.column_config.TextColumn("Security", width="medium"),
            "Symbol": st.column_config.TextColumn("Symbol", width="small"),
            "Quantity": st.column_config.NumberColumn("Qty", format="%.2f", width="small"),
            "Avg Cost": st.column_config.NumberColumn("Avg Cost", format="%.2f", width="small"),
            "Current Price": st.column_config.NumberColumn("Current Price", format="%.2f", width="small"),
            "Cost Basis": st.column_config.NumberColumn("Cost Basis", format="%,.2f", width="medium"),
        }

        if has_any_market_data and show_market_data:
            column_config.update({
                "Market Value": st.column_config.NumberColumn("Market Value", format="%,.2f", width="medium"),
                "P&L": st.column_config.NumberColumn("P&L", format="%,.2f", width="small"),
                "P&L %": st.column_config.NumberColumn("P&L %", format="%.1f%%", width="small"),
            })

        # Display table with compact styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            height=min(400, 50 + len(df) * 35)  # Compact height based on row count
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


def display_validation_results(
    positions: List[Position],
    actual_portfolio_path: str,
    quantity_tolerance: float = 0.01,
    cost_basis_tolerance_abs: float = 1.0,
    cost_basis_tolerance_pct: float = 0.1
):
    """
    Display portfolio validation results comparing calculated vs actual positions.

    Args:
        positions: List of calculated positions from transaction history
        actual_portfolio_path: Path to IBI actual portfolio Excel file
        quantity_tolerance: Maximum allowed difference in shares
        cost_basis_tolerance_abs: Maximum absolute difference in cost basis
        cost_basis_tolerance_pct: Maximum percentage difference in cost basis
    """
    st.subheader("🔍 Portfolio Validation")

    # Initialize validator
    validator = PortfolioValidator(
        quantity_tolerance=quantity_tolerance,
        cost_basis_tolerance_abs=cost_basis_tolerance_abs,
        cost_basis_tolerance_pct=cost_basis_tolerance_pct
    )

    # Show validation settings
    with st.expander("⚙️ Validation Settings"):
        st.write(f"**Quantity Tolerance:** ±{quantity_tolerance} shares")
        st.write(f"**Cost Basis Absolute Tolerance:** ±₪{cost_basis_tolerance_abs}")
        st.write(f"**Cost Basis Percentage Tolerance:** ±{cost_basis_tolerance_pct}%")

    # Run validation
    with st.spinner("Validating portfolio positions..."):
        try:
            result = validator.validate(positions, actual_portfolio_path)

            # Display status banner
            if result.passed:
                if len(result.discrepancies) == 0:
                    st.success(result.summary)
                else:
                    st.info(result.summary)
            else:
                st.error(result.summary)

            # Display metrics
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Calculated Positions", result.total_positions_calculated)
            with col2:
                st.metric("Actual Positions", result.total_positions_actual)
            with col3:
                st.metric("Matched Positions", result.matched_positions)
            with col4:
                critical_count = len(result.critical_discrepancies)
                st.metric(
                    "Critical Issues",
                    critical_count,
                    delta=None if critical_count == 0 else "⚠️ Review Required"
                )

            # Display discrepancies if any
            if result.discrepancies:
                st.markdown("---")
                st.markdown("### 📋 Discrepancies Found")

                # Create DataFrame for display
                discrep_data = []
                for d in result.discrepancies:
                    discrep_data.append({
                        "Severity": d.severity.upper(),
                        "Security": d.security_name,
                        "Symbol": d.symbol,
                        "Type": d.discrepancy_type.value.replace('_', ' ').title(),
                        "Calculated": d.calculated_value,
                        "Actual": d.actual_value,
                        "Difference": d.difference,
                        "Diff %": d.difference_pct,
                        "Details": d.details
                    })

                df = pd.DataFrame(discrep_data)

                # Add severity-based filtering
                severity_filter = st.multiselect(
                    "Filter by Severity",
                    options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                    default=["CRITICAL", "HIGH"]
                )

                if severity_filter:
                    df_filtered = df[df["Severity"].isin(severity_filter)]
                else:
                    df_filtered = df

                # Display table
                st.dataframe(
                    df_filtered,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Severity": st.column_config.TextColumn("Severity", width="small"),
                        "Security": st.column_config.TextColumn("Security", width="medium"),
                        "Symbol": st.column_config.TextColumn("Symbol", width="small"),
                        "Type": st.column_config.TextColumn("Type", width="medium"),
                        "Calculated": st.column_config.NumberColumn("Calculated", format="%.4f", width="small"),
                        "Actual": st.column_config.NumberColumn("Actual", format="%.4f", width="small"),
                        "Difference": st.column_config.NumberColumn("Difference", format="%.4f", width="small"),
                        "Diff %": st.column_config.NumberColumn("Diff %", format="%.2f%%", width="small"),
                        "Details": st.column_config.TextColumn("Details", width="large"),
                    }
                )

            # Export options
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📄 Generate Full Report"):
                    report_text = validator.generate_report(result)
                    st.text_area("Validation Report", report_text, height=400)
                    st.download_button(
                        label="📥 Download Report (TXT)",
                        data=report_text,
                        file_name="portfolio_validation_report.txt",
                        mime="text/plain"
                    )

            with col2:
                if st.button("📊 Export Discrepancies to CSV"):
                    import tempfile
                    import os
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w') as tmp:
                        csv_path = tmp.name

                    validator.export_discrepancies_csv(result, csv_path)

                    with open(csv_path, 'rb') as f:
                        csv_data = f.read()

                    os.unlink(csv_path)

                    st.download_button(
                        label="📥 Download Discrepancies (CSV)",
                        data=csv_data,
                        file_name="portfolio_discrepancies.csv",
                        mime="text/csv"
                    )
                    st.success("CSV exported successfully!")

        except FileNotFoundError as e:
            st.error(f"❌ Actual portfolio file not found: {str(e)}")
            st.info("Please ensure the actual portfolio file path is correctly configured in config.json")
        except Exception as e:
            st.error(f"❌ Validation failed: {str(e)}")
            st.exception(e)


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
