from pathlib import Path
import pandas as pd
from tabulate import tabulate

csv_path = Path('/Users/calvin/Documents/datafest/encounters.csv')
cache_path = csv_path.with_name('encounters_cache.parquet')

if cache_path.exists():
    df = pd.read_parquet(cache_path)
    print("Loaded from cache")
else:
    df = pd.read_csv(csv_path, engine='pyarrow', low_memory=False)
    df.to_parquet(cache_path, index=False)
    print("Loaded CSV and cached")

print(f"\n{'='*60}")
print(f"  DATASET OVERVIEW")
print('='*60)
print(f"  Rows: {len(df):,}")
print(f"  Columns: {df.shape[1]}")

def to_num(s):
    return pd.to_numeric(s, errors='coerce')

# Step 1
step1 = df.copy()
for c in ['AdmitYear', 'AdmitMonth', 'AdmitDay', 'AdmitHour', 'AdmitMinute']:
    step1[f'__{c}_num'] = to_num(step1[c])

step1 = step1.sort_values(
    ['__AdmitYear_num', '__AdmitMonth_num', '__AdmitDay_num', '__AdmitHour_num', '__AdmitMinute_num'],
    ascending=True, na_position='last', kind='stable'
)

print(f"\n{'='*60}")
print("  STEP 1: Admit Date/Time (Ascending)")
print('='*60)
cols = ['AdmitYear', 'AdmitMonth', 'AdmitDay', 'AdmitHour', 'AdmitMinute']
print(tabulate(step1[cols].head(20), headers='keys', tablefmt='grid', showindex=False))

# Step 2 - Filter out "Not Applicable" and similar
admission_source_summary = (
    step1.groupby('AdmissionSource', dropna=False)
    .size()
    .reset_index(name='RowCount')
    .sort_values('RowCount', ascending=False)
)

na_patterns = ['not applicable', 'nan', 'n/a', '*not applicable']
valid_sources = admission_source_summary[
    ~admission_source_summary['AdmissionSource'].fillna('').str.lower().isin(na_patterns)
]
na_sources = admission_source_summary[
    admission_source_summary['AdmissionSource'].fillna('').str.lower().isin(na_patterns)
]

print(f"\n{'='*60}")
print("  STEP 2: Admission Source Summary")
print('='*60)
print("\n--- VALID SOURCES ---")
print(tabulate(valid_sources, headers='keys', tablefmt='grid', showindex=False))
print(f"\n(Total valid: {valid_sources['RowCount'].sum():,} rows)")
print("\n--- NOT APPLICABLE ---")
if len(na_sources) > 0:
    print(tabulate(na_sources, headers='keys', tablefmt='grid', showindex=False))
    print(f"(Total N/A: {na_sources['RowCount'].sum():,} rows)")

# Step 3 - Filter out "Not Applicable"
admission_type_summary = (
    step1.groupby('AdmissionType', dropna=False)
    .size()
    .reset_index(name='RowCount')
    .sort_values('RowCount', ascending=False)
)

valid_types = admission_type_summary[
    ~admission_type_summary['AdmissionType'].fillna('').str.lower().isin(na_patterns)
]
na_types = admission_type_summary[
    admission_type_summary['AdmissionType'].fillna('').str.lower().isin(na_patterns)
]

print(f"\n{'='*60}")
print("  STEP 3: Admission Type Summary")
print('='*60)
print("\n--- VALID TYPES ---")
print(tabulate(valid_types, headers='keys', tablefmt='grid', showindex=False))
print(f"\n(Total valid: {valid_types['RowCount'].sum():,} rows)")
print("\n--- NOT APPLICABLE ---")
if len(na_types) > 0:
    print(tabulate(na_types, headers='keys', tablefmt='grid', showindex=False))
    print(f"(Total N/A: {na_types['RowCount'].sum():,} rows)")

# Step 4
step4 = step1.copy()
step4['__DischargeInstant_dt'] = pd.to_datetime(step4['DischargeInstant'], errors='coerce')
step4 = step4.sort_values('__DischargeInstant_dt', ascending=True, na_position='last', kind='stable')

print(f"\n{'='*60}")
print("  STEP 4: Discharge Date/Time (Ascending)")
print('='*60)
print(tabulate(step4[['DischargeInstant']].head(20), headers='keys', tablefmt='grid', showindex=False))

