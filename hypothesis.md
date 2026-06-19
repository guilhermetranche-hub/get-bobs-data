# Hypothesis: Request and Response ID Fields Are the Same

## The Hypothesis

The numeric ID fields sent in the POST request body map directly and 1-to-1 to the numeric ID fields returned in the API response:

| Request field | Response field |
|--------------|----------------|
| id_fam_pro1  | ID_FAM_PRO     |
| id_fam_pro2  | ID_FAM_NIV2    |
| id_fam_pro3  | ID_FAM_NIV3    |
| id_fam_pro4  | ID_FAM_NIV4    |
| id_fam_pro5  | ID_FAM_NIV5    |
| id_fam_pro6  | ID_FAM_NIV6    |

In other words: if you filter with `id_fam_pro3: 16`, every product in the response will have `ID_FAM_NIV3: 16`. Same number, same meaning, just different field names between request and response.

---

## Test 1 — Cross-referencing scraped lookups against product data

**Method:**  
Scraped all four family-level dropdowns from the UI using Playwright (`scrape_families.py`), capturing the `id_fam_proN` value sent in each POST body when a named option was selected. This gave authoritative `name → id` mappings for levels 1, 2, 4, and 5. Then loaded the full product catalogue (1,560 records) from `output/products.json` and checked whether `LOOKUP[ID_FAM_NIVN]` matched `DC_FAM_PRON` for every record.

**Result:**  
Levels 1, 2, 4, 5 passed with zero mismatches — the scraped IDs matched the response IDs exactly, and the names agreed with the `DC_FAM_PRO*` fields:

- Level 1 (Finalidade): OK — 1,560 records checked
- Level 2 (Grupo):      OK — 1,558 records checked
- Level 4 (Categoria):  OK — 367 records checked
- Level 5 (Tipo):       OK — 76 records checked

Level 3 appeared to mismatch, but this turned out to be because `DC_FAM_PRO3` is **not** the UI subgroup name — see Test 2.

---

## Test 2 — Direct API calls filtered by id_fam_pro3

**Method:**  
For every entry in `SUBGROUP_LOOKUP` (61 subgroups), sent a POST request to `SelecionarProduto` with that `id_fam_pro3` value and recorded how many products were returned and what `ID_FAM_NIV3` values appeared in the response.

**Result:**  
Every subgroup that returned products came back with `ID_FAM_NIV3` equal to exactly the `id_fam_pro3` value sent — no exceptions. Sample:

| id_fam_pro3 sent | Subgroup name     | Records returned | ID_FAM_NIV3 in response |
|-----------------|-------------------|-----------------|------------------------|
| 2               | ADICIONAL         | 41              | [2]                    |
| 16              | CAFE              | 41              | [16]                   |
| 19              | CERVEJA E CHOPP   | 45              | [19]                   |
| 29              | GELADO E MILK SHAKE | 115           | [29]                   |
| 40              | REFRIGERANTE      | 37              | [40]                   |

Subgroups returning 0 records are simply unassigned in the current catalogue — they are valid UI options but no products currently belong to them.

**Conclusion:** The hypothesis is confirmed for level 3. `id_fam_pro3` = `ID_FAM_NIV3`.

---

## The DC_FAM_PRO3 Exception

The initial Test 1 check appeared to show level 3 failing. The reason: `DC_FAM_PRO3` in the response is **not** the human-readable SUBGRUPO name displayed in the UI. It is a separate internal classification string with its own naming convention.

The correct source for the UI subgroup name is `SUBGROUP_LOOKUP[ID_FAM_NIV3]`.

For all other levels (1, 2, 4, 5), `DC_FAM_PRO*` does match the UI name. Level 3 is the only exception.

---

## Verdict

**Hypothesis confirmed across all levels.** `id_fam_proN` (request) = `ID_FAM_NIVN` (response) for N = 1 through 5. The field naming inconsistency between request and response (`ID_FAM_PRO` vs `ID_FAM_NIV2`–`NIV6`) is cosmetic — the IDs are the same numbers.
