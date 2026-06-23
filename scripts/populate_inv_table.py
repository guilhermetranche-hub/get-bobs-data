#!/usr/bin/env python3
"""
Sync products.json to Supabase inv_product_category table.

Mapping rules (priority order):
1. If subgroup is 'ADICIONAL' (case-insensitive):
   - category = 'ADICIONAIS'
   - sub_group = original json.category (if not 'ADICIONAIS'), else NULL
2. Else if goal != 'VENDAS':
   - category = goal (e.g., 'USO E CONSUMO', 'INSUMOS')
   - sub_group = subgroup (unchanged)
3. Else (goal == 'VENDAS' and not ADICIONAL):
   - category = json.category (if present, else NULL)
   - sub_group = subgroup

Always:
- main_group = group
- name = product_name
- generic_product_name = generic_product_name (from JSON)
- country = 'Brasil'
- brand = 'bobs'
- classified_by = 'system_import'
- classified_at = current timestamp
- sales_quality_score = 100 (VENDAS), 50 (INSUMOS), 10 (others)
- coupon_quantity_multiplier = 1.0
- other ingredient/purchase fields = NULL
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env from repo root (two levels up from this script)
_REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_REPO_ROOT / ".env")

# ------------------ Configuration ------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TABLE_NAME = "inv_product_category_duplicate_tranche"
PRODUCTS_JSON_PATH = str(_REPO_ROOT / "output" / "products.json")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

# ------------------ Helper Functions ------------------
def derive_row(product: dict) -> dict:
    """Apply mapping rules to a product dict and return a row dict for the table."""
    goal = product.get("goal", "")
    group = product.get("group")
    subgroup = product.get("subgroup")
    json_category = product.get("category")  # from products.json (may be None)
    product_name = product.get("product_name")
    generic_name = product.get("generic_product_name")  # now present in JSON

    # Determine category and sub_group (priority order)
    if subgroup and subgroup.upper() == "ADICIONAL":
        # Rule 2: ADICIONAL override
        category = "ADICIONAIS"
        # sub_group becomes original category (if not "ADICIONAIS")
        if json_category and json_category.upper() != "ADICIONAIS":
            sub_group = json_category
        else:
            sub_group = None
    elif goal != "VENDAS":
        # Rule 1: non-VENDAS -> category = goal
        category = goal
        sub_group = subgroup
    else:
        # Rule 3: VENDAS standard
        category = json_category if json_category else None
        sub_group = subgroup

    # Sales quality score
    if goal == "VENDAS":
        sales_score = 100
    elif goal == "INSUMOS":
        sales_score = 50
    else:
        sales_score = 10

    # Current timestamp for classification
    now = datetime.utcnow().isoformat()

    return {
        "name": product_name,
        "generic_product_name": generic_name,          # from JSON
        "category": category,
        "main_group": group,
        "sub_group": sub_group,
        "country": "Brasil",
        "brand": "bobs",
        "custom_category_client": None,
        "classified_by": "system_import",
        "classified_at": now,
        "sales_quality_score": sales_score,
        "ingredient_name": None,
        "ingredient_match_source": None,
        "ingredient_name_canonical": None,
        "coupon_quantity_multiplier": 1.0,
        "purchase_item_description_canonical": None,
    }

def upsert_product(supabase: Client, row: dict) -> None:
    """Check for existing record by name; update or insert accordingly."""
    name = row["name"]
    # Query for existing row with same name
    response = supabase.table(TABLE_NAME).select("id").eq("name", name).execute()
    if response.data:
        existing_id = response.data[0]["id"]
        row.pop("id", None)
        supabase.table(TABLE_NAME).update(row).eq("id", existing_id).execute()
        print(f"UPDATED: {name}")
    else:
        supabase.table(TABLE_NAME).insert(row).execute()
        print(f"INSERTED: {name}")

# ------------------ Main ------------------
def main():
    # Load products.json
    with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    for product in products:
        row = derive_row(product)
        upsert_product(supabase, row)

    print("Sync completed.")

if __name__ == "__main__":
    main()