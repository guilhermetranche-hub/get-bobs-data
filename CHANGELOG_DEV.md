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
