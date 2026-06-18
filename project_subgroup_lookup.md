---
name: project_subgroup_lookup
description: Pending task — wire in id_fam_niv3 → subgroup name lookup table once user provides the mapping
metadata: 
  node_type: memory
  type: project
  originSessionId: 265789bd-982b-4505-87bb-623e24654470
---

The `dc_fam_pro3` field in the API response does NOT contain the subgroup name shown on the website. The actual subgroup is identified by `id_fam_niv3` (set by `id_fam_pro3` in the request payload), which is an integer ID that maps to a subgroup name.

**Why:** The API returns the ID but not the resolved name for level-3 family. The website resolves it client-side from a separate lookup.

**How to apply:** User will provide the full ID → subgroup name table. Once received, add a `SUBGROUP_LOOKUP` dict to [fetch.py](fetch.py) and resolve the name in `filter_products()` — replace the raw `id_fam_niv3` value with the looked-up name under a `subgroup` key.
