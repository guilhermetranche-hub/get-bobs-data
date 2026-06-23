# Pipeline — get-bobs-data

Fluxo completo de dados do Bob's: da fonte bruta no GCOM até o Supabase.

```
GCOM Website
  ├── Scraping (Playwright)     →  output/family_lookup_*.json
  │                                output/subgroup_lookup.json
  └── API (urllib)              →  output/raw_products.json (intermediário)
          ↓
    Build products.json         →  output/products.json  (1.597 produtos)
          ↓
    Sync para Supabase          →  inv_product_category_duplicate_tranche
```

## Estágios

| Pasta | O que faz | Script principal |
|---|---|---|
| [`01_scraping/`](01_scraping/) | Raspa as famílias e subgrupos do GCOM via browser | `scrape_families.py`, `scrape_subgroups.py` |
| [`02_api_fetch/`](02_api_fetch/) | Busca a lista de produtos via API REST do GCOM | `fetch.py` |
| [`03_build_products/`](03_build_products/) | Combina saídas do scraping + API em `products.json` | veja o README do estágio |
| [`04_sync_supabase/`](04_sync_supabase/) | Upserta `products.json` na tabela do Supabase | `scripts/populate_inv_table.py` |

## Credenciais necessárias

Todas em `.env` na raiz do repo (nunca commitado):

```
API_URL=...
API_TOKEN=Bearer <jwt>
COOKIE_STACKIFY=...
COOKIE_SESSION=...
COOKIE_ASPNET_NAME=...
COOKIE_ASPNET=...
SUPABASE_URL=https://tbwkiluqvgzmixdmfani.supabase.co
SUPABASE_KEY=<service_role_key>
```

## Ordem de execução

```bash
# 1. Scraping de famílias (lento — usa browser real por causa do Akamai)
python scrape_families.py

# 2. Scraping de subgrupos
python scrape_subgroups.py

# 3. Fetch via API
python fetch.py

# 4. Sync para o Supabase
python scripts/populate_inv_table.py
```

> O estágio 03 (build) está embutido no `fetch.py` — ele já monta o `products.json` final usando os lookups do scraping. Veja [`03_build_products/README.md`](03_build_products/README.md) para detalhes.
