# Estágio 04 — Sync para o Supabase

## O que faz

Lê o `output/products.json` (estágio 03), aplica as regras de mapeamento e faz **upsert** na tabela `inv_product_category_duplicate_tranche` do Supabase.

## Script

**`scripts/populate_inv_table.py`**

## Regras de mapeamento

A lógica central está em `derive_row()` e segue prioridade estrita — detalhes completos em [`docs/Mapping between products.json and inv_product_table.md`](../../docs/Mapping%20between%20products.json%20and%20inv_product_table.md).

| Condição | `category` | `sub_group` |
|---|---|---|
| `subgroup == 'ADICIONAL'` | `'ADICIONAIS'` | `json.category` (se não for 'ADICIONAIS') |
| `goal != 'VENDAS'` | `goal` | `subgroup` |
| `goal == 'VENDAS'` | `json.category` | `subgroup` |

`main_group` é sempre `group`. `sales_quality_score` é sempre `NULL` (dado não disponível na fonte).

## Upsert

Conflito resolvido por `(brand, name, country)` — único por produto/marca/país. Em caso de conflito, atualiza todos os campos exceto `id`.

## Como rodar

```bash
# Requer SUPABASE_URL e SUPABASE_KEY no .env
python scripts/populate_inv_table.py
```

## Dependências Python

```
supabase
python-dotenv
```

Instalar: `pip install supabase python-dotenv`
