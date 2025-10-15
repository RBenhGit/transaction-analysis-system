"""
Test Pydantic validation with real IBI data.

Validates that the transaction model validators work correctly with
actual IBI transaction data without breaking existing functionality.
"""

from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from pydantic import ValidationError


def test_validation_with_real_data():
    """Test transaction validation using real IBI transaction data."""

    print("=" * 80)
    print("Testing Pydantic Validation with Real IBI Data")
    print("=" * 80)

    # Load real IBI transactions
    file_path = "Data_Files/IBI trans 2022-5_10_2025.xlsx"

    print(f"\nLoading transactions from: {file_path}")

    # Step 1: Read Excel file
    reader = ExcelReader()
    df_raw = reader.read(file_path)

    # Step 2: Transform using IBI adapter
    adapter = IBIAdapter()
    df_transformed = adapter.transform(df_raw)

    # Step 3: Convert to Transaction objects (with validation)
    json_adapter = JSONAdapter()

    try:
        transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)
        print(f"SUCCESS: Loaded and validated {len(transactions)} transactions")

        # Check for any validation errors
        validation_errors = 0
        for tx in transactions:
            try:
                # Try to access properties that trigger validation
                _ = tx.is_buy
                _ = tx.is_sell
                _ = tx.transaction_category
            except Exception as e:
                validation_errors += 1
                print(f"  Validation error for {tx.security_symbol}: {e}")

        if validation_errors == 0:
            print("SUCCESS: All transactions passed validation checks")
        else:
            print(f"WARNING: {validation_errors} transactions had validation issues")

        # Test specific validation scenarios
        print("\nValidation Statistics:")

        # Count transactions by category
        categories = {}
        for tx in transactions:
            cat = tx.transaction_category
            categories[cat] = categories.get(cat, 0) + 1

        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} transactions")

        # Check quantity validation
        zero_quantity = sum(1 for tx in transactions if tx.quantity == 0)
        positive_quantity = sum(1 for tx in transactions if tx.quantity > 0)
        print(f"\n  Quantity validation:")
        print(f"    Zero quantity: {zero_quantity}")
        print(f"    Positive quantity: {positive_quantity}")

        # Check currency validation
        currencies = {}
        for tx in transactions:
            currencies[tx.currency] = currencies.get(tx.currency, 0) + 1

        print(f"\n  Currency validation:")
        for curr, count in sorted(currencies.items()):
            print(f"    '{curr}': {count} transactions")

        # Check fee validation
        with_fees = sum(1 for tx in transactions if tx.transaction_fee > 0 or tx.additional_fees > 0)
        print(f"\n  Fee validation:")
        print(f"    Transactions with fees: {with_fees}")

        # Sample some transactions to show validation is working
        print("\nSample validated transactions (first 5):")
        for i, tx in enumerate(transactions[:5]):
            try:
                print(f"  {i+1}. {tx.security_symbol:8} | {tx.transaction_type:20} | "
                      f"Qty: {tx.quantity:>8.2f} | Price: {tx.execution_price:>8.2f} | "
                      f"Currency: {tx.currency}")
            except UnicodeEncodeError:
                # Handle Hebrew text encoding
                print(f"  {i+1}. {tx.security_symbol:8} | [Hebrew type] | "
                      f"Qty: {tx.quantity:>8.2f} | Price: {tx.execution_price:>8.2f} | "
                      f"Currency: {tx.currency}")

        print("\n" + "=" * 80)
        print("Validation Test Completed Successfully!")
        print("=" * 80)

        return True

    except ValidationError as e:
        print(f"\nVALIDATION ERROR: {e}")
        print("\nThis means the validation rules are too strict and need adjustment")
        return False

    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = test_validation_with_real_data()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
