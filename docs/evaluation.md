# Valutazione

## 1. Esecuzione

```bash
python -m kimk3.eval.run --model checkpoints/k3-small --suite all --seed 0
python -m kimk3.eval.run --model checkpoints/k3-small --suite humaneval,mbpp
```

## 2. Suite

| Suite | Cosa misura | Metrica |
| --- | --- | --- |
| MMLU | conoscenza generale | accuracy 5-shot |
| GSM8K | matematica elementare | accuracy, CoT |
| MATH | matematica avanzata | accuracy |
| HumanEval / MBPP | generazione di codice | pass@1 |
| BBH | ragionamento difficile | accuracy 3-shot |
| IFEval | aderenza alle istruzioni | strict/loose |
| LongBench | contesto lungo | punteggio medio |
| τ-bench | uso di strumenti | success rate |
| SWE-bench Verified | patch software reali | % risolte |
| MT-Bench | qualità conversazionale | giudizio 1-10 |

## 3. Regole

- Seed fisso e configurazione salvata accanto a ogni risultato.
- Nessun benchmark nei dati di training: decontaminazione con n-gram overlap.
- I risultati si pubblicano con numero di shot, prompt template e versione del dataset.
- Le regressioni superiori a 1 punto assoluto bloccano il merge.

## 4. Tabella dei risultati

| Benchmark | `k3-nano` | `k3-small` | `k3-base` | `k3-large` |
| --- | --- | --- | --- | --- |
| MMLU | — | — | — | — |
| GSM8K | — | — | — | — |
| HumanEval | — | — | — | — |
| LongBench | — | — | — | — |
| τ-bench | — | — | — | — |

I valori vengono compilati man mano che i run ufficiali vengono completati.

## 5. Valutazione umana

Campione di 200 prompt per release, valutazione in cieco a coppie su utilità,
correttezza, sicurezza e stile. Accordo tra annotatori riportato con Krippendorff's α.
