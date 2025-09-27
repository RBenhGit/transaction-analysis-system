#!/usr/bin/env python3
"""
Debug adapter creation
"""

import pandas as pd
from src.json_adapter import JSONAdapter
from src.config_manager import ConfigManager
from adapters.ibi_adapter import IBIAdapter

def main():
    print("Debugging adapter creation...")

    # Load data
    df = pd.read_excel("Data_Files/IBI trans 2022.xlsx", header=None)

    # Test 1: Direct IBI adapter (works)
    print("\n1. Direct IBI adapter:")
    direct_adapter = IBIAdapter()
    result1 = direct_adapter.process_dataframe(df)
    print(f"   Result: {len(result1.transaction_set.transactions) if result1.transaction_set else 0} transactions")

    # Test 2: JSON adapter created IBI adapter
    print("\n2. JSON adapter created IBI adapter:")
    config_manager = ConfigManager()
    json_adapter = JSONAdapter(config_manager)

    # Get the adapter the same way JSON adapter does
    config = config_manager.get_bank_config("IBI")
    print(f"   Config: {config}")

    if config:
        json_created_adapter = IBIAdapter(config)
        result2 = json_created_adapter.process_dataframe(df)
        print(f"   Result: {len(result2.transaction_set.transactions) if result2.transaction_set else 0} transactions")
    else:
        print("   ERROR: No config found")

    # Test 3: Compare configurations
    print("\n3. Configuration comparison:")
    print(f"   Direct adapter config: {direct_adapter.config}")
    if config:
        print(f"   JSON adapter config: {config}")

if __name__ == "__main__":
    main()