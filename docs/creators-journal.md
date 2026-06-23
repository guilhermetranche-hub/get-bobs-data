# CREATOR'S JOURNAL — get-bobs-data

A intenção, as decisões e o raciocínio de **quem construiu**, capturados *enquanto acontecem*.
É o que torna possível uma próxima pessoa **reproduzir os passos** — não só o estado final e as
decisões grandes (isso o `decisions.md` e o `status.md` já dão), mas a *narrativa*: o que se
quis, por que esta ordem, o que se tentou e abandonou, quando a direção virou e o que disparou.

> **Por que existe:** o "porquê" da construção é valiosíssimo e normalmente efêmero — vive só na
> conversa e some. Sem ele, o sucessor reconstrói as decisões mas **não os passos**. **Isto NÃO é
> um execution log** (que rastreia ações do agente) nem um ADR (uma decisão): rastreia o
> **pensamento do humano**. Também alimenta onboarding e a história da tool (marketing/docs).

## Como capturar (baixo atrito — é o ponto)

- **Write-only durante o trabalho.** Anexe uma entrada curta quando o criador expressa intenção;
  **nunca releia o journal inteiro** enquanto trabalha. Cada entrada é auto-contida, escrita do
  contexto que você já tem na conversa (~500–800 tokens/sessão — custo comparável ao do log).
- **Capture quando o criador:** explica *o que* quer construir e *por quê*; toma uma decisão de
  design; **rejeita uma abordagem e explica o motivo**; descreve o problema sendo resolvido;
  compartilha visão/objetivo; dá direção de prioridade/trade-off; expressa satisfação ou recusa
  ("é exatamente isso" / "não, assim não porque…").
- **NÃO capture:** detalhe de implementação trivial, comando rodado, passo mecânico (isso é log),
  nem informação pessoal/privada (este é repo de trabalho — DNA §4 do workspace).

---

## 2026-06-23 — Redirecionar populate para tabela de testes do Guilherme

Guilherme pediu rodar o `populate_inv_table.py` contra `inv_product_category_duplicate_tranche` (cópia da tabela de prod criada para ele testar sem risco). Intenção: validar o mapeamento products.json → Supabase antes de apontar para prod. Trade-off aceito: `TABLE_NAME` centralizado no topo do script — quem quiser mudar de volta para prod altera um único lugar. O path `output/products.json` foi corrigido para ser absoluto relativo ao script, eliminando dependência do diretório de trabalho atual.

---

## AAAA-MM-DD — <Título da entrada / momento>

<A fala/intenção do criador, em 1-4 linhas, na essência. Capture o **porquê** e o **trade-off**,
não o "como" mecânico. Se foi uma rejeição, registre o que foi rejeitado e a razão.>

---

## AAAA-MM-DD — <Próxima entrada>

<...>
