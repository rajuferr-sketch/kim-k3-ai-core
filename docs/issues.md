# Guida alle issue

## 1. Scegliere il template giusto

| Situazione | Template |
| --- | --- |
| Il codice lancia un errore riproducibile | 🐞 Bug report |
| Manca una funzionalità o si propone un'architettura | ✨ Feature request |
| Il modello risponde male, allucina o peggiora sui benchmark | 🧠 Model quality |
| Il training o l'inferenza è lento o consuma troppa memoria | ⚡ Performance |
| La documentazione è assente, sbagliata o poco chiara | 📖 Documentation |
| Una vulnerabilità | ❌ nessuna issue: `SECURITY.md` |

## 2. Anatomia di una buona issue

1. **Titolo** specifico: componente + sintomo + contesto.
   ✅ `OOM su k3-ultra con expert parallel 16`
   ❌ `non funziona`
2. **Ambiente** completo: commit SHA, Python, PyTorch, CUDA, driver, GPU, nodi.
3. **Comando esatto** e config YAML usata.
4. **Atteso vs osservato**, con numeri quando possibile.
5. **Riproduzione minima**: il caso più piccolo che mostra il problema.
6. **Log completo** in allegato, non incollato a metà.

## 3. Matrice priorità × impatto

| | Blocca il training | Degrada la qualità | Fastidio con workaround |
| --- | --- | --- | --- |
| **Tutti gli utenti** | P0 | P1 | P2 |
| **Una configurazione** | P1 | P2 | P3 |
| **Caso raro** | P2 | P3 | P3 |

## 4. SLA

| Priorità | Prima risposta | Fix atteso | Postmortem |
| --- | --- | --- | --- |
| P0 | 4 ore | 24 ore | obbligatoria |
| P1 | 24 ore | 7 giorni | consigliata |
| P2 | 72 ore | prossima minor | no |
| P3 | best effort | backlog | no |

## 5. Stati e transizioni

```text
needs-triage → needs-info → (stale dopo 14 giorni) → chiusa
needs-triage → confirmed → in-progress → chiusa da PR
needs-triage → duplicate / wontfix → chiusa con motivazione
in-progress → blocked → in-progress
```

## 6. Per i nuovi contributor

Le issue `good first issue` sono piccole, isolate e già triagate, con un puntatore ai file
da toccare e al test da aggiungere. Commenta per farti assegnare prima di iniziare.

## 7. Cosa chiude una issue

Solo una PR con `Closes #N`, oppure una motivazione esplicita del maintainer
(`duplicate`, `wontfix`, `stale`, non riproducibile). Le issue chiuse per inattività
possono essere riaperte con nuove informazioni.
