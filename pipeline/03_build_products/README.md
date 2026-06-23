# Estágio 03 — Build products.json

## O que faz

Combina a resposta bruta da API (estágio 02) com os lookups de família/subgrupo (estágio 01) para produzir o `output/products.json` estruturado.

## Onde acontece

Este estágio **não tem script separado** — está embutido no `fetch.py`. Ao final da execução do fetch, o script aplica os lookups e grava o `products.json` diretamente.

## Lógica de combinação

Para cada produto retornado pela API:

1. `IdFamPro1` → lookup `family_lookup_FINALIDADE.json` → `goal`
2. `IdFamPro2` → lookup `family_lookup_GRUPO.json` → `group`
3. `IdFamPro3` → lookup `subgroup_lookup.json` → `subgroup`
4. `IdFamPro4` → lookup `family_lookup_CATEGORIA.json` → `category`
5. `IdFamPro5` → lookup `family_lookup_TIPO.json` → `type`

Se o lookup não encontrar o ID (produto novo ou nível não mapeado pelo scraping), o campo fica `null`.

## Formato do output

```json
[
  {
    "product_code": "370019",
    "product_name": "ABAFADOR DE HB",
    "generic_product_name": "ABAFADOR DE HB",
    "goal": "USO E CONSUMO",
    "group": "USO E CONSUMO",
    "subgroup": null,
    "category": null,
    "type": null
  },
  ...
]
```

**Tamanho atual:** 1.597 produtos (Bob's Brasil).

## Dependência

Os arquivos `output/family_lookup_*.json` e `output/subgroup_lookup.json` precisam existir antes do `fetch.py` rodar para que a combinação seja possível. Se não existirem, os campos de família ficam todos `null`.
