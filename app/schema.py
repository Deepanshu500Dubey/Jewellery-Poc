import pandas as pd

CSV_PATH = "app/data/source.csv"

COLUMN_DESCRIPTIONS = {
    "SO Description": "Sales order description or item description",
    "CustCode": "Unique customer code",
    "Dsg Ctg": "Design category (e.g., Necklace, Ring, Bracelet)",
    "Prod Ctg": "Product category or product line",
    "PPC Delivery Period": "Planned delivery period or week for production",
    "Factory": "Factory or manufacturing unit identifier",
    "Set Type": "Set type classification (e.g., MS, WS)",
    "MS Qty": "Quantity of MS (Main Stone) items",
    "WS Qty": "Quantity of WS (Working Stone) items",
    "KT": "Metal purity or karat value",
    "Total Bag Bal": "Total bag balance quantity",
    "Bal To Prod Qty": "Balance quantity yet to be produced",
    "Bal To Exp Qty": "Balance quantity yet to be exported",
    "BalToMfg": "Balance quantity pending manufacturing",
    "CastBal": "Casting balance quantity"
}

def get_csv_schema():
    """
    Returns schema information for the CSV:
    - column name
    - human-readable description
    """
    df = pd.read_csv(CSV_PATH, nrows=0)

    schema = []
    for col in df.columns:
        schema.append({
            "name": col,
            "description": COLUMN_DESCRIPTIONS.get(col, "")
        })

    return schema
