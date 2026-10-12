import openpyxl
import pandas as pd
import json
import os

wb_path = 'Online Retail.xlsx'
wb = openpyxl.load_workbook(wb_path, read_only=True)
sheet_names = wb.sheetnames
print('Sheet names:', sheet_names)

df = pd.read_excel(wb_path, sheet_name=sheet_names[0])
print('Shape:', df.shape)
print('Columns:', df.columns.tolist())
print('\nData types:\n', df.dtypes)
print('\nMissing values:\n', df.isnull().sum())
print('\nDuplicates count:', df.duplicated().sum())

# Date range
date_cols = [c for c in df.columns if 'date' in c.lower()]
if date_cols:
    dcol = date_cols[0]
    print(f'Date col ({dcol}): min = {df[dcol].min()}, max = {df[dcol].max()}')

inv_col = [c for c in df.columns if 'invoice' in c.lower()][0]
qty_col = [c for c in df.columns if 'quant' in c.lower()][0]
price_col = [c for c in df.columns if 'price' in c.lower()][0]
cust_col = [c for c in df.columns if 'customer' in c.lower()][0]
stock_col = [c for c in df.columns if 'stock' in c.lower()][0]
country_col = [c for c in df.columns if 'country' in c.lower()][0]

c_invoices = df[df[inv_col].astype(str).str.startswith('C', na=False)]
neg_qty = df[df[qty_col] < 0]
zero_price = df[df[price_col] <= 0]
null_cust = df[df[cust_col].isnull()]

print(f'Invoices starting with C: {len(c_invoices)}')
print(f'Negative quantities: {len(neg_qty)}')
print(f'Zero or negative prices: {len(zero_price)}')
print(f'Missing customer IDs: {len(null_cust)}')
print(f'Unique customers (non-null): {df[cust_col].dropna().nunique()}')
print(f'Unique invoices: {df[inv_col].nunique()}')
print(f'Unique products: {df[stock_col].nunique()}')
print(f'Unique countries: {df[country_col].nunique()}')

print('\nTop 5 countries by rows:')
print(df[country_col].value_counts().head(5))

print('\nFirst 3 rows:')
print(df.head(3))
