import pandas as pd
import json

# Read the Excel file
excel_file = r'C:\AsusWebStorage\ran@benhur.co\MySyncFolder\python\investingAnalysis\Transaction\Data_Files\IBI trans 2024.xlsx'
df = pd.read_excel(excel_file)

# Display basic info
print("=" * 80)
print("EXCEL FILE STRUCTURE")
print("=" * 80)
print(f"\nColumns: {list(df.columns)}")
print(f"\nShape: {df.shape}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")
print(f"\nSample row as JSON:")
sample = df.iloc[0].to_dict()
print(json.dumps(sample, indent=2, default=str))
