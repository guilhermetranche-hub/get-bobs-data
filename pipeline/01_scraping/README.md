# Estágio 01 — Scraping (Playwright)

## O que faz

Raspa o portal GCOM para extrair os valores válidos de **família de produtos** em cada nível hierárquico:

- **FINALIDADE** (ex: VENDAS, INSUMOS, USO E CONSUMO)
- **GRUPO** (ex: SANDUICHES, BEBIDAS, FRIOS)
- **CATEGORIA** (ex: CLASSICOS, PREMIUM, HAMBURGUERES)
- **TIPO** (ex: BASICOS, RESPONSA)
- **SUBGRUPO** — mapeado separadamente por `scrape_subgroups.py`

## Por que Playwright e não requests?

O GCOM usa **Akamai Bot Manager**. Qualquer requisição HTTP direta é bloqueada ou retorna dados vazios. A única forma confiável de raspar é usar um browser real com `HEADLESS=False` — o Playwright navega na página como um humano, com cookies de sessão autenticados.

## Scripts

| Script | Output |
|---|---|
| `scrape_families.py` | `output/family_lookup_{level}.json` para cada nível (FINALIDADE, GRUPO, CATEGORIA, TIPO) |
| `scrape_subgroups.py` | `output/subgroup_lookup.json` |

## Pré-requisitos

- Sessão autenticada no GCOM (cookies em `.env`)
- Bearer token JWT em `.env`
- Playwright instalado: `pip install playwright && playwright install chromium`

## Como rodar

```bash
python scrape_families.py
python scrape_subgroups.py
```

O progresso é salvo em `output/family_progress_{level}.json` e `output/subgroup_progress.json` — se interromper, continua de onde parou.

## Output esperado

```json
// output/family_lookup_GRUPO.json
{
  "1": "SANDUICHES",
  "2": "BEBIDAS",
  ...
}
```
