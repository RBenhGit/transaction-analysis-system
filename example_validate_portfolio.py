"""
Example: Portfolio Validation

Demonstrates how to validate calculated portfolio against actual broker positions.
"""

import json
import sys
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.input.excel_reader import ExcelReader
from src.modules.portfolio_dashboard import PortfolioBuilder, PortfolioValidator


def load_config():
    """Load configuration file."""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Run portfolio validation example."""
    print("=" * 80)
    print("PORTFOLIO VALIDATION EXAMPLE")
    print("=" * 80)
    print()

    # Load configuration
    config = load_config()
    data_files_dir = Path(config['paths']['data_files'])
    actual_portfolio_path = config['paths']['actual_portfolio']

    # 1. Load transaction files
    print("📂 Loading transaction files...")
    excel_reader = ExcelReader()
    transaction_files = list(data_files_dir.glob("*.xlsx"))

    if not transaction_files:
        print("❌ No transaction files found in Data_Files/")
        return

    print(f"   Found {len(transaction_files)} transaction files")

    # 2. Process transactions with IBI adapter
    print("\n🔄 Processing transactions...")
    adapter = IBIAdapter()
    json_adapter = JSONAdapter()
    all_transactions = []

    for file_path in transaction_files:
        print(f"   Processing: {file_path.name}")
        df = excel_reader.read(str(file_path))
        df_transformed = adapter.transform(df)
        transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)
        all_transactions.extend(transactions)

    print(f"   Loaded {len(all_transactions)} total transactions")

    # 3. Build calculated portfolio
    print("\n📊 Building calculated portfolio...")
    builder = PortfolioBuilder()
    calculated_positions = builder.build(all_transactions)
    print(f"   Calculated {len(calculated_positions)} positions")

    # 4. Validate against actual portfolio
    print("\n🔍 Validating against actual broker positions...")
    print(f"   Actual portfolio file: {Path(actual_portfolio_path).name}")

    validator = PortfolioValidator(
        quantity_tolerance=0.01,          # ±0.01 shares
        cost_basis_tolerance_abs=1.0,     # ±₪1
        cost_basis_tolerance_pct=0.1      # ±0.1%
    )

    try:
        result = validator.validate(calculated_positions, actual_portfolio_path)

        # 5. Display results
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        print()
        print(result.summary)
        print()

        # Metrics
        print("📈 METRICS:")
        print(f"   Calculated Positions: {result.total_positions_calculated}")
        print(f"   Actual Positions:     {result.total_positions_actual}")
        print(f"   Matched Positions:    {result.matched_positions}")
        print(f"   Discrepancies:        {len(result.discrepancies)}")
        print()

        # Show discrepancies by severity
        if result.discrepancies:
            print("⚠️  DISCREPANCIES BY SEVERITY:")
            for severity in ['critical', 'high', 'medium', 'low']:
                severity_discreps = [d for d in result.discrepancies if d.severity == severity]
                if severity_discreps:
                    print(f"   {severity.upper()}: {len(severity_discreps)}")

            print()

            # Show critical and high severity details
            critical_and_high = [d for d in result.discrepancies if d.severity in ['critical', 'high']]
            if critical_and_high:
                print("\n🔴 CRITICAL & HIGH SEVERITY ISSUES:")
                print("-" * 80)
                for d in critical_and_high[:10]:  # Show first 10
                    print(f"\n   [{d.severity.upper()}] {d.security_name} ({d.symbol})")
                    print(f"   Type: {d.discrepancy_type.value.replace('_', ' ').title()}")
                    if d.calculated_value is not None and d.actual_value is not None:
                        print(f"   Calculated: {d.calculated_value:.4f}")
                        print(f"   Actual:     {d.actual_value:.4f}")
                        print(f"   Difference: {d.difference:.4f}")
                        if d.difference_pct:
                            print(f"   Diff %:     {d.difference_pct:.2f}%")
                    print(f"   Details: {d.details}")

                if len(critical_and_high) > 10:
                    print(f"\n   ... and {len(critical_and_high) - 10} more issues")

        # 6. Generate full report
        print("\n" + "=" * 80)
        print("📄 FULL REPORT")
        print("=" * 80)
        report = validator.generate_report(result)
        print(report)

        # 7. Export options
        print("\n" + "=" * 80)
        print("💾 EXPORT OPTIONS")
        print("=" * 80)

        # Export discrepancies to CSV
        if result.discrepancies:
            csv_path = "portfolio_validation_discrepancies.csv"
            validator.export_discrepancies_csv(result, csv_path)
            print(f"✅ Discrepancies exported to: {csv_path}")

        # Save full report to file
        report_path = "portfolio_validation_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Full report saved to: {report_path}")

        print()
        print("=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)

    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("   Please ensure the actual portfolio file path is correct in config.json")
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
