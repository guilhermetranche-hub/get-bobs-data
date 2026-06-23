# CHANGELOG_DEV (append-only)

Registro append-only de toda mudança relevante de código. **Nunca edite nem apague entradas
antigas.** Mantido pelo agente `scribe` (e atualizado por `/build`/`/fix` ao concluir). IDs
sequenciais por dia (`CHG-AAAAMMDD-###`).

---

### CHG-AAAAMMDD-001
- Responsável: <nome>
- Data: AAAA-MM-DD
- Tipo: feature | fix | refactor | ui | infra
- Arquivo(s): <caminhos tocados>

**Resumo**
- <o que foi feito, 1–3 linhas>

**Motivação**
- <por quê>

**Impacto / risco**
- <Baixo/Médio/Alto — descrição breve>

**Validação**
- <como foi validado, ou como validar>

---

### CHG-20260623-002
- Owner: Guilherme Tranche
- Date: 2026-06-23
- Type: feature + fix
- File(s): `scripts/populate_inv_table.py`, `docs/Mapping between products.json and inv_product_table.md`, `docs/learnings.md`, `pipeline/README.md`, `pipeline/0{1..4}_*/README.md`

**Summary**
- Upserted 1,597 Bob's products into `inv_product_category_duplicate_tranche` via 8 SQL batches (200 rows each). Removed fabricated `sales_quality_score` proxy logic (NUMERIC(3,2) overflow at values ≥10); column now always NULL. Created `pipeline/` folder with stage-by-stage documentation of the full data flow (scraping → API fetch → build products.json → Supabase sync).

**Motivation**
- Populate the test table with real Bob's product data to validate the `products.json → Supabase` mapping end-to-end. Documentation needed for onboarding and maintainability.

**Impact / risk**
- Low — all writes target `_duplicate_tranche` only; no production table touched. NUMERIC overflow fix prevents silent data corruption in future runs.

**Validation**
- `SELECT COUNT(*) FROM inv_product_category_duplicate_tranche WHERE brand = 'bobs'` returned 1,779 (1,597 new + pre-existing rows). All batches returned `[]` (success). Verified `sales_quality_score IS NULL` throughout.

---

### CHG-20260623-001
- Owner: Guilherme Tranche
- Date: 2026-06-23
- File: `scripts/populate_inv_table.py`, `requirements.txt`, `docker-compose.yml`

**Summary**
- Added environment loading via `python-dotenv`, extracted the target table name into a `TABLE_NAME` constant, fixed the broken relative path for `products.json`, and wired up a `populate` Docker Compose service to run the script in isolation.

**Motivation**
- Enable Guilherme to populate the test duplicate table (`inv_product_category_duplicate_tranche`) safely — validating the `products.json` → Supabase mapping end-to-end — before any writes reach the production table.

**Impact / risk**
- Low — all writes target the duplicate/test table only; no production data is touched. The path fix is a correctness improvement; the `TABLE_NAME` constant prevents accidental prod table writes by making the target explicit in one place.

**Validation**
- Run `docker compose run populate` from the repo root and confirm rows appear in `inv_product_category_duplicate_tranche` on Supabase with the expected field mapping.
