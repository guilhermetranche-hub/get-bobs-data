# LEARNINGS — get-bobs-data

Aprendizados **numerados e append-only** sobre como o sistema/domínio funciona **de verdade** —
o conhecimento que normalmente vive só na cabeça de quem construiu e se perde. Cada entrada é
uma verdade dura ganha na prática (uma API que mente, um encoding traiçoeiro, uma regra de
negócio não-óbvia). **Não é changelog** (o que mudou) **nem ADR** (uma decisão): é *o que
descobrimos sobre o terreno*.

> **Por que existe:** é o que faz a próxima pessoa (ou você daqui a 3 meses) **manter e estender**
> sem repetir a investigação na marra. Serve à disciplina de doc da DNA (§11) e ao compounding —
> cada aprendizado registrado é uma categoria de bug que não se repete.

## Regras

- **Numerado e append-only.** Cada aprendizado ganha o próximo número (`## N. <título>`). **Nunca
  apague nem reescreva** um aprendizado antigo — se ele se mostrar errado depois, adicione um novo
  (ex: `## N.1` ou um `## M` novo) que o corrige e **referencia o número antigo**. A trilha do
  que se acreditou (e por que mudou) é parte do valor.
- **Concreto e acionável.** Inclua o sintoma observado, o mecanismo real, e — quando útil — o
  `arquivo:linha`, o comando/query exato, ou o trecho de payload que revela o ponto.
- **Meta-aprendizado é bem-vindo.** Quando um aprendizado revela um *padrão de raciocínio*
  ("antes de implementar fix baseado em memo, re-validar contra o histórico bruto"), registre-o
  explícito — é o mais reutilizável.

---

## 1. `sales_quality_score` não existe na fonte — não fabricar pontuação

A lógica original do pipeline atribuía pontuações fixas: 100 para VENDAS, 50 para INSUMOS, 10 para os demais goals. Essa regra foi planejada como proxy de relevância comercial, mas a fonte (GCOM API) não carrega esse dado. Ao tentar inserir os valores calculados, o banco retornou `numeric field overflow` — a coluna `inv_product_category_duplicate_tranche.sales_quality_score` tem tipo `NUMERIC(3,2)`, que aceita apenas 0.00–9.99. Valores como 10, 50 e 100 simplesmente não cabem.

O ponto mais importante: a pontuação era inferência nossa, não dado da fonte. A coluna existe no schema para ser preenchida por outro processo que tenha acesso ao dado real (ex: histórico de vendas, frequência de pedidos). Inserir um proxy inventado polui o campo e confunde análises futuras.

**Implicação prática:** `sales_quality_score` deve ser inserido como `NULL` neste pipeline. Só preencher quando houver fonte real para o dado. Ver `scripts/populate_inv_table.py` e `docs/Mapping between products.json and inv_product_table.md` — ambos atualizados para refletir isso.
