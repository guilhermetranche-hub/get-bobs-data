# STATUS — get-bobs-data

- Responsável: <nome>
- Última atualização: AAAA-MM-DD — <resumo de 1 linha>

> Cronologia dos trabalhos relevantes (**mais recente em cima**). Mantido pelo agente `planner`.
> É o "onde estamos" — o que está no ar, o que está em andamento, o que ficou pendente.

---

## 2026-06-23 — Sync completo de 1.597 produtos Bob's → Supabase + docs pipeline

✅ Todos os produtos Bob's do `products.json` populados em `inv_product_category_duplicate_tranche`. Pipeline documentado em `pipeline/`. Fix de overflow `NUMERIC(3,2)` em `sales_quality_score`.

**Related:** CHG-20260623-002

### O que foi feito
- 8 batches SQL executados (200 rows cada) via Supabase MCP — todos com ON CONFLICT upsert por `(brand, name, country)`
- `scripts/populate_inv_table.py`: `sales_quality_score` → sempre `None` (removida lógica de proxy score que causava overflow no tipo `NUMERIC(3,2)`)
- `docs/Mapping between products.json and inv_product_table.md`: criado com mapeamento completo campo-a-campo
- `docs/learnings.md`: aprendizado #1 — não fabricar score de campo que não existe na fonte
- `pipeline/`: 5 READMEs documentando fluxo completo (scraping Playwright → API GCOM → products.json → Supabase)

### Impacto / risco
- Baixo — tabela de testes `_duplicate_tranche`; não toca prod
- Contagem final: 1.779 linhas com `brand='bobs'` (1.597 importadas + pré-existentes)

### Follow-ups
- [ ] Validar se o mapeamento está correto com produto real (amostragem visual)
- [ ] Decidir se aponta para `inv_product_category` (prod) após validação

---

## 2026-06-23 — Fix populate_inv_table.py + rodar contra tabela de testes

🔧 Script corrigido para apontar para `inv_product_category_duplicate_tranche`, caminho products.json e dotenv loading. Supabase adicionado ao requirements.txt.

**Related:** —

### O que foi feito
- `scripts/populate_inv_table.py`: `TABLE_NAME` = `inv_product_category_duplicate_tranche`, `PRODUCTS_JSON_PATH` absoluto via `Path(__file__)`, `load_dotenv` adicionado
- `requirements.txt`: `supabase>=2.0.0` adicionado
- `docker-compose.yml`: serviço `populate` adicionado

### Impacto / risco
- Escreve apenas na tabela de testes `_duplicate_tranche`, não em prod

### Follow-ups
- [ ] Criar `.env` com `SUPABASE_URL` e `SUPABASE_KEY` e rodar `docker compose run populate`
- [ ] Após validar, decidir se aponta para `inv_product_category` (prod)

---

## AAAA-MM-DD — <Título do trabalho>
<emoji + contexto de 1 linha>

**Related:** CHG-... · ADR-... · TD-... · investigation BUG-/INV-...

### O que foi feito
- <...>

### Impacto / risco
- <...>

### Follow-ups
- [ ] <pendência>
