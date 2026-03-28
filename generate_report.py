from pathlib import Path
import pandas as pd

csv_path = Path('/Users/calvin/Documents/datafest/encounters.csv')
cache_path = csv_path.with_name('encounters_cache.parquet')

df = pd.read_parquet(cache_path)

na_patterns = ['not applicable', 'nan', 'n/a', '*not applicable']

# AdmissionSource
src = df.groupby('AdmissionSource', dropna=False).size().reset_index(name='RowCount').sort_values('RowCount', ascending=False)
valid_src = src[~src['AdmissionSource'].fillna('').str.lower().isin(na_patterns)]
na_src = src[src['AdmissionSource'].fillna('').str.lower().isin(na_patterns)]

# AdmissionType
typ = df.groupby('AdmissionType', dropna=False).size().reset_index(name='RowCount').sort_values('RowCount', ascending=False)
valid_typ = typ[~typ['AdmissionType'].fillna('').str.lower().isin(na_patterns)]
na_typ = typ[typ['AdmissionType'].fillna('').str.lower().isin(na_patterns)]

# Create HTML
html = f"""<!DOCTYPE html>
<html>
<head>
    <title>DataFest Encounters Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        h1 {{ color: #333; text-align: center; }}
        h2 {{ color: #555; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-top: 40px; }}
        .summary {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .stat {{ display: inline-block; background: #007bff; color: white; padding: 10px 20px; margin: 5px; border-radius: 5px; }}
        .stat-label {{ font-size: 12px; opacity: 0.9; }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        th {{ background: #007bff; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f8f9fa; }}
        .na-table th {{ background: #6c757d; }}
        .na-table {{ margin-top: 30px; opacity: 0.8; }}
        .section {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .badge {{ display: inline-block; padding: 5px 10px; background: #28a745; color: white; border-radius: 15px; font-size: 12px; }}
        .badge-na {{ background: #dc3545; }}
    </style>
</head>
<body>
    <h1>DataFest Encounters Report</h1>
    
    <div class="summary">
        <h2 style="margin-top: 0;">Dataset Overview</h2>
        <div class="stat">
            <div class="stat-label">Total Rows</div>
            <div class="stat-value">{len(df):,}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Columns</div>
            <div class="stat-value">{df.shape[1]}</div>
        </div>
        <div class="stat" style="background: #28a745;">
            <div class="stat-label">Valid Admission Records</div>
            <div class="stat-value">{valid_src['RowCount'].sum():,}</div>
        </div>
        <div class="stat" style="background: #dc3545;">
            <div class="stat-label">Not Applicable</div>
            <div class="stat-value">{na_src['RowCount'].sum():,}</div>
        </div>
    </div>

    <div class="section">
        <h2>Admission Source <span class="badge">{valid_src['RowCount'].sum():,} valid</span></h2>
        <table>
            <tr><th>Source</th><th>Count</th><th>Percentage</th></tr>
"""

for _, row in valid_src.iterrows():
    pct = row['RowCount'] / len(df) * 100
    html += f"<tr><td>{row['AdmissionSource']}</td><td>{row['RowCount']:,}</td><td>{pct:.1f}%</td></tr>\n"

html += """
        </table>
        
        <h3 style="color: #dc3545;">Not Applicable</h3>
        <table class="na-table">
            <tr><th>Source</th><th>Count</th><th>Percentage</th></tr>
"""

for _, row in na_src.iterrows():
    pct = row['RowCount'] / len(df) * 100
    html += f"<tr><td>{row['AdmissionSource']}</td><td>{row['RowCount']:,}</td><td>{pct:.1f}%</td></tr>\n"

html += f"""
        </table>
    </div>

    <div class="section">
        <h2>Admission Type <span class="badge">{valid_typ['RowCount'].sum():,} valid</span></h2>
        <table>
            <tr><th>Type</th><th>Count</th><th>Percentage</th></tr>
"""

for _, row in valid_typ.iterrows():
    pct = row['RowCount'] / len(df) * 100
    html += f"<tr><td>{row['AdmissionType']}</td><td>{row['RowCount']:,}</td><td>{pct:.1f}%</td></tr>\n"

html += """
        </table>
        
        <h3 style="color: #dc3545;">Not Applicable</h3>
        <table class="na-table">
            <tr><th>Type</th><th>Count</th><th>Percentage</th></tr>
"""

for _, row in na_typ.iterrows():
    pct = row['RowCount'] / len(df) * 100
    html += f"<tr><td>{row['AdmissionType']}</td><td>{row['RowCount']:,}</td><td>{pct:.1f}%</td></tr>\n"

html += """
        </table>
    </div>
</body>
</html>
"""

# Save HTML
html_path = csv_path.with_name('encounters_report.html')
with open(html_path, 'w') as f:
    f.write(html)

print(f"Report saved: {html_path}")
print("\nOpen this file in your browser to view the report.")
