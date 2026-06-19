---
name: project-subgroup-lookup
description: id_fam_niv3 lookup table is now wired into fetch.py; subgroup resolved per product record
metadata:
  type: project
---

The `id_fam_niv3` → subgroup name lookup (61 entries, IDs 1–61) was provided by the user and added to `fetch.py` as `SUBGROUP_LOOKUP`.

`filter_products()` now resolves each record's `id_fam_niv3` through the lookup and outputs it as the `subgroup` field.

**Why:** `DC_FAM_PRO3` in the API response does not match the subgroup names shown on the website; the integer ID is the authoritative key.

**How to apply:** If the list grows or changes, update `SUBGROUP_LOOKUP` in `fetch.py` directly.
