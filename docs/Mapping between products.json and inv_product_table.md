# Data Mapping Rules: `products.json` → `inv_product_category`

## 1. Objective
Define the exact transformation logic to populate the `inv_product_category` table from `products.json`.  
The primary complexity lies in deriving the **`category`** and **`sub_group`** columns, which depend on a strict priority order.

---

## 2. Static / Injected Fields
These values are **not** derived from the JSON; they are supplied externally or set as constants:

| Target Column | Value |
|---------------|-------|
| `brand` | `'bobs'` (injected) |
| `country` | `'Brasil'` (injected) |
| `classified_by` | `'system_import'` |
| `classified_at` | `CURRENT_TIMESTAMP` |
| `coupon_quantity_multiplier` | `1.0` |
| `sales_quality_score` | `NULL` — source data does not carry this information |
| `custom_category_client`, `ingredient_name`, `ingredient_match_source`, `ingredient_name_canonical`, `purchase_item_description_canonical` | `NULL` |

> The `id` is **auto‑generated** by the database (UUID); `product_code` is **not** used as a primary key.

---

## 3. Core Derived Fields
The following columns are computed from the source JSON:

| Target Column | Source / Logic |
|---------------|----------------|
| `name` | `product_name` (direct) |
| `generic_product_name` | `generic_product_name` (from JSON; if absent, strip size/package and `- ITESTQ` from `product_name`) |
| `main_group` | **Always** `group` (no exceptions) |
| `category` | **Priority‑based** (see Section 4) |
| `sub_group` | **Priority‑based** (see Section 4) |

---

## 4. Priority Rules for `category` and `sub_group`

The rules are evaluated in **the exact order** shown below. The first matching condition wins.

### 🔹 Rule 1 – ADICIONAL Override (Highest Priority)
- **Trigger:** `subgroup` (case‑insensitive) equals `'ADICIONAL'` or `'ADICIONAIS'`.
- **Actions:**
  - `category` = `'ADICIONAIS'` (forced constant).
  - `sub_group` =
    - `products.json.category` if that field is **not null** **and** is **not equal** to `'ADICIONAIS'`;
    - otherwise `NULL`.
- **Rationale:** The target table has no `'ADICIONAL'` subgroup. The original source `category` (e.g., `'MOLHOS'`, `'DOCE'`) is demoted to `sub_group` to preserve the semantic context.

---

### 🔹 Rule 2 – Non‑VENDAS Goal
- **Trigger:** `goal != 'VENDAS'` (and **Rule 1 did not apply**).
- **Actions:**
  - `category` = `goal` (e.g., `'INSUMOS'`, `'USO E CONSUMO'`, `'MANUTENCOES E SERVICOS'`).
  - `sub_group` = `subgroup` (preserved as‑is; may be `NULL`).
- **Note:** This overrides any `category` that might exist in `products.json`.

---

### 🔹 Rule 3 – Standard VENDAS (Fallback)
- **Trigger:** `goal == 'VENDAS'` and **Rule 1 did not apply**.
- **Actions:**
  - `category` = `products.json.category` (if present; otherwise `NULL`).
  - `sub_group` = `products.json.subgroup` (if present; otherwise `NULL`).
- **Note:** This is the only case where `category` comes directly from the JSON’s own `category` field.

---

### 🔹 Rule 4 – Guaranteed Hierarchy (Always Applied)
- **`main_group`** is **always** set to `group`, regardless of which rule above fires.

---

## 5. Decision Flowchart (Text Representation)
Is subgroup == 'ADICIONAL' / 'ADICIONAIS'?
│
├── YES → category = 'ADICIONAIS'
│ sub_group = json.category (if NOT null AND != 'ADICIONAIS') else NULL
│
└── NO → Is goal != 'VENDAS'?
│
├── YES → category = goal
│ sub_group = subgroup
│
└── NO → (goal == 'VENDAS')
category = json.category (may be NULL)
sub_group = subgroup (may be NULL)

*main_group is always 'group' in all branches.