# Step 5 - Filter out -1 values
step5 = step4.copy()
step5['__AttendingProviderDurableKey_num'] = to_num(step5['AttendingProviderDurableKey'])
step5_valid = step5[step5['__AttendingProviderDurableKey_num'] != -1]
step5_na = step5[step5['__AttendingProviderDurableKey_num'] == -1]
step5 = step5.sort_values('__AttendingProviderDurableKey_num', ascending=True, na_position='last', kind='stable')

print(f"\n{'='*60}")
print("  STEP 5: Attending Provider (Ascending)")
print('='*60)
print("\n--- VALID PROVIDERS (first 20) ---")
print(tabulate(step5_valid[['AttendingProviderDurableKey']].head(20), headers='keys', tablefmt='grid', showindex=False))
print(f"\n(Total valid: {len(step5_valid):,} rows)")
print(f"(Total -1/NA: {len(step5_na):,} rows)")

# Step 6 - Filter out -1 values
step6 = step5.copy()
step6['__DischargeProviderDurableKey_num'] = to_num(step6['DischargeProviderDurableKey'])
step6_valid = step6[step6['__DischargeProviderDurableKey_num'] != -1]
step6_na = step6[step6['__DischargeProviderDurableKey_num'] == -1]
step6 = step6.sort_values('__DischargeProviderDurableKey_num', ascending=True, na_position='last', kind='stable')

print(f"\n{'='*60}")
print("  STEP 6: Discharge Provider (Ascending)")
print('='*60)
print("\n--- VALID PROVIDERS (first 20) ---")
print(tabulate(step6_valid[['DischargeProviderDurableKey']].head(20), headers='keys', tablefmt='grid', showindex=False))
print(f"\n(Total valid: {len(step6_valid):,} rows)")
print(f"(Total -1/NA: {len(step6_na):,} rows)")

# Step 7 - Filter out -1 values
step7 = step6.copy()
step7['__DepartmentKey_num'] = to_num(step7['DepartmentKey'])
step7_valid = step7[step7['__DepartmentKey_num'] != -1]
step7_na = step7[step7['__DepartmentKey_num'] == -1]
step7 = step7.sort_values('__DepartmentKey_num', ascending=True, na_position='last', kind='stable')

print(f"\n{'='*60}")
print("  STEP 7: Department (Ascending)")
print('='*60)
print("\n--- VALID DEPARTMENTS (first 20) ---")
print(tabulate(step7_valid[['DepartmentKey']].head(20), headers='keys', tablefmt='grid', showindex=False))
print(f"\n(Total valid: {len(step7_valid):,} rows)")
print(f"(Total -1/NA: {len(step7_na):,} rows)")

# Step 8 - Filter out -1 values
final_df = step7.copy()
final_df['__PrimaryDiagnosisKey_num'] = to_num(final_df['PrimaryDiagnosisKey'])
final_df_valid = final_df[final_df['__PrimaryDiagnosisKey_num'] != -1]
final_df_na = final_df[final_df['__PrimaryDiagnosisKey_num'] == -1]
final_df = final_df.sort_values('__PrimaryDiagnosisKey_num', ascending=True, na_position='last', kind='stable')

print(f"\n{'='*60}")
print("  STEP 8: Primary Diagnosis (Ascending)")
print('='*60)
print("\n--- VALID DIAGNOSES (first 20) ---")
print(tabulate(final_df_valid[['PrimaryDiagnosisKey']].head(20), headers='keys', tablefmt='grid', showindex=False))
print(f"\n(Total valid: {len(final_df_valid):,} rows)")
print(f"(Total -1/NA: {len(final_df_na):,} rows)")

# Save outputs
final_df.to_csv(csv_path.with_name('encounters_ordered_pipeline.csv'), index=False)
admission_source_summary.to_csv(csv_path.with_name('encounters_by_admissionsource_summary.csv'), index=False)
admission_type_summary.to_csv(csv_path.with_name('encounters_by_admissiontype_summary.csv'), index=False)

print(f"\n{'='*60}")
print("  OUTPUT FILES SAVED")
print('='*60)
print("  - encounters_ordered_pipeline.csv")
print("  - encounters_by_admissionsource_summary.csv")
print("  - encounters_by_admissiontype_summary.csv")
