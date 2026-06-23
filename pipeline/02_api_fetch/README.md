# Estágio 02 — API Fetch

## O que faz

Busca a lista completa de produtos do Bob's via **API REST do GCOM** e filtra para os campos relevantes.

## Endpoint

```
POST https://www2.gcom.com.br/api/GcomProdutoService/Produto/SelecionarProduto
```

Autenticação: Bearer JWT + cookies de sessão (todos em `.env`).

## Script

**`fetch.py`** — usa `urllib.request` (sem dependência de httpx).

Internamente contém os lookups `FINALIDADE_LOOKUP` e `GRUPO_LOOKUP` para decodificar os IDs retornados pela API em nomes legíveis.

## Output

```
output/raw_products.json   — resposta bruta da API (debug)
output/products.json       — filtrado + enriquecido com lookup de famílias do estágio 01
```

## Como rodar

```bash
python fetch.py
```

## Campos retornados pela API

A API retorna um objeto por produto com vários campos. O `fetch.py` extrai apenas:

| Campo fonte | Campo em `products.json` |
|---|---|
| `NomPro` | `product_name` |
| `NomGenPro` | `generic_product_name` |
| `CodPro` | `product_code` |
| `IdFamPro1` → lookup FINALIDADE | `goal` |
| `IdFamPro2` → lookup GRUPO | `group` |
| `IdFamPro3` → lookup SUBGRUPO | `subgroup` |
| `IdFamPro4` → lookup CATEGORIA | `category` |
| `IdFamPro5` → lookup TIPO | `type` |
