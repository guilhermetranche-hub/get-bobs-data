# STATUS — get-bobs-data

- Responsável: <nome>
- Última atualização: AAAA-MM-DD — <resumo de 1 linha>

> Cronologia dos trabalhos relevantes (**mais recente em cima**). Mantido pelo agente `planner`.
> É o "onde estamos" — o que está no ar, o que está em andamento, o que ficou pendente.

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
